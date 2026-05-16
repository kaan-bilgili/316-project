import tkinter as tk
from tkinter import messagebox

from data.configuration_repository import ConfigurationRepository
from model.configuration import Configuration


class configuration_dialog:

    def __init__(self, root, repository=None):
        self.root = root
        self.repository = repository or ConfigurationRepository()

        self.root.title("Configurations")
        self.root.geometry("620x320")

        self.list_frame = tk.Frame(root)
        self.list_frame.pack(side=tk.LEFT, fill=tk.Y, padx=10, pady=10)

        self.list_label = tk.Label(self.list_frame, text="Saved Configurations")
        self.list_label.pack()

        self.config_listbox = tk.Listbox(self.list_frame, width=25, height=12)
        self.config_listbox.pack(fill=tk.Y, expand=True)
        self.config_listbox.bind("<<ListboxSelect>>", self.load_selected_configuration)

        self.form_frame = tk.Frame(root)
        self.form_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=10, pady=10)

        self.name_label = tk.Label(self.form_frame, text="Name:")
        self.name_label.pack(anchor="w")
        self.name_entry = tk.Entry(self.form_frame, width=45)
        self.name_entry.pack(fill=tk.X)

        self.compiler_path_label = tk.Label(self.form_frame, text="Compiler Path:")
        self.compiler_path_label.pack(anchor="w", pady=(8, 0))
        self.compiler_path_entry = tk.Entry(self.form_frame, width=45)
        self.compiler_path_entry.pack(fill=tk.X)

        self.source_filename_label = tk.Label(self.form_frame, text="Source Filename:")
        self.source_filename_label.pack(anchor="w", pady=(8, 0))
        self.source_filename_entry = tk.Entry(self.form_frame, width=45)
        self.source_filename_entry.pack(fill=tk.X)

        self.compiler_args_label = tk.Label(self.form_frame, text="Compiler Args:")
        self.compiler_args_label.pack(anchor="w", pady=(8, 0))
        self.compiler_args_entry = tk.Entry(self.form_frame, width=45)
        self.compiler_args_entry.pack(fill=tk.X)

        self.button_frame = tk.Frame(self.form_frame)
        self.button_frame.pack(anchor="e", pady=15)

        self.new_button = tk.Button(self.button_frame, text="New", command=self.new_configuration)
        self.new_button.pack(side=tk.LEFT, padx=4)

        self.save_button = tk.Button(self.button_frame, text="Save", command=self.save_configuration)
        self.save_button.pack(side=tk.LEFT, padx=4)

        self.delete_button = tk.Button(self.button_frame, text="Delete", command=self.delete_configuration)
        self.delete_button.pack(side=tk.LEFT, padx=4)

        self.close_button = tk.Button(self.button_frame, text="Close", command=self.root.destroy)
        self.close_button.pack(side=tk.LEFT, padx=4)

        self.refresh_configuration_list()
        self.new_configuration()

    def refresh_configuration_list(self):
        self.config_listbox.delete(0, tk.END)

        configurations = self.repository.load_all()
        configurations.sort(key=lambda configuration: configuration.name.lower())

        for configuration in configurations:
            self.config_listbox.insert(tk.END, configuration.name)

    def new_configuration(self):
        self.config_listbox.selection_clear(0, tk.END)
        self._set_form_values(
            name="",
            compiler_path="gcc",
            source_filename="main.c",
            compiler_args="-o main.exe",
        )

    def load_selected_configuration(self, event=None):
        selection = self.config_listbox.curselection()

        if not selection:
            return

        name = self.config_listbox.get(selection[0])
        configuration = self.repository.load(name)

        if configuration is None:
            messagebox.showerror("Configuration Error", "Selected configuration was not found.")
            self.refresh_configuration_list()
            return

        self._set_form_values(
            name=configuration.name,
            compiler_path=configuration.compiler_path,
            source_filename=configuration.source_filename,
            compiler_args=configuration.compiler_args,
        )

    def save_configuration(self):
        try:
            configuration = Configuration(
                name=self.name_entry.get().strip(),
                compiler_path=self.compiler_path_entry.get().strip(),
                source_filename=self.source_filename_entry.get().strip(),
                compiler_args=self.compiler_args_entry.get().strip(),
            )
            self.repository.save(configuration)
        except ValueError as error:
            messagebox.showerror("Validation Error", str(error))
            return

        self.refresh_configuration_list()
        self._select_configuration(configuration.name)
        messagebox.showinfo("Configuration Saved", "Configuration saved successfully.")

    def delete_configuration(self):
        name = self.name_entry.get().strip()

        if not name:
            messagebox.showerror("Validation Error", "Select a configuration to delete.")
            return

        try:
            deleted = self.repository.delete(name)
        except ValueError as error:
            messagebox.showerror("Validation Error", str(error))
            return

        if not deleted:
            messagebox.showerror("Configuration Error", "Configuration was not found.")
            self.refresh_configuration_list()
            return

        self.refresh_configuration_list()
        self.new_configuration()
        messagebox.showinfo("Configuration Deleted", "Configuration deleted successfully.")

    def _set_form_values(self, name, compiler_path, source_filename, compiler_args):
        self.name_entry.delete(0, tk.END)
        self.name_entry.insert(0, name)

        self.compiler_path_entry.delete(0, tk.END)
        self.compiler_path_entry.insert(0, compiler_path)

        self.source_filename_entry.delete(0, tk.END)
        self.source_filename_entry.insert(0, source_filename)

        self.compiler_args_entry.delete(0, tk.END)
        self.compiler_args_entry.insert(0, compiler_args)

    def _select_configuration(self, name):
        for index in range(self.config_listbox.size()):
            if self.config_listbox.get(index) == name:
                self.config_listbox.selection_set(index)
                self.config_listbox.see(index)
                return
