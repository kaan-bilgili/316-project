import tkinter as tk
from tkinter import filedialog
import os


class open_project_dialog:

    def __init__(self, root):

        self.root = root

        self.root.title("Open Project")

        self.root.geometry("400x180")


        self.path_label = tk.Label(
            root,
            text="Project Folder:"
        )

        self.path_label.pack(pady=5)

        self.path_entry = tk.Entry(
            root,
            width=40
        )

        self.path_entry.pack()


        self.browse_button = tk.Button(
            root,
            text="Browse",
            command=self.select_project
        )

        self.browse_button.pack(pady=5)


        self.open_button = tk.Button(
            root,
            text="Open Project",
            command=self.open_project
        )

        self.open_button.pack(pady=10)


    def select_project(self):

        folder = filedialog.askdirectory()

        if folder:

            self.path_entry.delete(0, tk.END)

            self.path_entry.insert(0, folder)


    def open_project(self):

        project_path = self.path_entry.get()


        if not project_path:

            print("Please select a project folder.")

            return


        if not os.path.exists(project_path):

            print("Project folder does not exist.")

            return


        print(f"Project opened: {project_path}")

