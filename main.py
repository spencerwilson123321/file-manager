from tkinter import *
from tkinter import ttk
import os
import configparser

SINGLE_CLICK = '<Button-1>'
DOUBLE_CLICK = '<Double-Button-1>'

class Configuration:
    def __init__(self, initial_path, window_size):
        self.initial_path = initial_path
        self.window_size = window_size

    @staticmethod
    def build_configuration(path):
        """
            Read config file and set properties accordingly.
        """
        conf = configparser.ConfigParser()
        conf.read(path)
        initial_path = conf['USER']['initial_path']
        window_size = conf['USER']['window_size']
        return Configuration(initial_path, window_size)


class App(ttk.Frame):
    def __init__(self, configuration, *args, **kwargs):
        self.configuration: Configuration = configuration
        self.working_directory: str = self.configuration.initial_path
        self.scroll_index = 0
        self.files = []
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
        if self.working_directory != '/':
            # First, add the parent directory, if the current working directory isn't root.
            file_label = ttk.Label(self, text="..")
            file_label.bind(DOUBLE_CLICK, self.double_click_handler)
            file_label.grid(sticky=W, row=row_index)
            row_index += 1
            self.files.append(file_label)

        for file in os.listdir(self.working_directory):
            path = self.working_directory + "/" + file
            if os.path.isdir(path):
                file_label = ttk.Label(self, text=file + "/")
            else:
                file_label = ttk.Label(self, text=file)
            file_label.bind(DOUBLE_CLICK, self.double_click_handler)
            file_label.grid(sticky=W, row=row_index)
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
        path = self.working_directory + "/" + e.widget["text"]
        if os.path.isdir(path):
            self.working_directory = os.path.abspath(path)
            self.populate_files()


if __name__ == "__main__":
    config_path = './settings.ini'
    config = Configuration.build_configuration(config_path)
    root = Tk()
    root.geometry(config.window_size)
    root.title("mFiles - The Minimal File Manager")
    app = App(config, root, padding=10)
    app.populate_files()
    root.mainloop()
