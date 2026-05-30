"""Req 9: Generates and exports evaluation reports to text files."""

from datetime import datetime

from service.result_formatter import ResultFormatter
from ui.models import SubmissionStatus


class ReportGenerator:

    @staticmethod
    def export_txt(path, rows, headers):
        """Export raw tree-view rows as a tab-separated text file."""
        lines = ["\t".join(headers)] + [
            "\t".join(str(value) for value in row) for row in rows
        ]
        with open(path, "w", encoding="utf-8") as report_file:
            report_file.write("\n".join(lines))

    @staticmethod
    def export_entries_txt(path, entries, headers, project_name=""):
        """Export a formatted report: header, result table, detail logs, summary."""
        sep = "=" * 72
        thin = "-" * 72
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        # --- Header ---
        lines = [sep, "  IAE — Evaluation Report"]
        if project_name:
            lines.append(f"  Project  : {project_name}")
        lines += [f"  Generated: {timestamp}", sep, ""]

        # --- Result table ---
        col_id, col_st = 16, 22
        lines.append(
            headers[0].ljust(col_id)
            + headers[1].ljust(col_st)
            + (headers[2] if len(headers) > 2 else "")
        )
        lines.append(thin)
        for entry in entries:
            row = ResultFormatter.to_report_row(entry)
            first_line = (row[2] or "").splitlines()[0] if row[2] else ""
            lines.append(
                str(row[0]).ljust(col_id)
                + str(row[1]).ljust(col_st)
                + first_line
            )

        # --- Summary ---
        lines += ["", thin, ResultFormatter.summary_statistics(entries), sep, ""]

        # --- Detailed logs for non-successful entries ---
        failed = [e for e in entries if e.status != SubmissionStatus.SUCCESS]
        if failed:
            lines += ["", "DETAILED LOGS", sep]
            for entry in failed:
                lines.append(ResultFormatter.format_detail(entry))
                lines.append("")

        with open(path, "w", encoding="utf-8") as report_file:
            report_file.write("\n".join(lines))
