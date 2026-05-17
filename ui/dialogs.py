import customtkinter as ctk
from tkinter import messagebox


class NewProjectDialog(ctk.CTkToplevel):
    def __init__(self, parent, ui, config_names, on_created):
        super().__init__(parent)
        self.ui = ui
        self.on_created = on_created
        self.title(ui.tr("new_project_title"))
        self.geometry("420x280")
        self.resizable(False, False)
        self.transient(parent)
        self.grab_set()

        pad = 12
        form = ctk.CTkFrame(self, fg_color="transparent")
        form.pack(fill="both", expand=True, padx=20, pady=16)

        self.name_entry = self._row(form, ui.tr("project_name"), 0)
        self.desc_entry = self._row(form, ui.tr("project_description"), 1)

        ctk.CTkLabel(form, text=ui.tr("project_config_name"), anchor="w").grid(
            row=2, column=0, sticky="w", pady=(pad, 4)
        )
        self.config_var = ctk.StringVar(value=config_names[0] if config_names else "")
        self.config_menu = ctk.CTkOptionMenu(
            form,
            variable=self.config_var,
            values=config_names or [""],
            width=260,
        )
        self.config_menu.grid(row=2, column=1, sticky="ew", pady=(pad, 4))
        form.grid_columnconfigure(1, weight=1)

        actions = ctk.CTkFrame(self, fg_color="transparent")
        actions.pack(fill="x", padx=20, pady=(0, 16))
        ctk.CTkButton(
            actions, text=ui.tr("new_project"), command=self._submit
        ).pack(side="right", padx=(8, 0))
        ctk.CTkButton(actions, text=ui.tr("cancel"), command=self.destroy).pack(side="right")

    def _row(self, parent, label, row):
        ctk.CTkLabel(parent, text=label, anchor="w").grid(
            row=row, column=0, sticky="w", pady=8
        )
        entry = ctk.CTkEntry(parent, width=260)
        entry.grid(row=row, column=1, sticky="ew", pady=8)
        return entry

    def _submit(self):
        name = self.name_entry.get().strip()
        if not name:
            messagebox.showerror(
                self.ui.tr("new_project_title"), self.ui.tr("err_project_name")
            )
            return
        description = self.desc_entry.get().strip()
        configuration_name = self.config_var.get().strip()
        if not configuration_name:
            messagebox.showerror(
                self.ui.tr("new_project_title"), self.ui.tr("err_config_name")
            )
            return
        self.on_created(name, description, configuration_name)
        self.destroy()
