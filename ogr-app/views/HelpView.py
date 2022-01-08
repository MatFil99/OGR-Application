from tkinter import *
from tkinter import ttk

class HelpView(Toplevel):

    def __init__(self, parent):

        Toplevel.__init__(self, parent)
        top_label_text = "Parameters descrition"

        in_path_text = "Input path"
        out_path_text = "Output path"
        bg_brightness_text = "Background brightness"
        graph_type_text = "Graph type"
        in_img_type_text = "Input image type"
        vert_filled_text = "Vertices filled"

        labels_col0 = [in_path_text, out_path_text, bg_brightness_text, graph_type_text, in_img_type_text, vert_filled_text]

        in_path_desc_text = "Full path to image with graph, which will be processed. \
            Available extensions: .jpg, .png."
        out_path_desc_text = "It is full path (with filename and extension) where the recognized graph will be saved. \
            Remember about extension! Available: .grf (used by Modgraf - WUT's application), .xml (can be read by draw.io) and .graphml \
                (academic format)"
        bg_brightness_desc_text = "Choose BRIGHT if background is brighter than graph. Otherwise DARK."
        graph_type_desc_text = "Type of graph - depending on edge direction"
        in_img_type_desc_text = "Determine input image. If background is plain (one color) choose COMPUTER. The PHOTO \
            value is used for images that background is various brightness levels depending on place."
        vert_filled_desc_text = "Vertices filled - YES, otherwise - NO"

        labels_col1 = [in_path_desc_text, out_path_desc_text, bg_brightness_desc_text, graph_type_desc_text, in_img_type_desc_text, vert_filled_desc_text]

        self.title("Help")
        self.geometry("500x500")
        self.resizable(False, False)

        self.create_label(top_label_text, 0, 0, 2, 1, (N), (10, 10), (20, 20))
        
        for i in range(0, 6):
            self.create_label(labels_col0[i], 0, i+1, 1, 1, (NW), (10, 10), (10, 10))
            self.create_label(labels_col1[i], 1, i+1, 1, 1, (NW), (10,0), (10,10), 300)

    def create_label(self, text, col, row, colspan, rowspan, st, padx, pady, wraptext=0):
        label = ttk.Label(self, text=text)
        label.grid(column=col, row=row, columnspan=colspan, rowspan=rowspan, padx=padx, pady=pady, sticky=st)
        label.configure(wraplength=wraptext)
