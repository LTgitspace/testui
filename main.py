import tkinter as tk
from src.gui import CobotControlGUI


def main():
    root = tk.Tk()
    app = CobotControlGUI(root)
    root.mainloop()


if __name__ == "__main__":
    main()


