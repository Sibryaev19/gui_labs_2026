import os

from PyQt5.QtCore import Qt
from PyQt5.QtGui import QColor, QImage, QBitmap, QMovie, QPalette
from PyQt5.QtWidgets import (
    QHBoxLayout,
    QLabel,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
GIF_PATH = os.path.join(BASE_DIR, os.environ.get("GIF_PATH", os.path.join("assets", "giphy.gif")))
SHAPE_PATH = os.path.join(BASE_DIR, os.environ.get("SHAPE_PATH", os.path.join("assets", "shape.png")))


class Window(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Лабораторная работа 1")
        self.setWindowFlags(Qt.Window | Qt.FramelessWindowHint)
        self.resize(1200, 800)

        self.setAutoFillBackground(True)
        pal = self.palette()
        pal.setColor(QPalette.Window, QColor("lightgray"))
        self.setPalette(pal)

        self.label = QLabel("Это картинка")
        self.label.setAlignment(Qt.AlignCenter)

        self.btn1 = QPushButton("Кнопка1")
        self.btn2 = QPushButton("Кнопка2")
        self.btn_close = QPushButton("Закрыть")

        buttons = QHBoxLayout()
        buttons.addStretch()
        buttons.addWidget(self.btn1)
        buttons.addWidget(self.btn2)
        buttons.addWidget(self.btn_close)
        buttons.addStretch()

        box = QVBoxLayout()
        box.addStretch()
        box.addWidget(self.label)
        box.addStretch()
        box.addLayout(buttons)
        box.addStretch()
        self.setLayout(box)

        self.movie = QMovie(GIF_PATH)
        self.image_shown = False

        self.shape_img = QImage(SHAPE_PATH)
        if not self.shape_img.isNull():
            self.shape_img = self.shape_img.convertToFormat(QImage.Format_ARGB32)
        self.shaped = False

        self._drag_pos = None
        self._mask_busy = False
        self._mask_cache = {}

        self.btn1.clicked.connect(self.change_label)
        self.btn2.clicked.connect(self.change_shape)
        self.btn_close.clicked.connect(self.close)

    def build_mask(self):
        size = (self.width(), self.height())
        cached = self._mask_cache.get(size)
        if cached is not None:
            return cached

        if (self.shape_img.width(), self.shape_img.height()) == size:
            src = self.shape_img
        else:
            src = self.shape_img.scaled(
                self.width(), self.height(),
                Qt.IgnoreAspectRatio, Qt.FastTransformation
            )

        transparent = QColor(0, 0, 0, 0).rgba()
        mask = QBitmap.fromImage(src.createMaskFromColor(transparent, Qt.MaskInColor))

        if len(self._mask_cache) > 8:
            self._mask_cache.clear()
        self._mask_cache[size] = mask
        return mask

    def change_shape(self):
        if self.shaped:
            self.clearMask()
            self.shaped = False
        elif not self.shape_img.isNull():
            self.shaped = True
            self.setMask(self.build_mask())

    def resizeEvent(self, event):
        super().resizeEvent(event)
        if self.shaped and not self._mask_busy:
            self._mask_busy = True
            try:
                self.setMask(self.build_mask())
            finally:
                self._mask_busy = False

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self._drag_pos = event.globalPos() - self.frameGeometry().topLeft()
            event.accept()

    def mouseMoveEvent(self, event):
        if self._drag_pos is not None and event.buttons() & Qt.LeftButton:
            self.move(event.globalPos() - self._drag_pos)
            event.accept()

    def mouseReleaseEvent(self, event):
        self._drag_pos = None
        event.accept()

    def change_label(self):
        if self.image_shown:
            self.movie.stop()
            self.label.setText("you spin me right round...")
            self.image_shown = False
        else:
            self.label.setMovie(self.movie)
            self.movie.start()
            self.image_shown = True

    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Escape:
            self.close()
