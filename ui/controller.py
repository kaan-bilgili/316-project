from tkinter import filedialog, messagebox

from data.configuration_repository import ConfigurationRepository
from data.student_result_repository import StudentResultRepository
from service.evaluation_service import EvaluationService
from service.project_manager import ProjectManager
from service.report_generator import ReportGenerator
from ui.GUI import IAECompleteGUI
from ui.configuration_builder import build_configuration, config_to_prog_lang
from ui.dialogs import NewProjectDialog
from ui.config_manager_dialog import ConfigManagerDialog

class IAELogicController:
    def __init__(self, root):
        self.root = root
        self.ui = IAECompleteGUI(root)
        self.project_manager = ProjectManager()
        self.config_repo = ConfigurationRepository()
        self.evaluation_service = EvaluationService()
        self.report_generator = ReportGenerator()
        self.current_project_name = None
        self.loaded_results_count = 0
        self._eval_live_entries = []

        self.ui.btn_create.configure(command=self.create_project)
        self.ui.btn_open.configure(command=self.open_project)
        self.ui.btn_save.configure(command=self.save_project)
        self.ui.btn_clear_db.configure(command=self.clear_history)
        self.ui.btn_browse_path.configure(command=self.browse_compiler)
        self.ui.btn_zip.configure(command=self.select_zip_folder)
        self.ui.btn_output.configure(command=self.select_output_file)
        self.ui.btn_run.configure(command=self.start_evaluation_process)
        self.ui.btn_export.configure(command=self.export_report)
        self.ui.btn_manage_configs.configure(command=self.manage_configurations)

    def browse_compiler(self):
        path = filedialog.askopenfilename(title=self.ui.tr("dlg_compiler"))
        if path:
            self.ui.path_entry.delete(0, "end")
            self.ui.path_entry.insert(0, path)

    def manage_configurations(self):
        ConfigManagerDialog(self.root, self.config_repo, self.ui.tr)

    def select_zip_folder(self):
        path = filedialog.askdirectory(title=self.ui.tr("dlg_zip_folder"))
        if path:
            self.ui.set_zip_path(path)

    def select_output_file(self):
        path = filedialog.askopenfilename(title=self.ui.tr("dlg_output_file"))
        if path:
            self.ui.set_output_path(path)

    def create_project(self):
        if not self.ui._zip_path or not self.ui._output_path:
            messagebox.showwarning(
                self.ui.tr("new_project_title"), self.ui.tr("err_project_paths")
            )
            return

        config_names = [cfg.name for cfg in self.config_repo.load_all()]
        if not config_names:
            try:
                saved = self._build_configuration("project")
                if saved:
                    self.config_repo.save(saved)
                    config_names = [saved.name]
            except ValueError as exc:
                messagebox.showerror(self.ui.tr("new_project_title"), str(exc))
                return

        if not config_names:
            messagebox.showwarning(
                self.ui.tr("new_project_title"), self.ui.tr("err_no_config")
            )
            return

        NewProjectDialog(self.root, self.ui, config_names, self._finish_new_project)

    def _finish_new_project(self, name, description, configuration_name):
        if not configuration_name:
            messagebox.showwarning(
                self.ui.tr("new_project_title"), self.ui.tr("err_config_name")
            )
            return

        db_path = filedialog.asksaveasfilename(
            title=self.ui.tr("dlg_new_project_db"),
            defaultextension=".db",
            filetypes=[(self.ui.tr("dlg_project_db_filter"), "*.db")],
        )
        if not db_path:
            messagebox.showwarning(
                self.ui.tr("new_project_title"), self.ui.tr("err_project_db")
            )
            return

        try:
            self.project_manager.close_project()
            self.ui.set_active_project(None)
            self.project_manager.new_project(
                name=name,
                description=description,
                configuration_name=configuration_name,
                submissions_dir=self.ui._zip_path,
                expected_output_path=self.ui._output_path,
                db_path=db_path,
            )
            project = self.project_manager.get_current_project()

            self.current_project_name = project.name
            self.ui.set_active_project(project)

            self.ui.set_status_message(
                "status_project_created",
                text_color=self.ui.accent_color,
                name=project.name,
            )
            messagebox.showinfo(
                self.ui.tr("new_project_title"),
                self.ui.tr("project_created_msg").format(name=name),
            )
        except Exception as exc:
            messagebox.showerror(self.ui.tr("new_project_title"), str(exc))

    def open_project(self):
        db_path = filedialog.askopenfilename(
            title=self.ui.tr("dlg_open_project_db"),
            filetypes=[(self.ui.tr("dlg_project_db_filter"), "*.db")],
        )
        if not db_path:
            return

        try:
            self.project_manager.close_project()
            self.ui.set_active_project(None)
            project = self.project_manager.open_project(db_path)
            if project is None:
                raise ValueError(self.ui.tr("err_invalid_project_db"))
            self.ui.set_zip_path(project.submissions_dir)
            self.ui.set_output_path(project.expected_output_path)
            self._load_configuration(project.configuration_name)
            self._load_results_from_db(project.id)

            self.current_project_name = project.name
            self.ui.set_active_project(project)

            self.ui.set_status_message(
                "status_project_loaded",
                text_color=self.ui.accent_color,
                name=project.name,
            )
            messagebox.showinfo(
                self.ui.tr("open_project"),
                self.ui.tr("project_opened_body").format(
                    name=project.name,
                    configuration=project.configuration_name,
                    description=project.description or "—",
                    count=self.loaded_results_count,
                ),
            )
        except Exception as exc:
            messagebox.showerror(
                self.ui.tr("open_project"),
                f"{self.ui.tr('err_open_project')}\n{exc}",
            )

    def save_project(self):
        project = self.project_manager.get_current_project()
        if project is None:
            messagebox.showwarning(
                self.ui.tr("save_project"),
                self.ui.tr("err_no_project_to_save"),
            )
            return

        if not self.ui._zip_path or not self.ui._output_path:
            messagebox.showwarning(
                self.ui.tr("save_project"), self.ui.tr("err_project_paths")
            )
            return

        project.submissions_dir = self.ui._zip_path
        project.expected_output_path = self.ui._output_path

        try:
            configuration = self._build_configuration(project.configuration_name)
            if configuration is not None:
                self.config_repo.save(configuration)
            self.project_manager.save_project()
            self.current_project_name = project.name
            self.ui.set_active_project(project)
            self.ui.set_status_message(
                "status_project_saved",
                text_color=self.ui.accent_color,
                name=project.name,
            )
            messagebox.showinfo(
                self.ui.tr("save_project"),
                self.ui.tr("project_saved_msg").format(name=project.name),
            )
        except Exception as exc:
            messagebox.showerror(self.ui.tr("save_project"), str(exc))

    def _load_configuration(self, configuration_name):
        config = self.config_repo.load(configuration_name)
        if config is None:
            return

        self.ui.path_entry.delete(0, "end")
        self.ui.path_entry.insert(0, config.compiler_path)
        self.ui.prog_lang_var.set(config_to_prog_lang(config))

    def _load_results_from_db(self, project_id):
        repo = self._result_repo()
        if repo is None:
            self.loaded_results_count = 0
            self.ui.clear_result_rows()
            return

        entries = repo.load_by_project(project_id)
        self.loaded_results_count = len(entries)
        self.ui.load_result_rows(entries)

    def clear_history(self):
        if not messagebox.askyesno(
            self.ui.tr("confirm_clear_title"), self.ui.tr("confirm_clear")
        ):
            return

        self.ui.clear_result_rows()
        self.ui.set_status_message(
            "status_idle", text_color=self.ui.accent_color
        )
        self.project_manager.clear_results()
        self.loaded_results_count = 0

    def _build_configuration(self, config_name):
        return build_configuration(
            config_name,
            self.ui.prog_lang_var.get(),
            self.ui.path_entry.get(),
            self.ui.tr("select_prog_lang"),
        )

    def _validate_evaluation_inputs(self):
        if not self.ui._zip_path:
            messagebox.showwarning(
                self.ui.tr("start_evaluation"), self.ui.tr("err_no_zip")
            )
            return False
        if not self.ui._output_path:
            messagebox.showwarning(
                self.ui.tr("start_evaluation"), self.ui.tr("err_no_output")
            )
            return False
        if self.ui.prog_lang_var.get() == self.ui.tr("select_prog_lang"):
            messagebox.showwarning(
                self.ui.tr("start_evaluation"), self.ui.tr("err_no_prog_lang")
            )
            return False
        if not self.ui.path_entry.get().strip():
            messagebox.showwarning(
                self.ui.tr("start_evaluation"), self.ui.tr("err_no_compiler")
            )
            return False
        return True

    def start_evaluation_process(self):
        if not self._validate_evaluation_inputs():
            return

        try:
            timeout = int(self.ui.timeout_entry.get().strip() or "5")
        except ValueError:
            timeout = 5

        config_name = "session"
        project = self.project_manager.get_current_project()
        if project:
            config_name = project.configuration_name

        try:
            configuration = self._build_configuration(config_name)
            if configuration is None:
                messagebox.showwarning(
                    self.ui.tr("start_evaluation"), self.ui.tr("err_no_prog_lang")
                )
                return
            self.config_repo.save(configuration)
        except ValueError as exc:
            messagebox.showerror(self.ui.tr("start_evaluation"), str(exc))
            return

        self.ui.clear_result_rows()
        self._eval_live_entries = []
        if project:
            self.project_manager.clear_results()

        self.ui.begin_evaluation()
        self.ui.set_evaluation_progress(0, self.ui.tr("status_compiling"))
        self.root.update_idletasks()

        try:
            entries = self.evaluation_service.evaluate(
                self.ui._zip_path,
                self.ui._output_path,
                configuration,
                runtime_args=self.ui.args_entry.get().strip(),
                timeout=timeout,
                progress_callback=self._on_evaluation_progress,
            )
        except Exception as exc:
            messagebox.showerror(
                self.ui.tr("start_evaluation"),
                f"{self.ui.tr('err_evaluation')}\n{exc}",
            )
            self.ui.end_evaluation()
            self.ui.set_status_message(
                "status_idle", text_color=self.ui.accent_color
            )
            if self._eval_live_entries:
                self.ui.update_evaluation_summary(
                    self._eval_live_entries,
                    total_all=len(self._eval_live_entries),
                )
            else:
                self.ui.update_evaluation_summary([])
            return

        self.ui.end_evaluation()

        if not entries:
            messagebox.showinfo(
                self.ui.tr("start_evaluation"), self.ui.tr("err_no_students")
            )
        else:
            self.ui.update_evaluation_summary(
                self._eval_live_entries,
                total_all=len(self._eval_live_entries),
            )

        self.ui.set_status_message(
            "status_completed", text_color=self.ui.accent_color
        )

    def _on_evaluation_progress(self, event, **data):
        if event == "zip_start":
            self.ui.set_evaluation_progress(0, self.ui.tr("eval_progress_zip"))
        elif event == "zip_done":
            self.ui.set_evaluation_progress(0.05, self.ui.tr("status_compiling"))
        elif event == "eval_start":
            total = data.get("total", 0)
            if total == 0:
                self.ui.set_evaluation_progress(
                    0, self.ui.tr("eval_progress_none")
                )
            else:
                self.ui.set_evaluation_progress(
                    0.08,
                    self.ui.tr("eval_progress_start").format(total=total),
                )
        elif event == "student_start":
            index = data.get("index", 0)
            total = data.get("total", 0)
            student_id = data.get("student_id", "")
            fraction = ((index - 1) / total) if total else 0.0
            self.ui.set_evaluation_progress(
                0.08 + 0.92 * fraction,
                self.ui.tr("eval_progress_student").format(
                    student_id=student_id,
                    current=index,
                    total=total,
                ),
            )
        elif event == "student_done":
            entry = data.get("entry")
            if entry is not None:
                self._eval_live_entries.append(entry)
                self.ui.add_result_row(
                    entry.student_id, entry.status, entry.log_details
                )
                self._persist_result(entry)
            index = data.get("index", 0)
            total = data.get("total", 0)
            fraction = (index / total) if total else 1.0
            student_id = data.get("student_id", "")
            self.ui.set_evaluation_progress(
                0.08 + 0.92 * fraction,
                self.ui.tr("eval_progress_student").format(
                    student_id=student_id,
                    current=index,
                    total=total,
                ),
            )
        self.root.update_idletasks()

    def _result_repo(self):
        db = self.project_manager._db
        if db is None:
            return None
        return StudentResultRepository(db)

    def _persist_result(self, entry):
        project = self.project_manager.get_current_project()
        repo = self._result_repo()
        if project is None or repo is None:
            return
        repo.save(project.id, entry)

    def export_report(self):
        entries = self.ui._rows_to_entries(self.ui._tree_rows)
        if not entries:
            messagebox.showwarning(
                self.ui.tr("export_title"), self.ui.tr("export_empty")
            )
            return

        path = filedialog.asksaveasfilename(
            title=self.ui.tr("dlg_save_report"),
            defaultextension=".txt",
            filetypes=[(self.ui.tr("dlg_text_files"), "*.txt")],
        )
        if not path:
            return

        headers = (
            self.ui.tr("col_student_id"),
            self.ui.tr("col_status"),
            self.ui.tr("col_logs"),
        )
        project = self.project_manager.get_current_project()
        project_name = project.name if project else ""
        self.report_generator.export_entries_txt(path, entries, headers, project_name)
        messagebox.showinfo(
            self.ui.tr("export_title"), self.ui.tr("export_success")
        )
