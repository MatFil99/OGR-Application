from models.GraphModel import Graph, GraphModel
from models.GrfParamModel import GrfParam
from models.UserParametersModel import UserParameters
from views.AboutView import AboutView
from views.FileWOptView import FileWOpt
from views.HelpView import HelpView

from views.InputImgView import InputImg
from views.MainWindowView import MainWindow
from views.OptionsPanelView import OptionsPanel
from views.OutputImgView import OutputImg

class Controller:
    # # views
    # main_window = None
    # in_img_view = None
    # out_img_view = None
    # options_panel_view = None

    # # models
    # user_parameters_model = None
    # graph_model = None

    def __init__(self) -> None:
        pass
         # views
        self.main_window = MainWindow(self)
        self.options_panel_view = OptionsPanel(self, self.main_window)
        self.in_img_view = InputImg(self, self.main_window.get_visualization_panel())
        self.out_img_view = OutputImg(self, self.main_window.get_visualization_panel())

        self.main_window.add_panels(self.options_panel_view, self.in_img_view, self.out_img_view)
        
        # models
        self.user_parameters_model = UserParameters()
        self.graph_model = GraphModel()


    def start_app(self):
        self.main_window.mainloop()

    def visualization_panel_resize(self, event):
        self.in_img_view.update()
        self.out_img_view.update()

    def brightness_variable_changed(self, brightness_var):
        self.user_parameters_model.set_bg_brightness(brightness_var.get())

    def direction_variable_changed(self, direction_var):
        self.user_parameters_model.set_graph_type(direction_var.get())

    def image_type_variable_changed(self, image_type_var):
        self.user_parameters_model.set_in_img_type(image_type_var.get())

    def filled_variable_changed(self, filled_var):
        self.user_parameters_model.set_vertices_type(filled_var.get())

    def in_path_changed(self, in_path_var):
        self.user_parameters_model.set_input_path(in_path_var.get())

    def out_path_changed(self, out_path_var):
        self.user_parameters_model.set_output_path(out_path_var.get())
        
    def run_algorithm(self):
        if self.in_img_view.read_graph_image(self.user_parameters_model.input_path):
            self.in_img_view.update()

        success = self.graph_model.recognize_graph(self.user_parameters_model)

        if success:
            recg_img = self.graph_model.get_rec_graph_img()
            self.out_img_view.set_recog_graph_img(recg_img)
            self.out_img_view.update()
        else:
            self.main_window.notify_error("Cannot recognize graph! Check if all parameters are set correctly.")

    def clear_all(self):
        self.graph_model.clear_graph()
        self.out_img_view.clear_panel()
        self.in_img_view.clear_panel()

    def save_result(self):
        success = False
        grf_params = None
        graph_ext = None

        if self.user_parameters_model.output_path:
            graph_ext = self.graph_model.get_save_file_extension(self.user_parameters_model.output_path.lower())
        if graph_ext==".grf":
            grf_params = GrfParam()
            filew_opt = FileWOpt(self.main_window, grf_params)
            filew_opt.grab_set()
            self.main_window.wait_window(filew_opt)
            if grf_params.nr_edge_params is None or grf_params.graph_type is None:
                grf_params = None

        if self.user_parameters_model.output_path and self.graph_model.graph_exists():
            success = self.graph_model.save_graph_as(self.user_parameters_model.output_path, grf_params)
        
        if success == True:
            self.main_window.notify_success("File was saved")
        elif success == False and (graph_ext!=".grf" or grf_params is not None):
            self.main_window.notify_error("Error: Cannot save graph to file!")

    def load_image(self):
        print(f"in image path = {self.user_parameters_model.input_path}")
        if self.in_img_view.read_graph_image(self.user_parameters_model.input_path):
            self.in_img_view.update()
        else:
            self.main_window.notify_error("Error: Path or file does not exist!")

    def about_action(self):
        about = AboutView(self.main_window)
        about.grab_set()
        self.main_window.wait_window(about)

    def help_action(self):
        help = HelpView(self.main_window)
        help.grab_set()
        self.main_window.wait_window(help)