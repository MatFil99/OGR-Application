from tkinter import *
from tkinter import ttk
from tkinter import font
from tkinter.font import Font
from tkinter import messagebox
from PIL import ImageTk, Image

class MainWindow(Tk):
    

    def __init__(self, controller) -> None:
        Tk.__init__(self)
        self.controller = controller

        self.menubar = Menu(self)
        self.menu = Menu(self.menubar, tearoff=0)
        self.menu.add_command(label="Help", command=self.controller.help_action)
        self.menu.add_command(label="About", command=self.controller.about_action)
        self.menubar.add_cascade(label="Menu", menu=self.menu)
        self.config( menu=self.menubar)

        self.visualization_panel = ttk.Frame(self, padding=(5,0,5,0), borderwidth=5, relief="solid", width=550, height=650)
        self.in_img_panel = None
        self.out_img_panel = None

        self.columnconfigure(0, weight=1)
        self.rowconfigure(0, weight=1)
        self.columnconfigure(0, weight=1)
        self.columnconfigure(1, weight=1)
        self.rowconfigure(0, weight=1)

        self.visualization_panel.grid(column=1, row=0, columnspan=1, rowspan=1, sticky=(N, S, E, W))

        self.visualization_panel.rowconfigure(0, weight=1)
        self.visualization_panel.rowconfigure(1, weight=1)
        self.visualization_panel.columnconfigure(0, weight=1)

    def get_visualization_panel(self):
        return self.visualization_panel

    def add_panels(self, options_panel, in_img_panel, out_img_panel ):

        options_panel.grid(column=0, row=0, columnspan=1, rowspan=1, sticky=(NSEW))
        in_img_panel.place(x=0, y=0)
        out_img_panel.place(x=0, y=self.visualization_panel.winfo_height()/2)

        self.visualization_panel.bind("<Configure>", self.controller.visualization_panel_resize)
       
    def notify_success(self, message):
        messagebox.showinfo(title="OGR", message=message)
        

    def notify_error(self, message):
        messagebox.showerror(title="OGR", message=message)