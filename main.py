#!/usr/bin/env python3
"""
nextask/main.py
Entry point — initialises Qt app, database, and main window.
"""

import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from PyQt6.QtWidgets import QApplication
from PyQt6.QtGui import QIcon
from PyQt6.QtCore import Qt

from db import Database
from ui import MainWindow


def main():
    os.environ.setdefault("QT_AUTO_SCREEN_SCALE_FACTOR", "1")

    app = QApplication(sys.argv)
    app.setApplicationName("Nextask")
    app.setApplicationDisplayName("Nextask")

    icon_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "assets", "icon.png")
    if os.path.exists(icon_path):
        app.setWindowIcon(QIcon(icon_path))

    db  = Database()
    win = MainWindow(db)
    win.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()