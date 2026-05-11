import tkinter as tk
import database as db
from gui import CyberCafeApp


def main():
    # initialize database first
    db.create_tables()

    # launch GUI
    root = tk.Tk()
    app = CyberCafeApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
