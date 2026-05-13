import subprocess
from enum import Enum

class SubmissionStatus(Enum):
    NOT_PROCESSED = "NOT_PROCESSED"
    SUCCESS = "SUCCESS"
    ERROR = "ERROR"
    COMPILE_ERROR = "COMPILE_ERROR"
    RUNTIME_ERROR = "RUNTIME_ERROR"
    WRONG_OUTPUT = "WRONG_OUTPUT"

class error_handler:
    def __init__(self,timeout_seconds=5):
        self.timeout_seconds = timeout_seconds

    def handle_execution(self, command, is_compile_step=False, expected_file_exists=True):
        if not expected_file_exists:
            return self._format_result(
                status = SubmissionStatus.COMPILE_ERROR,
                log_details="Expected source file was not found after extraction."
            )
        try:
            process = subprocess.run(
                command,
                capture_output=True,
                text=True,
                timeout=self.timeout_seconds,
                check=True
            )
            return self._format_results(
                status=SubmissionStatus.SUCCESS,
                log_details= "Process completed successfully.",
                stdout=process.stdout
            )
        except subprocess.CalledProcessError as e:
            status = SubmissionStatus.COMPILE_ERROR if is_compile_step else SubmissionStatus.RUNTIME_ERROR
            error_output = e.stderr if e.stderr else e.stdout

            return self._format_result(
                status=status,
                log_details=f"Process failed with exit code {e.returncode}.\nDetails: {error_output}"
            )
        except Exception as e:
            return self._format_result(
                status= SubmissionStatus.ERROR,
                log_details=f"Unexpected system error: {str(e)}"
            )
    def _format_result(self, status,log_details,stdout=None):
        return {
            "status": status,
            "log_details": log_details,
            "stdout": stdout
        }
    