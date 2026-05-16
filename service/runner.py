# service/runner.py
import subprocess
import os
from model.student_result import StudentResult


class Runner:

    def run(self, student_dir: str, arguments: str, configuration) -> StudentResult:
        student_id = os.path.basename(student_dir)
        command = f"{configuration.run_command} {arguments}".strip()

        try:
            result = subprocess.run(
                command, shell=True, capture_output=True,
                text=True, timeout=10, cwd=student_dir
            )

            if result.returncode == 0:
                return StudentResult(
                    student_id=student_id,
                    status="ran",
                    actual_output=result.stdout.strip(),
                )
            else:
                return StudentResult(
                    student_id=student_id,
                    status="runtime_error",
                    error_log=result.stderr.strip(),
                )

        except subprocess.TimeoutExpired:
            return StudentResult(
                student_id=student_id,
                status="runtime_error",
                error_log="Program execution timed out.",
            )