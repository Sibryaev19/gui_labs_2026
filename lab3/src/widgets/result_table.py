from PyQt5.QtWidgets import QTableView
from PyQt5.QtGui import QStandardItemModel, QStandardItem


class ResultTable(QTableView):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.table_model = QStandardItemModel(self)
        self.setModel(self.table_model)

    def set_result(self, headers, rows):
        self.table_model.clear()
        self.table_model.setHorizontalHeaderLabels(headers)
        for row in rows:
            items = []
            for value in row:
                if value is None:
                    value = ""
                items.append(QStandardItem(str(value)))
            self.table_model.appendRow(items)
