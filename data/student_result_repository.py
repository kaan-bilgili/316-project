from ui.models import SubmissionStatus, ReportEntry


class StudentResultRepository:
    def __init__(self, db):
        self.db = db

    def load_by_project(self, project_id):
        rows = self.db.conn.execute(
            """
            SELECT student_id, status, error_log, actual_output
            FROM student_result
            WHERE project_id = ?
            ORDER BY student_id
            """,
            (project_id,),
        ).fetchall()

        entries = []
        for row in rows:
            status = self._map_db_status(row["status"])
            log = row["error_log"] or row["actual_output"] or ""
            entries.append(ReportEntry(row["student_id"], status, log))
        return entries

    def save(self, project_id, entry):
        self.db.conn.execute(
            """
            INSERT INTO student_result
                (project_id, student_id, status, error_log, actual_output)
            VALUES (?, ?, ?, ?, ?)
            """,
            (
                project_id,
                entry.student_id,
                entry.status.value,
                entry.log_details,
                "",
            ),
        )
        self.db.conn.commit()

    @staticmethod
    def _map_db_status(status):
        normalized = (status or "").lower()
        if normalized in ("success", "ran", "compiled"):
            return SubmissionStatus.SUCCESS
        if normalized in ("fail", "wrong_output"):
            return SubmissionStatus.FAIL
        return SubmissionStatus.ERROR
