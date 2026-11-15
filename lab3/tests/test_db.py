import os
import sqlite3
import sys
import tempfile
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.db import Database
from tests.db_fixture import make_test_db


class TestDatabase(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.db_path = os.path.join(self.temp_dir.name, "test.db")
        make_test_db(self.db_path)
        self.db = Database()

    def tearDown(self):
        self.db.close()
        self.temp_dir.cleanup()

    def test_connect(self):
        self.assertFalse(self.db.is_connected())
        self.db.connect(self.db_path)
        self.assertTrue(self.db.is_connected())
        self.assertEqual(self.db.db_path, self.db_path)

    def test_execute_query(self):
        self.db.connect(self.db_path)
        headers, rows = self.db.execute_query("SELECT name FROM sqlite_master")
        self.assertEqual(headers, ["name"])
        names = [row[0] for row in rows]
        self.assertIn("students", names)
        self.assertIn("teachers", names)
        self.assertIn("courses", names)

    def test_execute_query_data(self):
        self.db.connect(self.db_path)
        headers, rows = self.db.execute_query("SELECT * FROM students")
        self.assertEqual(headers, ["id", "name", "group_name", "rating"])
        self.assertEqual(len(rows), 30)

    def test_bad_query_raises(self):
        self.db.connect(self.db_path)
        with self.assertRaises(Exception):
            self.db.execute_query("SELECT * FROM no_such_table")

    def test_close(self):
        self.db.connect(self.db_path)
        self.db.close()
        self.assertFalse(self.db.is_connected())
        self.assertIsNone(self.db.db_path)

    def test_connect_creates_file(self):
        new_path = os.path.join(self.temp_dir.name, "new.db")
        self.assertFalse(os.path.exists(new_path))
        self.db.connect(new_path)
        self.assertTrue(os.path.exists(new_path))

    def test_reconnect_closes_old(self):
        self.db.connect(self.db_path)
        other_path = os.path.join(self.temp_dir.name, "other.db")
        self.db.connect(other_path)
        self.assertEqual(self.db.db_path, other_path)

    def test_list_tables_with_count(self):
        self.db.connect(self.db_path)
        result = self.db.list_tables_with_count()
        self.assertEqual(result, [("courses", 15), ("students", 30), ("teachers", 10)])

    def test_table_columns(self):
        self.db.connect(self.db_path)
        self.assertEqual(self.db.table_columns("students"),
                         ["id", "name", "group_name", "rating"])

    def test_column_types(self):
        self.db.connect(self.db_path)
        types = self.db.column_types("students")
        self.assertEqual(types["id"], "INTEGER")
        self.assertEqual(types["name"], "TEXT")
        self.assertEqual(types["rating"], "REAL")

    def test_table_stats(self):
        self.db.connect(self.db_path)
        stats = self.db.table_stats("students")
        self.assertEqual(len(stats), 4)
        by_name = dict((row[0], row) for row in stats)
        self.assertEqual(by_name["id"], ("id", "INTEGER", 30, 0))
        self.assertEqual(by_name["group_name"][2], 3)
        self.assertEqual(by_name["group_name"][3], 2)
        self.assertEqual(by_name["name"][3], 0)
        self.assertEqual(by_name["rating"], ("rating", "REAL", 11, 2))

    def test_limit(self):
        self.db.connect(self.db_path)
        headers, rows = self.db.execute_query(
            "SELECT * FROM \"students\" LIMIT 10")
        self.assertEqual(len(rows), 10)


if __name__ == "__main__":
    unittest.main()
