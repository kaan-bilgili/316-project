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

    @staticmethod
    def _student_directories(zip_folder):
        return sorted(
            name
            for name in os.listdir(zip_folder)
            if name.isdigit()
            and os.path.isdir(os.path.join(zip_folder, name))
        )

    def evaluate(
        self,
        zip_folder,
        output_path,
        configuration,
        runtime_args="",
        timeout=5,
        progress_callback=None,
    ):
        def notify(event, **kwargs):
            if progress_callback:
                progress_callback(event, **kwargs)

        notify("zip_start")
        ZipProcessor(zip_folder).process_zip_files()
        notify("zip_done")

        student_dirs = self._student_directories(zip_folder)
        total = len(student_dirs)
        notify("eval_start", total=total)

        entries = []
        for index, name in enumerate(student_dirs, start=1):
            notify(
                "student_start",
                student_id=name,
                index=index,
                total=total,
            )
            try:
                student_dir = os.path.join(zip_folder, name)

                compile_result = self.compiler.compile(student_dir, configuration)
                if compile_result.status == "compile_error":
                    entry = ReportEntry(
                        compile_result.student_id,
                        SubmissionStatus.ERROR,
                        compile_result.error_log,
                    )
                    entries.append(entry)
                    notify(
                        "student_done",
                        student_id=name,
                        index=index,
                        total=total,
                        entry=entry,
                    )
                    continue

                run_result = self.runner.run(
                    student_dir, runtime_args, configuration, timeout=timeout
                )
                if run_result.status == "runtime_error":
                    entry = ReportEntry(
                        run_result.student_id,
                        SubmissionStatus.ERROR,
                        run_result.error_log,
                    )
                    entries.append(entry)
                    notify(
                        "student_done",
                        student_id=name,
                        index=index,
                        total=total,
                        entry=entry,
                    )
                    continue

                compare = self.output_comparator.compare(
                    run_result.actual_output, output_path
                )
                entry = ReportEntry(
                    run_result.student_id,
                    self._map_service_status(compare["status"]),
                    compare["log_details"],
                )
                entries.append(entry)
                notify(
                    "student_done",
                    student_id=name,
                    index=index,
                    total=total,
                    entry=entry,
                )
            except Exception as e:
                entry = ReportEntry(
                    name,
                    SubmissionStatus.ERROR,
                    f"Unexpected Error: {str(e)}",
                )
                entries.append(entry)
                notify(
                    "student_done",
                    student_id=name,
                    index=index,
                    total=total,
                    entry=entry,
                )
                continue

        notify("eval_complete", total=total, processed=len(entries))
        return entries

    @staticmethod
    def _map_service_status(status):
        if status == ServiceStatus.SUCCESS:
            return SubmissionStatus.SUCCESS
        if status == ServiceStatus.WRONG_OUTPUT:
            return SubmissionStatus.FAIL
        return SubmissionStatus.ERROR