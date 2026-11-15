from PyQt5.QtWidgets import QTabWidget, QPushButton

from src.widgets.result_table import ResultTable


class TabsWidget(QTabWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setTabsClosable(True)
        self.setMovable(True)

        add_button = QPushButton("+")
        add_button.setFlat(True)
        add_button.clicked.connect(self.add_empty_tab)
        self.setCornerWidget(add_button)

        self.tabCloseRequested.connect(self.close_tab)
        self.add_empty_tab()

    def add_empty_tab(self):
        name = "Tab" + str(self.count() + 1)
        self.add_result(name, [], [])

    def add_result(self, name, headers, rows):
        table = ResultTable()
        table.set_result(headers, rows)
        index = self.addTab(table, name)
        self.setCurrentIndex(index)
        return table

    def close_tab(self, index):
        widget = self.widget(index)
        self.removeTab(index)
        widget.deleteLater()
