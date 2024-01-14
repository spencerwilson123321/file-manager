from tkinter import *
from tkinter import ttk
import os
import configparser
import shutil


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
        self.is_permanent_highlight = False
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
        self.copy_list = []
        self.bind_all("<Up>", self.on_up)
        self.bind_all("<Down>", self.on_down)
        self.bind_all("<Shift-Up>", self.on_shift_up)
        self.bind_all("<Shift-Down>", self.on_shift_down)
        self.bind_all("y", self.on_y)
        self.bind_all("<Control-c>", self.on_control_c)
        self.bind_all("<Control-v>", self.on_control_v)
        self.bind_all("<Return>", self.on_enter)
        self.bind_all("h", self.on_h)
        self.bind_all("<Escape>", self.on_escape)
        self.grid()

    def remove_files(self):
        for file_label in self.files:
            file_label.deselect()
            file_label.destroy()
        self.copy_list = []
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

    def on_h(self, e):
        self.hide_hidden_files = not self.hide_hidden_files
        self.clear_selected_files()
        self.populate_files()

    def on_control_c(self, e):
        self.copy_list = []
        for file in self.selected_files:
            if file.path == "..":
                continue
            self.copy_list.append(file)
            print(f"Copied: {file.path}")

    def on_control_v(self, e):
        current_directory = os.getcwd()
        for file in self.copy_list:
            shutil.copy(file.path, current_directory)
        self.populate_files()

    def on_enter(self, e):
        file = self.get_current_file()
        if os.path.isdir(file.path):
            os.chdir(file.path)
            self.populate_files()

    def clear_selected_files(self):
        for file in self.selected_files:
            file.deselect()
            file.is_permanent_highlight = False
        self.selected_files = []

    def on_escape(self, e):
        """
        Clear the selected files, and
        """
        self.clear_selected_files()
        self.files[self.current_file_index].select()
        self.selected_files.append(self.files[self.current_file_index])

    def on_y(self, e):
        """
        Highlight the current file permanently, it shouldn't be unselected unless Esc is pressed.
        """
        self.files[self.current_file_index].is_permanent_highlight = True

    def on_up(self, e):
        to_remove = []
        for file in self.selected_files:
            if file.is_permanent_highlight:
                continue
            file.deselect()
            to_remove.append(file)
        for file in to_remove:
            self.selected_files.remove(file)
        if self.current_file_index > 0:
            self.current_file_index -= 1
        new_file = self.get_current_file()
        if new_file.selected:
            return
        new_file.select()
        self.selected_files.append(new_file)

    def on_down(self, e):
        to_remove = []
        for file in self.selected_files:
            if file.is_permanent_highlight:
                continue
            file.deselect()
            to_remove.append(file)
        for file in to_remove:
            self.selected_files.remove(file)
        if self.current_file_index < len(self.files) - 1:
            self.current_file_index += 1
        new_file = self.get_current_file()
        if new_file.selected:
            return
        new_file.select()
        self.selected_files.append(new_file)

    def on_shift_up(self, e):
        if self.current_file_index > 0:
            self.current_file_index -= 1
        new_file = self.get_current_file()
        if new_file.selected:
            return
        new_file.select()
        self.selected_files.append(new_file)

    def on_shift_down(self, e):
        if self.current_file_index < len(self.files) - 1:
            self.current_file_index += 1
        new_file = self.get_current_file()
        if new_file.selected:
            return
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
