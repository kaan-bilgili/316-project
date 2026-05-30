"""Req 9: Formats evaluation results for display and export."""

from ui.models import ReportEntry, SubmissionStatus


class ResultFormatter:

    @staticmethod
    def to_report_row(entry: ReportEntry) -> tuple:
        """Returns a (student_id, status, log) tuple for treeview or TXT export."""
        return (entry.student_id, entry.status.value, entry.log_details)

    @staticmethod
    def summary_statistics(entries: list) -> str:
        """Returns a one-line summary broken down by status."""
        total = len(entries)
        success = sum(1 for e in entries if e.status == SubmissionStatus.SUCCESS)
        wrong = sum(1 for e in entries if e.status in (
            SubmissionStatus.FAIL, SubmissionStatus.WRONG_OUTPUT
        ))
        error = sum(1 for e in entries if e.status == SubmissionStatus.ERROR)
        return (
            f"Total: {total} | "
            f"Success: {success} | "
            f"Fail: {wrong} | "
            f"Error: {error}"
        )

    @staticmethod
    def format_detail(entry: ReportEntry) -> str:
        """Returns a human-readable detail block for a single entry."""
        separator = "-" * 40
        return (
            f"{separator}\n"
            f"Student : {entry.student_id}\n"
            f"Status  : {entry.status.value}\n"
            f"Details : {entry.log_details or 'No details.'}\n"
            f"{separator}"
        )
