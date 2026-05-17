from ui.models import ReportEntry, SubmissionStatus


class ResultFormatter:

    @staticmethod
    def to_report_row(entry: ReportEntry) -> tuple:
        """Returns a (student_id, status, log) tuple for treeview or TXT export."""
        return (entry.student_id, entry.status.value, entry.log_details)

    @staticmethod
    def summary_statistics(entries: list) -> str:
        """Returns a one-line summary: totals broken down by status."""
        total = len(entries)
        success = sum(1 for e in entries if e.status == SubmissionStatus.SUCCESS)
        fail = sum(1 for e in entries if e.status == SubmissionStatus.FAIL)
        error = sum(1 for e in entries if e.status == SubmissionStatus.ERROR)
        return (
            f"Total: {total} | "
            f"Success: {success} | "
            f"Fail: {fail} | "
            f"Error: {error}"
        )

    @staticmethod
    def format_detail(entry: ReportEntry) -> str:
        """Returns a human-readable detail string for a single entry."""
        return f"[{entry.status.value}] {entry.student_id}\n{entry.log_details}"
