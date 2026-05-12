from dataclasses import dataclass
from typing import Optional


@dataclass
class StudentResult:
    # User-provided fields
    student_id: str               
    status: str                   
    project_id: Optional[int] = None  
    error_log: str = ""                
    actual_output: str = ""            
    id: Optional[int] = None         

    def to_dict(self) -> dict:
        """Converts the result to a dict for SQLite storage."""
        return {
            "student_id": self.student_id,
            "status": self.status,
            "project_id": self.project_id,
            "error_log": self.error_log,
            "actual_output": self.actual_output,
        }

    @staticmethod
    def from_dict(data: dict) -> "StudentResult":
        """Creates a StudentResult instance from a SQLite row dict."""
        return StudentResult(
            id=data["id"],
            student_id=data["student_id"],
            status=data["status"],
            project_id=data["project_id"],
            error_log=data["error_log"],
            actual_output=data["actual_output"],
        )