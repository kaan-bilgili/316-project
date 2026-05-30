import os

import customtkinter as ctk
from tkinter import ttk, messagebox
from ui.dialogs import LogDetailDialog
from ui.models import SubmissionStatus, ReportEntry
from ui.i18n import LANGUAGES, TRANSLATIONS
from ui.fonts import AppFonts, resolve_font_family
from ui.theme import (
    ACCENT_COLOR,
    BG_COLOR,
    BTN_TEXT_COLOR,
    BUTTON_COLOR,
    BUTTON_HOVER,
    CLICK_CURSOR,
    CYBER_GLOW,
    GLASS_BG,
    GLASS_BG_INNER,
    GLASS_BORDER,
    GLASS_BORDER_LIGHT,
    GLASS_RADIUS,
    GLASS_RADIUS_PILL,
    GLASS_RADIUS_SM,
    TEXT_COLOR,
    TEXT_MUTED,
    TREE_HEADING_ACTIVE,
    TREE_HEADING_BG,
    TREE_ROW_FG,
    TREE_ROW_FG_MUTED,
    CUSTOMTKINTER_APPEARANCE,
    mix_hex,
)


class IAECompleteGUI:
    _COMPACT_PAD = 6
    _RESULT_FILTER_KEYS = ("all", "success", "fail", "error")

    def __init__(self, root, lang_code="en"):
        self.root = root
        self.root.geometry("1100x820")
        self.root.minsize(900, 640)
        self.root.configure(fg_color=BG_COLOR)

        family = resolve_font_family(root)
        self.fonts = AppFonts(family)
        self._apply_default_fonts()

        ctk.set_appearance_mode(CUSTOMTKINTER_APPEARANCE)
        self.current_lang = lang_code
        self._buttons = []
        self._ghost_buttons = []
        self._accent_labels = []
        self._muted_labels = []
        self._entries = []
        self._option_menus = []
        self._section_labels = []
        self._i18n_widgets = []
        self._glass_panels = []
        self._zip_path = None
        self._output_path = None
        self._active_project = None
        self._evaluation_running = False
        self._status_message_key = "status_idle"
        self._status_fmt = {}
        self._tree_rows = []
        self._results_filter_key = "all"

        self._build_top_bar()
        self._build_active_project_panel()
        self._build_layout()
        self._apply_language(lang_code)
        self._apply_styles()
        self.set_status_message("status_idle")
        self.set_active_project(None)
        self._update_inputs_paths_summary()
        self.update_evaluation_summary()

    def tr(self, key):
        return TRANSLATIONS[self.current_lang][key]

    def _apply_default_fonts(self):
        default = (self.fonts.family, self.fonts.SIZE_BODY)
        self.root.option_add("*Font", default)
        self.root.option_add("*Label.Font", default)
        self.root.option_add("*Button.Font", default)
        self.root.option_add("*Entry.Font", default)

    def _register(self, widget, key):
        self._i18n_widgets.append((widget, key))

    def _bind_hand_cursor(self, widget):
        def on_enter(_event):
            widget.configure(cursor=CLICK_CURSOR)
            for child in widget.winfo_children():
                try:
                    child.configure(cursor=CLICK_CURSOR)
                except Exception:
                    pass

        def on_leave(_event):
            widget.configure(cursor="")
            for child in widget.winfo_children():
                try:
                    child.configure(cursor="")
                except Exception:
                    pass

        widget.bind("<Enter>", on_enter, add="+")
        widget.bind("<Leave>", on_leave, add="+")
        widget.configure(cursor=CLICK_CURSOR)

    def _create_option_menu(self, parent, **kwargs):
        kwargs.setdefault("font", self.fonts.body)
        menu = ctk.CTkOptionMenu(parent, **kwargs)
        self._bind_hand_cursor(menu)
        return menu

    def _glass_panel(self, parent, inner=False, **kwargs):
        defaults = {
            "fg_color": GLASS_BG_INNER if inner else GLASS_BG,
            "border_width": 1,
            "border_color": GLASS_BORDER,
            "corner_radius": GLASS_RADIUS_SM if inner else GLASS_RADIUS,
        }
        defaults.update(kwargs)
        panel = ctk.CTkFrame(parent, **defaults)
        self._glass_panels.append(panel)
        return panel

    def _pill_menu_style(self):
        return {
            "fg_color": GLASS_BG_INNER,
            "corner_radius": GLASS_RADIUS_PILL,
        }

    def _update_glass_borders(self, accent):
        border = mix_hex(accent, GLASS_BORDER_LIGHT, 0.28)
        for panel in self._glass_panels:
            panel.configure(border_color=border)

    def _build_top_bar(self):
        self.top_bar = self._glass_panel(
            self.root,
            corner_radius=GLASS_RADIUS,
            height=44,
        )
        self.top_bar.pack(fill="x", side="top", padx=20, pady=(14, 0))
        self.top_bar.pack_propagate(False)

        self.lbl_brand = ctk.CTkLabel(
            self.top_bar,
            text="IAE",
            font=self.fonts.title,
            text_color=TEXT_COLOR,
            fg_color="transparent",
        )
        self.lbl_brand.pack(side="left", padx=24)
        self._accent_labels.append(self.lbl_brand)

        nav = ctk.CTkFrame(self.top_bar, fg_color="transparent")
        nav.pack(side="right", padx=16, pady=6)

        self.lbl_language = ctk.CTkLabel(
            nav, font=self.fonts.caption, text_color=TEXT_COLOR, fg_color="transparent"
        )
        self.lbl_language.pack(side="left", padx=(0, 8))
        self._register(self.lbl_language, "language")

        self.ui_lang_var = ctk.StringVar(value=LANGUAGES[self.current_lang])
        self.lang_selector = self._create_option_menu(
            nav,
            variable=self.ui_lang_var,
            values=list(LANGUAGES.values()),
            command=self._on_language_selected,
            width=120,
            height=30,
            button_color=GLASS_BG_INNER,
            button_hover_color=GLASS_BORDER_LIGHT,
            dropdown_fg_color=GLASS_BG,
            dropdown_hover_color=GLASS_BORDER_LIGHT,
            text_color=TEXT_COLOR,
            dropdown_text_color=TEXT_COLOR,
            font=self.fonts.caption,
            **self._pill_menu_style(),
        )
        self.lang_selector.pack(side="left", padx=(0, 14))

        self.btn_help = self._create_ghost_button(
            nav, text="User Manual", width=100, height=30, command=self.show_help
        )
        self.btn_help.pack(side="left", padx=(0, 8))
        self._register(self.btn_help, "user_manual")

        self.btn_about = self._create_ghost_button(
            nav, text="About", width=80, height=30, command=self.show_about
        )
        self.btn_about.pack(side="left")
        self._register(self.btn_about, "about")

    def _build_active_project_panel(self):
        self.active_project_frame = self._glass_panel(
            self.root,
            corner_radius=GLASS_RADIUS_SM,
        )
        self.active_project_frame.pack(fill="x", padx=20, pady=(8, 0))

        content = ctk.CTkFrame(self.active_project_frame, fg_color="transparent")
        content.pack(fill="x", padx=18, pady=10)

        self.lbl_active_title = ctk.CTkLabel(
            content,
            font=self.fonts.section,
            text_color=ACCENT_COLOR,
            fg_color="transparent",
            anchor="w",
        )
        self.lbl_active_title.pack(anchor="w")
        self._register(self.lbl_active_title, "active_project")

        self.lbl_project_name = ctk.CTkLabel(
            content,
            font=self.fonts.body,
            text_color=TEXT_COLOR,
            fg_color="transparent",
            anchor="w",
            justify="left",
        )
        self.lbl_project_name.pack(anchor="w", pady=(4, 0))

        self.lbl_project_meta = ctk.CTkLabel(
            content,
            font=self.fonts.muted,
            text_color=TEXT_MUTED,
            fg_color="transparent",
            anchor="w",
            justify="left",
        )
        self.lbl_project_meta.pack(anchor="w", pady=(2, 0))

    def set_active_project(self, project=None):
        self._active_project = project
        if project is None:
            self.lbl_project_name.configure(
                text=self.tr("active_project_none"),
                text_color=TEXT_MUTED,
            )
            self.lbl_project_meta.configure(text="")
            return

        self.lbl_project_name.configure(
            text=project.name,
            text_color=ACCENT_COLOR,
        )

        description = (project.description or "").strip()
        if description and len(description) > 72:
            description = description[:69] + "..."

        if description:
            meta = self.tr("active_project_meta").format(
                config=project.configuration_name,
                description=description,
            )
        else:
            meta = self.tr("active_project_config_only").format(
                config=project.configuration_name
            )
        self.lbl_project_meta.configure(text=meta)

    def _on_language_selected(self, display_name):
        for code, name in LANGUAGES.items():
            if name == display_name:
                self._apply_language(code)
                break

    def _apply_language(self, lang_code):
        if lang_code not in TRANSLATIONS:
            return
        self.current_lang = lang_code
        self.root.title(self.tr("app_title"))

        for widget, key in self._i18n_widgets:
            widget.configure(text=self.tr(key))

        self.ui_lang_var.set(LANGUAGES[lang_code])

        current_prog = self.prog_lang_var.get()
        self.lang_cb.configure(values=self._prog_lang_values())
        if current_prog in ("C (GCC)", "Java (JDK)", "Python (Interpreter)"):
            self.prog_lang_var.set(current_prog)
        else:
            self.prog_lang_var.set(self.tr("select_prog_lang"))

        self._refresh_path_labels()
        self._update_inputs_paths_summary()

        self.set_status_message(self._status_message_key, **self._status_fmt)

        self.tree.heading("student_id", text=self.tr("col_student_id"))
        self.tree.heading("status", text=self.tr("col_status"))
        self.tree.heading("log_details", text=self.tr("col_logs"))

        self.btn_clear_db.configure(width=150 if lang_code == "tr" else 115)

        self._sync_results_filter_menu()
        self.results_search_entry.configure(
            placeholder_text=self.tr("results_search_placeholder")
        )
        self.update_evaluation_summary()

        self.set_active_project(self._active_project)

    def _result_filter_values(self):
        return [self.tr(f"filter_{key}") for key in self._RESULT_FILTER_KEYS]

    def _result_filter_key_from_display(self, display):
        for key in self._RESULT_FILTER_KEYS:
            if self.tr(f"filter_{key}") == display:
                return key
        return "all"

    def _sync_results_filter_menu(self):
        if not hasattr(self, "results_filter_menu"):
            return
        current = self._results_filter_key
        self.results_filter_menu.configure(values=self._result_filter_values())
        self.results_filter_var.set(self.tr(f"filter_{current}"))

    def _rows_to_entries(self, rows):
        entries = []
        for student_id, status_text, log_details in rows:
            status = SubmissionStatus.ERROR
            for candidate in SubmissionStatus:
                if candidate.value == status_text:
                    status = candidate
                    break
            entries.append(ReportEntry(student_id, status, log_details))
        return entries

    def clear_result_rows(self):
        self._tree_rows.clear()
        self.tree.delete(*self.tree.get_children())
        self.results_search_var.set("")
        self._results_filter_key = "all"
        self.results_filter_var.set(self.tr("filter_all"))
        self.update_evaluation_summary([])

    def add_result_row(self, student_id, status, log_details):
        status_text = status.value if hasattr(status, "value") else str(status)
        self._tree_rows.append((str(student_id), status_text, log_details or ""))
        self._refresh_tree_view()

    def load_result_rows(self, entries):
        self._tree_rows.clear()
        for entry in entries:
            self._tree_rows.append(
                (str(entry.student_id), entry.status.value, entry.log_details or "")
            )
        self._refresh_tree_view()

    def _row_passes_filter(self, row):
        student_id, status_text, _log = row
        key = self._results_filter_key
        if key == "success" and status_text != SubmissionStatus.SUCCESS.value:
            return False
        if key == "fail" and status_text != SubmissionStatus.FAIL.value:
            return False
        if key == "error" and status_text != SubmissionStatus.ERROR.value:
            return False
        query = self.results_search_var.get().strip().lower()
        if query and query not in student_id.lower():
            return False
        return True

    def _refresh_tree_view(self):
        self.tree.delete(*self.tree.get_children())
        visible_rows = []
        for row in self._tree_rows:
            if self._row_passes_filter(row):
                self.tree.insert("", "end", values=row)
                visible_rows.append(row)
        all_entries = self._rows_to_entries(self._tree_rows)
        visible_entries = self._rows_to_entries(visible_rows)
        self.update_evaluation_summary(
            visible_entries,
            total_all=len(all_entries) if all_entries else None,
        )

    def _on_results_search_changed(self, *_args):
        self._refresh_tree_view()

    def _on_results_filter_selected(self, display):
        self._results_filter_key = self._result_filter_key_from_display(display)
        self._refresh_tree_view()

    def update_evaluation_summary(self, entries=None, total_all=None):
        if entries is None:
            visible_rows = [
                row for row in self._tree_rows if self._row_passes_filter(row)
            ]
            entries = self._rows_to_entries(visible_rows)
            if total_all is None:
                total_all = len(self._tree_rows)

        visible_count = len(entries)
        if visible_count == 0 and (total_all or 0) == 0:
            self.summary_lbl.configure(
                text=self.tr("summary_empty"),
                text_color=TEXT_MUTED,
            )
            return

        success = sum(1 for e in entries if e.status == SubmissionStatus.SUCCESS)
        fail = sum(1 for e in entries if e.status == SubmissionStatus.FAIL)
        error = visible_count - success - fail

        stats = self.tr("summary_format").format(
            total=visible_count,
            success=success,
            fail=fail,
            error=error,
        )
        if total_all is not None and visible_count < total_all:
            stats = (
                self.tr("summary_showing").format(
                    visible=visible_count, total=total_all
                )
                + "  |  "
                + stats
            )

        self.summary_lbl.configure(text=stats, text_color=ACCENT_COLOR)

    def _prog_lang_values(self):
        return [
            self.tr("select_prog_lang"),
            "C (GCC)",
            "Java (JDK)",
            "C++ (G++)",
            "Python (Interpreter)",
        ]

    def _build_layout(self):
        pad = self._COMPACT_PAD

        self.main_scroll = ctk.CTkFrame(self.root, fg_color="transparent")
        self.main_scroll.pack(fill="both", expand=True, padx=20, pady=(12, 16))
        self.main_scroll.grid_columnconfigure(0, weight=1)
        self.main_scroll.grid_rowconfigure(2, weight=1)

        self.project_frame = self._glass_panel(self.main_scroll)
        self.project_frame.grid(row=0, column=0, sticky="ew", pady=(0, 10))

        toolbar = ctk.CTkFrame(self.project_frame, fg_color="transparent")
        toolbar.pack(fill="x", padx=18, pady=(14, 0))
        self.project_toolbar = toolbar

        self.btn_create = self._create_button(toolbar, width=115, height=34)
        self.btn_create.pack(side="left", padx=(0, 4))
        self._register(self.btn_create, "new_project")

        self.btn_open = self._create_button(toolbar, width=115, height=34)
        self.btn_open.pack(side="left", padx=4)
        self._register(self.btn_open, "open_project")

        self.btn_manage_configs = self._create_button(toolbar, width=140, height=34)
        self.btn_manage_configs.pack(side="left", padx=4)
        self._register(self.btn_manage_configs, "manage_configs")

        self.status_lbl = ctk.CTkLabel(
            toolbar,
            text_color=TEXT_COLOR,
            font=self.fonts.status,
            fg_color="transparent",
        )
        self.status_lbl.pack(side="left", fill="x", expand=True, padx=12)
        self._accent_labels.append(self.status_lbl)

        self.btn_run = self._create_button(
            toolbar, width=210, height=36, font=self.fonts.button_emphasis
        )
        self.btn_run.pack(side="left", padx=4)
        self._register(self.btn_run, "start_evaluation")

        self.btn_clear_db = self._create_button(toolbar, width=115, height=34)
        self.btn_clear_db.pack(side="right", padx=(4, 0))
        self._register(self.btn_clear_db, "clear_history")

        self.eval_progress_row = ctk.CTkFrame(self.project_frame, fg_color="transparent")
        self.eval_progress_bar = ctk.CTkProgressBar(
            self.eval_progress_row,
            height=10,
            corner_radius=5,
            progress_color=ACCENT_COLOR,
            fg_color=GLASS_BG_INNER,
            border_width=0,
        )
        self.eval_progress_bar.pack(fill="x", padx=18, pady=(8, 14))
        self.eval_progress_bar.set(0)
        self._eval_busy_buttons = (
            self.btn_run,
            self.btn_create,
            self.btn_open,
            self.btn_clear_db,
            self.btn_manage_configs,
        )

        self.config_frame = self._glass_panel(self.main_scroll)
        self.config_frame.grid(row=1, column=0, sticky="ew", pady=(0, 10))
        self.config_frame.grid_columnconfigure(0, weight=1)
        self.config_frame.grid_columnconfigure(1, weight=1)

        settings_col = ctk.CTkFrame(self.config_frame, fg_color="transparent")
        settings_col.grid(row=0, column=0, sticky="nsew", padx=(18, 10), pady=16)
        paths_col = ctk.CTkFrame(self.config_frame, fg_color="transparent")
        paths_col.grid(row=0, column=1, sticky="nsew", padx=(10, 18), pady=16)

        self.settings_frame = settings_col
        self.paths_frame = paths_col

        settings_title = ctk.CTkLabel(
            settings_col, font=self.fonts.section, text_color=TEXT_COLOR, fg_color="transparent"
        )
        settings_title.grid(row=0, column=0, columnspan=3, sticky="w", pady=(0, pad))
        self._section_labels.append(settings_title)
        self._register(settings_title, "config_settings")

        self.lbl_prog_lang = self._label(settings_col, "prog_language", row=1, column=0)
        self.prog_lang_var = ctk.StringVar()
        self.lang_cb = self._create_option_menu(
            settings_col,
            variable=self.prog_lang_var,
            values=[],
            width=220,
            height=30,
            fg_color=GLASS_BG_INNER,
            button_color=GLASS_BG_INNER,
            button_hover_color=GLASS_BORDER,
            dropdown_fg_color=GLASS_BG_INNER,
            dropdown_hover_color=GLASS_BORDER,
            text_color=TEXT_COLOR,
            dropdown_text_color=TEXT_COLOR,
            font=self.fonts.body,
            corner_radius=GLASS_RADIUS_PILL,
        )
        self.lang_cb.grid(row=1, column=1, columnspan=2, padx=8, pady=pad, sticky="ew")
        self._option_menus.append(self.lang_cb)

        self.lbl_compiler = self._label(settings_col, "compiler_path", row=2, column=0)
        self.path_entry = self._create_entry(settings_col, width=280, height=30)
        self.path_entry.grid(row=2, column=1, padx=8, pady=pad, sticky="ew")
        settings_col.grid_columnconfigure(1, weight=1)
        self.btn_browse_path = self._create_button(settings_col, width=80, height=30)
        self.btn_browse_path.grid(row=2, column=2, padx=(4, 0), pady=pad)
        self._register(self.btn_browse_path, "browse")

        self.lbl_timeout = self._label(settings_col, "execution_timeout", row=3, column=0)
        self.timeout_entry = self._create_entry(settings_col, width=60, height=30)
        self.timeout_entry.grid(row=3, column=1, sticky="w", padx=8, pady=(pad, 0))
        self.timeout_entry.insert(0, "5")

        paths_header = ctk.CTkFrame(paths_col, fg_color="transparent")
        paths_header.grid(row=0, column=0, sticky="w", pady=(0, pad))

        paths_title = ctk.CTkLabel(
            paths_header,
            font=self.fonts.section,
            text_color=TEXT_COLOR,
            fg_color="transparent",
        )
        paths_title.pack(anchor="w")
        self._section_labels.append(paths_title)
        self._register(paths_title, "inputs_outputs")

        self.paths_summary = ctk.CTkLabel(
            paths_header,
            font=self.fonts.caption,
            text_color=TEXT_MUTED,
            fg_color="transparent",
            anchor="w",
        )
        self.paths_summary.pack(anchor="w", pady=(2, 0))
        self._muted_labels.append(self.paths_summary)

        self.btn_export = self._create_button(
            paths_col, width=140, height=34, font=self.fonts.button_emphasis
        )
        self.btn_export.grid(row=0, column=1, sticky="e", pady=(0, pad))
        self._register(self.btn_export, "export_report")
        self._eval_busy_buttons = self._eval_busy_buttons + (self.btn_export,)
        paths_col.grid_columnconfigure(1, weight=1)

        self.btn_zip = self._create_button(paths_col, width=195, height=30)
        self.btn_zip.grid(row=1, column=0, padx=(0, 6), pady=pad, sticky="w")
        self._register(self.btn_zip, "select_zip")

        self.lbl_zip = ctk.CTkLabel(
            paths_col, text_color=TEXT_MUTED, fg_color="transparent", font=self.fonts.muted
        )
        self.lbl_zip.grid(row=1, column=1, pady=pad, sticky="w")
        self._muted_labels.append(self.lbl_zip)
        self._register(self.lbl_zip, "no_folder")

        self.btn_output = self._create_button(paths_col, width=195, height=30)
        self.btn_output.grid(row=2, column=0, padx=(0, 6), pady=pad, sticky="w")
        self._register(self.btn_output, "select_output")

        self.lbl_output = ctk.CTkLabel(
            paths_col, text_color=TEXT_MUTED, fg_color="transparent", font=self.fonts.muted
        )
        self.lbl_output.grid(row=2, column=1, pady=pad, sticky="w")
        self._muted_labels.append(self.lbl_output)
        self._register(self.lbl_output, "no_file")

        self.lbl_runtime = self._label(paths_col, "runtime_args", row=3, column=0)
        self.args_entry = self._create_entry(paths_col, width=320, height=30)
        self.args_entry.grid(row=3, column=1, padx=8, pady=(pad, 0), sticky="ew")

        self.table_frame = self._glass_panel(self.main_scroll)
        self.table_frame.grid(row=2, column=0, sticky="nsew")

        log_header = ctk.CTkFrame(self.table_frame, fg_color="transparent")
        log_header.grid(row=0, column=0, sticky="ew", padx=20, pady=(16, 4))
        log_header.grid_columnconfigure(0, weight=1)

        log_title_col = ctk.CTkFrame(log_header, fg_color="transparent")
        log_title_col.grid(row=0, column=0, sticky="w")

        self.log_title = ctk.CTkLabel(
            log_title_col,
            font=self.fonts.section,
            text_color=TEXT_COLOR,
            fg_color="transparent",
        )
        self.log_title.pack(anchor="w")
        self._section_labels.append(self.log_title)
        self._register(self.log_title, "col_logs")

        self.log_hint = ctk.CTkLabel(
            log_title_col,
            font=self.fonts.caption,
            text_color=TEXT_MUTED,
            fg_color="transparent",
        )
        self.log_hint.pack(anchor="w", pady=(2, 0))
        self._register(self.log_hint, "log_detail_hint")

        log_filters = ctk.CTkFrame(log_header, fg_color="transparent")
        log_filters.grid(row=0, column=1, sticky="e", padx=(12, 0))

        self.results_search_var = ctk.StringVar()
        self.results_search_var.trace_add(
            "write", self._on_results_search_changed
        )
        self.results_search_entry = self._create_entry(
            log_filters,
            width=180,
            height=30,
            placeholder_text=self.tr("results_search_placeholder"),
            textvariable=self.results_search_var,
        )
        self.results_search_entry.pack(side="left", padx=(0, 8))

        self.results_filter_var = ctk.StringVar(value=self.tr("filter_all"))
        self.results_filter_menu = self._create_option_menu(
            log_filters,
            variable=self.results_filter_var,
            values=self._result_filter_values(),
            command=self._on_results_filter_selected,
            width=140,
            height=30,
            fg_color=GLASS_BG_INNER,
            button_color=GLASS_BG_INNER,
            button_hover_color=GLASS_BORDER,
            dropdown_fg_color=GLASS_BG,
            dropdown_hover_color=GLASS_BORDER_LIGHT,
            text_color=TEXT_COLOR,
            dropdown_text_color=TEXT_COLOR,
            font=self.fonts.caption,
            corner_radius=GLASS_RADIUS_PILL,
        )
        self.results_filter_menu.pack(side="left")
        self._option_menus.append(self.results_filter_menu)

        self.tree_glass = self._glass_panel(self.table_frame, inner=True)
        self.tree_glass.grid(row=1, column=0, sticky="nsew", padx=18, pady=(0, 6))
        self.table_frame.grid_rowconfigure(1, weight=1)
        self.table_frame.grid_columnconfigure(0, weight=1)

        self.summary_lbl = ctk.CTkLabel(
            self.table_frame,
            text="",
            font=self.fonts.muted,
            text_color=TEXT_MUTED,
            fg_color="transparent",
            anchor="w",
        )
        self.summary_lbl.grid(row=2, column=0, sticky="w", padx=20, pady=(0, 14))
        self._register(self.summary_lbl, "summary_empty")

        self.style = ttk.Style()
        self.style.theme_use("clam")

        columns = ("student_id", "status", "log_details")
        self.tree = ttk.Treeview(
            self.tree_glass,
            columns=columns,
            show="headings",
            style="Glass.Treeview",
        )
        self.tree.column("student_id", width=150, anchor="center")
        self.tree.column("status", width=180, anchor="center")
        self.tree.column("log_details", width=650)
        self.tree.pack(fill="both", expand=True, padx=8, pady=8)
        self._bind_hand_cursor(self.tree)
        self._tree_hover_item = None
        self._setup_tree_interactions()

    def _setup_tree_interactions(self):
        self.tree.bind("<Motion>", self._on_tree_motion)
        self.tree.bind("<Leave>", self._on_tree_leave)
        self.tree.bind("<<TreeviewSelect>>", lambda _e: self._clear_tree_hover())
        self.tree.bind("<Double-Button-1>", self._on_tree_double_click)

    def _on_tree_double_click(self, event):
        item = self.tree.identify_row(event.y)
        if not item:
            return
        values = self.tree.item(item, "values")
        if len(values) < 3:
            return
        self.show_log_detail(values[0], values[1], values[2])

    def show_log_detail(self, student_id, status, log_text):
        LogDetailDialog(self.root, self, student_id, status, log_text)

    def _clear_tree_hover(self):
        for item in self.tree.get_children():
            if item in self.tree.selection():
                continue
            tags = [t for t in self.tree.item(item, "tags") if t != "hover"]
            self.tree.item(item, tags=tuple(tags))

    def _on_tree_motion(self, event):
        item = self.tree.identify_row(event.y)
        if item == self._tree_hover_item:
            return
        self._clear_tree_hover()
        self._tree_hover_item = item
        if item and item not in self.tree.selection():
            self.tree.item(item, tags=("hover",))

    def _on_tree_leave(self, _event):
        self._tree_hover_item = None
        self._clear_tree_hover()

    def set_status_message(self, key, text_color=None, **fmt):
        self._status_message_key = key
        self._status_fmt = fmt
        text = self.tr(key).format(**fmt) if fmt else self.tr(key)
        kwargs = {"text": text}
        if text_color is not None:
            kwargs["text_color"] = text_color
        self.status_lbl.configure(**kwargs)

    def begin_evaluation(self):
        self._evaluation_running = True
        self._set_evaluation_controls_busy(True)
        self.eval_progress_row.pack(fill="x", after=self.project_toolbar)
        self.eval_progress_bar.set(0)

    def end_evaluation(self):
        self._evaluation_running = False
        self._set_evaluation_controls_busy(False)
        self.eval_progress_row.pack_forget()
        self.eval_progress_bar.set(0)

    def set_evaluation_progress(self, fraction, status_text=None):
        if fraction is not None:
            self.eval_progress_bar.set(max(0.0, min(1.0, fraction)))
        if status_text is not None:
            self.status_lbl.configure(text=status_text, text_color="#f1c40f")

    def _set_evaluation_controls_busy(self, busy):
        state = "disabled" if busy else "normal"
        for btn in self._eval_busy_buttons:
            btn.configure(state=state)

    @staticmethod
    def _path_display_name(path):
        if not path:
            return None
        name = os.path.basename(path.rstrip("/\\"))
        return name or path

    def _refresh_path_labels(self):
        if self._zip_path:
            self.lbl_zip.configure(
                text=self._path_display_name(self._zip_path),
                text_color=self.accent_color,
            )
        else:
            self.lbl_zip.configure(
                text=self.tr("no_folder"), text_color=TEXT_MUTED
            )
        if self._output_path:
            self.lbl_output.configure(
                text=self._path_display_name(self._output_path),
                text_color=self.accent_color,
            )
        else:
            self.lbl_output.configure(
                text=self.tr("no_file"), text_color=TEXT_MUTED
            )

    def _update_inputs_paths_summary(self):
        zip_name = self._path_display_name(self._zip_path)
        out_name = self._path_display_name(self._output_path)
        if not zip_name and not out_name:
            self.paths_summary.configure(text=self.tr("inputs_paths_summary_empty"))
        else:
            self.paths_summary.configure(
                text=self.tr("inputs_paths_summary").format(
                    zip=zip_name or "—",
                    output=out_name or "—",
                )
            )

    def set_zip_path(self, path):
        self._zip_path = path
        self._refresh_path_labels()
        self._update_inputs_paths_summary()

    def set_output_path(self, path):
        self._output_path = path
        self._refresh_path_labels()
        self._update_inputs_paths_summary()

    def _label(self, parent, key, row, column):
        lbl = ctk.CTkLabel(
            parent,
            text_color=TEXT_COLOR,
            fg_color="transparent",
            font=self.fonts.body,
        )
        lbl.grid(row=row, column=column, sticky="w", padx=(0, 8), pady=self._COMPACT_PAD)
        self._register(lbl, key)
        return lbl

    def _create_button(self, parent, **kwargs):
        height = kwargs.get("height", 32)
        kwargs.setdefault("cursor", CLICK_CURSOR)
        kwargs.setdefault("font", self.fonts.button)
        kwargs.setdefault("corner_radius", height // 2)
        kwargs.setdefault("text_color", BTN_TEXT_COLOR)
        kwargs.setdefault("border_width", 0)
        btn = ctk.CTkButton(parent, **kwargs)
        self._buttons.append(btn)
        self._bind_hand_cursor(btn)
        return btn

    def _create_ghost_button(self, parent, **kwargs):
        kwargs.setdefault("cursor", CLICK_CURSOR)
        kwargs.setdefault("font", self.fonts.caption)
        kwargs.setdefault("corner_radius", GLASS_RADIUS_PILL)
        kwargs.setdefault("fg_color", GLASS_BG_INNER)
        kwargs.setdefault("text_color", TEXT_COLOR)
        kwargs.setdefault("border_width", 0)
        btn = ctk.CTkButton(parent, **kwargs)
        self._ghost_buttons.append(btn)
        self._bind_hand_cursor(btn)
        return btn

    def _create_entry(self, parent, **kwargs):
        kwargs.setdefault("font", self.fonts.body)
        kwargs.setdefault("corner_radius", GLASS_RADIUS_PILL)
        entry = ctk.CTkEntry(
            parent,
            fg_color=GLASS_BG_INNER,
            border_color=GLASS_BORDER,
            border_width=1,
            text_color=TEXT_COLOR,
            **kwargs,
        )
        self._entries.append(entry)
        return entry

    def _apply_styles(self):
        accent = ACCENT_COLOR
        menu_hover = mix_hex(accent, GLASS_BG_INNER, 0.2)

        for btn in self._buttons:
            btn.configure(
                fg_color=BUTTON_COLOR,
                hover_color=BUTTON_HOVER,
                border_width=0,
            )

        ghost_hover = mix_hex(accent, GLASS_BG_INNER, 0.12)
        for btn in self._ghost_buttons:
            btn.configure(
                hover_color=ghost_hover,
                border_width=0,
            )

        self.lang_selector.configure(
            fg_color=GLASS_BG_INNER,
            button_color=accent,
            button_hover_color=menu_hover,
            dropdown_fg_color=GLASS_BG,
            dropdown_hover_color=menu_hover,
            text_color=TEXT_COLOR,
            dropdown_text_color=TEXT_COLOR,
        )
        for menu in self._option_menus:
            menu.configure(
                fg_color=GLASS_BG_INNER,
                button_color=accent,
                button_hover_color=menu_hover,
                dropdown_fg_color=GLASS_BG,
                dropdown_hover_color=menu_hover,
                text_color=TEXT_COLOR,
                dropdown_text_color=TEXT_COLOR,
            )
        for lbl in self._section_labels + self._accent_labels:
            if lbl is not self.status_lbl:
                lbl.configure(text_color=accent)

        self.status_lbl.configure(text_color=TEXT_COLOR)
        for lbl in self._muted_labels:
            if lbl.cget("text") in (
                self.tr("no_folder"),
                self.tr("no_file"),
            ):
                lbl.configure(text_color=TEXT_MUTED)

        for entry in self._entries:
            entry.configure(
                fg_color=GLASS_BG_INNER,
                border_color=mix_hex(accent, GLASS_BORDER, 0.35),
                text_color=TEXT_COLOR,
            )

        self._configure_treeview(accent)
        self._update_glass_borders(accent)
        self.tree_glass.configure(
            border_color=mix_hex(accent, GLASS_BORDER_LIGHT, 0.32)
        )

    def _configure_treeview(self, accent_color):
        row_hover = mix_hex(accent_color, GLASS_BG_INNER, 0.14)
        self._tree_row_hover = row_hover
        selected_bg = mix_hex(accent_color, CYBER_GLOW, 0.35)

        self.style.configure(
            "Glass.Treeview",
            background=GLASS_BG_INNER,
            foreground=TREE_ROW_FG,
            fieldbackground=GLASS_BG_INNER,
            rowheight=36,
            borderwidth=0,
            relief="flat",
            font=self.fonts.tree_row,
            focuscolor=GLASS_BG_INNER,
            lightcolor=GLASS_BG_INNER,
            darkcolor=GLASS_BG_INNER,
            bordercolor=GLASS_BG_INNER,
        )
        self.style.configure(
            "Glass.Treeview.Heading",
            background=TREE_HEADING_BG,
            foreground=TREE_ROW_FG_MUTED,
            font=self.fonts.tree_heading,
            relief="flat",
            borderwidth=0,
            padding=(8, 10),
            lightcolor=TREE_HEADING_BG,
            darkcolor=TREE_HEADING_BG,
            bordercolor=TREE_HEADING_BG,
        )
        self.style.layout("Glass.Treeview", [("Treeview.treearea", {"sticky": "nswe"})])
        self.style.layout(
            "Glass.Treeview.Heading",
            [("Treeheading.cell", {"sticky": "nswe"})],
        )
        self.style.map(
            "Glass.Treeview",
            background=[
                ("selected", selected_bg),
                ("selected !focus", selected_bg),
                ("!selected", GLASS_BG_INNER),
            ],
            foreground=[
                ("selected", TEXT_COLOR),
                ("!selected", TREE_ROW_FG),
            ],
            focuscolor=[("focus", GLASS_BG_INNER), ("!focus", GLASS_BG_INNER)],
        )
        self.style.map(
            "Glass.Treeview.Heading",
            background=[
                ("active", TREE_HEADING_ACTIVE),
                ("pressed", TREE_HEADING_ACTIVE),
                ("!active", TREE_HEADING_BG),
            ],
            foreground=[
                ("active", accent_color),
                ("!active", TREE_ROW_FG_MUTED),
            ],
            relief=[("active", "flat"), ("pressed", "flat")],
        )
        self.tree.tag_configure("hover", background=row_hover, foreground=TREE_ROW_FG)

    @property
    def accent_color(self):
        return ACCENT_COLOR

    def show_help(self):
        import os

        manual_path = os.path.join(
            os.path.dirname(os.path.abspath(__file__)), "..", "manual.txt"
        )
        manual_path = os.path.normpath(manual_path)

        win = ctk.CTkToplevel(self.root)
        win.title(self.tr("help_title"))
        win.geometry("600x500")
        win.resizable(False, False)
        win.configure(fg_color=BG_COLOR)
        win.transient(self.root)
        win.lift()
        win.focus_force()
        win.grab_set()

        textbox = ctk.CTkTextbox(
            win,
            wrap="word",
            font=self.fonts.body,
            fg_color=GLASS_BG,
            border_color=mix_hex(self.accent_color, GLASS_BORDER, 0.35),
            text_color=TEXT_COLOR,
        )
        textbox.pack(fill="both", expand=True, padx=16, pady=16)

        if os.path.exists(manual_path):
            with open(manual_path, "r", encoding="utf-8") as f:
                textbox.insert("end", f.read())
        else:
            textbox.insert("end", "Manual file not found.")

        textbox.configure(state="disabled")

        ctk.CTkButton(
            win,
            text=self.tr("cancel"),
            command=win.destroy,
            fg_color=BUTTON_COLOR,
            hover_color=BUTTON_HOVER,
            border_width=0,
            text_color=BTN_TEXT_COLOR,
        ).pack(pady=(0, 16))

        win.after(10, win.lift)
        win.after(10, win.focus_force)

    def show_about(self):
        messagebox.showinfo(self.tr("about_title"), self.tr("about_body"))