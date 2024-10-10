from typing import Union
import sqlite3


class DB:
    def __init__(self, db_path: str):
        self.db_path = db_path
        self.connection = sqlite3.connect(db_path)
        self.cursor = self.connection.cursor()

    def query(self, query: str, params: Union[tuple, list[tuple]] = ()):
        if isinstance(params, list):  # If it's a list of tuples, use executemany
            self.cursor.executemany(query, params)
        else:  # Otherwise, use execute for a single set of parameters
            self.cursor.execute(query, params)
        return self.cursor

    def commit(self) -> None:
        self.connection.commit()

    def close(self) -> None:
        self.connection.close()
