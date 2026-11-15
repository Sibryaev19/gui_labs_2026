import os
import sys

# Форма окна через setMask работает только под X11/XWayland.
# Нативный Wayland молча игнорирует маску, поэтому форсим xcb.
if os.name == "posix":
    os.environ["QT_QPA_PLATFORM"] = "xcb"

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from PyQt5.QtWidgets import QApplication

from src.main import Window


if __name__ == "__main__":
    app = QApplication(sys.argv)
    print(f"[start] platform: {app.platformName()}")

    window = Window()
    window.show()
    sys.exit(app.exec_())
