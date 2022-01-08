# optical graph recognition module

required libraries:
opencv-contrib-python==4.5.3.56 
numpy==1.21.2
pillow==8.3.1

# how to use

# imports:
from .OGR.preprocessing import preprocess
from .OGR.segmentation import segment
from .OGR.topology_recognition import recognize_topology
from .OGR.share import *
from .OGR.graph_writer import GraphWriter
from .OGR.graph import Graph
from .OGR.postprocessing import draw_graph

# run algorithm
preprocessed = preprocess(in_img, user_params)
vertices, vert_img = segment(preprocessed, user_params)
vertices, edges = recognize_topology(preprocessed, vert_img, vertices, user_params)

# input:
- in_img - input image (numpy.ndarray)
- user_params - parameters object (class share.UserParams)

# output:
- vertices list (Vertex class in graph.py file)
- edges list (Edge class in graph.py file)

# write to file:
GraphWriter.WriteGraph(graph, path, grf_params)
- graph - object of graph.Graph class
- path - path to save with filename and extension
- grf_params - .grf format parameters (GrfParam class)