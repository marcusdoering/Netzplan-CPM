from tkinter import Tk, Canvas, Menu, Button


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
            height=500)

        self.btn = Button(self.root, text="Placeholder")

        self.btn.grid(column=0, row=0)
        self.main_canvas.grid(column=0, row=1)

        # 
        self.root.mainloop()
