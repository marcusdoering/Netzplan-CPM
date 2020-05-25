from tkinter import Label, Entry, Button, Toplevel


class AddProcess:

    def __init__(self, root):
        self.root = Toplevel(root)
        self.root.title("New File - Software")
        self.root.resizable(False, False)
        self.root.geometry('300x200')

        label_id = Label(self.root, text='ID')
        label_name = Label(self.root, text='Name')
        label_duration = Label(self.root, text='Dauer')

        entry_id = Entry(self.root, width=40)
        entry_name = Entry(self.root, width=40)
        entry_duration = Entry(self.root, width=40)

        btn_confirm = Button(self.root, text="Erstellen", width=30, command=self.return_info)

        label_id.grid(row=0, column=0)
        label_name.grid(row=2, column=0)
        label_duration.grid(row=4, column=0)
        entry_id.grid(row=1, column=0)
        entry_name.grid(row=3, column=0)
        entry_duration.grid(row=5, column=0)
        btn_confirm.grid(row=7, column=0)

        # center all widget elements
        self.root.columnconfigure(0, weight=1)

    def return_info(self):
        self.root.destroy()
        self.root.update()
