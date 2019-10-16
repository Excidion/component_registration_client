import tkinter as tk
import tkinter.messagebox as tm
from threading import Thread
from time import sleep
from qr_code import qr_cam
from utils import generate_part_id
from datetime import datetime


class UserInterface():
    def __init__(self, connection_manager):
        self.root = tk.Tk()
        self.root.title("Component Registration")
        self.root.bind("<Escape>", lambda x: self.root.destroy())
        self.connection_manager = connection_manager
        self.online_status_indicator = tk.Button(
            self.root,
            text = "Connecting...",
            command = self.enter_credentials,
        )
        self.main_frame = tk.Frame(self.root)

        self.new_part_button = tk.Button(
            self.main_frame,
            text = "New Component",
            width = 25,
            height = 3,
            command = self.new_part,
        )
        self.scan_part_button = tk.Button(
            self.main_frame,
            text = "Scan Component",
            width = 25,
            height = 3,
            command = self.scan_part,
        )

        self.working_frame = tk.LabelFrame(
            self.main_frame,
            text = "Component",
        )
        self.display_id = DisplayFrame(
            self.working_frame,
            label = "ID",
        )
        self.display_assembly_group = SelectionFrame(
            self.working_frame,
            label = "Assembly Group",
        )
        self.display_module = SelectionFrame(
            self.working_frame,
            label = "Module",
        )
        self.display_state = DisplayFrame(
            self.working_frame,
            label = "State",
        )
        self.display_state_time = DisplayFrame(
            self.working_frame,
            label = "In state since",
        )
        self.display_state_comment = DisplayFrame(
            self.working_frame,
            label = "Last comment"
        )

        self.display_new_state = SelectionFrame(
            self.working_frame,
            label = "New State",
            options = [
                "manufactured",
                "installed",
                "removed",
                "damaged",
                "repaired",
            ],
            expandable = False,
        )
        self.display_new_time = EntryFrame(
            self.working_frame,
            label = "Time",
        )
        self.display_new_comment = EntryFrame(
            self.working_frame,
            label = "Comment"
        )


        self.main_frame.pack()
        self.online_status_indicator.pack()

        self.new_part_button.grid(row=0, column=0)
        self.scan_part_button.grid(row=1, column=0)
        self.working_frame.grid(row=0, column=1, rowspan=2, sticky="nesw")

        self.display_id.grid(row=0, column=0, sticky="nesw")
        self.display_assembly_group.grid(row=0, column=1, sticky="nesw")
        self.display_module.grid(row=0, column=2, sticky="nesw")

        self.display_state_time.grid(row=1, column=0, sticky="nesw")
        self.display_state.grid(row=1, column=1, sticky="nesw")
        self.display_state_comment.grid(row=1, column=2, sticky="nesw")

        self.display_new_time.grid(row=2, column=0, sticky="nesw")
        self.display_new_state.grid(row=2, column=1, sticky="nesw")
        self.display_new_comment.grid(row=2, column=2, sticky="nesw")



    def start(self):
        t = Thread(
            target = self.supervise_online_status,
            args = [],
        )
        t.start()
        self.root.mainloop()


    def supervise_online_status(self):
        while not sleep(5):
            self.update_online_status()

    def update_online_status(self):
        if self.connection_manager.check_online_status():
            text = f"Online as " + self.connection_manager.config["user"]
        else:
            text = "Offline"
        self.online_status_indicator.config(text=text)


    def enter_credentials(self):
        LoginFrame(self.connection_manager, self.update_online_status)


    def scan_part(self):
        id = qr_cam()
        self.display_id.set(id)
        self.display_new_state.set("")
        self.display_new_comment.set("-")
        self.display_new_time.set(str(datetime.now()).split(".")[0])
        self.display_assembly_group.freeze()
        self.display_module.freeze()

    def new_part(self):
        id = generate_part_id()
        self.display_id.set(id)
        self.display_state_time.set("NA")
        self.display_state.set("NA")
        self.display_state_comment.set("NA")

        self.display_new_time.set(str(datetime.now()).split(".")[0])
        self.display_new_state.set("manufactured")
        self.display_new_comment.set("-")
        self.display_assembly_group.unfreeze()
        self.display_module.unfreeze()


class DisplayFrame(tk.LabelFrame):
    def __init__(self, *args, label, **kwargs):
        super().__init__(*args, **kwargs)
        self.label = label
        self.var = ""
        self.config(text=self.label)
        self.display = tk.Label(self, text="")
        self.display.pack()
        self.set()

    def set(self, entry=None):
        if not entry == None:
            self.var = entry
            display_text = entry
        else:
            self.var = ""
            display_text = f"<{self.label}>"
        self.display.config(text=display_text)

    def get(self):
        return self.var



class EntryFrame(tk.LabelFrame):
    def __init__(self, *args, label, **kwargs):
        super().__init__(*args, **kwargs)
        self.label = label
        self.config(text=self.label)
        self.display = tk.Entry(self)
        self.display.pack()

    def set(self, entry):
        self.display.delete(0, tk.END)
        self.display.insert(0, entry)
        #self.display.set(entry)

    def get(self):
        return self.display.get()



class SelectionFrame(tk.LabelFrame):
    def __init__(self, *args, label, options=[], expandable=True,**kwargs):
        super().__init__(*args, **kwargs)
        self.label = label
        self.options = options
        self.var = tk.StringVar()
        self.config(text=self.label)
        self.display = tk.OptionMenu(
            self,
            self.var,
            "",
            *options,
        )
        self.display.grid(sticky="ew")
        if expandable:
            self.button = tk.Button(
                self,
                text = f"Add {self.label}",
                width=30, height=2,
                command=self.add_option_dialogue,
            )
            self.button.grid(sticky="ew")
            self.freeze()


    def freeze(self):
        try:
            self.display.config(state="disabled")
            self.button.config(state="disabled")
        except: pass

    def unfreeze(self):
        try:
            self.display.config(state="normal")
            self.button.config(state="normal")
        except: pass

    def add_option_dialogue(self):
        add_and_exit = lambda x: [self.add_option(entry.get()), popup.destroy()]
        popup = tk.Toplevel()
        popup.bind("<Return>", add_and_exit)
        popup.bind("<Escape>", lambda x: popup.destroy())
        entry = tk.Entry(popup)
        add = tk.Button(popup,
            text = f"Add {self.label}",
            command = lambda: add_and_exit(0),
        )
        cancel = tk.Button(popup, text="Cancel", command=popup.destroy)
        entry.grid()
        add.grid(sticky="ew")
        cancel.grid(sticky="ew")
        popup.mainloop()


    def add_option(self, option):
        self.display['menu'].add_command(
            label = option,
            command = tk._setit(self.var, option),
        )
        self.set(option)

    def set(self, val):
        self.var.set(val)

    def get(self):
        return self.var.get()



class LoginFrame(tk.Toplevel):
    def __init__(self, connection_manager, update_ui):
        super().__init__()
        self.connection_manager = connection_manager
        self.update_ui = update_ui

        self.label_username = tk.Label(self, text="Username")
        self.label_password = tk.Label(self, text="Password")
        self.entry_username = tk.Entry(self)
        self.entry_password = tk.Entry(self, show="*")
        boolvar = tk.BooleanVar()
        self.checkbox = tk.Checkbutton(
            self,
            text = "Remember Crendentials.",
            var = boolvar,
            onvalue = True,
            offvalue = False,
        )
        self.checkbox.var = boolvar
        self.logbtn = tk.Button(self, text="Login", command=self.login)
        self.bind("<Return>", self.login)

        self.label_username.grid(row=0, sticky="e")
        self.label_password.grid(row=1, sticky="e")
        self.entry_username.grid(row=0, column=1)
        self.entry_password.grid(row=1, column=1)
        self.checkbox.grid(columnspan=2)
        self.logbtn.grid(columnspan=2)


    def login(self, event=None):
        username = self.entry_username.get()
        password = self.entry_password.get()
        self.connection_manager.set_credentials(
            username,
            password,
            self.checkbox.var.get(),
        )
        if self.connection_manager.check_online_status():
            tm.showinfo("Database Connection", "Login successfull.")
        else:
            tm.showerror("Database Connection", "Connection could not be established.")
        self.update_ui()
        self.destroy()
