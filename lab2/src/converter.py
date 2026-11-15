from PyQt5.QtCore import QObject, pyqtSignal, pyqtSlot

from src import rates


class Converter(QObject):
    ratesChanged = pyqtSignal()

    def __init__(self):
        super().__init__()
        self.rates, self.online, self.date = rates.get_rates()
        self.error = rates.last_error

    def updateRates(self):
        fetched, date = rates.fetch_rates()
        if fetched is not None:
            self.rates, self.online, self.date = fetched, True, date
            self.error = ""
        else:
            # неудачная попытка: старый курс сохраняется, показываем причину
            self.online = False
            self.error = rates.last_error
        self.ratesChanged.emit()

    def toRub(self, cur, value):
        return value * self.rates[cur]

    def fromRub(self, cur, value):
        return value / self.rates[cur]

    @pyqtSlot()
    def onRefresh(self):
        self.updateRates()
