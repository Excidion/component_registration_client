import tkinter as tk
import tkinter.messagebox as tm
from tkinter.filedialog import asksaveasfilename as save_as
from PIL import ImageTk
from threading import Thread
from time import sleep
from qr_code import qr_cam, create_qr_code, save_qr_code
from utils import generate_part_id
from datetime import datetime


class UserInterface():
    def __init__(self, connection_manager):
        self.root = tk.Tk()
        self.root.title("Component Registration")
        self.root.bind("<Escape>", lambda x: self.root.destroy())
        self.root.resizable(width=False, height=False)
        self.connection_manager = connection_manager
        self.main_frame = tk.Frame(self.root)
        self.online_status_indicator = tk.Button(
            self.main_frame,
            text = "Connecting...",
            command = self.enter_credentials,
        )

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
        self.submit_work_button = tk.Button(
            self.main_frame,
            text = "Submit Entries",
            width = 25,
            height = 3,
            command = lambda: print("PUSH!"),
        )

        self.working_frame = tk.LabelFrame(
            self.main_frame,
            text = "Component",
        )

        self.display_id = DisplayFrame(
            self.working_frame,
            label = "ID",
        )
        self.display_qr = ImageButton(
            self.display_id,
            image = create_qr_code(self.display_id.get()),
            resize = (250, 250),
            command = lambda: save_qr_code(
                self.display_id.get(),
                save_as(filetypes=[("PNG files","*.png"),("all files","*.*")]),
            ),
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
        self.new_part_button.grid(row=0, column=0, sticky="new")
        self.scan_part_button.grid(row=0, column=0, sticky="esw")
        self.submit_work_button.grid(row=2, column=0)
        self.online_status_indicator.grid(row=3, column=0)
        self.working_frame.grid(row=0, column=1, rowspan=4, sticky="nesw")

        self.display_id.grid(row=0, column=0, sticky="nesw")
        self.display_qr.pack()
        self.display_assembly_group.grid(row=0, column=1, sticky="nesw")
        self.display_module.grid(row=0, column=2, sticky="nesw")

        self.display_state_time.grid(row=1, column=0, sticky="nesw")
        self.display_state.grid(row=1, column=1, sticky="nesw")
        self.display_state_comment.grid(row=1, column=2, sticky="nesw")

        self.display_new_time.grid(row=2, column=0, sticky="nesw")
        self.display_new_state.grid(row=2, column=1, sticky="nesw")
        self.display_new_comment.grid(row=2, column=2, sticky="nesw")

        self.reset_ui()


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
            text = f"Online as\n" + self.connection_manager.config["user"]
        else:
            text = "Offline"
        self.online_status_indicator.config(text=text)


    def enter_credentials(self):
        LoginWindow(self.connection_manager, self.update_online_status)


    def scan_part(self):
        self.reset_ui()
        id = qr_cam()
        if self.connection_manager.check_part_existence(id, allow_offline=True):
            self.display_id.set(id)
            self.display_new_state.set("")
            self.display_new_comment.set("-")
            self.display_new_time.set(str(datetime.now()).split(".")[0])
            slef.display_new_state.unfreeze()
        else:
            tm.showerror("Database Lookup", f"Part ({id}) could not be found.")
            self.display_id.set("")
        self.display_qr.change_image(create_qr_code(self.display_id.get()))


    def new_part(self):
        self.reset_ui()
        id = generate_part_id()
        self.display_id.set(id)
        self.display_qr.change_image(create_qr_code(self.display_id.get()))
        self.display_state_time.set("NA")
        self.display_state.set("NA")
        self.display_state_comment.set("NA")

        self.display_new_time.set(str(datetime.now()).split(".")[0])
        self.display_new_state.set("manufactured")
        self.display_new_state.freeze()
        self.display_new_comment.set("-")
        self.display_assembly_group.unfreeze()
        self.display_module.unfreeze()


    def reset_ui(self):
        for child in self.working_frame.winfo_children():
            try:
                child.freeze()
            except: pass
            try:
                child.set("")
            except: pass



class DisplayFrame(tk.LabelFrame):
    def __init__(self, *args, label, **kwargs):
        super().__init__(*args, **kwargs)
        self.label = label
        self.var = ""
        self.config(text=self.label)
        self.display = tk.Label(self, text="")
        self.display.pack()
        self.set("")

    def set(self, entry):
        if not entry == "":
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




class ImageButton(tk.Button):
    def __init__(self, *args, image, resize=None, **kwargs):
        image = self.prep_image(image, resize)
        super(ImageButton, self).__init__(
            *args,
            **kwargs,
            image = image,
            width = image.width(),
            height = image.height(),
            anchor = tk.CENTER,
        )
        self.image = image # wtf magic pls don't touch

    def change_image(self, image, resize=None, **kwargs):
        image = self.prep_image(image, resize)
        self.config(image=image)
        self.image = image

    def prep_image(self, image, resize):
        if not resize == None:
            image = image.resize(resize)
        else:
            try:
                image = image.resize((self.image.width(), self.image.height()))
            except: pass
        return ImageTk.PhotoImage(image)




class LoginWindow(tk.Toplevel):
    def __init__(self, connection_manager, update_ui):
        super().__init__()
        self.title("Login")
        self.bind("<Escape>", lambda x: self.destroy())
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
