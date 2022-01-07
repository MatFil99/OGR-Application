import cv2 as cv
import numpy as np
import functools

from models.OGR.preprocessing import preprocess

from .share import *
from .graph import *

def recognize_topology(preprocessed, vertices_img, vertices_list, user_params: UserParams):
    """
    """
    # if not vertices_list:
    #     return [], []


    # closed_img = preprocessed
    closed_img = cv.morphologyEx(preprocessed, cv.MORPH_CLOSE, Kernel.k3, iterations=1)

    thinned = skeletonize(closed_img)

    without_intersections = remove_lines_intersections(thinned)

    lines_img = remove_vertices(without_intersections, vertices_img, vertices_list)

    lines = lines_from_contours(lines_img)
    linked_lines = link_nearby_lines(lines_img, lines, vertices_list)
    vertices_linked, connected_edges, unconnected_lines = link_vertices(vertices_list, linked_lines)

    potential_arrow_lines = classify_arrow_lines(unconnected_lines)


    if user_params.graph_type != UserParams.GraphType.UNDIRECTED:
        detect_direction_of_edges(vertices_linked, connected_edges, potential_arrow_lines)

    # draw_graph(preprocessed, vertices_linked, connected_edges)

    return vertices_linked, connected_edges

def draw_graph(img, vertices, edgess):
    img = np.zeros((img.shape[0], img.shape[1], 3), np.uint8)
    for v in vertices:
        pass
        cv.circle(img, (v.x, v.y), v.r, Color.BLUE, thickness=2)
    for e in edgess:
        cv.line(img, e.pt1, e.pt2, Color.GREEN, thickness=2)
    cv.imshow("result", img)
    cv.waitKey()    

def skeletonize(binary_img, opt=cv.ximgproc.THINNING_GUOHALL):
    """
    second option: cv.ximgproc.THINNING_ZHANGSUEN
    """
    
    thinned = cv.ximgproc.thinning(binary_img, opt)
    return thinned

def classify_arrow_lines(lines):
    """
    """

    result_lines = []
    for line in lines:
        if line.length() < Options.MAX_ARROW_LENGTH:
            result_lines.append(line)

    return result_lines

def remove_vertices(img, vertices_img, vertices_list):
    """
    remove vertices from thinned image
    """
    result = cv.subtract(img, vertices_img)

    return result

def remove_lines_intersections(lines_img):
    """
    """
    result = lines_img.copy()

    kn = 0
    for kernel in lines_intersections_kernels:
        kn += 1
        for i in range(0, 4):
            intersections = cv.morphologyEx(lines_img, cv.MORPH_HITMISS, kernel)
            intersections = cv.dilate(intersections, Kernel.k3, iterations=3) # define iterations
            result = cv.subtract(result, intersections)

            kernel = np.rot90(kernel)

    return result

def lines_from_contours(lines_segmented, min_line_length=Options.MIN_LINE_LENGTH):
    """

    returns list of lines (not connected into edges)
    """
    lines_list = []    
    contours, _ = cv.findContours(lines_segmented, cv.RETR_LIST, cv.CHAIN_APPROX_NONE)
    
    tmp = np.zeros((lines_segmented.shape[0], lines_segmented.shape[1], 1), np.uint8)

    for i in range(0, len(contours)):
        cnt = contours[i]
        pt1, pt2 = fit_line(cnt, contours)

        if pt1 is not None and pt2 is not None and distance_2P(pt1, pt2) > min_line_length:
            angle_pt1, angle_pt2 = angles_of_line_endpoints(cnt, pt1, pt2) # calculate angle of endpoints (tangents in endpoints)
            nline = Line(pt1, pt2, angle_pt1, angle_pt2)
            lines_list.append(nline)

            cv.line(tmp, nline.pt1, nline.pt2, Color.WHITE, thickness=1)

    lines_list = sorted(lines_list, key=functools.cmp_to_key(lines_length_compare), reverse=True) # sort descending by length

    return lines_list

def angles_of_line_endpoints(cnt, pt1, pt2):
    angle_pt1 = Options.UNDEFINED_ANGLE
    angle_pt2 = Options.UNDEFINED_ANGLE
    
    neighbors_pt1 = get_nearby_points(pt1, cnt, 10, 15) # 
    neighbors_pt2 = get_nearby_points(pt2, cnt, 10, 15) # 10-15

    if len(cnt) > 0:
        if len(neighbors_pt1) == 0:
            angle_pt1 = vector_angle(pt2, pt1)
        else:
            angle_pt1 = angle_of_tangent(pt1, neighbors_pt1)
        
        if len(neighbors_pt2) == 0:
            angle_pt2 = vector_angle(pt1, pt2)
        else:
            angle_pt2 = angle_of_tangent(pt2, neighbors_pt2)
            
    return angle_pt1, angle_pt2

def get_nearby_points(pt, cnt, min_dis=10, max_dis=15):
    """
    returns array of points which belong to contour and are closer than max_dis and farther than min_dis
    """
    neighbors_points = []
    for point in cnt:
        if min_dis < distance_2P(pt, point[0]) < max_dis:
            neighbors_points.append(point[0])

    return neighbors_points

def angle_of_tangent(pt, neighbors):
    """
    calculate angle of tangent in endpoint - direction is important (from neighbors to endpoint)
    angle between [-180, 180)
    """
    # function to test 

    angle_sum = 0
    angles_list = []
    for point in neighbors:
        angles_list.append(vector_angle(point, pt))
    
    max_diff = max(angles_list) - min(angles_list)

    if max_diff > 180:
        angles_list = np.array(angles_list)
        angles_list = np.where(angles_list < 0, angles_list+360, angles_list) #

    angle_sum = np.sum(angles_list)
    angle_approx = angle_sum / len(neighbors)
    angle_approx = angle_approx if angle_approx < 180 else angle_approx - 360

    return angle_approx

def fit_line(cnt, contours):
    """
    """
    # to test

    endpt1, endpt2 = None, None
    tmp_img = np.zeros((800, 1200, 3), np.uint8)
    cv.drawContours(tmp_img, cnt, -1, (255, 255, 255))

    x_min = min(cnt[:,0,0])
    width = max(cnt[:,0,0]) - x_min
    y_min = min(cnt[:,0,1])
    height = max(cnt[:,0,1]) - y_min

    contour_bmp = np.zeros((height + 3, width + 3, 1), np.uint8)
    neighbors_counter = np.zeros(((len(cnt))), np.uint8)

    for pt in cnt:
        contour_bmp[pt[0,1] - y_min +1 , pt[0,0] - x_min +1] = 1

    for i in range(0, len(cnt)):
        # there could be used cv.filter2D, but it is not needed to get count neighbors for all pixels (only for contour pixels)
        pt = cnt[i] # pt = [x, y]
        neighbors_counter[i] += contour_bmp[pt[0,1] - y_min + 1 -1, pt[0,0] - x_min +1 -1]
        neighbors_counter[i] += contour_bmp[pt[0,1] - y_min + 1 -1, pt[0,0] - x_min +1]
        neighbors_counter[i] += contour_bmp[pt[0,1] - y_min + 1 -1, pt[0,0] - x_min +1 +1]
        neighbors_counter[i] += contour_bmp[pt[0,1] - y_min + 1 , pt[0,0] - x_min +1 -1]
        neighbors_counter[i] += contour_bmp[pt[0,1] - y_min + 1 , pt[0,0] - x_min +1 +1]
        neighbors_counter[i] += contour_bmp[pt[0,1] - y_min + 1 +1, pt[0,0] - x_min +1 -1]
        neighbors_counter[i] += contour_bmp[pt[0,1] - y_min + 1 +1, pt[0,0] - x_min +1 ]
        neighbors_counter[i] += contour_bmp[pt[0,1] - y_min + 1 +1, pt[0,0] - x_min +1 +1]

    one_neighbor = np.where(neighbors_counter==1)

    if len(one_neighbor[0])==2:
        endpt1, endpt2 = cnt[one_neighbor[0][0]][0], cnt[one_neighbor[0][1]][0]
     
    elif len(one_neighbor[0]) < 2:
        # one endpoint is found - searching second
        endpts = [] # list of candidates to be the second endpoint
        contour_bmp = contour_bmp*255
        for kernel in lines_endpoints_kernels:
            for i in range(0, 4):
                endpoints = cv.morphologyEx(contour_bmp, cv.MORPH_HITMISS, kernel)
                y,x = np.where(endpoints>0)
                
                pt2 = [x[0] + x_min - 1, y[0] + y_min - 1] if x != None and y != None else None
                
                if pt2 != None:
                    endpts.append(pt2)
                    # second endpoint is found
                    cv.circle(tmp_img, endpt2, 4, (100, 250, 10), thickness=cv.FILLED)

                kernel = np.rot90(kernel)


        if len(endpts) == 1:
            endpt1 = cnt[one_neighbor[0][0]][0] if len(one_neighbor[0]) == 1 else None
            endpt2 = np.array(endpts[0])
        elif len(endpts) == 2:
            endpt1 = np.array(endpts[0])
            endpt2 = np.array(endpts[1])
    
    return endpt1, endpt2

def link_nearby_lines(img, lines, vertices):
    """
    link lines into edges
    img - segmented lines

    """
    new_lines_list = []

    for i in range(0, len(lines)):
        line1 = lines[i]
        if line1 is None:
            continue
        
        linked = True # check if lines were linked and continue searching possible linking
        while linked:
            nearby_lines = get_nearby_lines(line1, lines, i+1)
            min_delta = Options.XY_THRESHOLD+1 
            best_line_index = -1
            
            for index_nl in nearby_lines:
                line2 = lines[index_nl]

                are_parts, delta = are_parts_of_line_or_curve(line1, line2)

                if are_parts and delta <= min_delta and not is_vertex_between_lines(vertices, line1, line2):
                    min_delta = delta
                    best_line_index = index_nl
                
            if best_line_index != -1:

                line1 = link(line1, lines[best_line_index])
                lines[i] = line1
                lines[best_line_index] = None

            else:
                new_lines_list.append(line1) # add linked line
                linked = False
                

    return new_lines_list

def link(line1, line2):
    """
    """
    pl1, pl2, _, _ = closest_points_of_two_lines(line1, line2) # points which will be connected
    
    # get new endpoints
    nendpt1, nangle_pt1 = (line1.pt1, line1.angle_pt1) if line1.pt1 is not pl1 else (line1.pt2, line1.angle_pt2)
    nendpt2, nangle_pt2 = (line2.pt1, line2.angle_pt1) if line2.pt1 is not pl2 else (line2.pt2, line2.angle_pt2)

    if distance_2P(line2.pt1, line2.pt2) < Options.MIN_LINE_LENGTH * 5:
        new_angle = vector_angle(pl1, pl2)
        if line1.pt1 is not pl1:
            # nangle_pt2 = line1.angle_pt2
            nangle_pt2 = new_angle
        else:
            nangle_pt2 = new_angle
            # nangle_pt2 = line1.angle_pt1


    nline = Line(nendpt1, nendpt2, nangle_pt1, nangle_pt2)

    return nline

def get_nearby_lines(line, lines, start_search_idx = 0, max_distance = Options.RADIUS_NEARBY_LINES):
    """
    returns indexes of nearby lines to given line
    """
    # to eventualy refactor get lines near to endpoint - then change in linking lines

    nearby_lines = []
    for i in range(start_search_idx, len(lines)):
        if lines[i] is None:
            continue
        pt1, pt2, _, _ = closest_points_of_two_lines(line, lines[i]) #

        if distance_2P(pt1, pt2) < Options.RADIUS_NEARBY_LINES and not (pt1[0]==pt2[0] and pt1[1]==pt2[1]):
            nearby_lines.append(i)

    return nearby_lines

def vector2line_angle(vangle):
    """
    returns 
    """
    if -90 <= vangle <= 90:
        return vangle
    elif vangle < -90:
        return vangle + 180
    else:
        return vangle - 180

def line_angle(pt1, pt2):
    """
    returns the angle of the line (unit - degrees)
    returns values [-PI, PI] (ignores direction of vector)
    remember that y axis is directed down
    """
    if (pt2[0] - pt1[0]) == 0:
        if pt2[1] != pt1[1]:
            return 90
        else:
            return Options.UNDEFINED_ANGLE

    angle = np.arctan((pt2[1] - pt1[1])/(pt2[0] - pt1[0]))
    
    return np.degrees(angle)

def are_parts_of_line_or_curve(line1, line2, angle_threshold=Options.ANGLE_THRESHOLD, xy_threshold=Options.XY_THRESHOLD):
    """
    check if lines / curves are parts of one line / curve (if one of them extend, second ) 
    """
    are_parts = False
    delta = Options.XY_THRESHOLD+1
   
    # calculate difference between angles of lines' tangents
    P1, P2, angle_t1, angle_t2 = closest_points_of_two_lines(line1, line2)
    langle_t1, langle_t2 = (vector2line_angle(angle_t1), vector2line_angle(angle_t2))
    P1_angle = line1.angle_pt1 if line1.pt1 is P1 else line1.angle_pt2 # angle
    angle_diff_tang = min(abs(langle_t1 - langle_t2), abs(max(langle_t1,langle_t2) - (180+min(langle_t1,langle_t2))))

    if -angle_threshold <= angle_diff_tang <= angle_threshold:
    
        if -45 <= langle_t1 <= 45:
            y3_p = P1[1] + np.tan(np.radians(angle_t1)) * (P2[0] - P1[0]) # P2.y + tan(angle1) * (P3.x-P2.x)
            delta = min(delta, np.abs(P2[1] - y3_p))
        else:
            
            x3_p = P1[0] + (P2[1] - P1[1])/np.tan(np.radians(angle_t1)) # P1.x + (P2.y - P1.y) / tan(angle1)
            delta = np.abs(P2[0] - x3_p)

    if P1_angle == Options.UNDEFINED_ANGLE or delta > xy_threshold or not smooth_continous(P1, P2, angle_t1):
        return are_parts, Options.XY_THRESHOLD+1

    # linked line must be continuation of line1
    elif abs(abs(angle_t1 - angle_t2) - 180) <= 2*Options.ANGLE_THRESHOLD:
        are_parts = True

    return are_parts, delta #

def smooth_continous(pt1, pt2, angle1):
    if -45 < angle1 < 45:
        if pt1[0] <= pt2[0]:
            return True
    elif -135 < angle1 <= -45:
        if pt1[1] >= pt2[1]:
            return True
    elif 45 <= angle1 < 135:
        if pt1[1] <= pt2[1]:
            return True
    else:
        if pt1[0] >= pt2[0]:
            return True
    
    return False

def is_curve(angle1, angle2, angle3, angle_threshold = 15):
    """
    """
    
    result = False
    a1 = vector2line_angle(angle1)
    a2 = vector2line_angle(angle2)
    a3 = vector2line_angle(angle3)

    max_diff = max(abs(a1-a2), abs(a1-a3), abs(a2-a3))

    if max_diff > Options.CURVE_ANGLE_THRESHOLD:
        result = True
    
    return result
        
def lines_length_compare(line1, line2):
    """
    function compares distances of two lines
    parameters:
    line1
    line2
    return:
    1 - length of line1 is greater than length line2
    0 - lengths of lines are the same
    -1 - line2 is longer than line1
    """
    
    len1 = distance_2P(line1.pt1, line1.pt2)
    len2 = distance_2P(line2.pt1, line2.pt2)
    if len1 > len2:
        return 1
    elif len1 == len2:
        return 0
    else:
        return -1

def is_vertex_between_lines(vertices: list, line1, line2):
    """
    check if circle is between lines
    """
    p1, p2, _, _ = closest_points_of_two_lines(line1, line2)
    p_center = int((p1[0]+p2[0])/2), int((p1[1]+p2[1])/2)
    p1p2_distance = distance_2P(p1, p2)

    for vertex in vertices:
        if distance_2P(p_center, [vertex.x, vertex.y]) < p1p2_distance/2:
            return True
    return False

def closest_points_of_two_lines(line1, line2):
    """
    """
    angle_pt1 = line1.angle_pt1
    angle_pt2 = line2.angle_pt1
    pl1 = line1.pt1
    pl2 = line2.pt1
    dis = [[0,0],[0,0]] # dis [pt_line1, pt_line2]
    dis[0][0] = distance_2P(line1.pt1, line2.pt1)
    dis[0][1] = distance_2P(line1.pt1, line2.pt2)
    dis[1][0] = distance_2P(line1.pt2, line2.pt1)
    dis[1][1] = distance_2P(line1.pt2, line2.pt2)
    arg_min = np.argmin(dis)
    idx_l1, idx_l2 = int(arg_min/2), int(arg_min%2)
    pl1, angle_pt1 = (line1.pt1, line1.angle_pt1) if idx_l1 == 0 else (line1.pt2, line1.angle_pt2)
    pl2, angle_pt2 = (line2.pt1, line2.angle_pt1) if idx_l2 == 0 else (line2.pt2, line2.angle_pt2)

    return pl1, pl2, angle_pt1, angle_pt2

def farthest_points_of_two_lines(line1, line2):
    angle_pt1 = line1.angle_pt1
    angle_pt2 = line2.angle_pt1
    pl1 = line1.pt1
    pl2 = line2.pt1
    dis = [[0,0],[0,0]] # dis [pt_line1, pt_line2]
    dis[0][0] = distance_2P(line1.pt1, line2.pt1)
    dis[0][1] = distance_2P(line1.pt1, line2.pt2)
    dis[1][0] = distance_2P(line1.pt2, line2.pt1)
    dis[1][1] = distance_2P(line1.pt2, line2.pt2)
    arg_min = np.argmax(dis)
    idx_l1, idx_l2 = int(arg_min/2), int(arg_min%2)
    pl1, angle_pt1 = (line1.pt1, line1.angle_pt1) if idx_l1 == 0 else (line1.pt2, line1.angle_pt2)
    pl2, angle_pt2 = (line2.pt1, line2.angle_pt1) if idx_l2 == 0 else (line2.pt2, line2.angle_pt2)

    return pl1, pl2, angle_pt1, angle_pt2

def link_vertices(vertices_list, lines):
    """
    return 
    """
    linked_vertices = []
    incident_matrix = np.zeros((len(vertices_list), len(lines)), dtype=np.int8) # 
    
    linked_edges = []
    other_lines = []

    for lidx in range(0, len(lines)):
        l = lines[lidx]
        near_vertices = nearby_vertices_of_line(l, vertices_list)
        if None not in near_vertices:
            incident_matrix[near_vertices[0], lidx] = 1
            incident_matrix[near_vertices[1], lidx] = 1
    
    for vidx in range(0, len(vertices_list)):
        vertex = vertices_list[vidx]
        for lidx in range(0, len(lines)):
            if incident_matrix[vidx, lidx] != 0 and np.sum(incident_matrix[:,lidx]) == 2:
                
                to_connect = (np.where(incident_matrix[:, lidx] == 1))[0]
                to_connect = to_connect[0] if to_connect[0] != vidx else to_connect[1]
                
                edge = Edge(lines[lidx], vidx, to_connect)
                exists, eidx = edge_exists(edge, linked_edges)
                if not exists:
                    linked_edges.append(edge)
                    eidx = len(linked_edges) - 1

                vertex.add_edge(eidx)
                vertex.add_neighbor(to_connect)

        linked_vertices.append(vertex)
    
    for lidx in range(0, len(lines)):
        if np.sum(incident_matrix[:, lidx]) != 2:
            other_lines.append(lines[lidx])

    return linked_vertices, linked_edges, other_lines

def nearby_vertices_of_line(line, vertices):

    best_v1 = None
    best_v2 = None

    best_dis1 = Options.MAX_VERTEX_RADIUS * Options.AREA_VERTEX_EDGE#(1 + Options.AREA_VERTEX_EDGE)
    best_dis2 = Options.MAX_VERTEX_RADIUS * Options.AREA_VERTEX_EDGE#(1 + Options.AREA_VERTEX_EDGE)


    for vidx in range(0, len(vertices)):
        v = vertices[vidx]

        max_dis1 = v.r * Options.AREA_VERTEX_EDGE#(1 + Options.AREA_VERTEX_EDGE)
        max_dis2 = v.r * Options.AREA_VERTEX_EDGE#(1 + Options.AREA_VERTEX_EDGE)

        dis1 = distance_2P([v.x, v.y], line.pt1) - v.r
        dis2 = distance_2P([v.x, v.y], line.pt2) - v.r
        # if dis1 < dis2:
        if  dis1 < max_dis1 and dis1 < best_dis1:
            best_dis1 = dis1
            best_v1 = vidx
        # else:
        if dis2 < max_dis2 and dis2 < best_dis2:
            best_dis2 = dis2
            best_v2 = vidx
    
    return [best_v1, best_v2]

def edge_exists(edge, edges):
    """
    check if edge is in edges list
    parameters:

    """
    for eidx in range(0, len(edges)):
        e = edges[eidx]
        if edge == e:
            return True, eidx
    return False, None

def closest_vertex_to_line(line, vertices):
    """
    return the closest vertex to given line and distance between them
    """
    min_distance = Options.MAXWIDTH #
    vertex = None

    for v in vertices:
        distance = min(distance_2P(line.pt1, [v.x, v.y]), distance_2P(line.pt2, [v.x, v.y]))
        if distance < min_distance:
            vertex = v
            min_distance = distance

    return vertex, min_distance

def detect_direction_of_edges(vertices, edges, potential_arrow_lines):
    """
    """

    for pa_line in potential_arrow_lines:
        vertex, distance = closest_vertex_to_line(pa_line, vertices)
        closest_edge = None

        if vertex and distance <= vertex.r * (1+Options.AREA_VERTEX_EDGE):
            min_distance = vertex.r * Options.MAX_ARROW_EDGE_DIS # arrow must be close to edge to be classify as its arrow
            closest_edge = None
            for eidx in vertex.edges:
                e = edges[eidx]
                pt1, pt2, _, _ = closest_points_of_two_lines(pa_line, e) # change name to closest_endpoints_of_two_lines
                d = distance_2P(pt1, pt2)
                if d < min_distance:
                    min_distance = d
                    closest_edge = eidx

            if closest_edge is not None:
                pass
                arr_edge = edges[closest_edge]
                arr_edge.type = Edge.DIRECTED
                v_target = int(vertex.label) # convert label to index
                if arr_edge.target != v_target:
                    temp = arr_edge.source
                    arr_edge.source = arr_edge.target
                    arr_edge.target = temp