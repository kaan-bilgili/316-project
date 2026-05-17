import customtkinter as ctk

from ui.controller import IAELogicController


def main():
    root = ctk.CTk()
    IAELogicController(root)
    root.mainloop()


if __name__ == "__main__":
    main()
