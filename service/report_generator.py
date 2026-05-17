class ReportGenerator:
    @staticmethod
    def export_txt(path, rows, headers):
        lines = ["\t".join(headers)] + [
            "\t".join(str(value) for value in row) for row in rows
        ]
        with open(path, "w", encoding="utf-8") as report_file:
            report_file.write("\n".join(lines))
