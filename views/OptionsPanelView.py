from tkinter import *
from tkinter import ttk
from tkinter import font
from tkinter import filedialog
from tkinter.font import Font
from PIL import ImageTk, Image
from cv2 import stylization


class OptionsPanel(ttk.Frame):
    UNDEFINED = -1

    def __init__(self,controller, root) -> None:
        ttk.Frame.__init__(self, root, padding=(5,5,5,5), borderwidth=5, relief="solid", width=550, height=650)
        self.controller = controller

        ttk.Style().configure('btnfont.TButton', font=("TkDefaultFont",9))
        ttk.Style().configure('rbtnfont.TRadiobutton', font=("TkDefaultFont", 10))

        # left side labels
        self.file_opt_label = ttk.Label(self, text="Input and output file parameters", font=("TkDefaultFont",12), padding=(0, 20, 0, 30)) \
            .grid(column=0, row=1, columnspan=6, rowspan=1)
        self.in_img_path_l = ttk.Label(self, text="Input graph's path:", font=("TkDefaultFont",10), padding=(0, 0, 0, 10)) \
            .grid(column=0, row=2, columnspan=6, rowspan=1, sticky=(W))
        self.save_file_path_l = ttk.Label(self, text="Save path:", font=("TkDefaultFont",10), padding=(0, 20, 0, 10)) \
            .grid(column=0, row=4, columnspan=6, rowspan=1, sticky=(W))


        self.recog_par_label = ttk.Label(self, text="Graph and image parameters", font=("TkDefaultFont",12), padding=(0, 30, 0, 30)) \
            .grid(column=0, row=6, columnspan=6, rowspan=1)
        self.bg_brigthness_l = ttk.Label(self, text="Background brightness", font=("TkDefaultFont",10), padding=(0, 0, 0, 10)) \
            .grid(column=0, row=7, columnspan=2, rowspan=1, sticky=(W))
        self.graph_type_l = ttk.Label(self, text="Graph type", font=("TkDefaultFont",10), padding=(0, 0, 0, 10)) \
            .grid(column=0, row=8, columnspan=2, rowspan=1, sticky=(W))
        self.in_img_type_l = ttk.Label(self, text="Input image type", font=("TkDefaultFont",10), padding=(0, 0, 0, 10)) \
            .grid(column=0, row=9, columnspan=2, rowspan=1, sticky=(W))
        self.vertices_filled_l = ttk.Label(self, text="Vertices filled", font=("TkDefaultFont",10), padding=(0, 0, 0, 10)) \
            .grid(column=0, row=10, columnspan=2, rowspan=1, sticky=(W))

        # text fields and browse buttons
        in_path_var = StringVar()
        # in_path_var.trace("w", lambda name, index, mode, var=in_path_var: self.controller.in_path_changed(var))
        self.in_path_entry = ttk.Entry(self, font=("TkDefaultFont",9), textvariable=in_path_var)
        self.in_path_entry.grid(column=0, row=3, columnspan=5, rowspan=1, sticky=(W, E))
        self.in_path_entry.bind("<FocusOut>", lambda e, var=in_path_var: self.controller.in_path_changed(var))

        out_path_var = StringVar()
        # out_path_var.trace("w", lambda name, index, mode, var=out_path_var: self.controller.out_path_changed(var))
        self.save_path_entry = ttk.Entry(self, font=("TkDefaultFont",9), textvariable=out_path_var)
        self.save_path_entry.grid(column=0, row=5, columnspan=5, rowspan=1, sticky=(W, E))
        self.save_path_entry.bind("<FocusOut>", lambda e, var=out_path_var: self.controller.out_path_changed(var))
        self.in_fd_button = ttk.Button(self, text="Browse", style='btnfont.TButton', command = lambda var=in_path_var : self.load_filedialog(var)) \
            .grid(column=4, row=3, columnspan=1, rowspan=1, sticky=(E))
        self.save_fd_button = ttk.Button(self, text="Browse", style='btnfont.TButton', command = lambda var=out_path_var : self.save_filedialog(var)) \
            .grid(column=4, row=5, columnspan=1, rowspan=1, sticky=(E))

        # Radiobuttons
        brightness_var = IntVar(None, OptionsPanel.UNDEFINED) # BRIGHT = 0, DARK = 1
        brightness_var.trace("w", lambda name, index, mode, bv=brightness_var: controller.brightness_variable_changed(bv))
        self.bright_rb = ttk.Radiobutton(self, text="BRIGHT", variable=brightness_var, value=0, style='rbtnfont.TRadiobutton', padding=(20, 0, 0, 10)) \
            .grid(column=2, row=7, columnspan=1, rowspan=1, sticky=(W))
        self.dark_rb = ttk.Radiobutton(self, text="DARK", variable=brightness_var, value=1, style='rbtnfont.TRadiobutton', padding=(0, 0, 0, 10)) \
            .grid(column=3, row=7, columnspan=1, rowspan=1, sticky=(W))

        direction_var = IntVar(None, OptionsPanel.UNDEFINED) # DIRECTED = 0, UNDIRECTED = 1, MIXED = 2 (0)
        direction_var.trace("w", lambda name, index, mode, var=direction_var: controller.direction_variable_changed(var))
        self.directed_rb = ttk.Radiobutton(self, text="DIRECTED", variable=direction_var, value=0, style='rbtnfont.TRadiobutton', padding=(20, 0, 0, 10)) \
            .grid(column=2, row=8, columnspan=1, rowspan=1, sticky=(W))
        self.undirected_rb = ttk.Radiobutton(self, text="UNDIRECTED", variable=direction_var, value=1, style='rbtnfont.TRadiobutton', padding=(0, 0, 0, 10)) \
            .grid(column=3, row=8, columnspan=1, rowspan=1, sticky=(W))
        self.mixed_rb = ttk.Radiobutton(self, text="MIXED", variable=direction_var, value=2, style='rbtnfont.TRadiobutton', padding=(0, 0, 0, 10)) \
            .grid(column=4, row=8, columnspan=1, rowspan=1, sticky=(W))

        image_type_var = IntVar(None, OptionsPanel.UNDEFINED)
        image_type_var.trace("w", lambda name, index, mode, var=image_type_var: controller.image_type_variable_changed(var))
        self.photo_rb = ttk.Radiobutton(self, text="PHOTO", variable=image_type_var, value=0, style='rbtnfont.TRadiobutton', padding=(20, 0, 0, 10)) \
            .grid(column=2, row=9, columnspan=1, rowspan=1, sticky=(W))
        self.computer_rb = ttk.Radiobutton(self, text="COMPUTER", variable=image_type_var, value=1, style='rbtnfont.TRadiobutton', padding=(0, 0, 0, 10)) \
            .grid(column=3, row=9, columnspan=1, rowspan=1, sticky=(W))

        filled_var = IntVar(None, OptionsPanel.UNDEFINED)
        filled_var.trace("w", lambda name, index, mode, var=filled_var: controller.filled_variable_changed(var))
        self.filled_rb = ttk.Radiobutton(self, text="YES", variable=filled_var, value=0, style='rbtnfont.TRadiobutton', padding=(20, 0, 0, 10)) \
            .grid(column=2, row=10, columnspan=1, rowspan=1, sticky=(W))
        self.unfilled_rb = ttk.Radiobutton(self, text="NO", variable=filled_var, value=1, style='rbtnfont.TRadiobutton', padding=(0, 0, 0, 10)) \
            .grid(column=3, row=10, columnspan=1, rowspan=1, sticky=(W))

        # Bottom simple buttons
        self.load_button = ttk.Button(self, text="Load image", style='btnfont.TButton', command=self.controller.load_image)
        self.load_button.grid(column=0, row=12, columnspan=1, rowspan=1, sticky=(E, S))
        self.recog_button = ttk.Button(self, text="Recognise graph", style='btnfont.TButton', command=self.controller.run_algorithm)
        self.recog_button.grid(column=1, row=12, columnspan=1, rowspan=1, sticky=(W, S))
        self.save_button = ttk.Button(self, text="Save result", style='btnfont.TButton', command=self.controller.save_result)
        self.save_button.grid(column=2, row=12, columnspan=1, rowspan=1, sticky=(W, S))
        self.clear_button = ttk.Button(self, text="Clear all", style='btnfont.TButton', command=self.controller.clear_all)
        self.clear_button.grid(column=4, row=12, columnspan=1, rowspan=1, sticky=(E,S))

        self.columnconfigure(2, weight=2)
        self.columnconfigure(3, weight=2)
        self.columnconfigure(4, weight=2)
        self.rowconfigure(11, weight=1)

    def load_filedialog(self, var):
        types = (
            ("All","*"),
            ("JPG","*.jpg"), 
            ("PNG","*.png"))
        filename = filedialog.askopenfilename(
            title='Open a file',
            filetypes=types
        )
        if filename:
            var.set(filename)
            self.controller.in_path_changed(var)

    def save_filedialog(self, var):
        types = (
            ("All", "*"),
            ("GraphML - simple graph format","*.graphml"), 
            ("XML - format used by draw.io", "*.xml"),
            ("GRF - format used by Modgraf", "*.grf"))
        filename = filedialog.asksaveasfilename(
            title='Save a file',
            filetypes=types
        )
        
        if filename:
            var.set(filename)
            self.controller.out_path_changed(var)

        print(f"Save filedialog")
