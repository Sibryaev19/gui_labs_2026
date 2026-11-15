import os

from PyQt5.QtWidgets import (QMainWindow, QFileDialog, QMessageBox, QLabel,
                             QVBoxLayout, QWidget, QHBoxLayout, QPushButton)

from src.db import Database
from src.window.tabs import TabsWidget
from src.widgets.query_panel import QueryPanel
from src.dialogs.query_dialog import QueryDialog


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("ЛР3 — SQL браузер")
        self.resize(1000, 700)

        self.db = Database()
        self.target_path = os.environ.get("DB_PATH", "local_db/test.db")

        self.build_layout()
        self.connect_signals()
        self.update_status()
        self.set_controls_enabled(False)

    def build_layout(self):
        self.bt_choose = QPushButton("Выбрать БД")
        self.bt_connect = QPushButton("Connect")
        self.bt_disconnect = QPushButton("Disconnect")
        self.bt_sql = QPushButton("SQL query")

        top_row = QWidget()
        top_layout = QHBoxLayout(top_row)
        top_layout.setContentsMargins(0, 0, 0, 0)
        top_layout.addStretch()
        top_layout.addWidget(self.bt_choose)
        top_layout.addWidget(self.bt_connect)
        top_layout.addWidget(self.bt_disconnect)
        top_layout.addWidget(self.bt_sql)

        self.status_label = QLabel("статус: отключено")

        self.panel = QueryPanel()
        self.tabs = TabsWidget()

        central = QWidget()
        layout = QVBoxLayout(central)
        layout.addWidget(top_row)
        layout.addWidget(self.status_label)
        layout.addWidget(self.panel)
        layout.addWidget(self.tabs)
        self.setCentralWidget(central)

    def connect_signals(self):
        self.bt_choose.clicked.connect(self.on_choose_db)
        self.bt_connect.clicked.connect(self.on_connect)
        self.bt_disconnect.clicked.connect(self.on_disconnect)
        self.bt_sql.clicked.connect(self.on_sql_dialog)
        self.panel.tablesListRequested.connect(self.on_tables_list)
        self.panel.showTableRequested.connect(self.on_show_table)
        self.panel.statsRequested.connect(self.on_stats)

    def set_controls_enabled(self, enabled):
        self.panel.setEnabled(enabled)
        self.bt_sql.setEnabled(enabled)
        self.bt_disconnect.setEnabled(enabled)

    def update_status(self):
        if self.db.is_connected():
            self.status_label.setText("статус: подключено к БД " + self.db.db_path)
        else:
            self.status_label.setText("статус: отключено")

    def reset_tabs(self):
        while self.tabs.count() > 0:
            self.tabs.close_tab(0)
        self.tabs.add_empty_tab()

    def next_tab_name(self):
        numbers = []
        for i in range(self.tabs.count()):
            text = self.tabs.tabText(i)
            if text.startswith("Tab"):
                try:
                    numbers.append(int(text[3:]))
                except ValueError:
                    pass
        return "Tab" + str(max(numbers or [0]) + 1)

    def add_tab(self, headers, rows):
        return self.tabs.add_result(self.next_tab_name(), headers, rows)

    def on_choose_db(self):
        path, _ = QFileDialog.getOpenFileName(
            self, "Выберите базу данных", "",
            "SQLite databases (*.db *.sqlite *.sqlite3);;All files (*)")
        if not path:
            return
        self.target_path = path
        if not self.db.is_connected():
            self.status_label.setText("статус: отключено")

    def on_connect(self):
        directory = os.path.dirname(self.target_path)
        if directory and not os.path.exists(directory):
            os.makedirs(directory)
        try:
            self.db.connect(self.target_path)
        except Exception as e:
            QMessageBox.critical(self, "Ошибка соединения", str(e))
            return
        self.set_controls_enabled(True)
        self.reset_tabs()
        tables = self.db.list_tables_with_count()
        self.panel.set_tables([name for name, count in tables])
        self.update_status()

    def on_disconnect(self):
        self.db.close()
        self.set_controls_enabled(False)
        self.panel.set_tables([])
        self.reset_tabs()
        self.update_status()

    def run_query(self, sql):
        try:
            return self.db.execute_query(sql)
        except Exception as e:
            QMessageBox.critical(self, "Ошибка запроса", str(e))
            return None

    def on_tables_list(self):
        try:
            rows = self.db.list_tables_with_count()
        except Exception as e:
            QMessageBox.critical(self, "Ошибка запроса", str(e))
            return
        self.add_tab(["name", "count(*)"], rows)

    def on_show_table(self):
        table = self.panel.current_table()
        if not table:
            QMessageBox.information(self, "Нет таблиц",
                                    "В базе нет таблиц.")
            return
        result = self.run_query("SELECT * FROM \"" + table + "\" LIMIT 10")
        if result is not None:
            self.add_tab(result[0], result[1])

    def on_stats(self):
        table = self.panel.current_table()
        if not table:
            QMessageBox.information(self, "Нет таблиц",
                                    "В базе нет таблиц.")
            return
        try:
            rows = self.db.table_stats(table)
        except Exception as e:
            QMessageBox.critical(self, "Ошибка запроса", str(e))
            return
        self.add_tab(["column", "type", "unique", "null"], rows)

    def on_sql_dialog(self):
        dialog = QueryDialog(self)
        if dialog.exec_() != QueryDialog.Accepted:
            return
        sql = dialog.get_query()
        if not sql:
            return
        result = self.run_query(sql)
        if result is not None:
            self.add_tab(result[0], result[1])
