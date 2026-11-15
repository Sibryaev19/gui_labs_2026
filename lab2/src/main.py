from PyQt5.QtCore import pyqtSlot
from PyQt5.QtWidgets import QDoubleSpinBox, QFormLayout, QLabel, QMainWindow, QPushButton, QVBoxLayout, QWidget

from src.converter import Converter


class Window(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Конвертер валют")
        self.resize(1200, 800)

        self.converter = Converter()
        self.converter.ratesChanged.connect(self.onRatesChanged)

        self.usd = QDoubleSpinBox()
        self.usd.setDecimals(2)
        self.usd.setRange(0.0, 1000000000.0)
        self.eur = QDoubleSpinBox()
        self.eur.setDecimals(2)
        self.eur.setRange(0.0, 1000000000.0)
        self.rub = QDoubleSpinBox()
        self.rub.setDecimals(2)
        self.rub.setRange(0.0, 1000000000.0)

        self.usd.valueChanged.connect(self.onUsdChanged)
        self.eur.valueChanged.connect(self.onEurChanged)
        self.rub.valueChanged.connect(self.onRubChanged)

        self.status = QLabel()
        self.refreshBtn = QPushButton("Обновить курсы")
        self.refreshBtn.clicked.connect(self.converter.onRefresh)

        form = QFormLayout()
        form.addRow("Доллар, $", self.usd)
        form.addRow("Евро, €", self.eur)
        form.addRow("Рубль, ₽", self.rub)

        layout = QVBoxLayout()
        layout.addLayout(form)
        layout.addWidget(self.refreshBtn)
        layout.addWidget(self.status)

        central = QWidget()
        central.setLayout(layout)
        self.setCentralWidget(central)

        self.onRatesChanged()
        self.usd.setValue(1.0)

    @pyqtSlot()
    def onRatesChanged(self):
        usd = self.converter.rates["USD"]
        eur = self.converter.rates["EUR"]
        size = self.status.font().pointSize() + 1
        if self.converter.online:
            head = "<b>Рыночный курс forex на</b> <i>%s</i>" % self.converter.date
        else:
            head = "<b>Нет сети, курсы из .env</b>"
        self.status.setText('<span style="font-size:%dpt">%s<br>1.00 $ = %.2f ₽<br>1.00 € = %.2f ₽</span>'
                            % (size, head, usd, eur))

    def updateFields(self, source):
        box = getattr(self, source.lower())
        if source == "RUB":
            rub = box.value()
        else:
            rub = self.converter.toRub(source, box.value())
        pairs = [("usd", self.converter.fromRub("USD", rub)),
                 ("eur", self.converter.fromRub("EUR", rub)),
                 ("rub", rub)]
        for name, value in pairs:
            box = getattr(self, name)
            if name == source.lower():
                continue
            box.blockSignals(True)
            box.setValue(value)
            box.blockSignals(False)

    @pyqtSlot(float)
    def onUsdChanged(self, value):
        self.updateFields("USD")

    @pyqtSlot(float)
    def onEurChanged(self, value):
        self.updateFields("EUR")

    @pyqtSlot(float)
    def onRubChanged(self, value):
        self.updateFields("RUB")
