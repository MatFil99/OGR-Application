from tkinter import *
from tkinter import ttk
from tkinter import font
from tkinter.font import Font
from PIL import ImageTk, Image


class OutputImg(ttk.Frame):

    def __init__(self, controller, visualization_panel: ttk.Frame) -> None:
        
        self.recog_graph_img = None

        visualization_panel.update()
        np_width = visualization_panel.winfo_width()-20
        np_height = int(visualization_panel.winfo_height()/2)-20
        self.controller = controller

        ttk.Frame.__init__(self, visualization_panel)

        self.place(width=np_width, height=np_height)

        self.desc_label = ttk.Label(self, text="Recognised graph")
        self.desc_label.grid(column=0, row=0, columnspan=1, rowspan=1, sticky=(N))
        self.img_label = ttk.Label(self, borderwidth=5, relief="flat")
        self.img_label.grid(column=0, row=1, columnspan=1, rowspan=9, sticky=(NS))

        self.rowconfigure(1, weight=1)
        self.columnconfigure(0, weight=1)
        

    def update(self):
        frame_parent = self.master
        nwidth = frame_parent.winfo_width() - 20
        nheight = int(frame_parent.winfo_height()/2) - 20
        
        self.place(y=frame_parent.winfo_height()/2, width=nwidth, height=nheight)
        self.update_img()
        if self.recog_graph_img:
            self.img_label.configure(relief="solid")

    def set_recog_graph_img(self, img):
        self.recog_graph_img = Image.fromarray(img)

    def clear_panel(self):
        self.recog_graph_img = None
        self.update()


    def update_img(self):
        if self.recog_graph_img:
            self.img_label.update()
            maxheight = self.img_label.winfo_height()

            scale = maxheight / self.recog_graph_img.height
            nwidth = int(self.recog_graph_img.width * scale)
            nheight = maxheight
            img = self.recog_graph_img.resize((nwidth, nheight), Image.ANTIALIAS)
            image = ImageTk.PhotoImage(img)
            self.img_label.configure(image=image)
            self.img_label.image = image
            self.img_label.update()
        else:
            self.img_label.configure(image=None, relief="flat")
            self.img_label.image = None