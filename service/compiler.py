import subprocess
import os
from model.student_result import StudentResult


class Compiler:

    def compile(self, student_dir: str, configuration) -> StudentResult:
        """
        Compiles the student's source code using the given configuration.
        Skips compilation for interpreted languages (e.g. Python).
        Expected fields: compiler_path, source_filename, compiler_args, is_interpreted
        """
        student_id = os.path.basename(student_dir)

        # skip compilation for interpreted languages
        if configuration.is_interpreted:
            return StudentResult(student_id=student_id, status="compiled")

        source_file = os.path.join(student_dir, configuration.source_filename)

        if not os.path.exists(source_file):
            return StudentResult(
                student_id=student_id,
                status="compile_error",
                error_log=f"Source file '{configuration.source_filename}' not found.",
            )

        command = f"{configuration.compiler_path} {source_file} {configuration.compiler_args}".strip()

        try:
            result = subprocess.run(
                command, shell=True, capture_output=True,
                text=True, timeout=30, cwd=student_dir
            )

            if result.returncode == 0:
                return StudentResult(student_id=student_id, status="compiled")
            else:
                return StudentResult(
                    student_id=student_id,
                    status="compile_error",
                    error_log=result.stderr.strip(),
                )

        except subprocess.TimeoutExpired:
            return StudentResult(
                student_id=student_id,
                status="compile_error",
                error_log="Compilation timed out.",
            )
        except Exception as e:
            return StudentResult(
                student_id=student_id,
                status="compile_error",
                error_log=f"Compiler Error: {str(e)}",
            )