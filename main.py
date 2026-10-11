import math
import sqlite3
from abc import ABC, abstractmethod

FIELD_SIZE = 100


class Calculator:
    def solve(self, s1, s2, s3):
        try:
            a, b, c = float(s1), float(s2), float(s3)
        except ValueError:
            return "", "некорректные входные данные", []

        if not (a > 0 and b > 0 and c > 0
                and a + b > c and a + c > b and b + c > a):
            return "", "не треугольник", []

        x = (b * b + a * a - c * c) / (2 * a)
        y = math.sqrt(b * b - x * x)
        left = min(x, 0.0, a)
        k = (FIELD_SIZE - 1) / max(max(x, 0.0, a) - left, y)

        if a == b == c:
            kind = "равносторонний"
        elif a == b or b == c or a == c:
            kind = "равнобедренный"
        else:
            kind = "разносторонний"

        coords = [
            (round((x - left) * k), round(y * k)),
            (round(-left * k), 0),
            (round((a - left) * k), 0),
        ]
        return kind, "", coords


class Database:
    def __init__(self):
        self.conn = sqlite3.connect(":memory:")
        self.conn.execute(
            "CREATE TABLE IF NOT EXISTS triangles ("
            "s1 TEXT, s2 TEXT, s3 TEXT, kind TEXT, error TEXT, "
            "PRIMARY KEY (s1, s2, s3))"
        )

    def add(self, s1, s2, s3, kind, error):
        self.conn.execute(
            "INSERT OR REPLACE INTO triangles VALUES (?, ?, ?, ?, ?)",
            (s1, s2, s3, kind, error),
        )
        self.conn.commit()

    def get(self, s1, s2, s3):
        return self.conn.execute(
            "SELECT kind, error FROM triangles WHERE s1=? AND s2=? AND s3=?",
            (s1, s2, s3),
        ).fetchone()

    def delete(self, s1, s2, s3):
        cursor = self.conn.execute(
            "DELETE FROM triangles WHERE s1=? AND s2=? AND s3=?",
            (s1, s2, s3),
        )
        self.conn.commit()
        return cursor.rowcount


class UserInterface(ABC):
    @abstractmethod
    def get_sides(self):
        pass


class ConsoleUI(UserInterface):
    def get_sides(self):
        return (
            input("Первая сторона: "),
            input("Вторая сторона: "),
            input("Третья сторона: "),
        )


class Notifier(ABC):
    @abstractmethod
    def send(self, message):
        pass


class ServerNotifier(Notifier):
    def send(self, message):
        print("Отправлено на сервер:", message)


class Controller:
    def __init__(self, calc, db, ui, notifier):
        self.calc = calc
        self.db = db
        self.ui = ui
        self.notifier = notifier

    def run(self):
        s1, s2, s3 = self.ui.get_sides()

        row = self.db.get(s1, s2, s3)
        if row is None:
            kind, error, coords = self.calc.solve(s1, s2, s3)
            self.db.add(s1, s2, s3, kind, error)
        else:
            kind, error = row
            coords = []

        self.notifier.send(error if error else "Тип треугольника: " + kind)
        return kind, error, coords


def main():
    controller = Controller(Calculator(), Database(), ConsoleUI(), ServerNotifier())
    print(controller.run())


if __name__ == "__main__":
    main()
