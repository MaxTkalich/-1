import sqlite3
from pathlib import Path


class DatabaseConnection:
    def __init__(self, database_path):
        self.database_path = Path(database_path)

    def exists(self):
        return self.database_path.exists()

    def get_connection(self):
        return sqlite3.connect(self.database_path)

    def get_connection_with_rows(self):
        connection = sqlite3.connect(self.database_path)
        connection.row_factory = sqlite3.Row
        return connection