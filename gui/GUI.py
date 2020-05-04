from tkinter import Tk, Canvas, Menu, Button
from src.ProcessXT import ProcessXT
import time


class ProPlanG:
    def __init__(self):
        # Establish tkinter object
        self.root = Tk()
        self.root.title("ProPlanG")
        # self.root.geometry('600x530')

        # Create Tkinter Menu (menubar on top, below window title)
        menubar = Menu(self.root)
        # Create pulldown menu (set tearoff=0 to disable detaching the menu)
        filemenu = Menu(menubar, tearoff=0)

        # Menu content
        menubar.add_cascade(label="File", menu=filemenu)
        menubar.add_command(label="Placeholder")
        # Pulldown menu content
        filemenu.add_command(label="Open...")
        filemenu.add_command(label="Save...")

        # display the menu
        self.root.config(menu=menubar)

        # Prepare the main canvas
        self.main_canvas = Canvas(
            self.root,
            width=500,
            height=500,
            borderwidth=1)

        self.btn_add_process = Button(self.root, text="Prozess hinzufuegen", command=self.insert_new_process)
        self.btn_rem_process = Button(self.root, text="Prozess entfernen")

        self.btn_add_process.grid(column=0, row=0)
        self.btn_rem_process.grid(column=1, row=0)
        self.main_canvas.grid(column=0, row=1, columnspan=2)

        self.root.mainloop()

    @staticmethod
    def handle_process_calculation(list_of_proc):
        # todo: testing data as placeholder
        proc0 = ProcessXT(0, "Start", 0)
        proc1 = ProcessXT(1, "A1", 1)
        proc2 = ProcessXT(2, "B1", 1)
        proc3 = ProcessXT(3, "B2", 3)
        proc4 = ProcessXT(4, "End", 0)

        proc0.add_successor_and_predecessor(proc1)
        proc1.add_successor_and_predecessor(proc2)
        proc1.add_successor_and_predecessor(proc3)
        proc2.add_successor_and_predecessor(proc4)
        proc3.add_successor_and_predecessor(proc4)

        list_of_proc = [proc0, proc1, proc2, proc3, proc4]

        # Vorwaertsterminierung
        for element in list_of_proc:
            element.calc_faz()
            element.calc_fez()

        # Rueckwaertsterminierung
        for element in list_of_proc[::-1]:
            element.calc_sez()
            element.calc_saz()

        # Pufferberechnung
        for element in list_of_proc:
            element.calc_gp()
            element.calc_fp()

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
        self.main_canvas.create_rectangle(10, 10, 40, 40, tags=process.name)
        self.main_canvas.create_text(25, 25, text=process.faz)
        # bot left
        self.main_canvas.create_rectangle(10, 100, 40, 130, tags=process.name)
        self.main_canvas.create_text(25, 115, text=process.duration)


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

    def insert_new_process(self):
        self.draw_empty_process(ProcessXT(0, "Start", 0))
        self.main_canvas.update()
