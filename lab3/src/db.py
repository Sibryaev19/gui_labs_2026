import sqlite3


class Database:
    def __init__(self):
        self.connection = None
        self.db_path = None

    def connect(self, path):
        if self.connection is not None:
            self.close()
        self.connection = sqlite3.connect(path)
        self.db_path = path

    def close(self):
        if self.connection is not None:
            self.connection.close()
            self.connection = None
            self.db_path = None

    def is_connected(self):
        return self.connection is not None

    def execute_query(self, sql):
        cursor = self.connection.cursor()
        cursor.execute(sql)
        headers = [d[0] for d in cursor.description]
        rows = cursor.fetchall()
        cursor.close()
        return headers, rows

    def list_tables_with_count(self):
        cursor = self.connection.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name")
        names = [row[0] for row in cursor.fetchall()]
        result = []
        for name in names:
            cursor.execute("SELECT COUNT(*) FROM \"" + name + "\"")
            count = cursor.fetchone()[0]
            result.append((name, count))
        cursor.close()
        return result

    def table_columns(self, table):
        cursor = self.connection.cursor()
        cursor.execute("PRAGMA table_info(\"" + table + "\")")
        columns = [row[1] for row in cursor.fetchall()]
        cursor.close()
        return columns

    def column_types(self, table):
        cursor = self.connection.cursor()
        cursor.execute("PRAGMA table_info(\"" + table + "\")")
        types = {}
        for row in cursor.fetchall():
            types[row[1]] = row[2]
        cursor.close()
        return types

    def table_stats(self, table):
        types = self.column_types(table)
        columns = self.table_columns(table)
        cursor = self.connection.cursor()
        stats = []
        for column in columns:
            cursor.execute("SELECT COUNT(DISTINCT \"" + column + "\"), "
                           "SUM(\"" + column + "\" IS NULL) FROM \"" + table + "\"")
            unique, nulls = cursor.fetchone()
            stats.append((column, types[column], unique, nulls))
        cursor.close()
        return stats
