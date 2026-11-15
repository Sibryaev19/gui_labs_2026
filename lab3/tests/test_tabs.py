import os
import sys
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from PyQt5.QtWidgets import QApplication

from src.window.tabs import TabsWidget


def get_app():
    app = QApplication.instance()
    if app is None:
        app = QApplication([])
    return app


class TestTabsWidget(unittest.TestCase):
    def setUp(self):
        self.app = get_app()
        self.tabs = TabsWidget()

    def test_starts_with_one_empty_tab(self):
        self.assertEqual(self.tabs.count(), 1)
        self.assertEqual(self.tabs.tabText(0), "Tab1")

    def test_add_empty_tab(self):
        self.tabs.add_empty_tab()
        self.assertEqual(self.tabs.count(), 2)
        self.assertEqual(self.tabs.tabText(1), "Tab2")

    def test_add_result(self):
        table = self.tabs.add_result("students", ["id", "name"], [(1, "Анна")])
        self.assertEqual(self.tabs.tabText(self.tabs.count() - 1), "students")
        model = table.model()
        self.assertEqual(model.horizontalHeaderItem(0).text(), "id")
        self.assertEqual(model.item(0, 1).text(), "Анна")

    def test_add_result_replaces_old_data(self):
        table = self.tabs.add_result("a", ["x"], [(1,)])
        table.set_result(["y"], [])
        model = table.model()
        self.assertEqual(model.columnCount(), 1)
        self.assertEqual(model.rowCount(), 0)
        self.assertEqual(model.horizontalHeaderItem(0).text(), "y")

    def test_close_tab(self):
        self.tabs.add_empty_tab()
        self.assertEqual(self.tabs.count(), 2)
        self.tabs.close_tab(0)
        self.assertEqual(self.tabs.count(), 1)


if __name__ == "__main__":
    unittest.main()
