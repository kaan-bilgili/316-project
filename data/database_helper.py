import sqlite3
import os
from typing import Optional


class DatabaseHelper:

    def __init__(self, db_path: str):
        """Opens a connection to the SQLite database at the given path."""
        self.db_path = db_path
        self.conn = sqlite3.connect(db_path)
        self.conn.row_factory = sqlite3.Row  # allows accessing columns by name
        self._create_tables()

    def _create_tables(self):
        """Creates the required tables if they do not already exist."""
        self.conn.executescript("""
            CREATE TABLE IF NOT EXISTS project (
                id                   INTEGER PRIMARY KEY AUTOINCREMENT,
                name                 TEXT NOT NULL,
                description          TEXT,
                configuration_name   TEXT,
                submissions_dir      TEXT,
                expected_output_path TEXT,
                created_at           TEXT
            );

            CREATE TABLE IF NOT EXISTS student_result (
                id             INTEGER PRIMARY KEY AUTOINCREMENT,
                project_id     INTEGER NOT NULL,
                student_id     TEXT NOT NULL,
                status         TEXT NOT NULL,
                error_log      TEXT,
                actual_output  TEXT,
                FOREIGN KEY (project_id) REFERENCES project(id)
            );
        """)
        self.conn.commit()

    def close(self):
        """Closes the database connection."""
        self.conn.close()