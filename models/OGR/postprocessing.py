import cv2 as cv
import numpy as np
from .share import *
from .graph import *

def draw_graph(size, vertices, edges):

    result = np.ones((size[0], size[1], 3), np.uint8) * 255
    
    for v in vertices:
        cv.circle(result, (v.x, v.y), v.r, Color.GREEN, cv.FILLED)
        cv.putText(result, f"{v.label}", (v.x, v.y), cv.FONT_HERSHEY_SIMPLEX, 0.7, (0,0,0))
        # for i in v.neighbors:
        #     vn = vertices[i]
            # cv.line(result, [v.x, v.y], [vn.x, vn.y], Color.BLUE, thickness=2)

    for eidx in range(0, len(edges)):
        e = edges[eidx]
        pt = ((e.pt1 + e.pt2)/2).astype(int)
        cv.putText(result, f"{eidx}", pt, cv.FONT_HERSHEY_SIMPLEX, 0.7, (0,0,0))
        cv.line(result, e.pt1, e.pt2, Color.BLUE, thickness=2)

        # v1 = vertices[e.source]
        # v2 = vertices[e.target]
        # cv.line(result, (v1.x, v1.y), (v2.x, v2.y), Color.BLUE, thickness=2)

        if e.type == Edge.DIRECTED:
            pt, angle = e.get_arrow_endpoint(vertices)
            if pt is not None:
                pt, pt1, pt2 = get_arrow_points(pt, angle)
                # cv.circle(result, pt, 5, (130, 0, 130), thickness=cv.FILLED)

                cv.line(result, pt, pt1, Color.BLUE, thickness=2)
                cv.line(result, pt, pt2, Color.BLUE, thickness=2)
            
    # cv.imshow("result", result)
    # cv.imwrite(r"results\out.jpg", result)

    result = cv.cvtColor(result, cv.COLOR_BGR2RGB)

    return result