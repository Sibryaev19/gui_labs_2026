import os
import sqlite3


def make_test_db(path):
    directory = os.path.dirname(path)
    if directory and not os.path.exists(directory):
        os.makedirs(directory)
    if os.path.exists(path):
        os.remove(path)

    students = []
    for i in range(1, 31):
        name = "Студент {:02d}".format(i)
        group = "ИТ-2" + str((i - 1) % 3 + 1)
        rating = round(2.5 + (i % 10) * 0.25, 2)
        students.append((name, group, rating))
    students[4] = ("Студент 05", None, 4.1)
    students[9] = ("Студент 10", "ИТ-23", None)
    students[14] = ("Студент 15", None, None)

    departments = ["ИиВТ", "ВМ", "ФИО"]
    teachers = []
    for i in range(1, 11):
        teachers.append(("Преподаватель {:02d}".format(i), departments[(i - 1) % 3]))

    courses = []
    for i in range(1, 16):
        courses.append(("Курс {:02d}".format(i), (i - 1) % 10 + 1))

    conn = sqlite3.connect(path)
    cur = conn.cursor()

    cur.executescript("""
CREATE TABLE students (
    id INTEGER PRIMARY KEY,
    name TEXT NOT NULL,
    group_name TEXT,
    rating REAL
);

CREATE TABLE teachers (
    id INTEGER PRIMARY KEY,
    name TEXT NOT NULL,
    department TEXT
);

CREATE TABLE courses (
    id INTEGER PRIMARY KEY,
    title TEXT NOT NULL,
    teacher_id INTEGER REFERENCES teachers(id)
);
""")

    cur.executemany(
        "INSERT INTO students (name, group_name, rating) VALUES (?, ?, ?)", students)
    cur.executemany(
        "INSERT INTO teachers (name, department) VALUES (?, ?)", teachers)
    cur.executemany(
        "INSERT INTO courses (title, teacher_id) VALUES (?, ?)", courses)

    conn.commit()
    conn.close()
