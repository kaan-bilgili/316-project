from service.error_handler import SubmissionStatus


class OutputComparator:

    def compare(self, actual_output: str, expected_output_path: str) -> dict:
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

        actual_normalized = (actual_output or "").strip()
        expected_normalized = expected_output.strip()

        if actual_normalized == expected_normalized:
            return {
                "status": SubmissionStatus.SUCCESS,
                "log_details": "Output matches expected.",
            }
        else:
            return {
                "status": SubmissionStatus.WRONG_OUTPUT,
                "log_details": (
                    f"Output mismatch.\n"
                    f"Expected:\n{expected_normalized}\n\n"
                    f"Actual:\n{actual_normalized}"
                ),
            }
