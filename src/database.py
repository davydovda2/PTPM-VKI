import sqlite3


class DatabaseRepository:

    MAX_NAME_LENGTH = 256
    MAX_MESSAGE_LENGTH = 8096

    def __init__(self, db_path=":memory:"):
        self.db_path = db_path
        self.connection = sqlite3.connect(self.db_path)
        self.connection.row_factory = sqlite3.Row
        self._create_table()

    def _create_table(self):
        cursor = self.connection.cursor()
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS comments (
                id INTEGER PRIMARY KEY,
                name TEXT NOT NULL CHECK (length(name) <= 256),
                message TEXT NOT NULL CHECK (length(message) <= 8096)
            )
            """
        )
        self.connection.commit()

    def _row_to_dict(self, row):
        if row is None:
            return None
        return {
            "id": row["id"],
            "name": row["name"],
            "message": row["message"],
        }

    def _validate_message(self, message):
        if not isinstance(message, str):
            raise TypeError("Сообщение должно быть строкой")
        if not message.strip():
            raise ValueError("Сообщение не может быть пустым")
        if len(message) > self.MAX_MESSAGE_LENGTH:
            raise ValueError(
                "Сообщение длиннее {} символов".format(self.MAX_MESSAGE_LENGTH)
            )

    def get_by_id(self, comment_id):
        cursor = self.connection.cursor()
        cursor.execute(
            "SELECT id, name, message FROM comments WHERE id = ?",
            (comment_id,),
        )
        return self._row_to_dict(cursor.fetchone())

    def get_by_name(self, username):
        cursor = self.connection.cursor()
        cursor.execute(
            "SELECT id, name, message FROM comments WHERE name = ? ORDER BY id",
            (username,),
        )
        return [self._row_to_dict(row) for row in cursor.fetchall()]

    def add(self, comment_id, username, message):
        if not isinstance(comment_id, int) or isinstance(comment_id, bool):
            raise TypeError("ID должен быть целым числом")
        if not isinstance(username, str):
            raise TypeError("Имя пользователя должно быть строкой")
        if not username.strip():
            raise ValueError("Имя пользователя не может быть пустым")
        if len(username) > self.MAX_NAME_LENGTH:
            raise ValueError(
                "Имя пользователя длиннее {} символов".format(
                    self.MAX_NAME_LENGTH
                )
            )
        self._validate_message(message)

        cursor = self.connection.cursor()
        cursor.execute(
            "INSERT INTO comments (id, name, message) VALUES (?, ?, ?)",
            (comment_id, username, message),
        )
        self.connection.commit()
        return True

    def update(self, comment_id, new_message):
        if not isinstance(comment_id, int) or isinstance(comment_id, bool):
            raise TypeError("ID должен быть целым числом")
        self._validate_message(new_message)

        cursor = self.connection.cursor()
        cursor.execute(
            "UPDATE comments SET message = ? WHERE id = ?",
            (new_message, comment_id),
        )
        self.connection.commit()

        if cursor.rowcount == 0:
            raise ValueError("Запись с id={} не найдена".format(comment_id))
        return True

    def delete(self, comment_id):
        cursor = self.connection.cursor()
        cursor.execute("DELETE FROM comments WHERE id = ?", (comment_id,))
        self.connection.commit()
        return cursor.rowcount > 0

    def close(self):
        self.connection.close()
