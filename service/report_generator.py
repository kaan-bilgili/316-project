from service.result_formatter import ResultFormatter


class ReportGenerator:
    @staticmethod
    def export_txt(path, rows, headers):
        lines = ["\t".join(headers)] + [
            "\t".join(str(value) for value in row) for row in rows
        ]
        with open(path, "w", encoding="utf-8") as report_file:
            report_file.write("\n".join(lines))

    @staticmethod
    def export_entries_txt(path, entries, headers):
        rows = [ResultFormatter.to_report_row(e) for e in entries]
        lines = ["\t".join(headers)] + [
            "\t".join(str(v) for v in row) for row in rows
        ]
        lines += ["", ResultFormatter.summary_statistics(entries)]
        with open(path, "w", encoding="utf-8") as report_file:
            report_file.write("\n".join(lines))
