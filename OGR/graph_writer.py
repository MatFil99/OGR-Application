
from .share import *
from .graph import *

class GrfParam:

    graph_types_desc = ["undirected", "directed"]
    nrs_edge_params_desc = ["0", "1", "2"]

    def __init__(self) -> None:
        self.graph_type = None
        self.nr_edge_params = None

    def set_nr_edge_params(self, nrparams):
        self.nr_edge_params = nrparams

    def set_graph_type(self, type):
        self.graph_type = type

class GraphWriter:
    
    headerXML = '<?xml version="1.0" encoding="UTF-8" standalone="no"?>\n' \
        '<graphml xmlns="http://graphml.graphdrawing.org/xmlns"\n' \
            'xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"\n' \
            'xmlns:y="http://www.yworks.com/xml/graphml"\n' \
            'xmlns:yed="http://www.yworks.com/xml/yed/3"\n' \
            'xsi:schemaLocation="http://graphml.graphdrawing.org/xmlns\n' \
            'http://www.yworks.com/xml/schema/graphml/1.1/ygraphml.xsd">\n' \
        '<key for="node" id="d1" yfiles.type="nodegraphics"/>\n' \
        '<key for="edge" id="d2" yfiles.type="edgegraphics"/>\n' \
        '<graph edgedefault="directed" id="G">\n'

    footerXML = '</graph>\n' \
        '</graphml>'

    headerGRAPHML = '<?xml version="1.0" encoding="UTF-8"?>\n' \
        '<graphml xmlns="http://graphml.graphdrawing.org/xmlns"\n' \
            'xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"\n' \
            'xsi:schemaLocation="http://graphml.graphdrawing.org/xmlns\n' \
                'http://graphml.graphdrawing.org/xmlns/1.0/graphml.xsd">\n' \
            '<key id="d0" for="node" attr.name="cx" attr.type="int">\n' \
            '<key id="d1" for="node" attr.name="cy" attr.type="int">\n' \
            '<key id="d2" for="node" attr.name="r" attr.type="int">\n' \
            '<key id="d3" for="edge" attr.name="x1" attr.type="int">\n' \
            '<key id="d4" for="edge" attr.name="y1" attr.type="int">\n' \
            '<key id="d5" for="edge" attr.name="x2" attr.type="int">\n' \
            '<key id="d6" for="edge" attr.name="y2" attr.type="int">\n' \
            '<key id="d7" for="edge" attr.name="directed" attr.type="string">\n' \
                '<graph id="G" edgedefault="undirected">\n'

    footerGRAPHML = '</graph>\n' \
        '</graphml>'        

    headerGRF = "Created by OGRpw v1.0\n\n"
    
    def WriteGraph(graph, full_path, grf_params: GrfParam = None):

        try:
            extension = full_path[full_path.rindex("."):]
        except:
            print("Wrong extension")
            return False
        
        return {
            '.graphml': GraphWriter.WriteGraphML,
            '.xml': GraphWriter.WriteXML,
            '.grf': lambda graph, path, params=grf_params: GraphWriter.WriteGrf(graph, path, params)
        }.get(extension, lambda g, f: print("This extension is not available"))(graph, full_path)

    def WriteGraphML(Graph, path):
        success = False

        file_content = GraphWriter.headerGRAPHML

        for vidx in range(0, len(Graph.vertices)):
            v = Graph.vertices[vidx]
            file_content += f'<node id="n{vidx}">\n' \
                    f'<data key="d0">{v.x}</data>\n' \
                    f'<data key="d1">{v.y}</data>\n' \
                    f'<data key="d2">{v.r}</data>\n' \
                '</node>\n'

        for eidx in range(0, len(Graph.edges)):
            e = Graph.edges[eidx]
            directed = "undirected" if e.type == Edge.UNDIRECTED else "directed"
            file_content += f'<edge id="e{eidx}" source="{e.source}" target="{e.target}">\n' \
                    f'<data key="d3">{e.pt1[0]}</data>\n' \
                    f'<data key="d4">{e.pt1[1]}</data>\n' \
                    f'<data key="d5">{e.pt2[0]}</data>\n' \
                    f'<data key="d6">{e.pt2[1]}</data>\n' \
                    f'<data key="d7">{directed}</data>\n' \
                '</edge>\n'

        file_content += GraphWriter.footerGRAPHML
        success = GraphWriter.write_to_file(file_content, path)

        return success

    def WriteXML(Graph, path):
        success = False

        file_content = GraphWriter.headerXML

        for vidx in range(0, len(Graph.vertices)):
            v = Graph.vertices[vidx]
            file_content += f'<node id="n{vidx}">\n' \
                '<data key="d1">\n' \
                    '<y:ShapeNode>\n' \
                        f'<y:Geometry height="{2*v.r}" width="{2*v.r}" x="{v.x}" y="{v.y}"/>\n' \
                        '<y:Fill color="#FFCC00" transparent="false"/>\n' \
                        '<y:BorderStyle color="#000000" type="line" width="4.0"/>\n' \
                        '<y:Shape type="ellipse"/>\n' \
                    '</y:ShapeNode>\n' \
                '</data>\n' \
                '</node>\n'
        for eidx in range(0, len(Graph.edges)):
            e = Graph.edges[eidx]
            s, t = ("none", "none") if e.type == Edge.UNDIRECTED else ("none", f"n{e.target}")
            file_content += f'<edge id="e{eidx}" source="n{e.source}" target="n{e.target}">\n' \
                    '<data key="d2">\n' \
                        '<y:PolyLineEdge>\n' \
                            '<y:LineStyle color="#000000" type="line" width="2.0"/>\n' \
                            f'<y:Arrows source="{s}" target="{t}"/>\n' \
                        '</y:PolyLineEdge>\n' \
                    '</data>\n' \
                '</edge>\n'

        file_content += GraphWriter.footerXML
        success = GraphWriter.write_to_file(file_content, path)

        return success

    def WriteGrf(Graph, path, grf_params: GrfParam = None):
        success = False
        if grf_params is None:
            return success
            
        directed = "nieskierowany" if grf_params.graph_type=="undirected" else "skierowany"
        nparams = grf_params.nr_edge_params

        GraphWriter.remove_undirected_vertices(Graph)

        file_content = GraphWriter.headerGRF
        file_content += f'{directed}\n\n'
        params_str = {
            0: '\n',
            1: '\t0.0\n',
            2: '\t0.0\t0.0\n'
        }.get(nparams, '\n')
        
        for eidx in range(0, len(Graph.edges)):
            e = Graph.edges[eidx]
            file_content += f'{e.source}\t{e.target}' \
                f'{params_str}'
        
        file_content += '\n'
        for vidx in range(0, len(Graph.vertices)):
            v = Graph.vertices[vidx]
            if v:
                file_content += f'{vidx}\t{v.y}.0\t{v.x}.0\n'
                
        success = GraphWriter.write_to_file(file_content, path)

        return success

    def write_to_file(content, path):
        try:
            with open(path, "w") as f:
                f.write(content)
            return True
        except:
            print("ERROR: Path does not exist")
            return False

    def remove_undirected_vertices(Graph):
        for vidx in range(0, len(Graph.vertices)):
            v = Graph.vertices[vidx]
            if v and not v.neighbors:
                print(v)
                Graph.vertices[vidx] = None

    def get_file_extension(path):
        extension = "unknown"
        try:
            extension = path[path.rindex("."):]
        except:
            print("Wrong extension")

        return extension
