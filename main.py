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


class Dialog(ttk.Frame):
    NEW_FILE = 1
    NEW_DIRECTORY = 2

    def __init__(self, label_text, action, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.label = Label(self, text=label_text)
        self.entry = Entry(self)
        self.action = action
        self.label.pack(side=LEFT)
        self.entry.pack(side=LEFT)
        self.entry.focus()

    def get_value(self):
        return self.entry.get()


class App(ttk.Frame):
    def __init__(self, configuration, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.configuration: Configuration = configuration
        self.hide_hidden_files = True
        self.current_file_index = 0
        self.files: list[File] = []
        self.selected_files: list[File] = []
        self.copy_list = []
        self.cut_list = []
        self.dialog = None
        self.bind_all("<Up>", self.on_up)
        self.bind_all("<Down>", self.on_down)
        self.bind_all("<Shift-Up>", self.on_shift_up)
        self.bind_all("<Shift-Down>", self.on_shift_down)
        self.bind_all("y", self.on_y)
        self.bind_all("<Control-c>", self.on_control_c)
        self.bind_all("<Control-x>", self.on_control_x)
        self.bind_all("<Control-v>", self.on_control_v)
        self.bind_all("<Control-n>", self.on_control_n)
        self.bind_all("<Return>", self.on_enter)
        self.bind_all("h", self.on_h)
        self.bind_all("<Escape>", self.on_escape)
        self.pack(expand=True, fill=BOTH)

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
            file_label = File("..", self, text="..")
            file_label.pack(side=TOP, fill=X)
            row_index += 1
            self.files.append(file_label)
        for file in os.listdir(current_directory):
            if file.startswith(".") and self.hide_hidden_files:
                continue
            path = current_directory + "/" + file
            if os.path.isdir(path):
                file_label = File(path, self, text=file + "/")
            else:
                file_label = File(path, self, text=file)
            file_label.pack(side=TOP, fill=X)
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

    def clear_dialog(self):
        if self.dialog is not None:
            self.dialog.forget()
            self.dialog = None

    def on_h(self, e):
        if self.dialog is not None:
            return
        self.hide_hidden_files = not self.hide_hidden_files
        self.clear_selected_files()
        self.populate_files()

    def on_control_n(self, e):
        self.clear_selected_files()
        self.dialog = Dialog("New filename: ", Dialog.NEW_FILE, self)
        self.dialog.pack(side=BOTTOM, anchor=W)

    def on_control_c(self, e):
        self.copy_list = []
        self.cut_list = []
        for file in self.selected_files:
            if file.path == "..":
                continue
            self.copy_list.append(file)
            print(f"Copied: {file.path}")

    def on_control_x(self, e):
        self.copy_list = []
        self.cut_list = []
        for file in self.selected_files:
            if file.path == "..":
                continue
            self.cut_list.append(file)
            print(f"Cut: {file.path}")

    def on_control_v(self, e):
        if not self.copy_list and not self.cut_list:
            return
        current_directory = os.getcwd()
        if self.copy_list:
            for file in self.copy_list:
                shutil.copy(file.path, current_directory)
                print(f"copied: {file.path} to {current_directory}")
        elif self.cut_list:
            for file in self.cut_list:
                shutil.move(file.path, current_directory)
                print(f"moved: {file.path} to {current_directory}")
        self.populate_files()

    def on_enter(self, e):
        if self.dialog is not None:
            if self.dialog.action == Dialog.NEW_FILE:
                filename = self.dialog.get_value()
                with open(filename, "w") as f:
                    pass
                self.populate_files()
            return
        if not self.selected_files:
            return
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
        self.clear_dialog()
        self.clear_selected_files()
        self.files[self.current_file_index].select()
        self.selected_files.append(self.files[self.current_file_index])

    def on_y(self, e):
        """
        Highlight the current file permanently, it shouldn't be unselected unless Esc is pressed.
        """
        if self.dialog is not None:
            return
        self.files[self.current_file_index].is_permanent_highlight = True

    def on_up(self, e):
        self.clear_dialog()
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
        self.clear_dialog()
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
        self.clear_dialog()
        if self.current_file_index > 0:
            self.current_file_index -= 1
        new_file = self.get_current_file()
        if new_file.selected:
            return
        new_file.select()
        self.selected_files.append(new_file)

    def on_shift_down(self, e):
        self.clear_dialog()
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
