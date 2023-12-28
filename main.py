from tkinter import *
from tkinter import ttk
import os
import configparser

SINGLE_CLICK = '<Button-1>'
DOUBLE_CLICK = '<Double-Button-1>'
CTRL_CLICK = "<Control-Button-1>"


class Configuration:
    def __init__(self, window_size):
        self.window_size = window_size

    @staticmethod
    def build_configuration(path):
        """
            Read config file and set properties accordingly.
        """
        conf = configparser.ConfigParser()
        conf.read(path)
        window_size = conf['USER']['window_size']
        return Configuration(window_size)


class File(ttk.Label):
    def __init__(self, path, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.path = path

    def __repr__(self):
        return f"{self.path}"

    def select(self):
        self.config(background="light blue")

    def deselect(self):
        self.config(background="")


class App(ttk.Frame):
    def __init__(self, configuration, *args, **kwargs):
        self.configuration: Configuration = configuration
        self.scroll_index = 0
        self.files: list[File] = []
        self.selected_files: list[File] = []
        super().__init__(*args, **kwargs)
        self.grid()
        self.bind_all('<Button-4>', self.scroll_handler_up)
        self.bind_all('<Button-5>', self.scroll_handler_down)

    def remove_files(self):
        for file_label in self.files:
            file_label.destroy()
        self.files = []

    def populate_files(self):
        self.remove_files()
        self.scroll_index = 0
        row_index = 0
        current_directory = os.getcwd()
        if current_directory != '/':
            # First, add the parent directory, if the current working directory isn't root.
            file_label = File("..", text="..")
            file_label.bind(DOUBLE_CLICK, self.double_click_handler)
            file_label.grid(sticky=W, row=row_index, rowspan=1)
            row_index += 1
            self.files.append(file_label)

        for file in os.listdir(current_directory):
            path = current_directory + "/" + file
            if os.path.isdir(path):
                file_label = File(path, text=file + "/")
            else:
                file_label = File(path, text=file)
            file_label.bind(SINGLE_CLICK, self.single_click_handler)
            file_label.bind(DOUBLE_CLICK, self.double_click_handler)
            file_label.bind(CTRL_CLICK, self.ctrl_click_handler)
            file_label.grid(sticky=W, row=row_index, rowspan=1)
            row_index += 1
            self.files.append(file_label)

    def scroll_handler_up(self, e):
        # Hide current.
        self.files[self.scroll_index].grid_forget()
        if self.scroll_index != len(self.files) - 1:
            self.scroll_index += 1

    def scroll_handler_down(self, e):
        self.files[self.scroll_index].grid(sticky=W, row=self.scroll_index)
        if self.scroll_index != 0:
            self.scroll_index -= 1

    def double_click_handler(self, e):
        path = e.widget.path
        if os.path.isdir(path):
            os.chdir(path)
            self.populate_files()
            self.selected_files = []

    def single_click_handler(self, e):
        for file in self.selected_files:
            file.deselect()
        self.selected_files = []
        self.selected_files.append(e.widget)
        e.widget.select()

    def ctrl_click_handler(self, e):
        self.selected_files.append(e.widget)
        e.widget.select()


if __name__ == "__main__":
    config_path = './settings.ini'
    config = Configuration.build_configuration(config_path)
    root = Tk()
    root.geometry(config.window_size)
    root.title("mFiles - The Minimal File Manager")
    app = App(config, root, padding=10)
    app.populate_files()
    root.mainloop()
