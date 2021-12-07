from tkinter import *
from tkinter import ttk
from tkinter import font
from tkinter.font import Font
from PIL import ImageTk, Image, JpegImagePlugin
# import PIL
import cv2 as cv

class InputImg(ttk.Frame):

    def __init__(self, controller, visualization_panel: ttk.Frame) -> None:
        visualization_panel.update()
        np_width = visualization_panel.winfo_width()-20
        np_height = int(visualization_panel.winfo_height()/2)-20
        self.controller = controller

        ttk.Frame.__init__(self, visualization_panel)

        self.place(width=np_width, height=np_height)

        self.desc_label = ttk.Label(self, text="Input image")
        self.desc_label.grid(column=0, row=0, columnspan=1, rowspan=1, sticky=(N))
        self.img_label = ttk.Label(self, borderwidth=5, relief="flat")# \
        self.img_label.grid(column=0, row=1, columnspan=1, rowspan=9, sticky=(NS))

        self.rowconfigure(1, weight=1)
        self.columnconfigure(0, weight=1)

        self.graph_image = None

    
    def update(self):
        frame_parent = self.master
        nwidth = frame_parent.winfo_width() - 20
        nheight = int(frame_parent.winfo_height()/2) - 20
        
        self.place(width=nwidth, height=nheight)
        self.update_image()

    def read_graph_image(self, path):
        success = False
        print(f"read path {path}")
        try:
            img = cv.imread(path)
            img = cv.cvtColor(img, cv.COLOR_BGR2RGB)
            width, height = img.shape[1], img.shape[0]
            if width < height:
                print("width < height")
                img = cv.rotate(img, cv.ROTATE_90_CLOCKWISE)
            self.graph_image = Image.fromarray(img)
            success = True
        except IOError as e:
            print(e)
        except:
            print("Unknown exception")
        return success

    def clear_panel(self):
        self.graph_image = None
        self.update()

    def update_image(self):
        if self.graph_image:
            self.img_label.update()
            maxheight = self.img_label.winfo_height()

            scale = maxheight / self.graph_image.height
            nwidth = int(self.graph_image.width * scale)
            nheight = maxheight
            img = self.graph_image.resize((nwidth, nheight), Image.ANTIALIAS)
            image = ImageTk.PhotoImage(img)
            self.img_label.configure(image=image, relief="solid")
            self.img_label.image = image
            self.img_label.update()
        else:
            self.img_label.configure(image = None, relief="flat")
            self.img_label.image = None