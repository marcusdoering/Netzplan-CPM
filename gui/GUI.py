from tkinter import Tk, Canvas, Menu, filedialog
from src.ProcessXT import ProcessXT

import json


class ProPlanG:
    def __init__(self):
        # Establish tkinter object
        self.root = Tk()
        self.root.title("ProPlanG")
        # self.root.geometry('600x530')
        self.process_data = []

        # Create Tkinter Menu (menubar on top, below window title)
        menubar = Menu(self.root)
        # Create pulldown menu (set tearoff=0 to disable detaching the menu)
        filemenu = Menu(menubar, tearoff=0)

        # Menu content
        menubar.add_cascade(label="File", menu=filemenu)
        menubar.add_command(label="Placeholder")
        # Pulldown menu content
        filemenu.add_command(label="Open...", command=self.read_config_file)
        filemenu.add_command(label="Save...")

        # display the menu
        self.root.config(menu=menubar)

        # Prepare the main canvas
        self.main_canvas = Canvas(
            self.root,
            width=500,
            height=500,
            borderwidth=1)

        self.main_canvas.grid(column=0, row=0)

        self.root.mainloop()

    def handle_process_calculation(self):
        # Vorwaertsterminierung
        for element in self.process_data:
            element.calc_faz()
            element.calc_fez()

        # Rueckwaertsterminierung
        for element in self.process_data[::-1]:
            element.calc_sez()
            element.calc_saz()

        # Pufferberechnung
        for element in self.process_data:
            element.calc_gp()
            element.calc_fp()

        print()

        # todo: calculate positioning of processes on canvas

        # todo: place all processes on canvas

    def draw_empty_process(self, process):
        """
        Draw the process rectangles and fill them with default values.

        For the creation of the rectangle use the coords (x1, y1, x2, y2, **kwargs).
        For the creation of text use the coords (x, y, **kwargs).

        The entire process may be called using the tag (= process name).

        :param process:
        :return:
        """
        # for the outer values
        # top left
        self.main_canvas.create_text(55, 25, text=process.faz, tags=process.name)
        # bot left
        self.main_canvas.create_text(55, 115, text=process.saz, tags=process.name)
        # top right
        self.main_canvas.create_text(115, 25, text=process.fez, tags=process.name)
        # bot right
        self.main_canvas.create_text(115, 115, text=process.sez, tags=process.name)

        # for the inner values
        # top left
        self.main_canvas.create_rectangle(40, 40, 70, 70, tags=process.name)
        self.main_canvas.create_text(55, 55, text=process.id)
        # bot left
        self.main_canvas.create_rectangle(40, 70, 70, 100, tags=process.name)
        self.main_canvas.create_text(55, 85, text=process.duration)
        # bot mid
        self.main_canvas.create_rectangle(70, 70, 100, 100, tags=process.name)
        self.main_canvas.create_text(85, 85, text=process.gp)
        # top right
        self.main_canvas.create_rectangle(70, 40, 130, 70, tags=process.name)
        self.main_canvas.create_text(85, 55, text=process.name)
        # bot right
        self.main_canvas.create_rectangle(100, 70, 130, 100, tags=process.name)
        self.main_canvas.create_text(115, 85, text=process.fp)

    def move_process(self, process_tag: str, movement_x, movement_y):
        self.main_canvas.move(process_tag, movement_x, movement_y)
        self.main_canvas.update()

    def insert_new_process(self, process):
        self.draw_empty_process(process)
        self.list_of_process.append(process)
        self.handle_process_calculation()
        self.main_canvas.update()

    @staticmethod
    def open_file():
        save_path = filedialog.askopenfilename(
            title="Konfigurationsdatei auswaehlen..."
        )
        if save_path and save_path.endswith("json"):
            return save_path
        else:
            return None

    def read_config_file(self):
        save_path = self.open_file()

        if save_path is not None:
            with open(save_path, "r") as file:
                json_process_data = json.load(file)

            # Iterate over the json process data
            for element in json_process_data.get("Prozesse"):
                # Create a new process object for each data set, append all to list
                self.process_data.append(ProcessXT(element.get("id"), element.get("name"), element.get("duration")))

            # Iterate over the json process data
            for element in json_process_data.get("Prozesse"):
                # Iterate over the list of successors
                for single_successor in element.get("successor"):
                    # Append the current successor (as obj) to the current data set (as obj)
                    self.process_data[element.get("id")].add_successor_and_predecessor(self.process_data[single_successor])

        self.handle_process_calculation()
