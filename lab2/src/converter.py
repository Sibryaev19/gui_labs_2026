from PyQt5.QtCore import QObject, pyqtSignal, pyqtSlot

from src import rates


class Converter(QObject):
    ratesChanged = pyqtSignal()

    def __init__(self):
        super().__init__()
        self.rates, self.online, self.date = rates.get_rates()

    def updateRates(self):
        self.rates, self.online, self.date = rates.get_rates()
        self.ratesChanged.emit()

    def toRub(self, cur, value):
        return value * self.rates[cur]

    def fromRub(self, cur, value):
        return value / self.rates[cur]

    @pyqtSlot()
    def onRefresh(self):
        self.updateRates()
