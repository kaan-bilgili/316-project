"""Modern UI font stack with Plus Jakarta Sans and system fallbacks."""

import tkinter as tk
import tkinter.font as tkfont

import customtkinter as ctk

FONT_CANDIDATES = (
    "Plus Jakarta Sans",
    "Plus Jakarta Sans Regular",
    "Plus Jakarta Sans Medium",
    "Plus Jakarta Sans SemiBold",
    "Segoe UI",
    "Helvetica",
    "Helvetica Neue",
    "Arial",
)


def resolve_font_family(root=None):
    """Pick the first available geometric sans-serif family on this system."""
    owns_root = False
    if root is None:
        root = tk.Tk()
        root.withdraw()
        owns_root = True
    try:
        families = {name.lower(): name for name in tkfont.families(root)}
        for candidate in FONT_CANDIDATES:
            if candidate.lower() in families:
                return families[candidate.lower()]
        for key, value in families.items():
            if "plus jakarta" in key:
                return value
    finally:
        if owns_root:
            root.destroy()
    return "Segoe UI"


class AppFonts:
    """Central font definitions for CustomTkinter and ttk widgets."""

    SIZE_TITLE = 15
    SIZE_SECTION = 13
    SIZE_BODY = 12
    SIZE_CAPTION = 11
    SIZE_TREE = 11

    def __init__(self, family: str):
        self.family = family

    def ctk(self, size=None, weight="normal", slant="roman"):
        return ctk.CTkFont(
            family=self.family,
            size=size if size is not None else self.SIZE_BODY,
            weight=weight,
            slant=slant,
        )

    @property
    def title(self):
        return self.ctk(self.SIZE_TITLE, weight="bold")

    @property
    def section(self):
        return self.ctk(self.SIZE_SECTION, weight="bold")

    @property
    def body(self):
        return self.ctk(self.SIZE_BODY)

    @property
    def caption(self):
        return self.ctk(self.SIZE_CAPTION)

    @property
    def button(self):
        return self.ctk(self.SIZE_BODY)

    @property
    def button_emphasis(self):
        return self.ctk(self.SIZE_BODY, weight="bold")

    @property
    def status(self):
        return self.ctk(self.SIZE_BODY, slant="italic")

    @property
    def muted(self):
        return self.ctk(self.SIZE_BODY)

    def ttk(self, size=None, weight="normal"):
        size = size if size is not None else self.SIZE_TREE
        if weight == "bold":
            return (self.family, size, "bold")
        return (self.family, size)

    @property
    def tree_heading(self):
        return self.ttk(self.SIZE_TREE, weight="bold")

    @property
    def tree_row(self):
        return self.ttk(self.SIZE_TREE)
