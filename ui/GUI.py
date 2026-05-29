import customtkinter as ctk
from tkinter import ttk, messagebox
from ui.models import SubmissionStatus, ReportEntry
from ui.i18n import LANGUAGES, TRANSLATIONS, THEME_NAME_KEYS
from ui.fonts import AppFonts, resolve_font_family

CUSTOMTKINTER_THEME_DARK = "dark"
CUSTOMTKINTER_THEME_COLOR_SINGLE_PANEL = "#1a1625"
TEXT_COLOR = "#ffffff"
TEXT_MUTED = "#9b94ad"
BG_COLOR = "#0b0812"
GLASS_BG = "#1a1625"
GLASS_BG_INNER = "#14111c"
GLASS_BORDER = "#2e283d"
GLASS_BORDER_LIGHT = "#3d3654"
GLASS_RADIUS = 24
GLASS_RADIUS_SM = 16
GLASS_RADIUS_PILL = 20
TREE_HEADING_BG = "#1f1b2e"
TREE_HEADING_ACTIVE = "#2a2438"
CLICK_CURSOR = "hand2"

GRADIENT_PINK = "#D81B60"
GRADIENT_ORANGE = "#FF6D00"


def _mix_hex(color_a, color_b, ratio=0.5):
    a = color_a.lstrip("#")
    b = color_b.lstrip("#")
    rgb_a = tuple(int(a[i : i + 2], 16) for i in (0, 2, 4))
    rgb_b = tuple(int(b[i : i + 2], 16) for i in (0, 2, 4))
    mixed = tuple(int(rgb_a[i] * (1 - ratio) + rgb_b[i] * ratio) for i in range(3))
    return "#{:02x}{:02x}{:02x}".format(*mixed)


GRADIENT_MIX = _mix_hex(GRADIENT_PINK, GRADIENT_ORANGE, 0.5)
GRADIENT_MIX_HOVER = _mix_hex("#B8154F", "#E55D00", 0.5)


def _solid_accent(color):
    if isinstance(color, (tuple, list)):
        return color[0]
    return color


COLOR_THEMES = {
    "gold": {
        "button": (GRADIENT_PINK, GRADIENT_MIX),
        "button_hover": ("#B8154F", GRADIENT_MIX_HOVER),
        "accent": GRADIENT_MIX,
    },
    "green": {
        "button": "#2ecc71",
        "button_hover": "#27ae60",
        "accent": "#2ecc71",
    },
    "blue": {
        "button": "#3498db",
        "button_hover": "#2980b9",
        "accent": "#3498db",
    },
}


class IAECompleteGUI:
    _COMPACT_PAD = 6

    def __init__(self, root, theme_key="blue", lang_code="en"):
        self.root = root
        self.root.geometry("1100x820")
        self.root.minsize(900, 640)
        self.root.configure(fg_color=BG_COLOR)

        family = resolve_font_family(root)
        self.fonts = AppFonts(family)
        self._apply_default_fonts()

        ctk.set_appearance_mode(CUSTOMTKINTER_THEME_DARK)
        self.current_theme = theme_key
        self.current_lang = lang_code
        self._buttons = []
        self._accent_labels = []
        self._muted_labels = []
        self._entries = []
        self._option_menus = []
        self._topbar_menus = []
        self._section_labels = []
        self._i18n_widgets = []
        self._glass_panels = []
        self._zip_path = None
        self._output_path = None

        self._build_top_bar()
        self._build_layout()
        self._apply_language(lang_code)
        self._apply_theme(theme_key)

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

    def _theme_name(self, theme_key):
        return self.tr(THEME_NAME_KEYS[theme_key])

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
        border = _mix_hex(accent, GLASS_BORDER_LIGHT, 0.22)
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

        ctk.CTkLabel(
            self.top_bar,
            text="IAE",
            font=self.fonts.title,
            text_color=TEXT_COLOR,
            fg_color="transparent",
        ).pack(side="left", padx=24)

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
        self._topbar_menus.append(self.lang_selector)

        self.lbl_theme = ctk.CTkLabel(
            nav, font=self.fonts.caption, text_color=TEXT_COLOR, fg_color="transparent"
        )
        self.lbl_theme.pack(side="left", padx=(0, 8))
        self._register(self.lbl_theme, "theme")

        self.theme_var = ctk.StringVar()
        self.theme_selector = self._create_option_menu(
            nav,
            variable=self.theme_var,
            values=[],
            command=self._on_theme_selected,
            width=190,
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
        self.theme_selector.pack(side="left", padx=(0, 14))
        self._topbar_menus.append(self.theme_selector)

        self.btn_help = ctk.CTkButton(
            nav,
            text="User Manual",
            width=100,
            height=30,
            fg_color=GLASS_BG_INNER,
            hover_color=GLASS_BORDER_LIGHT,
            text_color=TEXT_COLOR,
            font=self.fonts.caption,
            corner_radius=GLASS_RADIUS_PILL,
            command=self.show_help,
        )
        self.btn_help.pack(side="left", padx=(0, 8))
        self._register(self.btn_help, "user_manual")

        self.btn_about = ctk.CTkButton(
            nav,
            text="About",
            width=80,
            height=30,
            fg_color=GLASS_BG_INNER,
            hover_color=GLASS_BORDER_LIGHT,
            text_color=TEXT_COLOR,
            font=self.fonts.caption,
            corner_radius=GLASS_RADIUS_PILL,
            command=self.show_about,
        )
        self.btn_about.pack(side="left")
        self._register(self.btn_about, "about")

    def _style_topbar_menus(self, button_color, hover_color):
        for menu in self._topbar_menus:
            menu.configure(
                fg_color=GLASS_BG_INNER,
                button_color=button_color,
                button_hover_color=hover_color,
                dropdown_fg_color=GLASS_BG,
                dropdown_hover_color=hover_color,
            )

    def _on_language_selected(self, display_name):
        for code, name in LANGUAGES.items():
            if name == display_name:
                self._apply_language(code)
                break

    def _on_theme_selected(self, theme_name):
        for key in COLOR_THEMES:
            if self._theme_name(key) == theme_name:
                self._apply_theme(key)
                break

    def _apply_language(self, lang_code):
        if lang_code not in TRANSLATIONS:
            return
        self.current_lang = lang_code
        self.root.title(self.tr("app_title"))

        for widget, key in self._i18n_widgets:
            widget.configure(text=self.tr(key))

        self.ui_lang_var.set(LANGUAGES[lang_code])
        self.theme_selector.configure(values=[self._theme_name(k) for k in COLOR_THEMES])
        self.theme_var.set(self._theme_name(self.current_theme))

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

        self.btn_export = self._create_button(
            toolbar, width=140, height=36, font=self.fonts.button_emphasis
        )
        self.btn_export.pack(side="left", padx=4)
        self._register(self.btn_export, "export_report")

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
        paths_title.grid(row=0, column=0, columnspan=2, sticky="w", pady=(0, pad))
        self._section_labels.append(paths_title)
        self._register(paths_title, "inputs_outputs")

        self.btn_zip = self._create_button(paths_col, width=195, height=30)
        self.btn_zip.grid(row=1, column=0, padx=(0, 6), pady=pad, sticky="w")
        self._register(self.btn_zip, "select_zip")

        self.lbl_zip = ctk.CTkLabel(
            paths_col, text_color=TEXT_MUTED, fg_color="transparent", font=self.fonts.muted
        )
        self.lbl_zip.grid(row=1, column=1, pady=pad, sticky="w")
        self._muted_labels.append(self.lbl_zip)
        self._register(self.lbl_zip, "no_folder")
        paths_col.grid_columnconfigure(1, weight=1)

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
        btn = ctk.CTkButton(
            parent,
            text_color=TEXT_COLOR,
            **kwargs,
        )
        self._buttons.append(btn)
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

    def _apply_theme(self, theme_key):
        if theme_key not in COLOR_THEMES:
            return
        self.current_theme = theme_key
        spec = COLOR_THEMES[theme_key]
        button_color = spec["button"]
        hover_color = spec["button_hover"]
        accent = spec.get("accent", _solid_accent(button_color))

        for btn in self._buttons:
            btn.configure(fg_color=button_color, hover_color=hover_color)

        menu_btn_color = accent if isinstance(button_color, (tuple, list)) else button_color
        menu_hover = (
            hover_color[1] if isinstance(hover_color, (tuple, list)) else hover_color
        )
        if theme_key == "gold":
            menu_hover = GRADIENT_MIX_HOVER
        self._style_topbar_menus(button_color, hover_color)
        for menu in self._option_menus:
            menu.configure(
                fg_color=GLASS_BG_INNER,
                button_color=menu_btn_color,
                button_hover_color=menu_hover,
                dropdown_fg_color=GLASS_BG,
                dropdown_hover_color=menu_hover,
            )
        for lbl in self._section_labels + self._accent_labels:
            if lbl is not self.status_lbl:
                lbl.configure(text_color=accent)

        self._configure_treeview(accent)
        self._update_glass_borders(accent)
        self.tree_glass.configure(
            border_color=_mix_hex(accent, GLASS_BORDER_LIGHT, 0.18)
        )
        self.theme_var.set(self._theme_name(theme_key))

    def _configure_treeview(self, accent_color):
        row_hover = _mix_hex(accent_color, GLASS_BG_INNER, 0.18)
        self._tree_row_hover = row_hover

        self.style.configure(
            "Glass.Treeview",
            background=GLASS_BG_INNER,
            foreground="#ebe8f2",
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
            foreground="#a39eb5",
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
                ("selected", accent_color),
                ("selected !focus", accent_color),
                ("!selected", GLASS_BG_INNER),
            ],
            foreground=[
                ("selected", TEXT_COLOR),
                ("!selected", "#ebe8f2"),
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
                ("active", "#e2e4ec"),
                ("!active", "#b8bcc8"),
            ],
            relief=[("active", "flat"), ("pressed", "flat")],
        )
        self.tree.tag_configure("hover", background=row_hover, foreground="#ececf2")

    @property
    def accent_color(self):
        spec = COLOR_THEMES[self.current_theme]
        return spec.get("accent", _solid_accent(spec["button"]))

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

        textbox = ctk.CTkTextbox(win, wrap="word", font=self.fonts.body)
        textbox.pack(fill="both", expand=True, padx=16, pady=16)

        if os.path.exists(manual_path):
            with open(manual_path, "r", encoding="utf-8") as f:
                textbox.insert("end", f.read())
        else:
            textbox.insert("end", "Manual file not found.")

        textbox.configure(state="disabled")

        ctk.CTkButton(win, text=self.tr("cancel"), command=win.destroy).pack(pady=(0, 16))

    def show_about(self):
        messagebox.showinfo(self.tr("about_title"), self.tr("about_body"))