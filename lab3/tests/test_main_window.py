import os
import sys
import tempfile
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from PyQt5.QtWidgets import QApplication

from src.window.main_window import MainWindow
from tests.db_fixture import make_test_db


def get_app():
    app = QApplication.instance()
    if app is None:
        app = QApplication([])
    return app


class TestMainWindow(unittest.TestCase):
    def setUp(self):
        self.app = get_app()
        self.temp_dir = tempfile.TemporaryDirectory()
        self.db_path = os.path.join(self.temp_dir.name, "test.db")
        make_test_db(self.db_path)
        os.environ["DB_PATH"] = self.db_path
        self.window = MainWindow()

    def tearDown(self):
        self.window.db.close()
        self.window.close()
        self.temp_dir.cleanup()
        os.environ.pop("DB_PATH", None)

    def tab_names(self):
        return [self.window.tabs.tabText(i) for i in range(self.window.tabs.count())]

    def test_starts_disconnected(self):
        self.assertFalse(self.window.db.is_connected())
        self.assertFalse(self.window.panel.isEnabled())
        self.assertFalse(self.window.bt_sql.isEnabled())
        self.assertEqual(self.window.status_label.text(), "статус: отключено")
        self.assertEqual(self.window.target_path, self.db_path)

    def test_connect_enables_and_shows_tab1(self):
        self.window.on_connect()
        self.assertTrue(self.window.db.is_connected())
        self.assertTrue(self.window.panel.isEnabled())
        self.assertTrue(self.window.bt_sql.isEnabled())
        self.assertEqual(self.tab_names(), ["Tab1"])
        self.assertEqual(self.window.status_label.text(),
                         "статус: подключено к БД " + self.db_path)

    def test_combo_filled_after_connect(self):
        self.window.on_connect()
        combo = self.window.panel.table_combo
        names = [combo.itemText(i) for i in range(combo.count())]
        self.assertEqual(names, ["courses", "students", "teachers"])
        self.assertEqual(self.window.panel.current_table(), "courses")

    def test_tables_list(self):
        self.window.on_connect()
        self.window.on_tables_list()
        table = self.window.tabs.widget(1)
        model = table.model()
        self.assertEqual(self.tab_names(), ["Tab1", "Tab2"])
        self.assertEqual(model.horizontalHeaderItem(0).text(), "name")
        self.assertEqual(model.horizontalHeaderItem(1).text(), "count(*)")
        self.assertEqual(model.item(1, 0).text(), "students")
        self.assertEqual(model.item(1, 1).text(), "30")

    def test_show_table_uses_selected(self):
        self.window.on_connect()
        self.window.panel.table_combo.setCurrentIndex(1)
        self.assertEqual(self.window.panel.current_table(), "students")
        self.window.on_show_table()
        model = self.window.tabs.widget(1).model()
        self.assertEqual(model.columnCount(), 4)
        self.assertEqual(model.rowCount(), 10)

    def test_stats(self):
        self.window.on_connect()
        self.window.panel.table_combo.setCurrentIndex(1)
        self.window.on_stats()
        model = self.window.tabs.widget(1).model()
        self.assertEqual(model.rowCount(), 4)
        self.assertEqual(model.columnCount(), 4)
        self.assertEqual(model.horizontalHeaderItem(0).text(), "column")
        self.assertEqual(model.item(0, 0).text(), "id")
        self.assertEqual(model.item(0, 2).text(), "30")

    def test_disconnect(self):
        self.window.on_connect()
        self.window.on_tables_list()
        self.window.on_disconnect()
        self.assertFalse(self.window.db.is_connected())
        self.assertFalse(self.window.panel.isEnabled())
        self.assertFalse(self.window.bt_sql.isEnabled())
        self.assertFalse(self.window.bt_disconnect.isEnabled())
        self.assertEqual(self.window.panel.table_combo.count(), 0)
        self.assertEqual(self.tab_names(), ["Tab1"])
        self.assertEqual(self.window.status_label.text(), "статус: отключено")

    def test_disconnect_then_connect_again(self):
        self.window.on_connect()
        self.window.on_disconnect()
        self.window.on_connect()
        self.assertTrue(self.window.db.is_connected())
        self.assertEqual(self.window.panel.table_combo.count(), 3)
        self.assertEqual(self.tab_names(), ["Tab1"])

    def test_tab_numbers_after_close(self):
        self.window.on_connect()
        self.window.on_tables_list()
        self.window.on_tables_list()
        self.window.tabs.close_tab(0)
        self.assertEqual(self.window.next_tab_name(), "Tab4")

    def test_sql_query_adds_tab(self):
        self.window.on_connect()
        self.window.db.execute_query("SELECT 1")
        self.window.add_tab(["x"], [(1,)])
        self.assertEqual(self.tab_names()[-1], "Tab2")


if __name__ == "__main__":
    unittest.main()
