from .OGR.share import UserParams

class UserParameters(UserParams):

    def __init__(self) -> None:
        UserParams.__init__(self)
        
    def set_bg_brightness(self, value):
        if value in [item.value for item in UserParameters.BgBrightness]:
            self.bg_brightness = UserParameters.BgBrightness(value)
        # else wrong value

    def set_graph_type(self, value):
        if value in [item.value for item in UserParameters.GraphType]:
            self.graph_type = UserParameters.GraphType(value)
        # else wrong value
        
    def set_in_img_type(self, value):
        if value in [item.value for item in UserParameters.InImgType]:
            self.in_img_type = UserParameters.InImgType(value)
        # else wrong value

    def set_vertices_type(self, value):
        if value in [item.value for item in UserParameters.VerticesType]:
            self.vertices_type = UserParameters.VerticesType(value)
        # else wrong value

    def set_input_path(self, value):
        self.input_path = value

    def set_output_path(self, value):
        self.output_path = value