import os
import sys

from PyQt5.QtCore import QUrl
from PyQt5.QtWidgets import QApplication
from PyQt5.QtQml import QQmlApplicationEngine

from src.backend import Interface

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def run():
    app = QApplication(sys.argv)

    interface = Interface(BASE_DIR)
    engine = QQmlApplicationEngine()
    engine.rootContext().setContextProperty("_backend", interface)

    qml_path = os.path.join(BASE_DIR, "src", "qml", "mainWindow.qml")
    engine.load(QUrl.fromLocalFile(qml_path))

    if not engine.rootObjects():
        print("Ошибка: Не удалось загрузить QML файл!")
        sys.exit(-1)

    app.aboutToQuit.connect(interface.save)

    sys.exit(app.exec())
