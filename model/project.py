from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional, List


@dataclass
class Project:
    # Kullanıcının girdiği bilgiler
    name: str
    description: str
    configuration_name: str       # Evren'in Configuration'ından gelecekkk
    submissions_dir: str          # ZIP'lerin bulunduğu klasör yolu
    expected_output_path: str     # Beklenen çıktı dosyasının yolu

    # Otomatik oluşturulanlar
    created_at: str = field(
        default_factory=lambda: datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    )
    results: List = field(default_factory=list)  # StudentResult listesi (Nur ekleyeceeek)
    id: Optional[int] = None      # SQLite'tan gelecek

    def to_dict(self) -> dict:
        """SQLite'a kaydetmek için dict'e çevirir."""
        return {
            "name": self.name,
            "description": self.description,
            "configuration_name": self.configuration_name,
            "submissions_dir": self.submissions_dir,
            "expected_output_path": self.expected_output_path,
            "created_at": self.created_at,
        }

    @staticmethod
    def from_dict(data: dict) -> "Project":
        """Creates a Project instance from a SQLite row dict."""
        return Project(
            id=data["id"],
            name=data["name"],
            description=data["description"],
            configuration_name=data["configuration_name"],
            submissions_dir=data["submissions_dir"],
            expected_output_path=data["expected_output_path"],
            created_at=data["created_at"],
        )