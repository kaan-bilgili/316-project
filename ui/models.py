"""UI data models for submission results and report entries."""

from enum import Enum

class SubmissionStatus(Enum):
    SUCCESS = "Success"
    FAIL = "Fail"
    ERROR = "Compile/Runtime Error"

class Result:
    def __init__(self, actual_output, expected_output):
        self.actual_output = actual_output
        self.expected_output = expected_output
        self.is_success = self.compare_outputs(actual_output, expected_output)

    def compare_outputs(self, actual, expected):
        # Req 8: Basit bir karşılaştırma algoritması (boşlukları temizler)
        return actual.strip() == expected.strip()

    def get_diff(self):
        if not self.is_success:
            return f"Expected: {self.expected_output} | Got: {self.actual_output}"
        return "Outputs match."

class ReportEntry:
    def __init__(self, student_id, status: SubmissionStatus, log_details="", result: Result = None):
        self.student_id = student_id
        self.status = status
        self.log_details = log_details
        self.evaluation_result = result