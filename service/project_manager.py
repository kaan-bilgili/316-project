from typing import Optional, List
from model.project import Project
from data.database_helper import DatabaseHelper
from data.project_repository import ProjectRepository


class ProjectManager:

    def __init__(self):
        """Initializes the manager with no active project or database."""
        self._current_project: Optional[Project] = None
        self._db: Optional[DatabaseHelper] = None
        self._repo: Optional[ProjectRepository] = None

    def new_project(
        self,
        name: str,
        description: str,
        configuration_name: str,
        submissions_dir: str,
        expected_output_path: str,
        db_path: str
    ) -> Project:
        """Creates a new project and saves it to a new SQLite database file."""
        self._db = DatabaseHelper(db_path)
        self._repo = ProjectRepository(self._db)

        project = Project(
            name=name,
            description=description,
            configuration_name=configuration_name,
            submissions_dir=submissions_dir,
            expected_output_path=expected_output_path,
        )
        project.id = self._repo.save(project)
        self._current_project = project
        return project

    def open_project(self, db_path: str) -> Project:
        """Opens an existing project from a SQLite database file."""
        self._db = DatabaseHelper(db_path)
        self._repo = ProjectRepository(self._db)

        projects = self._repo.load_all()
        if not projects:
            raise FileNotFoundError("No project found in the selected file.")

        self._current_project = projects[0]
        return self._current_project

    def save_project(self) -> None:
        """Saves the current project state to the database."""
        if self._current_project is None:
            raise RuntimeError("No active project to save.")
        self._repo.save(self._current_project)

    def close_project(self) -> None:
        """Closes the current project and database connection."""
        if self._db:
            self._db.close()
        self._current_project = None
        self._db = None
        self._repo = None

    def get_current_project(self) -> Optional[Project]:
        """Returns the currently active project."""
        return self._current_project

    def get_all_projects(self) -> List[Project]:
        """Returns all projects stored in the current database."""
        if self._repo is None:
            return []
        return self._repo.load_all()