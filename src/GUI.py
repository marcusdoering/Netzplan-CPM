from tkinter import Tk, Canvas, Menu, filedialog, messagebox, Scrollbar, BooleanVar
from tkinter.ttk import Sizegrip
import json
from math import ceil
from ProcessXT import ProcessXT


class ProPlanG:
    def __init__(self):
        """
        Constructor for the GUI.
        """
        # Establish tkinter object
        self.root = Tk()
        self.root.title("ProPlanG")
        self.process_data = []
        self.prev_visited = []

        # data of the process that is currently being moved
        # x and y are the coordinates, item is the tag of the object group
        self.drag_x = 0
        self.drag_y = 0
        self.drag_item = None

        # Create Tkinter Menu (menubar on top, below window title)
        menubar = Menu(self.root)
        # Create pulldown menu (set tearoff=0 to disable detaching the menu)
        filemenu = Menu(menubar, tearoff=0)
        debugmenu = Menu(menubar, tearoff=0)

        # Menu content
        menubar.add_cascade(label="File", menu=filemenu)
        menubar.add_cascade(label="Settings", menu=debugmenu)
        # Filemenu content
        filemenu.add_command(label="Open...", command=self.read_config_file)
        # Debugmenu content
        self.detailed_arrow = BooleanVar(self.root, False)
        debugmenu.add_checkbutton(label="Show detailed arrows", variable=self.detailed_arrow, command=self.handle_arrow_drawing)
        self.arrow_split = BooleanVar(self.root, False)
        debugmenu.add_checkbutton(label="Directly connect arrows", variable=self.arrow_split, command=self.handle_arrow_drawing)

        # scrollbar
        x_scrollbar = Scrollbar(self.root, orient="horizontal")
        y_scrollbar = Scrollbar(self.root, orient="vertical")
        # sizegrip
        sizegrip = Sizegrip(self.root)

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

        # bind mouse buttons to the drag functions
        self.main_canvas.bind("<ButtonPress-1>", self.drag_start)
        self.main_canvas.bind("<ButtonRelease-1>", self.drag_stop)
        self.main_canvas.bind("<B1-Motion>", self.drag)

        # place widgets in grid
        x_scrollbar.pack(fill="x", side="bottom", expand=False)
        y_scrollbar.pack(fill="y", side="right", expand=False)
        sizegrip.pack(in_=x_scrollbar, side="bottom", anchor="se")
        self.main_canvas.pack(fill="both", side="left", expand=True)

        # start the gui
        self.root.mainloop()

    def drag_start(self, event):
        """
        Begin the dragging of an object (or group of objects) on the canvas.
        Function is called when the user holds down the mouse button.

        :param event: Event data of where the mouse cursor is.
        :return: None
        """
        # find the closest process, then get the data of this process
        self.drag_item = self.main_canvas.gettags(self.main_canvas.find_closest(
            self.main_canvas.canvasx(event.x),
            self.main_canvas.canvasy(event.y))
        )[0]

        self.drag_x = self.main_canvas.canvasx(event.x)
        self.drag_y = self.main_canvas.canvasy(event.y)

    def drag_stop(self, event):
        """
        Stop the dragging of an object (or group of objects) on the canvas.
        Function is called when the user releases the mouse button.

        The event parameter is not used in the function but is still required as
        the function is called by a bind event.

        :param event: Event data of where the mouse cursor is.
        :return: None
        """
        # reset the drag information
        self.drag_item = None
        self.drag_x = 0
        self.drag_y = 0
        # redraw the arrows using new positioning
        self.handle_arrow_drawing()

    def drag(self, event):
        """
        Perform the position change of an object (or group of objects) on the canvas.
        Function is called when the user moves the mouse while holding / dragging object(s).
        The new position is constantly saved so that multiple movements are possible.

        :param event: Event data of where the mouse cursor is.
        :return: None
        """
        # do not allow dragging of arrows (as they will reposition anyways)
        if "arrow" not in self.main_canvas.gettags(self.drag_item):
            # check how far the mouse moved
            new_pos_x = self.main_canvas.canvasx(event.x) - self.drag_x
            new_pos_y = self.main_canvas.canvasy(event.y) - self.drag_y
            # move the object(s)
            self.main_canvas.move(self.drag_item, new_pos_x, new_pos_y)
            # save the new position for next calculation
            self.drag_x = self.main_canvas.canvasx(event.x)
            self.drag_y = self.main_canvas.canvasy(event.y)

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
        self.main_canvas.delete("arrow")
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
        adj_origin_name = origin.name.replace(" ", "_")
        adj_target_name = target.name.replace(" ", "_")

        origin_coords = self.main_canvas.coords(adj_origin_name)
        target_coords = self.main_canvas.coords(adj_target_name)

        if origin.is_critical(target):
            color = "red"
        else:
            color = "black"

        # reference positions
        origin_ref_x = origin_coords[0] + 75
        origin_ref_y = origin_coords[1] + 45
        target_ref_x = target_coords[0] - 15
        target_ref_y = target_coords[1] + 45

        # distance from origin until line splits
        split_distance_x = (target_ref_x - origin_ref_x) / 2

        # if debug is active all three lines end on arrows
        if self.detailed_arrow.get():
            adj_arrow_type = "last"
        else:
            adj_arrow_type = None

        # for debug
        if self.arrow_split.get():
            self.main_canvas.create_line(
                origin_ref_x,
                origin_ref_y,
                target_ref_x,
                target_ref_y,
                arrow="last",
                fill=color,
                tags=(adj_origin_name + "_arrow", "arrow")
            )
        # for no debug
        else:
            # x: out from origin
            self.main_canvas.create_line(
                origin_ref_x,
                origin_ref_y,
                origin_ref_x + split_distance_x,
                origin_ref_y,
                arrow=adj_arrow_type,
                fill=color,
                tags=(adj_origin_name + "_arrow", "arrow"))

            # y: up / down
            self.main_canvas.create_line(
                origin_ref_x + split_distance_x,
                origin_ref_y,
                target_ref_x - split_distance_x,
                target_ref_y,
                arrow=adj_arrow_type,
                fill=color,
                tags=(adj_origin_name + "_arrow", "arrow"))

            # x: connect with target
            self.main_canvas.create_line(
                target_ref_x - split_distance_x,
                target_ref_y,
                target_ref_x,
                target_ref_y,
                arrow="last",
                fill=color,
                tags=(adj_origin_name + "_arrow", "arrow"))

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
        self.main_canvas.create_text(
            inc_amount_side + 55,
            inc_amount_height + 25,
            text=process.faz,
            tags=process.name.replace(" ", "_")
        )
        # bot left
        self.main_canvas.create_text(
            inc_amount_side + 55,
            inc_amount_height + 115,
            text=process.saz,
            tags=process.name.replace(" ", "_")
        )
        # top right
        self.main_canvas.create_text(
            inc_amount_side + 115,
            inc_amount_height + 25,
            text=process.fez,
            tags=process.name.replace(" ", "_")
        )
        # bot right
        self.main_canvas.create_text(
            inc_amount_side + 115,
            inc_amount_height + 115,
            text=process.sez,
            tags=process.name.replace(" ", "_")
        )

        # for the inner values
        # top left
        self.main_canvas.create_rectangle(
            inc_amount_side + 40,
            inc_amount_height + 40,
            inc_amount_side + 70,
            inc_amount_height + 70,
            tags=process.name.replace(" ", "_")
        )
        self.main_canvas.create_text(
            inc_amount_side + 55,
            inc_amount_height + 55,
            text=process.id,
            tags=process.name.replace(" ", "_")
        )
        # bot left
        self.main_canvas.create_rectangle(
            inc_amount_side + 40,
            inc_amount_height + 70,
            inc_amount_side + 70,
            inc_amount_height + 100,
            tags=process.name.replace(" ", "_")
        )
        self.main_canvas.create_text(
            inc_amount_side + 55,
            inc_amount_height + 85,
            text=process.duration,
            tags=process.name.replace(" ", "_")
        )
        # bot mid
        self.main_canvas.create_rectangle(
            inc_amount_side + 70,
            inc_amount_height + 70,
            inc_amount_side + 100,
            inc_amount_height + 100,
            tags=process.name.replace(" ", "_")
        )
        self.main_canvas.create_text(
            inc_amount_side + 85,
            inc_amount_height + 85,
            text=process.gp,
            tags=process.name.replace(" ", "_")
        )
        # top right
        self.main_canvas.create_rectangle(
            inc_amount_side + 70,
            inc_amount_height + 40,
            inc_amount_side + 130,
            inc_amount_height + 70,
            tags=process.name.replace(" ", "_")
        )

        # amount of rows
        val = ceil(len(process.name) / 11)
        # the amount of rows determines how big the text is (to make sure it fits in the box)
        if val == 1:
            font_size = 10
        elif val == 2:
            font_size = 8
        else:
            font_size = 7

        self.main_canvas.create_text(
            inc_amount_side + 100,
            inc_amount_height + 55,
            text=process.name,
            width=60,
            font=("Arial", font_size),
            tags=process.name.replace(" ", "_")
        )
        # bot right
        self.main_canvas.create_rectangle(
            inc_amount_side + 100,
            inc_amount_height + 70,
            inc_amount_side + 130,
            inc_amount_height + 100,
            tags=process.name.replace(" ", "_")
        )
        self.main_canvas.create_text(
            inc_amount_side + 115,
            inc_amount_height + 85,
            text=process.fp,
            tags=process.name.replace(" ", "_")
        )

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
            title="Konfigurationsdatei auswaehlen...",
            filetypes=(("json-Dateien", "*.json"), ("Alle Dateien", "*.*"))
        )
        if save_path and save_path.endswith("json"):
            return save_path
        else:
            messagebox.showerror(
                "Fehler",
                "Die Eingabedatei muss eine json-Datei sein."
            )
            return None

    def read_config_file(self):
        """
        Handle the reading of a config file.
        The config is then passed to other functions to handle calculation.

        :return: None
        """
        save_path = self.open_file()

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

                self.handle_json_to_valid_dataset(json_process_data)

    def handle_json_to_valid_dataset(self, json_process_data):
        """
        Sort all the data sets by ID and create process objects for every set.

        Afterwards begin the handling of process calculation and drawing.

        :param json_process_data: Input data that was imported.
        :return: None
        """
        prev_ids = []

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

            # the starting id used to adjust following function calls
            id_offset = self.process_data[0].id

            # Iterate over the json process data
            for element in process_list:
                # Iterate over the list of successors
                for single_successor in element.get("successor"):
                    # Append the current successor (as obj) to the current data set (as obj)
                    self.process_data[element.get("id") - id_offset].add_successor_and_predecessor(
                        self.process_data[single_successor - id_offset])

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
