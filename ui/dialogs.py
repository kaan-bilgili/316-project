import customtkinter as ctk
from tkinter import messagebox

from ui.theme import BG_COLOR, BTN_TEXT_COLOR, BUTTON_COLOR, BUTTON_HOVER, GLASS_BG, TEXT_COLOR


def _cyber_button(parent, text, command):
    return ctk.CTkButton(
        parent,
        text=text,
        command=command,
        fg_color=BUTTON_COLOR,
        hover_color=BUTTON_HOVER,
        border_width=0,
        text_color=BTN_TEXT_COLOR,
    )


class NewProjectDialog(ctk.CTkToplevel):
    def __init__(self, parent, ui, config_names, on_created):
        super().__init__(parent)
        self.ui = ui
        self.on_created = on_created
        self.title(ui.tr("new_project_title"))
        self.geometry("420x280")
        self.resizable(False, False)
        self.configure(fg_color=BG_COLOR)
        self.transient(parent)
        self.grab_set()

        pad = 12
        form = ctk.CTkFrame(self, fg_color="transparent")
        form.pack(fill="both", expand=True, padx=20, pady=16)

        self.name_entry = self._row(form, ui.tr("project_name"), 0)
        self.desc_entry = self._row(form, ui.tr("project_description"), 1)

        ctk.CTkLabel(form, text=ui.tr("project_config_name"), anchor="w", text_color=TEXT_COLOR).grid(
            row=2, column=0, sticky="w", pady=(pad, 4)
        )
        self.config_var = ctk.StringVar(value=config_names[0] if config_names else "")
        self.config_menu = ctk.CTkOptionMenu(
            form,
            variable=self.config_var,
            values=config_names if config_names else ["No Configurations"],
            width=260,
            fg_color=GLASS_BG,
            text_color=TEXT_COLOR,
        )
        self.config_menu.grid(row=2, column=1, sticky="ew", pady=(pad, 4))
        form.grid_columnconfigure(1, weight=1)

        actions = ctk.CTkFrame(self, fg_color="transparent")
        actions.pack(fill="x", padx=20, pady=(0, 16))
        _cyber_button(
            actions, text=ui.tr("new_project"), command=self._submit
        ).pack(side="right", padx=(8, 0))
        _cyber_button(actions, text=ui.tr("cancel"), command=self.destroy).pack(side="right")

        self.name_entry.focus()

        self.bind("<Return>", lambda event: self._submit())

    def _row(self, parent, label, row):
        ctk.CTkLabel(parent, text=label, anchor="w", text_color=TEXT_COLOR).grid(
            row=row, column=0, sticky="w", pady=8
        )
        entry = ctk.CTkEntry(parent, width=260, fg_color=GLASS_BG, text_color=TEXT_COLOR)
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
        if not configuration_name or configuration_name == "No Configurations":
            messagebox.showerror(
                self.ui.tr("new_project_title"), self.ui.tr("err_config_name")
            )
            return
        self.on_created(name, description, configuration_name)
        self.destroy()
