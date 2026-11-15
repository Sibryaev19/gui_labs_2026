import os
import sys

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, BASE_DIR)

from src.db_seed import make_test_db


def db_path():
    path = os.environ.get("DB_PATH", "local_db/test.db")
    if not os.path.isabs(path):
        path = os.path.join(BASE_DIR, path)
    return path


def main():
    path = db_path()
    if os.path.exists(path):
        print("База уже есть:", path)
        return
    make_test_db(path)
    print("Создана база с тестовыми данными:", path)


if __name__ == "__main__":
    main()
