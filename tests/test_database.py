import sqlite3
import unittest

from src.database import DatabaseRepository


class DatabaseRepositoryTestCase(unittest.TestCase):

    def setUp(self):
        self.repo = DatabaseRepository(":memory:")

    def tearDown(self):
        self.repo.close()

    def test_add_saves_record(self):
        result = self.repo.add(1, "student", "Первый комментарий")
        self.assertTrue(result)

        saved = self.repo.get_by_id(1)
        self.assertIsNotNone(saved)
        self.assertEqual(saved["name"], "student")
        self.assertEqual(saved["message"], "Первый комментарий")

    def test_add_duplicate_id_raises_integrity_error(self):
        self.repo.add(1, "student", "Первый комментарий")
        with self.assertRaises(sqlite3.IntegrityError):
            self.repo.add(1, "other_user", "Комментарий с тем же id")

    def test_add_too_long_name_raises_value_error(self):
        with self.assertRaises(ValueError):
            self.repo.add(1, "a" * 257, "Текст сообщения")

    def test_add_too_long_message_raises_value_error(self):
        with self.assertRaises(ValueError):
            self.repo.add(1, "student", "a" * 8097)

    def test_get_by_id_returns_record(self):
        self.repo.add(10, "alex", "Привет, мир")

        comment = self.repo.get_by_id(10)
        self.assertIsNotNone(comment)
        self.assertEqual(comment["id"], 10)
        self.assertEqual(comment["name"], "alex")
        self.assertEqual(comment["message"], "Привет, мир")

    def test_get_by_id_returns_none_for_missing_record(self):
        self.assertIsNone(self.repo.get_by_id(999))

    def test_get_by_name_returns_all_user_comments(self):
        self.repo.add(1, "alex", "Первый")
        self.repo.add(2, "alex", "Второй")
        self.repo.add(3, "maria", "Чужой комментарий")

        comments = self.repo.get_by_name("alex")
        self.assertEqual(len(comments), 2)
        self.assertEqual([comment["id"] for comment in comments], [1, 2])

    def test_get_by_name_returns_empty_list_for_unknown_user(self):
        self.repo.add(1, "alex", "Первый")
        self.assertEqual(self.repo.get_by_name("nobody"), [])

    def test_update_changes_message(self):
        self.repo.add(1, "alex", "Старый текст")

        result = self.repo.update(1, "Новый текст")
        self.assertTrue(result)
        self.assertEqual(self.repo.get_by_id(1)["message"], "Новый текст")

    def test_update_missing_id_raises_value_error(self):
        with self.assertRaises(ValueError):
            self.repo.update(999, "Новый текст")

    def test_update_too_long_message_raises_value_error(self):
        self.repo.add(1, "alex", "Старый текст")
        with self.assertRaises(ValueError):
            self.repo.update(1, "a" * 8097)

    def test_delete_removes_record(self):
        self.repo.add(1, "alex", "Текст")

        self.assertTrue(self.repo.delete(1))
        self.assertIsNone(self.repo.get_by_id(1))

    def test_delete_missing_id_returns_false(self):
        self.assertFalse(self.repo.delete(999))

    def test_delete_leaves_other_records(self):
        self.repo.add(1, "alex", "Первый")
        self.repo.add(2, "alex", "Второй")

        self.repo.delete(1)
        self.assertEqual(len(self.repo.get_by_name("alex")), 1)


if __name__ == "__main__":
    unittest.main()
