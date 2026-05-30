"""Req 8: Compares student program output against the expected output file."""

from ui.models import SubmissionStatus


class OutputComparator:

    def compare(self, actual_output: str, expected_output_path: str) -> dict:
        """Read expected output file and compare with actual output line by line."""
        try:
            with open(expected_output_path, "r", encoding="utf-8") as f:
                expected_output = f.read()
        except FileNotFoundError:
            return {
                "status": SubmissionStatus.ERROR,
                "log_details": f"Expected output file not found: {expected_output_path}",
            }
        except Exception as e:
            return {
                "status": SubmissionStatus.ERROR,
                "log_details": f"Could not read expected output file: {str(e)}",
            }

        actual_lines = (actual_output or "").strip().splitlines()
        expected_lines = expected_output.strip().splitlines()

        if actual_lines == expected_lines:
            return {
                "status": SubmissionStatus.SUCCESS,
                "log_details": "Output matches expected.",
            }

        diff = self._build_diff(actual_lines, expected_lines)
        return {
            "status": SubmissionStatus.WRONG_OUTPUT,
            "log_details": (
                f"Output mismatch "
                f"(expected {len(expected_lines)} line(s), got {len(actual_lines)} line(s)).\n\n"
                + diff
            ),
        }

    @staticmethod
    def _build_diff(actual_lines: list, expected_lines: list) -> str:
        """Return a human-readable list of differing lines."""
        max_lines = max(len(actual_lines), len(expected_lines))
        sections = []
        for i in range(max_lines):
            exp = expected_lines[i] if i < len(expected_lines) else "<missing>"
            act = actual_lines[i] if i < len(actual_lines) else "<missing>"
            if exp != act:
                sections.append(
                    f"Line {i + 1}:\n  Expected: {exp}\n  Actual:   {act}"
                )
        return "\n".join(sections)
