# service/runner.py
import subprocess
import os
from model.student_result import StudentResult


class Runner:

    def run(self, student_dir: str, arguments: str, configuration, timeout: int = 10) -> StudentResult:
        student_id = os.path.basename(student_dir)

        # Interpreted dillerde source dosyasını full path ile belirt
        run_command = configuration.run_command
        if configuration.is_interpreted and configuration.source_filename:
            source_full = os.path.join(student_dir, configuration.source_filename)
            # run_command içindeki source_filename'i full path ile değiştir
            run_command = run_command.replace(
                configuration.source_filename, f'"{source_full}"'
            )

        command = f"{run_command} {arguments}".strip()

        try:
            result = subprocess.run(
                command, shell=True, capture_output=True,
                text=True, timeout=timeout, cwd=student_dir
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
        except Exception as e:
            return StudentResult(
                student_id=student_id,
                status="runtime_error",
                error_log=f"Runtime Error: {str(e)}",
            )