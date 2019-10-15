import tkinter as tk
import tkinter.messagebox as tm
from threading import Thread
from time import sleep
from qr_code import qr_cam


class UserInterface():
    def __init__(self, connection_manager):
        self.root = tk.Tk()
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
        )
        self.scan_part_button = tk.Button(
            self.main_frame,
            text = "Scan Component",
            command = self.scan_part,
        )


        self.main_frame.pack()
        self.online_status_indicator.pack()

        self.new_part_button.grid(row=0, column=0)
        self.scan_part_button.grid(row=1, column=0)



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
            text = "Online"
        else:
            text = "Offline"
        self.online_status_indicator.config(text=text)


    def enter_credentials(self):
        LoginFrame(self.connection_manager, self.update_online_status)


    def scan_part(self):
        id = qr_cam()



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
