import customtkinter as ctk
from tkinter import filedialog, messagebox
import os

from data.configuration_repository import ConfigurationRepository
from model.configuration import Configuration
from ui.theme import (
    BG_COLOR,
    BTN_TEXT_COLOR,
    BUTTON_COLOR,
    BUTTON_HOVER,
    GLASS_BG,
    GLASS_BORDER,
    TEXT_COLOR,
    TEXT_MUTED,
)


def _cyber_button(parent, text, command, width=None, fg_override=None, hover_override=None):
    kwargs = {
        "text": text,
        "command": command,
        "fg_color": fg_override or BUTTON_COLOR,
        "hover_color": hover_override or BUTTON_HOVER,
        "border_width": 0,
        "text_color": BTN_TEXT_COLOR,
    }
    if width is not None:
        kwargs["width"] = width
    return ctk.CTkButton(parent, **kwargs)


def _truncate_text(text: str, max_len: int = 44) -> str:
    text = " ".join(str(text).split())
    if len(text) <= max_len:
        return text
    keep = max_len - 1
    front = keep // 2
    back = keep - front
    return f"{text[:front]}…{text[-back:]}"


def _config_summary_text(config: Configuration) -> str:
    compiler = (config.compiler_path or "").strip()
    if compiler and len(compiler) > 28:
        compiler = f"...{os.sep}{os.path.basename(compiler)}"
    return _truncate_text(f"{compiler}  |  {config.source_filename}", max_len=44)


class ConfigManagerDialog(ctk.CTkToplevel):
    _ACTION_BUTTON_WIDTH = 88
    def __init__(self, parent, config_repo: ConfigurationRepository, tr):
        super().__init__(parent)
        self.config_repo = config_repo
        self.tr = tr
        self.title(tr("manage_configs_title"))
        self.geometry("680x420")
        self.resizable(False, False)
        self.configure(fg_color=BG_COLOR)
        self.transient(parent)
        self.grab_set()

        self._build_ui()
        self._refresh_list()

    def _build_ui(self):
        self.listbox = ctk.CTkScrollableFrame(self)
        self.listbox.pack(fill="both", expand=True, padx=16, pady=(16, 8))

        btn_frame = ctk.CTkFrame(self, fg_color="transparent")
        btn_frame.pack(fill="x", padx=16, pady=(0, 16))

        _cyber_button(
            btn_frame, text=self.tr("new_config_title"), command=self._new_config
        ).pack(side="left")

        _cyber_button(
            btn_frame, text=self.tr("import_config"), command=self._import_config
        ).pack(side="left", padx=(8, 0))

        _cyber_button(
            btn_frame, text=self.tr("cancel"), command=self.destroy
        ).pack(side="right")

    def _refresh_list(self):
        for widget in self.listbox.winfo_children():
            widget.destroy()

        configs = self.config_repo.load_all()
        if not configs:
            ctk.CTkLabel(
                self.listbox, text=self.tr("no_configs"), text_color=TEXT_MUTED
            ).pack(pady=20)
            return

        for config in configs:
            row = ctk.CTkFrame(self.listbox, fg_color="transparent")
            row.pack(fill="x", pady=4)
            row.grid_columnconfigure(1, weight=1)

            ctk.CTkLabel(
                row,
                text=config.name,
                anchor="w",
                width=140,
                text_color=TEXT_COLOR,
            ).grid(row=0, column=0, sticky="w", padx=(8, 4))

            ctk.CTkLabel(
                row,
                text=_config_summary_text(config),
                text_color=TEXT_MUTED,
                anchor="w",
            ).grid(row=0, column=1, sticky="ew", padx=4)

            actions = ctk.CTkFrame(row, fg_color="transparent")
            actions.grid(row=0, column=2, sticky="e", padx=(4, 8))

            _cyber_button(
                actions,
                text=self.tr("export_config"),
                width=self._ACTION_BUTTON_WIDTH,
                command=lambda c=config: self._export_config(c),
            ).pack(side="left", padx=(0, 4))

            _cyber_button(
                actions,
                text=self.tr("delete"),
                width=self._ACTION_BUTTON_WIDTH,
                fg_override=("#DC2626", "#B91C1C"),
                hover_override=("#B91C1C", "#991B1B"),
                command=lambda c=config: self._delete_config(c),
            ).pack(side="left", padx=(0, 4))

            _cyber_button(
                actions,
                text=self.tr("edit"),
                width=self._ACTION_BUTTON_WIDTH,
                command=lambda c=config: self._edit_config(c),
            ).pack(side="left")

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

    def _import_config(self):
        path = filedialog.askopenfilename(
            title=self.tr("import_config"),
            filetypes=[("JSON Files", "*.json")]
        )
        if path:
            try:
                self.config_repo.import_from_file(path)
                self._refresh_list()
            except Exception as exc:
                messagebox.showerror(self.tr("import_config"), str(exc), parent=self)

    def _export_config(self, config: Configuration):
        path = filedialog.asksaveasfilename(
            title=self.tr("export_config"),
            defaultextension=".json",
            filetypes=[("JSON Files", "*.json")],
            initialfile=f"{config.name}.json"
        )
        if path:
            try:
                self.config_repo.export_to_file(config.name, path)
            except Exception as exc:
                messagebox.showerror(self.tr("export_config"), str(exc), parent=self)


class ConfigEditDialog(ctk.CTkToplevel):
    def __init__(self, parent, config, config_repo: ConfigurationRepository, tr, on_save):
        super().__init__(parent)
        self.config_repo = config_repo
        self.tr = tr
        self.on_save = on_save
        self.old_name = config.name if config else None
        self.title(tr("edit_config_title") if config else tr("new_config_title"))
        self.geometry("460x400")
        self.resizable(False, False)
        self.configure(fg_color=BG_COLOR)
        self.transient(parent)
        self.grab_set()

        self._build_form(config)
        self.after(10, self.lift)
        self.after(10, self.focus_force)
        self.entries["config_name"].focus()

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
            ctk.CTkLabel(form, text=self.tr(key), anchor="w", text_color=TEXT_COLOR).grid(
                row=i, column=0, sticky="w", pady=6, padx=(0, 12)
            )
            entry = ctk.CTkEntry(
                form,
                width=280,
                fg_color=GLASS_BG,
                border_color=GLASS_BORDER,
                border_width=1,
                text_color=TEXT_COLOR,
            )
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

        _cyber_button(
            btn_frame, text=self.tr("config_saved"), command=self._submit
        ).pack(side="right", padx=(8, 0))

        _cyber_button(
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
        except (ValueError, OSError) as exc:
            messagebox.showerror(self.tr("edit_config_title"), str(exc), parent=self)
