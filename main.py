from tkinter import *
from tkinter import ttk
import os
from subprocess import run
import configparser

CLICK = '<Button-1>'


class Configuration:
    def __init__(self, initial_path):
        self.initial_path = initial_path

    def __repr__(self):
        out = (f"Configuration:\n"
               f"Initial Path: {self.initial_path}\n")
        return out

    @staticmethod
    def build_configuration(path):
        """
            Read config file and set properties accordingly.
        """
        conf = configparser.ConfigParser()
        conf.read(path)
        option1 = conf['USER']['initial_path']
        return Configuration(option1)


class App(ttk.Frame):
    def __init__(self, configuration, *args, **kwargs):
        self.configuration: Configuration = configuration
        self.working_directory: str = self.configuration.initial_path
        self.files = []
        super().__init__(*args, **kwargs)
        self.grid()

    def remove_files(self):
        for file_label in self.files:
            file_label.destroy()

    def populate_files(self):
        self.remove_files()
        if self.working_directory != '/':
            # First, add the parent directory, if the current working directory isn't root.
            file_label = ttk.Label(self, text="..")
            file_label.bind(CLICK, lambda e: self.click_handler(e))
            file_label.pack(side="top", anchor="w")
            self.files.append(file_label)
        for file in os.listdir(self.working_directory):
            path = self.working_directory + "/" + file
            if os.path.isdir(path):
                file_label = ttk.Label(self, text=file + "/")
            else:
                file_label = ttk.Label(self, text=file)
            file_label.bind(CLICK, lambda e: self.click_handler(e))
            file_label.pack(side="top", anchor="w")
            self.files.append(file_label)

    def click_handler(self, e):
        path = self.working_directory + "/" + e.widget["text"]
        if os.path.isdir(path):
            self.working_directory = os.path.abspath(path)
            self.populate_files()
        else:
            text_files = {'txt', 'csv', 'json', 'py'}
            extension = os.path.basename(path).split(".")[-1].lower()
            if extension in text_files:
                run([f"/usr/bin/gnome-terminal", "--", "vim", os.path.basename(path)])


if __name__ == "__main__":
    root = Tk()
    DEFAULT_SIZE = "400x400"
    root.geometry(DEFAULT_SIZE)
    root.title("mFiles - The Minimal File Manager")
    config_path = './settings.ini'
    config = Configuration.build_configuration("./settings.ini")
    app = App(config, root, padding=10)
    app.populate_files()
    root.mainloop()
