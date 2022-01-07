from models.OGR.share import UserParams
from models.GraphModel import GraphModel

gm = GraphModel()

params = UserParams()
params.input_path = r"tests/obrazki_testowe/in5.jpg"
params.output_path = r"tests/results/out.xml"
params.bg_brightness = UserParams.BgBrightness.BG_BRIGHT
params.graph_type = UserParams.GraphType.UNDIRECTED
params.in_img_type = UserParams.InImgType.COMPUTER_IMG
params.vertices_type = UserParams.VerticesType.FILLED

gm.recognize_graph(params)