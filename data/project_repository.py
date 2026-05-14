import sqlite3
from typing import Optional, List
from data.database_helper import DatabaseHelper
from model.project import Project


class ProjectRepository:

    def __init__(self, db: DatabaseHelper):
        """Initializes the repository with a DatabaseHelper instance."""
        self.db = db

    def save(self, project: Project) -> int:
        """Inserts a new project into the database and returns its id."""
        cursor = self.db.conn.execute(
            """
            INSERT INTO project 
                (name, description, configuration_name, submissions_dir, expected_output_path, created_at)
            VALUES 
                (:name, :description, :configuration_name, :submissions_dir, :expected_output_path, :created_at)
            """,
            project.to_dict()
        )
        self.db.conn.commit()
        return cursor.lastrowid

    def load(self, project_id: int) -> Optional[Project]:
        """Loads a single project by id. Returns None if not found."""
        row = self.db.conn.execute(
            "SELECT * FROM project WHERE id = ?", (project_id,)
        ).fetchone()

        if row is None:
            return None
        return Project.from_dict(dict(row))

    def load_all(self) -> List[Project]:
        """Loads all projects from the database."""
        rows = self.db.conn.execute(
            "SELECT * FROM project ORDER BY created_at DESC"
        ).fetchall()
        return [Project.from_dict(dict(row)) for row in rows]

    def delete(self, project_id: int) -> None:
        """Deletes a project and its associated results from the database."""
        self.db.conn.execute(
            "DELETE FROM student_result WHERE project_id = ?", (project_id,)
        )
        self.db.conn.execute(
            "DELETE FROM project WHERE id = ?", (project_id,)
        )
        self.db.conn.commit()