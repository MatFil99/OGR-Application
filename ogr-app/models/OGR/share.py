from enum import Enum

import numpy as np

class Color:
    BG = 0
    WHITE = 255
    BLUE = (255,0,0)
    GREEN = (0,255,0)
    RED = (0,0,255)
    WHITE_RGB = (255,255,255)

class UserParams:

    # BG_BRIGHTNESS
    class BgBrightness(Enum):
        BG_BRIGHT = 0
        BG_DARK = 1

    # GRAPH_TYPE
    class GraphType(Enum):
        DIRECTED = 0
        UNDIRECTED = 1
        AUTO = 2
        
    # IN_IMG_TYPE
    class InImgType(Enum):
        PHOTO_IMG = 0
        COMPUTER_IMG = 1

    class VerticesType(Enum):
        FILLED = 0
        UNFILLED = 1

    UNDEFINED = None

    def __init__(self) -> None:

        self.input_path = UserParams.UNDEFINED
        self.output_path = UserParams.UNDEFINED
        self.bg_brightness = UserParams.UNDEFINED
        self.graph_type = UserParams.UNDEFINED
        self.in_img_type = UserParams.UNDEFINED
        self.vertices_type = UserParams.UNDEFINED

    def correct_parameters_all(self):
        return self.input_path != UserParams.UNDEFINED and \
            self.bg_brightness != UserParams.UNDEFINED and \
            self.graph_type != UserParams.UNDEFINED and \
            self.in_img_type != UserParams.UNDEFINED and \
            self.vertices_type != UserParams.UNDEFINED

    def correct_parameters_required(self):
        return self.input_path != UserParams.UNDEFINED

class Options:
    # preprocessing options
    MAXWIDTH = 1200 # 1400 
    MAXHEIGHT = 800 # 1000
    MAXNOISE = 6 #

    # segmnetation options
    CIRCLE_DETECTION_PRECISION = 50 # ~50 optimal # higher precision causes that more contours (also wrong) can be recognised as a circle
    MIN_VERTEX_RADIUS = int(0.015 * MAXHEIGHT)
    MAX_VERTEX_RADIUS = int(0.2 * MAXHEIGHT)

    # topology recognition options
    MIN_LINE_LENGTH = int(0.005 * MAXHEIGHT)
    MAX_ARROW_EDGE_DIS = 0.75

    XY_THRESHOLD = 8
    ANGLE_THRESHOLD = 25
    RADIUS_NEARBY_LINES = 70
    AREA_VERTEX_EDGE = 2.0 # define how far from vertex can be edge to connect them (radius ratio) 1.2

    MAX_RADIUS_STD = 2 # more than [2] times bigger or smaller vertices are wrong
    MAX_ARROW_LENGTH = int(0.05 * MAXHEIGHT)
    CURVE_ANGLE_THRESHOLD = 40

    UNDEFINED_ANGLE = 361

class Kernel:
    k1 = np.ones((1,1), dtype=np.uint8)
    k2 = np.ones((2,2), dtype=np.uint8)
    k3 = np.ones((3,3), dtype=np.uint8)
    k5 = np.ones((5, 5), dtype=np.uint8)
    k7 = np.ones((7, 7), dtype=np.uint8)

    # to detect intersection of lines
    i1 = np.array([[1, 0, 1],
                  [0, 1, 0],
                  [0, 1, 0]])
    i2 = np.array([[0, 1, 0],
                  [0, 1, 1],
                  [1, 0, 0]])
    i3 = np.array([[1, 0, 0],
                  [0, 1, 0],
                  [1, 0, 1]])
    i4 = np.array([[0, 0, 0],
                  [1, 1, 1],
                  [0, 1, 0]])

    # to detect lines' endpoints
    e1 = np.array([[-1, 1, 1],
                  [-1, 1, -1],
                  [-1, -1, -1]])
    e2 = np.array([[1, 1, -1],
                  [-1, 1, -1],
                  [-1, -1, -1]])
    e3 = np.array([[-1, 1, 1],
                  [-1, 1, 1],
                  [-1, -1, -1]])


lines_intersections_kernels = [
        Kernel.i1,
        Kernel.i2,
        Kernel.i3,
        Kernel.i4
    ]

lines_endpoints_kernels = [ # base kernels to endpoints detection (other can be gained by rotating)
        Kernel.e1,
        Kernel.e2,
        Kernel.e3
    ]

def distance_2P(p1, p2):
    return np.sqrt((p1[0]-p2[0])**2 + (p1[1]-p2[1])**2)

def get_arrow_points(pt, angle):
    arr_length = 15

    angle1 = angle - 180 + 30 if angle>0 else angle + 180 + 30
    angle2 = angle - 180 - 30 if angle>0 else angle + 180 - 30

    tan1 = np.tan(np.radians(angle1))
    tan2 = np.tan(np.radians(angle2))
    
    delta_x1 = np.sqrt(arr_length**2/(1+tan1**2))
    delta_y1 = delta_x1*tan1

    delta_x2 = np.sqrt(arr_length**2/(1+tan2**2))
    delta_y2 = delta_x2*tan2

    if -90 <= angle1 <= 90:
        pt1 = pt + [delta_x1, delta_y1]
    else:
        pt1 = pt - [delta_x1, delta_y1]

    
    if -90 <= angle2 <= 90:
        pt2 = pt + [delta_x2, delta_y2]
    else:
        pt2 = pt - [delta_x2, delta_y2]

    return pt, pt1.astype(int), pt2.astype(int)

def vector_angle(pt1, pt2):
    """
    returns angle between vector and x axis
    angle [-180, 180)
    pt1 - start point of vector
    pt2 - endpoint of vector
    """
    return np.degrees(np.arctan2(pt2[1]-pt1[1], pt2[0]-pt1[0]))