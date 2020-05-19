from tkinter import Tk, Canvas, Menu, filedialog, Scrollbar, messagebox
from PIL import ImageGrab, Image
import json
import io
from src.ProcessXT import ProcessXT
from pyscreenshot import grab


class ProPlanG:
    def __init__(self):
        # Establish tkinter object
        self.root = Tk()
        self.root.title("ProPlanG")
        self.process_data = []
        self.prev_visited = []

        # Create Tkinter Menu (menubar on top, below window title)
        menubar = Menu(self.root)
        # Create pulldown menu (set tearoff=0 to disable detaching the menu)
        filemenu = Menu(menubar, tearoff=0)

        # Menu content
        menubar.add_cascade(label="File", menu=filemenu)
        # Pulldown menu content
        filemenu.add_command(label="Open...", command=self.read_config_file)
        filemenu.add_command(label="Save as png...", command=self.save_as_png)

        # scrollbar
        x_scrollbar = Scrollbar(self.root, orient="horizontal")
        y_scrollbar = Scrollbar(self.root, orient="vertical")

        # display the menu
        self.root.config(menu=menubar)

        # Prepare the main canvas
        self.main_canvas = Canvas(
            self.root,
            width=1000,
            height=500,
            borderwidth=1,
            scrollregion=(0, 0, 2000, 1000),
            xscrollcommand=x_scrollbar.set,
            yscrollcommand=y_scrollbar.set
        )

        # enable actual scrolling
        x_scrollbar.config(command=self.main_canvas.xview)
        y_scrollbar.config(command=self.main_canvas.yview)

        # place widgets in grid
        self.main_canvas.grid(column=0, row=0)
        x_scrollbar.grid(row=1, column=0, sticky="E" + "W")
        y_scrollbar.grid(row=0, column=1, sticky="N" + "S")

        self.root.mainloop()

    def handle_process_calculation(self):
        """
        Iterate over all process objects and handle the calculation of the required values.
        The calculation needs to be performed in multiple steps as certain values
        cannot be calculated without knowing additional values from other processes.

        :return: None
        """
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

    def handle_process_drawing(self):
        """
        Handle the drawing of processes.
        The calculation of the side_count and height_count is also performed.
        The processing logic for this function is as follows:

        - The starting process is at (0, 0).
        - A process with only one predecessor inherits the height from the previous process.
        - Processes that share the same predecessor are placed below each other.
        - A process with multiple predecessors uses the smallest height of those processes.

        :return: None
        """
        # Draw processes
        side_count = 0
        for element in self.process_data:
            # the starting process
            if len(element.predecessor) == 0:
                element.gui_height = 0
                self.insert_new_process(side_count, element.gui_height, element)
            else:
                # a process that is used as the exit for a single process
                if len(element.predecessor) == 1:
                    # the first process on top
                    if self.prev_visited.count(element.faz) == 0:
                        element.gui_height = element.predecessor[0].gui_height
                        self.insert_new_process(side_count, element.gui_height, element)
                        self.prev_visited.append(element.faz)
                    # additional processes, placed below
                    elif self.prev_visited.count(element.faz) > 0:
                        side_count -= 1
                        element.gui_height = self.prev_visited.count(element.faz)
                        self.insert_new_process(side_count, element.gui_height, element)
                        self.prev_visited.append(element.faz)
                # a process that acts as the exit for multiple processes
                elif len(element.predecessor) > 1:
                    # the first element is automatically the reference value
                    lowest_gui_height = element.predecessor[0].gui_height
                    for pre_elements in element.predecessor:
                        # replace reference value if a lower value is found
                        if pre_elements.gui_height < lowest_gui_height:
                            lowest_gui_height = pre_elements.gui_height
                    element.gui_height = lowest_gui_height
                    self.insert_new_process(side_count, element.gui_height, element)
                    self.prev_visited.append(element.faz)
            side_count += 1

    def handle_arrow_drawing(self):
        """
        Iterate through all processes and handle the drawing of the arrows.

        :return: None
        """
        # Draw arrows / connections
        for element in self.process_data:
            for successor in element.successor:
                self.draw_arrow(element, successor)

    def draw_arrow(self, origin, target):
        """
        Draw the arrows that connect from the origin process to all processes
        that follow afterwards.
        If the processes that are to be connected do not share the same height
        three lines are drawn instead.
        If the process is part of the critical path color the arrow red instead.

        :param origin: The origin process to draw the arrow from.
        :param target: The target process to draw the arrow to.
        :return: None
        """
        origin_coords = self.main_canvas.coords(origin.name)
        target_coords = self.main_canvas.coords(target.name)

        if origin.is_critical(target):
            color = "red"
        else:
            color = "black"

        # same height, one straight line:
        if origin.gui_height == target.gui_height:
            self.main_canvas.create_line(
                origin_coords[0] + 75,
                origin_coords[1] + 45,
                target_coords[0] - 15,
                target_coords[1] + 45,
                arrow="last",
                fill=color)
        # different height, three lines (as a curve):
        else:
            # if difference is positive: arrow moves down
            # if difference is negative: arrow moves up
            difference = target.gui_height - origin.gui_height
            # x: 10 out
            self.main_canvas.create_line(
                origin_coords[0] + 75,
                origin_coords[1] + 45,
                origin_coords[0] + 95,
                origin_coords[1] + 45,
                arrow=None,
                fill=color)
            # y: 130 up / down
            self.main_canvas.create_line(
                origin_coords[0] + 95,
                origin_coords[1] + 45,
                origin_coords[0] + 95,
                origin_coords[1] + 45 + 130 * difference,
                arrow=None,
                fill=color)
            # x: connect with target
            self.main_canvas.create_line(
                origin_coords[0] + 95,
                origin_coords[1] + 45 + 130 * difference,
                target_coords[0] - 15,
                target_coords[1] + 45,
                arrow="last",
                fill=color)

        self.main_canvas.update()

    def draw_empty_process(self, side_count, height_count, process):
        """
        Draw the process rectangles and fill them with default values.

        For the creation of the rectangle use the coords (x1, y1, x2, y2, **kwargs).
        For the creation of text use the coords (x, y, **kwargs).

        The entire process may be called using the tag (= process name).

        :param side_count: Count which column the process should be in.
        :param height_count: Count which row the process should be in.
        :param process: The process to insert.
        :return: None
        """
        # calc offset
        inc_amount_side = side_count * 130
        inc_amount_height = height_count * 130
        # for the outer values
        # top left
        self.main_canvas.create_text(inc_amount_side + 55, inc_amount_height + 25, text=process.faz, tags=process.name)
        # bot left
        self.main_canvas.create_text(inc_amount_side + 55, inc_amount_height + 115, text=process.saz, tags=process.name)
        # top right
        self.main_canvas.create_text(inc_amount_side + 115, inc_amount_height + 25, text=process.fez, tags=process.name)
        # bot right
        self.main_canvas.create_text(inc_amount_side + 115, inc_amount_height + 115, text=process.sez, tags=process.name)

        # for the inner values
        # top left
        self.main_canvas.create_rectangle(inc_amount_side + 40, inc_amount_height + 40, inc_amount_side + 70, inc_amount_height + 70, tags=process.name)
        self.main_canvas.create_text(inc_amount_side + 55, inc_amount_height + 55, text=process.id)
        # bot left
        self.main_canvas.create_rectangle(inc_amount_side + 40, inc_amount_height + 70, inc_amount_side + 70, inc_amount_height + 100, tags=process.name)
        self.main_canvas.create_text(inc_amount_side + 55, inc_amount_height + 85, text=process.duration)
        # bot mid
        self.main_canvas.create_rectangle(inc_amount_side + 70, inc_amount_height + 70, inc_amount_side + 100, inc_amount_height + 100, tags=process.name)
        self.main_canvas.create_text(inc_amount_side + 85, inc_amount_height + 85, text=process.gp)
        # top right
        self.main_canvas.create_rectangle(inc_amount_side + 70, inc_amount_height + 40, inc_amount_side + 130, inc_amount_height + 70, tags=process.name)
        self.main_canvas.create_text(inc_amount_side + 85, inc_amount_height + 55, text=process.name)
        # bot right
        self.main_canvas.create_rectangle(inc_amount_side + 100, inc_amount_height + 70, inc_amount_side + 130, inc_amount_height + 100, tags=process.name)
        self.main_canvas.create_text(inc_amount_side + 115, inc_amount_height + 85, text=process.fp)

    def insert_new_process(self, side_count, height_count, process):
        """
        Handle inserting a new process and update the canvas element
        afterwards to show the changes.

        :param side_count: Count which column the process should be in.
        :param height_count: Count which row the process should be in.
        :param process: The process to insert.
        :return: None
        """
        self.draw_empty_process(side_count, height_count, process)

    @staticmethod
    def open_file():
        """
        Open a dialogue that asks the user to select a file.

        :return: The path to the file or None if the dialogue was interrupted.
        """
        save_path = filedialog.askopenfilename(
            title="Konfigurationsdatei auswaehlen..."
        )
        if save_path and save_path.endswith("json"):
            return save_path
        else:
            messagebox.showerror(
                "Fehler",
                "Die Eingabedatei muss eine json-Datei sein."
            )
            return None

    @staticmethod
    def save_file():
        """
        Open a dialogue that asks the user where to save a file.

        :return: The path where to save the file or None if the dialogue was interrupted.
        """
        save_path = filedialog.asksaveasfilename(
            title="Speicherort auswaehlen...",
            defaultextension='.png'
        )
        if save_path:
            return save_path
        else:
            return None

    def read_config_file(self):
        """
        Handle the reading of a config file.
        First get the path to the config file and then open it.
        Sort all the data sets by ID and create process objects for every set.

        Afterwards begin the handling of process calculation and drawing.

        :return: None
        """
        save_path = self.open_file()
        prev_ids = []

        if save_path is not None:
            with open(save_path, "r") as file:
                # set window name to json file name
                self.root.title(save_path.split("/")[-1] + " - ProPlanG")
                # reset previous data
                self.reset_data()

                json_process_data = None
                try:
                    json_process_data = json.load(file)
                except json.decoder.JSONDecodeError:
                    messagebox.showerror(
                        "Fehler",
                        "Die angegebene json-Datei ist nicht gültig."
                    )

            if json_process_data is not None:
                # sort processes in json if they are not ordered
                process_list = sorted(json_process_data["Prozesse"], key=lambda k: k['id'])

                # Iterate over the json process data
                for element in process_list:
                    if element.get("id") not in prev_ids:
                        # Create a new process object for each data set, append all to list
                        self.process_data.append(ProcessXT(element.get("id"), element.get("name"), element.get("duration")))
                        prev_ids.append(element.get("id"))
                    else:
                        messagebox.showerror(
                            "Fehler",
                            "Die Prozess-ID " + element.get("id") + " wird bereits für eine anderen Prozess verwendet.")

                # Iterate over the json process data
                for element in process_list:
                    # Iterate over the list of successors
                    for single_successor in element.get("successor"):
                        # Append the current successor (as obj) to the current data set (as obj)
                        self.process_data[element.get("id")].add_successor_and_predecessor(self.process_data[single_successor])

            self.handle_process_calculation()
            self.handle_process_drawing()
            self.handle_arrow_drawing()
            self.main_canvas.update()

    def reset_data(self):
        """
        Reset the data from previous calculations.

        :return: None
        """
        self.process_data = []
        self.prev_visited = []
        self.main_canvas.delete("all")
        self.main_canvas.update()

    def save_as_png(self):
        print()
