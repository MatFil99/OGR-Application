from tkinter import *
from tkinter import ttk
# from tkinter import font
# from tkinter.font import Font
# from PIL import ImageTk, Image, JpegImagePlugin
# import PIL

from models.GrfParamModel import *

class FileWOpt(Toplevel):

    GRAPH_TYPE_DESC = ["select", "undirected", "directed"]
    EDGE_PARAMS_NR_DESC = ["select", "0 - no parameters", "1 - weigth of edge", "2 - weight and cost"]

    def __init__(self, master = None, grf_params: GrfParam = None ):
        super().__init__(master = master)

        self.title("File save options")
        self.geometry("320x160")
        self.desc = ttk.Label(self, text = "Enter file .grf parameters:", padding=(10,10,10,10), font=("TkDefaultFont",11))
        self.desc.grid(column=0, row=0, columnspan=2, rowspan=1, sticky=W)
        self.graph_type_label = ttk.Label(self, text = "Graph type:", padding=(10,10,10,10))
        self.graph_type_label.grid(column=0, row=1, columnspan=1, rowspan=1, sticky=W)
        graph_type = StringVar(None, FileWOpt.GRAPH_TYPE_DESC[0])
        self.droplist_gt = ttk.OptionMenu(self, graph_type, *FileWOpt.GRAPH_TYPE_DESC, command=lambda grfpar=grf_params, g_type=graph_type: self.graph_type_change(grf_params, g_type))
        self.droplist_gt.grid(column=1, row=1, columnspan=1, rowspan=1, sticky=W)

        self.edge_params_nr_label = ttk.Label(self, text = "Number of edge parameters:", padding=(10,10,10,10))
        self.edge_params_nr_label.grid(column=0, row=2, columnspan=1, rowspan=1, sticky=W)
        edge_params_nr = StringVar(None, FileWOpt.EDGE_PARAMS_NR_DESC[0])
        self.droplist_epnr = ttk.OptionMenu(self, edge_params_nr, *FileWOpt.EDGE_PARAMS_NR_DESC, command=lambda grfpar=grf_params, eparams=edge_params_nr: self.edge_params_nr_change(grf_params, eparams))
        self.droplist_epnr.grid(column=1, row=2, columnspan=1, rowspan=1, sticky=W)

        self.ok_btn = ttk.Button(self, text="OK", command=self.ok_action)
        self.ok_btn.grid(column=0, row=3, columnspan=1, rowspan=1, sticky=W, padx=(10,0))
        self.cancel_btn = ttk.Button(self, text="Cancel", command=lambda gparams=grf_params: self.cancel_action(gparams))
        self.cancel_btn.grid(column=1, row=3, columnspan=1, rowspan=1, sticky=W, padx=(55,0))

    def graph_type_change(self, grf_params: GrfParam = None, var = None):
        idx = FileWOpt.GRAPH_TYPE_DESC.index(var.get())
        
        if 0 < idx < 3:
            grf_params.set_graph_type(FileWOpt.GRAPH_TYPE_DESC[idx])


    def edge_params_nr_change(self, grf_params: GrfParam = None, var = None):
        idx = FileWOpt.EDGE_PARAMS_NR_DESC.index(var.get()) -1
        if -1 < idx < 3:
            grf_params.set_nr_edge_params(idx)
        
    def cancel_action(self, grf_params: GrfParam = None):
        grf_params.set_graph_type(None)# undefined
        grf_params.set_nr_edge_params(None)# undefined
        self.destroy()

    def ok_action(self):
        self.destroy()