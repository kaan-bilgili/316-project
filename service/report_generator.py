"""Req 9: Generates and exports evaluation reports to text files."""

from datetime import datetime

from service.result_formatter import ResultFormatter


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
        """Export a formatted report with header, result table, and summary."""
        sep = "=" * 72
        thin = "-" * 72
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        lines = [
            sep,
            "  IAE — Evaluation Report",
        ]
        if project_name:
            lines.append(f"  Project  : {project_name}")
        lines += [
            f"  Generated: {timestamp}",
            sep,
            "",
        ]

        col_widths = [16, 22, 0]
        header_line = (
            headers[0].ljust(col_widths[0])
            + headers[1].ljust(col_widths[1])
            + (headers[2] if len(headers) > 2 else "")
        )
        lines += [header_line, thin]

        for entry in entries:
            row = ResultFormatter.to_report_row(entry)
            log_first_line = (row[2] or "").splitlines()[0] if row[2] else ""
            lines.append(
                str(row[0]).ljust(col_widths[0])
                + str(row[1]).ljust(col_widths[1])
                + log_first_line
            )

        lines += [
            thin,
            "",
            ResultFormatter.summary_statistics(entries),
            sep,
        ]

        with open(path, "w", encoding="utf-8") as report_file:
            report_file.write("\n".join(lines))
