from PyQt5.QtWidgets import QWidget, QGridLayout, QPushButton, QComboBox, QLabel
from PyQt5.QtCore import pyqtSignal


class QueryPanel(QWidget):
    tablesListRequested = pyqtSignal()
    showTableRequested = pyqtSignal()
    statsRequested = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)
        layout = QGridLayout(self)

        self.bt_tables = QPushButton("Список таблиц")
        self.table_label = QLabel("Таблицы:")
        self.table_combo = QComboBox()
        self.bt_show = QPushButton("Вывод таблицы")
        self.bt_stats = QPushButton("Статистика колонок")

        layout.addWidget(self.bt_tables, 0, 0)
        layout.setRowMinimumHeight(1, 12)
        layout.addWidget(self.table_label, 2, 0)
        layout.addWidget(self.table_combo, 2, 1)
        layout.addWidget(self.bt_show, 3, 0)
        layout.addWidget(self.bt_stats, 3, 1)

        self.bt_tables.clicked.connect(self.tablesListRequested.emit)
        self.bt_show.clicked.connect(self.showTableRequested.emit)
        self.bt_stats.clicked.connect(self.statsRequested.emit)

    def set_tables(self, names):
        self.table_combo.blockSignals(True)
        self.table_combo.clear()
        self.table_combo.addItems(names)
        self.table_combo.blockSignals(False)

    def current_table(self):
        return self.table_combo.currentText()
