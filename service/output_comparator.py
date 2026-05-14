from service.error_handler import SubmissionStatus


class OutputComparator:

    def compare(self, actual_output: str, expected_output_path: str) -> dict:
        with open(expected_output_path, "r", encoding="utf-8") as f:
            expected_output = f.read()

        if actual_output.strip() == expected_output.strip():
            return {
                "status": SubmissionStatus.SUCCESS,
                "log_details": "Output matches expected.",
            }
        else:
            return {
                "status": SubmissionStatus.WRONG_OUTPUT,
                "log_details": "Output does not match expected.",
            }
