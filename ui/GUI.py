import customtkinter as ctk
from tkinter import ttk, messagebox
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

        self._build_top_bar()
        self._build_layout()
        self._apply_language(lang_code)
        self._apply_styles()

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

        if self._zip_path:
            self.lbl_zip.configure(text=self._zip_path)
        else:
            self.lbl_zip.configure(text=self.tr("no_folder"))
        if self._output_path:
            self.lbl_output.configure(text=self._output_path)
        else:
            self.lbl_output.configure(text=self.tr("no_file"))

        idle_statuses = {
            TRANSLATIONS[code]["status_idle"] for code in LANGUAGES
        }
        if self.status_lbl.cget("text") in idle_statuses:
            self.status_lbl.configure(text=self.tr("status_idle"))

        self.tree.heading("student_id", text=self.tr("col_student_id"))
        self.tree.heading("status", text=self.tr("col_status"))
        self.tree.heading("log_details", text=self.tr("col_logs"))

        self.btn_clear_db.configure(width=150 if lang_code == "tr" else 115)

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
        toolbar.pack(fill="x", padx=18, pady=14)

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
        self._register(self.status_lbl, "status_idle")

        self.btn_run = self._create_button(
            toolbar, width=210, height=36, font=self.fonts.button_emphasis
        )
        self.btn_run.pack(side="left", padx=4)
        self._register(self.btn_run, "start_evaluation")

        self.btn_clear_db = self._create_button(toolbar, width=115, height=34)
        self.btn_clear_db.pack(side="right", padx=(4, 0))
        self._register(self.btn_clear_db, "clear_history")

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

        paths_title = ctk.CTkLabel(
            paths_col, font=self.fonts.section, text_color=TEXT_COLOR, fg_color="transparent"
        )
        paths_title.grid(row=0, column=0, sticky="w", pady=(0, pad))
        self._section_labels.append(paths_title)
        self._register(paths_title, "inputs_outputs")

        self.btn_export = self._create_button(
            paths_col, width=140, height=34, font=self.fonts.button_emphasis
        )
        self.btn_export.grid(row=0, column=1, sticky="e", pady=(0, pad))
        self._register(self.btn_export, "export_report")
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

        self.log_title = ctk.CTkLabel(
            self.table_frame,
            font=self.fonts.section,
            text_color=TEXT_COLOR,
            fg_color="transparent",
        )
        self.log_title.grid(row=0, column=0, sticky="w", padx=20, pady=(16, 4))
        self._section_labels.append(self.log_title)
        self._register(self.log_title, "col_logs")

        self.tree_glass = self._glass_panel(self.table_frame, inner=True)
        self.tree_glass.grid(row=1, column=0, sticky="nsew", padx=18, pady=(0, 16))
        self.table_frame.grid_rowconfigure(1, weight=1)
        self.table_frame.grid_columnconfigure(0, weight=1)

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

    def set_zip_path(self, path):
        self._zip_path = path
        self.lbl_zip.configure(text=path, text_color=self.accent_color)

    def set_output_path(self, path):
        self._output_path = path
        self.lbl_output.configure(text=path, text_color=self.accent_color)

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