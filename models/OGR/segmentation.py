import cv2 as cv
import numpy as np
from numpy.core.numeric import count_nonzero

from .graph import *
from .share import *


def segment(preprocessed, user_params: UserParams):
    """
    finds vertices based on closed contours
    return: vertices list, vertices image
    """

    preprocessed = cv.morphologyEx(preprocessed, cv.MORPH_CLOSE, np.ones((3,3), dtype=np.uint8), iterations=2) # close operation

    # if vertices are FILLED
    if user_params.vertices_type == UserParams.VerticesType.FILLED:
        filled_vertices_img = get_filled_vertices(preprocessed, 2)
        vertices, vertices_img = find_filled_vertices(filled_vertices_img)
    # if vertices are UNFILLED
    else:
        vertices, vertices_img = find_unfilled_vertices(preprocessed)

    # cv.imshow("vertices_img", vertices_img)
    # cv.waitKey()

    return vertices, vertices_img

def find_filled_vertices(binary_img):
    pass

    contours, _ = cv.findContours(binary_img, cv.RETR_LIST, cv.CHAIN_APPROX_NONE)
    result = np.zeros((binary_img.shape[0], binary_img.shape[1], 1), np.uint8)
    vertices_list = []

    it = 0
    for c in contours:
        (x, y), r = cv.minEnclosingCircle(c)
        if Options.MIN_VERTEX_RADIUS <= r <= Options.MAX_VERTEX_RADIUS:
            v = Vertex(int(x), int(y), int(r), str(it))
            vertices_list.append(v)
            cv.circle(result, (v.x,v.y), v.r, Color.WHITE, thickness=cv.FILLED)
            it+=1

    return vertices_list, result

def find_unfilled_vertices(binary_img):
    """
    detect vertices and fill them
    search contours which look like circles
    return: vertices list, image of filled vertices
    """

    # temp = np.ones((binary_img.shape[0],binary_img.shape[1],3), np.uint8)*255


    contours, hierarchy = cv.findContours(binary_img, cv.RETR_LIST, cv.CHAIN_APPROX_NONE) # CHAIN_APPROX_SIMPLE
    result_img = np.zeros((binary_img.shape[0], binary_img.shape[1], 1), np.uint8)

    vertices_list = []
    vertices_contours = []
    vertices_ratios = []

    # minimum and maximum contours which can be detect as vertex
    MIN_ = 1 # to define
    MAX_ = 10000 # to define

    it = 0
    for cnt in contours:
        if MAX_ > len(cnt) > MIN_:
            (x, y), r = cv.minEnclosingCircle(cnt)
            area = cv.contourArea(cnt)
            encl_cir_area = np.pi*r**2 - 2*np.pi*r
            if area != 0:
                areas_ratio = (encl_cir_area/area - 1)*100 # percent
            else:
                continue # dont analyze 

            if areas_ratio < Options.CIRCLE_DETECTION_PRECISION and \
                    Options.MIN_VERTEX_RADIUS <= r <= Options.MAX_VERTEX_RADIUS:
                # print(f"{Options.MIN_VERTEX_RADIUS} <= {r} <= {Options.MAX_VERTEX_RADIUS} ")
                v = Vertex(x, y, r, str(it)) 
                vertices_list.append(v)
                vertices_contours.append(cnt)
                vertices_ratios.append(areas_ratio)
                it+=1

    # remove vertices that intersect (duplicates)
    result_vertices, result_contours = remove_interseting_vertices(vertices_list,vertices_ratios,vertices_contours)

    cv.drawContours(result_img, result_contours, -1, Color.WHITE, thickness=cv.FILLED)

    result_img = cv.dilate(result_img, Kernel.k3, iterations=2)# or it = 2

    return result_vertices, result_img

def remove_interseting_vertices(vertices_list, vertices_ratios, vertices_contours):
    median_r = np.median([v.r for v in vertices_list]) if vertices_list else 0
    result_vertices = []
    result_contours = []
    idx = 0
    for i in range(0, len(vertices_list)):
        v = vertices_list[i]

        if v is None:
            continue
        
        if v.r > Options.MAX_RADIUS_STD * median_r or v.r < median_r / Options.MAX_RADIUS_STD:
            vertices_list[i] = None
            continue

        intersecting = intersecting_vertices(v, vertices_list)
        cir_ratio = vertices_ratios[i]
        proper_cir = True

        for j in intersecting:
            vj = vertices_list[j]
            if vj.r > Options.MAX_RADIUS_STD * median_r or vj.r < median_r / Options.MAX_RADIUS_STD:
                continue
            vj = vertices_list[j]
            if vertices_ratios[j] < cir_ratio:
                proper_cir = False
                break

        if proper_cir:
            for j in intersecting:
                vertices_list[j] = None
            v.set_label(str(idx))
            result_vertices.append(v)
            result_contours.append(vertices_contours[i])
            idx += 1
        else:
            vertices_list[i] = None

    return result_vertices, result_contours


def intersecting_vertices(vertex, vertices):
    """
    searching vertices (circles) that intersect
    """
    intersecting = []
    for i in range(1, len(vertices)):
        v = vertices[i]
        if v is not None and distance_2P([vertex.x, vertex.y], [v.x, v.y]) < (v.r + vertex.r + Options.MIN_LINE_LENGTH) and v != vertex:
            intersecting.append(i)

    return intersecting

def get_filled_vertices(binary_img, iters=2):
    """"""
    binary_tmp = binary_img.copy()
    nr_objects, _ = cv.connectedComponents(binary_img, 8)
    any_removed = False
    counter_same_nr = 0
    prev_nr_objs = nr_objects
    it = 0
    max_it = 10
    
    while (not any_removed or counter_same_nr < 2) and it < max_it:
        binary_tmp = cv.erode(binary_tmp, Kernel.k3, iterations=iters)
        new_nr_objs, _ = cv.connectedComponents(binary_tmp, 8)
        if new_nr_objs != nr_objects:
            any_removed = True
        if new_nr_objs == prev_nr_objs:
            counter_same_nr += 1
        else:
            counter_same_nr = 0

        prev_nr_objs = new_nr_objs
        it += 1

    result = cv.dilate(binary_tmp, Kernel.k3, iterations=it*iters)
    # cv.imshow("result", result)
    # cv.imshow("binary_img", binary_tmp)
    # cv.waitKey()

    return result
