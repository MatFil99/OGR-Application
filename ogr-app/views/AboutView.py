from tkinter import *
from tkinter import ttk

class AboutView(Toplevel):

    def __init__(self, parent):
        Toplevel.__init__(self, parent)
        project_desc = "Project done as a part of Bachelor's Thesis."
        labels = ["Thesis title:", "Thesis supervisor:", "Author:", "College:", "Faculty:", "Term:"]

        thesis_title = "Aplikacja do rozpoznawania struktury grafu z rysunku rastrowego"
        thesis_supervisor = "dr inz. Izabela Zoltowska"
        author = "Filip Mazur"
        college = "Warsaw University of Technology"
        faculty = "The Faculty of Electronics and Information Technology"
        term = "2021Z"

        desc_labels = [thesis_title, thesis_supervisor, author, college, faculty, term]

        print("About creating")
        self.title("About")
        self.geometry("500x250")
        self.resizable(False, False)
        
        self.create_label(project_desc, 0, 0, 2, 1, (N), (10, 10), (20))
        for i in range(0, 6):
            self.create_label(labels[i], 0, i+1, 1, 1, (NW), (10, 10), (10, 0))
            self.create_label(desc_labels[i], 1, i+1, 1, 1, (NW), (10, 10), (10, 0))

    def create_label(self, text, col, row, colspan, rowspan, st, padx, pady, wraptext=0):
        label = ttk.Label(self, text=text)
        label.grid(column=col, row=row, columnspan=colspan, rowspan=rowspan, padx=padx, pady=pady, sticky=st)
        label.configure(wraplength=wraptext)