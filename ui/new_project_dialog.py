import tkinter as tk
from tkinter import filedialog
import os


class new_project_dialog:

    def __init__(self, root):

        self.root = root

        self.root.title("New Project")

        self.root.geometry("400x200")


        self.name_label = tk.Label(root, text="Project Name:")

        self.name_label.pack()

        self.name_entry = tk.Entry(root, width=40)

        self.name_entry.pack()


        self.location_label = tk.Label(root, text="Project Location:")

        self.location_label.pack()

        self.location_entry = tk.Entry(root, width=40)

        self.location_entry.pack()


        self.browse_button = tk.Button(
            root,
            text="Browse",
            command=self.select_folder
        )

        self.browse_button.pack()


        self.create_button = tk.Button(
            root,
            text="Create Project",
            command=self.create_project
        )

        self.create_button.pack(pady=10)


    def select_folder(self):

        folder = filedialog.askdirectory()

        if folder:

            self.location_entry.delete(0, tk.END)

            self.location_entry.insert(0, folder)


    def create_project(self):

        project_name = self.name_entry.get()

        project_location = self.location_entry.get()


        if not project_name or not project_location:

            print("Please fill all fields.")

            return


        project_path = os.path.join(
            project_location,
            project_name
        )

        os.makedirs(project_path, exist_ok=True)

        print(f"Project created at: {project_path}")

