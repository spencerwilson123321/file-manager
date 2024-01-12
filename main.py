from tkinter import *
from tkinter import ttk
import os
import configparser

SINGLE_CLICK = "<Button-1>"
DOUBLE_CLICK = "<Double-Button-1>"
CTRL_CLICK = "<Control-Button-1>"


class Configuration:
    def __init__(self, window_size, font_size):
        self.window_size = window_size
        self.font_size = font_size

    @staticmethod
    def build_configuration(path):
        """
        Read config file and set properties accordingly.
        """
        conf = configparser.ConfigParser()
        conf.read(path)
        return Configuration(conf["USER"]["window_size"], conf["USER"]["font_size"])


class File(ttk.Label):
    def __init__(self, path, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.selected = False
        self.path = path

    def __repr__(self):
        return f"{self.path} | {self.selected}"

    def select(self):
        self.config(background="light blue")
        self.selected = True

    def deselect(self):
        self.config(background="")
        self.selected = False


class App(ttk.Frame):
    def __init__(self, configuration, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.configuration: Configuration = configuration
        self.hide_hidden_files = True
        self.current_file_index = 0
        self.files: list[File] = []
        self.selected_files: list[File] = []
        self.bind_all("<Up>", self.move_up)
        self.bind_all("<Down>", self.move_down)
        self.bind_all("<Shift-Up>", self.shift_move_up)
        self.bind_all("<Shift-Down>", self.shift_move_down)
        self.bind_all("<Return>", self.interact)
        self.bind_all("h", self.toggle_hidden_files)
        self.bind_all("<Escape>", lambda e: exit(1))
        self.grid()

    def remove_files(self):
        for file_label in self.files:
            file_label.deselect()
            file_label.destroy()
        self.selected_files = []
        self.files = []

    def populate_files(self):
        self.remove_files()
        self.current_file_index = 0
        current_directory = os.getcwd()
        row_index = 0
        if current_directory != "/":
            # First, add the parent directory, if the current working directory isn't root.
            file_label = File("..", text="..")
            file_label.grid(sticky=W, row=row_index)
            row_index += 1
            self.files.append(file_label)
        for file in os.listdir(current_directory):
            if file.startswith(".") and self.hide_hidden_files:
                continue
            path = current_directory + "/" + file
            if os.path.isdir(path):
                file_label = File(path, text=file + "/")
            else:
                file_label = File(path, text=file)
            file_label.grid(sticky=W, row=row_index)
            row_index += 1
            self.files.append(file_label)
        self.selected_files.append(self.files[0])
        self.files[0].select()

    def get_current_file(self):
        return self.files[self.current_file_index]

    def debug(self):
        print(f"selected files: {self.selected_files}")
        print(f"all files: {self.selected_files}")
        print(f"current file index: {self.current_file_index}")

    def toggle_hidden_files(self, e):
        self.hide_hidden_files = not self.hide_hidden_files
        for file in self.selected_files:
            file.deselect()
        self.selected_files = []
        self.populate_files()

    def interact(self, e):
        file = self.get_current_file()
        if os.path.isdir(file.path):
            os.chdir(file.path)
            self.populate_files()

    def move_up(self, e):
        for file in self.selected_files:
            file.deselect()
        if self.current_file_index > 0:
            self.current_file_index -= 1
        new_file = self.get_current_file()
        new_file.select()
        self.selected_files = []
        self.selected_files.append(new_file)

    def move_down(self, e):
        for file in self.selected_files:
            file.deselect()
        if self.current_file_index < len(self.files) - 1:
            self.current_file_index += 1
        new_file = self.get_current_file()
        new_file.select()
        self.selected_files = []
        self.selected_files.append(new_file)

    def shift_move_up(self, e):
        if self.current_file_index > 0:
            self.current_file_index -= 1
        new_file = self.get_current_file()
        new_file.select()
        self.selected_files.append(new_file)

    def shift_move_down(self, e):
        if self.current_file_index < len(self.files) - 1:
            self.current_file_index += 1
        new_file = self.get_current_file()
        new_file.select()
        self.selected_files.append(new_file)


if __name__ == "__main__":
    config_path = "./settings.ini"
    config = Configuration.build_configuration(config_path)
    root = Tk()
    root.geometry(config.window_size)
    root.title("mFiles - The Minimal File Manager")
    app = App(config, root, padding=10)
    app.populate_files()
    root.mainloop()
