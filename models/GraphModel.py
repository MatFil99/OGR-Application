import cv2 as cv

from .UserParametersModel import UserParameters
from .OGR.preprocessing import preprocess
from .OGR.segmentation import segment
from .OGR.topology_recognition import recognize_topology
from .OGR.share import *
from .OGR.graph_writer import GraphWriter
from .OGR.graph import Graph
from .OGR.postprocessing import draw_graph

class GraphModel(Graph):

    def __init__(self) -> None:
        Graph.__init__(self)
        self.img_height = None
        self.img_width = None
        self.rec_graph_img = None
        # self.graph_image = 

    def recognize_graph(self, user_params: UserParams):
        success = False
        try:
            in_img = cv.imread(user_params.input_path)

            if not user_params.correct_parameters():
                print("Raising exception wrong params")
                raise Exception('Parameters are not set')

            preprocessed = preprocess(in_img, user_params)

            vertices, vert_img = segment(preprocessed, user_params)
            vertices, edges = recognize_topology(preprocessed, vert_img, vertices, user_params)

            self.vertices = vertices
            self.edges = edges
            self.type = user_params.graph_type

            # get size of recognized graph's image (base, which szie will be adjust to frame size)
            self.img_height = preprocessed.shape[0]
            self.img_width = preprocessed.shape[1]
            self.rec_graph_img = draw_graph((self.img_height, self.img_width), self.vertices, self.edges)

            success = True
            
        except:
            print("Error")
            success = False

        return success

    def get_rec_graph_img(self):
        return self.rec_graph_img

    def get_save_file_extension(self, path):
        return GraphWriter.get_file_extension(path)

    def save_graph_as(self, path, grf_params=None):
        success = False
        success = GraphWriter.WriteGraph(self, path, grf_params)
        return success

    def clear_graph(self):
        self.vertices = None
        self.edges = None
        self.type = None

    def graph_exists(self):
        return self.vertices