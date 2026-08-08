import sqlite3

from pathlib import Path


class SQLiteDatabase:
	def __init__(self, path: Path) -> None:
		self._connection = sqlite3.connect(path)
		self._connection.row_factory = sqlite3.Row

	def close(self) -> None:
		self._connection.close()
	