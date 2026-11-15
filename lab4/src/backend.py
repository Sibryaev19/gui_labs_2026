import base64
import os

from PyQt5.QtCore import QObject, QTimer, QMetaObject, Qt, pyqtSlot

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


class Interface(QObject):
    def __init__(self, base_dir=BASE_DIR):
        super().__init__()
        self.canvas = None

        save_dir = os.path.join(base_dir, os.environ.get("CHECKPOINT_DIR", ".paint_checkpoints"))
        os.makedirs(save_dir, exist_ok=True)
        self.save_path = os.path.join(save_dir, "canvas.png")
        self.tmp_path = self.save_path + ".part"

        self.timer = QTimer(self)
        self.timer.setInterval(int(os.environ.get("INTERVAL_MS", "5000")))
        self.timer.timeout.connect(self.save)

    def start(self):
        if not self.timer.isActive():
            self.timer.start()

    @pyqtSlot(QObject)
    def registerCanvas(self, canvas):
        self.canvas = canvas
        self.start()

    def save(self):
        if self.canvas is None:
            return
        QMetaObject.invokeMethod(self.canvas, "snapshot", Qt.DirectConnection)

    @pyqtSlot(result=str)
    def loadSnapshot(self):
        if not os.path.exists(self.save_path):
            return ""
        with open(self.save_path, "rb") as f:
            data = base64.b64encode(f.read()).decode()
        return "data:image/png;base64," + data

    @pyqtSlot(str)
    def receiveSnapshot(self, data_url):
        data = base64.b64decode(data_url.split(",", 1)[1])
        for attempt in range(2):
            try:
                with open(self.tmp_path, "wb") as f:
                    f.write(data)
                    f.flush()
                    os.fsync(f.fileno())
                os.replace(self.tmp_path, self.save_path)
                return
            except OSError:
                if attempt == 1:
                    raise
