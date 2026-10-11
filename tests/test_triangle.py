import unittest
from unittest.mock import Mock, patch

from main import (
    Calculator,
    ConsoleUI,
    Controller,
    Database,
    Notifier,
    UserInterface,
)


class TestController(unittest.TestCase):
    def setUp(self):
        self.calculator = Calculator()
        self.db = Database()
        self.ui = Mock(spec=UserInterface)
        self.notifier = Mock(spec=Notifier)
        self.controller = Controller(
            self.calculator, self.db, self.ui, self.notifier
        )
        self.addCleanup(self.db.conn.close)

    def test_new_input_is_computed_stored_and_sent(self):
        self.ui.get_sides.return_value = ("7", "8", "9")

        kind, error, coords = self.controller.run()

        self.assertEqual(kind, "разносторонний")
        self.assertEqual(error, "")
        self.assertEqual(self.db.get("7", "8", "9"), ("разносторонний", ""))
        self.notifier.send.assert_called_once_with(
            "Тип треугольника: разносторонний"
        )

    def test_existing_record_is_taken_from_database(self):
        self.db.add("5", "5", "5", "равносторонний", "")
        self.ui.get_sides.return_value = ("5", "5", "5")
        self.controller.calculator = Mock(spec=Calculator)

        kind, error, coords = self.controller.run()

        self.assertEqual(kind, "равносторонний")
        self.assertEqual(error, "")
        self.controller.calculator.solve.assert_not_called()

    def test_error_is_stored_and_sent(self):
        self.ui.get_sides.return_value = ("1", "1", "3")

        kind, error, coords = self.controller.run()

        self.assertEqual(error, "не треугольник")
        self.assertEqual(self.db.get("1", "1", "3"), ("", "не треугольник"))
        self.notifier.send.assert_called_once_with("не треугольник")


class TestUnit(unittest.TestCase):
    def test_database_add_get_delete(self):
        db = Database()
        self.addCleanup(db.conn.close)

        db.add("3", "4", "5", "разносторонний", "")
        self.assertEqual(db.get("3", "4", "5"), ("разносторонний", ""))
        self.assertIsNone(db.get("1", "2", "3"))
        self.assertEqual(db.delete("3", "4", "5"), 1)
        self.assertIsNone(db.get("3", "4", "5"))

    def test_user_interfaces(self):
        with self.assertRaises(TypeError):
            UserInterface()
        with self.assertRaises(TypeError):
            Notifier()

        with patch("builtins.input", side_effect=["3", "4", "5"]):
            self.assertEqual(ConsoleUI().get_sides(), ("3", "4", "5"))


if __name__ == "__main__":
    unittest.main()