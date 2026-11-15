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
ASSETS = os.path.join(BASE_DIR, "assets")
SHAPE_PATH = os.path.join(ASSETS, "shape.png")


class Window(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Лабораторная работа 1")
        self.setWindowFlags(Qt.Window | Qt.FramelessWindowHint)
        self.resize(1200, 800)

        # Серый фон. Без WA_TranslucentBackground — иначе фон не рисуется
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

        self.movie = QMovie(os.path.join(ASSETS, "giphy.gif"))
        self.image_shown = False

        # QImage, а не QPixmap: на X11 pixmap может потерять альфу
        self.shape_img = QImage(SHAPE_PATH)
        if self.shape_img.isNull():
            print(f"[main] НЕ НАЙДЕН: {SHAPE_PATH}")
        else:
            self.shape_img = self.shape_img.convertToFormat(QImage.Format_ARGB32)
            w, h = self.shape_img.width(), self.shape_img.height()
            corner = self.shape_img.pixelColor(0, 0).alpha()
            center = self.shape_img.pixelColor(w // 2, h // 2).alpha()
            print(f"[main] shape.png {w}x{h}, alpha: угол={corner}, центр={center}")
            if corner == 255:
                print("[main] ВНИМАНИЕ: угол непрозрачный — в assets старый PNG "
                      "с белым фоном, замени его на сгенерированный")
        self.shaped = False

        self._drag_pos = None
        self._mask_busy = False

        self.btn1.clicked.connect(self.change_label)
        self.btn2.clicked.connect(self.change_shape)
        self.btn_close.clicked.connect(self.close)

    # ---------- форма окна по PNG ----------

    def build_mask(self):
        # FastTransformation: альфа остаётся 0/255, без полупрозрачных краёв,
        # поэтому createMaskFromColor со строгим сравнением работает точно
        src = self.shape_img.scaled(
            self.size(), Qt.IgnoreAspectRatio, Qt.FastTransformation
        )
        transparent = QColor(0, 0, 0, 0).rgba()
        # MaskInColor: видимыми остаются пиксели, НЕ совпавшие с прозрачным
        return QBitmap.fromImage(src.createMaskFromColor(transparent, Qt.MaskInColor))

    def change_shape(self):
        if self.shaped:
            self.clearMask()          # обычное прямоугольное серое окно
            self.shaped = False
        elif not self.shape_img.isNull():
            self.shaped = True
            self.setMask(self.build_mask())
        print(f"[main] shaped={self.shaped}")

    def resizeEvent(self, event):
        super().resizeEvent(event)
        # setMask сам может вызвать resize — защищаемся от рекурсии
        if self.shaped and not self._mask_busy:
            self._mask_busy = True
            try:
                self.setMask(self.build_mask())
            finally:
                self._mask_busy = False

    # ---------- перетаскивание frameless-окна ----------

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

    # ---------- картинка / гифка ----------

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
