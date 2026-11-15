import base64
import os
import sys
import tempfile

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

from PyQt5.QtCore import QBuffer
from PyQt5.QtGui import QImage, QColor

from src.backend import Interface


def png_data_url(color):
    img = QImage(4, 4, QImage.Format_RGB32)
    img.fill(QColor(color))
    buf = QBuffer()
    buf.open(QBuffer.ReadWrite)
    img.save(buf, "PNG")
    return "data:image/png;base64," + base64.b64encode(bytes(buf.data())).decode()


def make_iface():
    base = tempfile.mkdtemp()
    return Interface(base), base


def test_dirs_created():
    iface, base = make_iface()
    assert os.path.isdir(os.path.join(base, ".paint_checkpoints"))
    assert iface.save_path.endswith("canvas.png")
    assert iface.tmp_path == iface.save_path + ".part"


def test_interval_from_env():
    os.environ["INTERVAL_MS"] = "700"
    iface, _ = make_iface()
    assert iface.timer.interval() == 700
    del os.environ["INTERVAL_MS"]


def test_receive_snapshot_atomic():
    iface, base = make_iface()
    iface.receiveSnapshot(png_data_url("red"))
    assert os.path.exists(iface.save_path)
    assert not os.path.exists(iface.tmp_path)

    img = QImage(iface.save_path)
    assert not img.isNull()
    assert img.pixelColor(0, 0) == QColor("red")


def test_receive_snapshot_replaces_old():
    iface, base = make_iface()
    iface.receiveSnapshot(png_data_url("red"))
    old_mtime = os.path.getmtime(iface.save_path)

    iface.receiveSnapshot(png_data_url("blue"))
    assert os.path.exists(iface.save_path)
    assert not os.path.exists(iface.tmp_path)
    assert os.path.getmtime(iface.save_path) >= old_mtime

    img = QImage(iface.save_path)
    assert img.pixelColor(0, 0) == QColor("blue")


def test_save_without_canvas():
    iface, base = make_iface()
    iface.save()
