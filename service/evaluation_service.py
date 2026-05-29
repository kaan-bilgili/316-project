import os

from service.compiler import Compiler
from service.output_comparator import OutputComparator
from service.runner import Runner
from service.zip_processor import ZipProcessor
from ui.models import SubmissionStatus as ServiceStatus
from ui.models import SubmissionStatus, ReportEntry


class EvaluationService:
    def __init__(self):
        self.compiler = Compiler()
        self.runner = Runner()
        self.output_comparator = OutputComparator()

    def evaluate(
        self,
        zip_folder,
        output_path,
        configuration,
        runtime_args="",
        timeout=5,
    ):
        ZipProcessor(zip_folder).process_zip_files()

        entries = []
        for name in sorted(os.listdir(zip_folder)):
            try:
                student_dir = os.path.join(zip_folder, name)
                if not os.path.isdir(student_dir):
                    continue
                if not name.isdigit():
                    continue

                compile_result = self.compiler.compile(student_dir, configuration)
                if compile_result.status == "compile_error":
                    entries.append(
                        ReportEntry(
                            compile_result.student_id,
                            SubmissionStatus.ERROR,
                            compile_result.error_log,
                        )
                    )
                    continue

                run_result = self.runner.run(
                    student_dir, runtime_args, configuration, timeout=timeout
                )
                if run_result.status == "runtime_error":
                    entries.append(
                        ReportEntry(
                            run_result.student_id,
                            SubmissionStatus.ERROR,
                            run_result.error_log,
                        )   
                    )
                    continue

                compare = self.output_comparator.compare(
                    run_result.actual_output, output_path
                )
                entries.append(
                    ReportEntry(
                        run_result.student_id,
                        self._map_service_status(compare["status"]),
                        compare["log_details"],
                    )
                )
            except Exception as e:

                entries.append(
                    ReportEntry(
                        name,
                        SubmissionStatus.ERROR,
                        f"Unexpected Error: {str(e)}",
                    )
                )
                continue

        return entries

    @staticmethod
    def _map_service_status(status):
        if status == ServiceStatus.SUCCESS:
            return SubmissionStatus.SUCCESS
        if status == ServiceStatus.WRONG_OUTPUT:
            return SubmissionStatus.FAIL
        return SubmissionStatus.ERROR