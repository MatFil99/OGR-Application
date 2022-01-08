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