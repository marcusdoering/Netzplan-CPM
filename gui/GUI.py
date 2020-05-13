from tkinter import Tk, Canvas, Menu, filedialog, Scrollbar
from PIL import ImageGrab
import json
from src.ProcessXT import ProcessXT


class ProPlanG:
    def __init__(self):
        # Establish tkinter object
        self.root = Tk()
        self.root.title("ProPlanG")
        # self.root.geometry('600x530')
        self.process_data = []
        self.prev_visited = []

        # Create Tkinter Menu (menubar on top, below window title)
        menubar = Menu(self.root)
        # Create pulldown menu (set tearoff=0 to disable detaching the menu)
        filemenu = Menu(menubar, tearoff=0)

        # Menu content
        menubar.add_cascade(label="File", menu=filemenu)
        menubar.add_command(label="Placeholder")
        # Pulldown menu content
        filemenu.add_command(label="Open...", command=self.read_config_file)
        filemenu.add_command(label="Save as json...")
        filemenu.add_command(label="Save as png...", command=self.save_as_png)

        # scrollbar
        x_scrollbar = Scrollbar(self.root, orient="horizontal")
        y_scrollbar = Scrollbar(self.root, orient="vertical")

        x_scrollbar.grid(row=1, column=0, sticky="E" + "W")
        y_scrollbar.grid(row=0, column=1, sticky="N" + "S")

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
        # Draw processes
        side_count = 0
        height_count = 0
        for element in self.process_data:
            if element.duration == 0:
                height_count = 0
                self.insert_new_process(side_count, height_count, element)
            elif element.duration != 0 and element.faz in self.prev_visited:
                # place one below
                side_count -= 1
                height_count += 1
                self.insert_new_process(side_count, height_count, element)
            else:
                self.prev_visited.append(element.faz)
                self.insert_new_process(side_count, height_count, element)
                height_count = 0
            side_count += 1

        # Draw arrows / connections
        for element in self.process_data:
            for successor in element.successor:
                self.draw_arrow(element, successor)

    def draw_arrow(self, origin, target):
        origin_coords = self.main_canvas.coords(origin.name)
        target_coords = self.main_canvas.coords(target.name)

        if origin.is_critical():
            color = "red"
        else:
            color = "black"

        self.main_canvas.create_line(
            origin_coords[0] + 75,
            origin_coords[1] + 45,
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

        :param side_count:
        :param process:
        :return:
        """
        # calc offset
        # todo
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

    def move_process(self, process_tag: str, movement_x, movement_y):
        self.main_canvas.move(process_tag, movement_x, movement_y)
        self.main_canvas.update()

    def insert_new_process(self, side_count, height_count, process):
        self.draw_empty_process(side_count, height_count, process)
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

    @staticmethod
    def save_file():
        save_path = filedialog.asksaveasfilename(
            title="Speicherort auswaehlen..."
        )
        if save_path:
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

    def save_as_png(self):
        save_path = self.save_file()
        x = self.root.winfo_rootx() + self.main_canvas.winfo_x()
        y = self.root.winfo_rooty() + self.main_canvas.winfo_y()
        x1 = x + self.main_canvas.winfo_width()
        y1 = y + self.main_canvas.winfo_height()
        # todo: this aint working yet
        ImageGrab.grab().crop((x, y, x1, y1)).save(save_path)
