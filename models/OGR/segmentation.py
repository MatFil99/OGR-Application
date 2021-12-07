import cv2 as cv
import numpy as np

from .graph import *
from .share import *


def segment(preprocessed, user_params: UserParams):
    """
    finds vertices based on closed contours
    return: vertices list, vertices image
    """

    # cv.imshow("preprocessed", preprocessed)

    preprocessed = cv.morphologyEx(preprocessed, cv.MORPH_CLOSE, np.ones((3,3), dtype=np.uint8), iterations=2) # close operation

    # cv.imshow("preprocessed", preprocessed)

    # if vertices are FILLED
    if user_params.vertices_type == UserParams.VerticesType.FILLED:
        preprocessed = skeletonize_thick_obj(preprocessed, 2)

    vertices, vertices_img = find_vertices(preprocessed)



    # cv.imshow("vertices_img", vertices_img)
    # vertices = 0
    # vertices_img = 0

    return vertices, vertices_img

def find_vertices(binary_img):
    """
    detect vertices and fill them
    search contours which look like circles
    return: vertices list, image of filled vertices
    """

    contours, hierarchy = cv.findContours(binary_img, cv.RETR_LIST, cv.CHAIN_APPROX_NONE) # CHAIN_APPROX_SIMPLE
    result_img = np.zeros((binary_img.shape[0], binary_img.shape[1], 1), np.uint8)

    vertices_list = []
    vertices_contours = []

    MIN_ = 1 # to define
    MAX_ = 10000 # to define

    it = 0
    for cnt in contours:
        if MAX_ > len(cnt) > MIN_:
            (x, y), r = cv.minEnclosingCircle(cnt)
            area = cv.contourArea(cnt)
            encl_cir_area = np.pi*r**2
            if area != 0:
                areas_ratio = (encl_cir_area/area - 1)*100 # percent
            else:
                continue # dont analyze 

            if areas_ratio < Options.CIRCLE_DETECTION_PRECISION and \
                    Options.MIN_VERTEX_RADIUS <= r <= Options.MAX_VERTEX_RADIUS:
                v = Vertex(x, y, r, str(it)) 
                vertices_list.append(v)
                vertices_contours.append(cnt)
                it+=1
    
    # remove vertices that intersect (duplicates)
    median_r = np.median([v.r for v in vertices_list]) if vertices_list else 0
    result_vertices = []
    result_contours = []
    idx = 0
    for i in range(0, len(vertices_list)):
        v = vertices_list[i]

        if v is None:
            continue
        intersecting = intersecting_vertices(v, vertices_list)
        idx_best_vertex = i
        diff_r = np.abs(v.r - median_r)
        v_best = vertices_list[i]

        for j in intersecting:
            vj = vertices_list[j]
            if np.abs(vj.r - median_r) < diff_r:
                diff_r = np.abs(vj.r - median_r)
                idx_best_vertex = j
                v_best = vertices_list[idx_best_vertex]

                vertices_list[i] = None # better vertex found, so remove 
            vertices_list[j] = None

        v_best.set_label(str(idx))
        result_vertices.append(v_best)
        result_contours.append(vertices_contours[idx_best_vertex])
        idx += 1

    cv.drawContours(result_img, result_contours, -1, Color.WHITE, thickness=cv.FILLED)
    result_img = cv.dilate(result_img, Kernel.k3, iterations=2)

    # cv.imshow("vertices", result_img)

    return result_vertices, result_img

def intersecting_vertices(vertex, vertices):
    """
    searching vertices (circles) that intersect
    """
    intersecting = []
    for i in range(1, len(vertices)):
        v = vertices[i]
        if v is not None and distance_2P([vertex.x, vertex.y], [v.x, v.y]) < (v.r + vertex.r) and v != vertex:
            intersecting.append(i)

    return intersecting

def skeletonize_thick_obj(binary_img, iters=2):
    """"""
    binary_tmp = binary_img.copy()
    nr_objects, _ = cv.connectedComponents(binary_img, 8)
    any_removed = False
    counter_same_nr = 0
    prev_nr_objs = nr_objects
    it = 0
    max_it = 5
    
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

    return result
