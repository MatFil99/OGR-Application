from .share import *

class Graph:# GraphTopology
    # type directed or undirected
    UNDIRECTED = 0
    DIRECTED = 1

    def __init__(self) -> None:
        self.type = None
        self.vertices = None
        self.edges = None

    def get_type(self):
        return self.type

class Vertex:

    count = 0
    def __init__(self, x, y, r, label = None):
        self.label = label
        self.x = int(x)
        self.y = int(y)
        self.r = int(r)
        self.neighbors = [] # list of unique vertices' labels

        self.edges = [] # list of all connected edges

    def __str__(self) -> str:
        return str(f"label = {self.label}, (x = {self.x}, y = {self.y}), r = {self.r}")

    def __eq__(self, o: object) -> bool:
        return self.label == o.label and self.x==o.x and self.y==o.y and self.r==o.r

    def add_edge(self, edge):
        self.edges.append(edge)

    def add_neighbor(self, v):
        self.neighbors.append(v)

    def set_label(self, nlabel):
        self.label = nlabel

    def print_edges(self):
        print(self)
        for e in self.edges:
            print(e)

class Line:
    LINE = 0
    CURVE = 1
    def __init__(self, pt1, pt2, angle_pt1, angle_pt2):
        self.pt1 = pt1
        self.pt2 = pt2
        self.angle_pt1 = angle_pt1
        self.angle_pt2 = angle_pt2

    def __str__(self) -> str:
        return str(f"[{self.pt1}, {self.pt2}] angles: [{self.angle_pt1}, {self.angle_pt2}]")

    def length(self):
        return distance_2P(self.pt1, self.pt2)

class Edge(Line):
    UNDIRECTED = 0
    DIRECTED = 1
    
    def __init__(self, line, source, target, type=UNDIRECTED):
        Line.__init__(self, line.pt1, line.pt2, line.angle_pt1, line.angle_pt2)
        self.source = source
        self.target = target
        self.type = type

    def __str__(self) -> str:
        return f"source = {self.source} target = {self.target} type = {self.type}"

    def __eq__(self, o: object) -> bool:
        if type == Edge.DIRECTED:
            return self.source == o.source and self.target==o.target and self.type==o.type
        return self.type==o.type and \
            ((self.source == o.source and self.target==o.target) or (self.source == o.target and self.target == o.source))
            
    def get_arrow_endpoint(self, vertices):
        arrow_endpt = None
        arrow_angle = None

        v = vertices[self.target]
        
        d1 = distance_2P([v.x, v.y], self.pt1)
        d2 = distance_2P([v.x, v.y], self.pt2)

        if d1 <= d2:
            arrow_endpt = self.pt1
            arrow_angle = vector_angle(self.pt2, self.pt1)
        else:
            arrow_endpt = self.pt2
            arrow_angle = vector_angle(self.pt1, self.pt2)

        return arrow_endpt, arrow_angle