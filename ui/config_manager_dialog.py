import customtkinter as ctk
from tkinter import messagebox

from data.configuration_repository import ConfigurationRepository
from model.configuration import Configuration


class ConfigManagerDialog(ctk.CTkToplevel):
    """Dialog for listing, editing and deleting configurations. Covers Req 4."""

    def __init__(self, parent, config_repo: ConfigurationRepository, tr):
        super().__init__(parent)
        self.config_repo = config_repo
        self.tr = tr
        self.title(tr("manage_configs_title"))
        self.geometry("620x420")
        self.resizable(False, False)
        self.transient(parent)
        self.grab_set()

        self._build_ui()
        self._refresh_list()

    def _build_ui(self):
        self.listbox = ctk.CTkScrollableFrame(self)
        self.listbox.pack(fill="both", expand=True, padx=16, pady=(16, 8))

        btn_frame = ctk.CTkFrame(self, fg_color="transparent")
        btn_frame.pack(fill="x", padx=16, pady=(0, 16))

        ctk.CTkButton(
            btn_frame, text=self.tr("new_config_title"), command=self._new_config
        ).pack(side="left")

        ctk.CTkButton(
            btn_frame, text=self.tr("cancel"), command=self.destroy
        ).pack(side="right")

    def _refresh_list(self):
        for widget in self.listbox.winfo_children():
            widget.destroy()

        configs = self.config_repo.load_all()
        if not configs:
            ctk.CTkLabel(
                self.listbox, text=self.tr("no_configs"), text_color="gray"
            ).pack(pady=20)
            return

        for config in configs:
            row = ctk.CTkFrame(self.listbox, fg_color="transparent")
            row.pack(fill="x", pady=4)

            ctk.CTkLabel(row, text=config.name, anchor="w", width=180).pack(
                side="left", padx=8
            )
            ctk.CTkLabel(
                row,
                text=f"{config.compiler_path}  |  {config.source_filename}",
                text_color="gray",
                anchor="w",
            ).pack(side="left", expand=True)

            ctk.CTkButton(
                row, text=self.tr("edit"), width=70,
                command=lambda c=config: self._edit_config(c),
            ).pack(side="right", padx=(4, 0))

            ctk.CTkButton(
                row, text=self.tr("delete"), width=70,
                fg_color="#c0392b", hover_color="#922b21",
                command=lambda c=config: self._delete_config(c),
            ).pack(side="right", padx=(4, 0))

    def _new_config(self):
        ConfigEditDialog(self, None, self.config_repo, self.tr, self._refresh_list)

    def _edit_config(self, config: Configuration):
        ConfigEditDialog(self, config, self.config_repo, self.tr, self._refresh_list)

    def _delete_config(self, config: Configuration):
        confirmed = messagebox.askyesno(
            self.tr("delete_config_title"),
            self.tr("confirm_delete_config").format(config.name),
            parent=self,
        )
        if confirmed:
            self.config_repo.delete(config.name)
            self._refresh_list()


class ConfigEditDialog(ctk.CTkToplevel):
    """Form for creating or editing a single configuration."""

    def __init__(self, parent, config, config_repo: ConfigurationRepository, tr, on_save):
        super().__init__(parent)
        self.config_repo = config_repo
        self.tr = tr
        self.on_save = on_save
        self.old_name = config.name if config else None
        self.title(tr("edit_config_title") if config else tr("new_config_title"))
        self.geometry("460x400")
        self.resizable(False, False)
        self.transient(parent)
        self.grab_set()

        self._build_form(config)

    def _build_form(self, config):
        form = ctk.CTkFrame(self, fg_color="transparent")
        form.pack(fill="both", expand=True, padx=20, pady=16)

        fields = [
            ("config_name",            config.name if config else ""),
            ("config_compiler_path",   config.compiler_path if config else ""),
            ("config_source_filename", config.source_filename if config else "main.c"),
            ("config_compiler_args",   config.compiler_args if config else ""),
            ("config_run_command",     config.run_command if config else ""),
        ]

        self.entries = {}
        for i, (key, value) in enumerate(fields):
            ctk.CTkLabel(form, text=self.tr(key), anchor="w").grid(
                row=i, column=0, sticky="w", pady=6, padx=(0, 12)
            )
            entry = ctk.CTkEntry(form, width=280)
            entry.insert(0, value)
            entry.grid(row=i, column=1, sticky="ew", pady=6)
            self.entries[key] = entry

        self.interpreted_var = ctk.BooleanVar(
            value=config.is_interpreted if config else False
        )
        ctk.CTkCheckBox(
            form, text=self.tr("config_is_interpreted"),
            variable=self.interpreted_var,
        ).grid(row=len(fields), column=0, columnspan=2, sticky="w", pady=10)

        form.grid_columnconfigure(1, weight=1)

        btn_frame = ctk.CTkFrame(self, fg_color="transparent")
        btn_frame.pack(fill="x", padx=20, pady=(0, 16))

        ctk.CTkButton(
            btn_frame, text=self.tr("config_saved"), command=self._submit
        ).pack(side="right", padx=(8, 0))

        ctk.CTkButton(
            btn_frame, text=self.tr("cancel"), command=self.destroy
        ).pack(side="right")

    def _submit(self):
        name = self.entries["config_name"].get().strip()
        compiler_path = self.entries["config_compiler_path"].get().strip()
        source_filename = self.entries["config_source_filename"].get().strip()
        compiler_args = self.entries["config_compiler_args"].get().strip()
        run_command = self.entries["config_run_command"].get().strip()

        if not name or not compiler_path or not source_filename:
            messagebox.showerror(
                self.tr("edit_config_title"),
                self.tr("err_config_fields"),
                parent=self,
            )
            return

        config = Configuration(
            name=name,
            compiler_path=compiler_path,
            source_filename=source_filename,
            compiler_args=compiler_args,
            run_command=run_command,
            is_interpreted=self.interpreted_var.get(),
        )

        try:
            if self.old_name:
                self.config_repo.update(self.old_name, config)
            else:
                self.config_repo.save(config)
            self.on_save()
            self.destroy()
        except ValueError as exc:
            messagebox.showerror(self.tr("edit_config_title"), str(exc), parent=self)