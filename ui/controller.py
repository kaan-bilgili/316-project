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

        
        self.ui.btn_create.configure(command=self.create_project)
        self.ui.btn_open.configure(command=self.open_project)
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

            self.ui.status_lbl.configure(
                text=f"Project Created: {project.name}",
                text_color=self.ui.accent_color,
            )
            messagebox.showinfo(
                self.ui.tr("new_project_title"),
                f"Project '{name}' created successfully."
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
            project = self.project_manager.open_project(db_path)
            if project is None:
                raise ValueError(
                    "Selected database does not contain a valid project."
            )
            self.ui.set_zip_path(project.submissions_dir)
            self.ui.set_output_path(project.expected_output_path)
            self._load_configuration(project.configuration_name)
            self._load_results_from_db(project.id)

            self.current_project_name = project.name

            self.ui.status_lbl.configure(
                text=f"Loaded Project: {project.name}",
                text_color=self.ui.accent_color,
            )
            messagebox.showinfo(
                self.ui.tr("open_project"),
                f"Project Name: {project.name}\n"
                f"Configuration: {project.configuration_name}\n"
                f"Description: {project.description}\n"
                f"Loaded Results: {self.loaded_results_count}"
            )
        except Exception as exc:
            messagebox.showerror(
                self.ui.tr("open_project"),
                f"{self.ui.tr('err_open_project')}\n{exc}",
            )

    def _load_configuration(self, configuration_name):
        config = self.config_repo.load(configuration_name)
        if config is None:
            return

        self.ui.path_entry.delete(0, "end")
        self.ui.path_entry.insert(0, config.compiler_path)
        self.ui.prog_lang_var.set(config_to_prog_lang(config))

    def _load_results_from_db(self, project_id):
        self.ui.tree.delete(*self.ui.tree.get_children())
        repo = self._result_repo()
        if repo is None:
            self.loaded_results_count = 0
            return

        entries = repo.load_by_project(project_id)

        self.loaded_results_count = len(entries)

        for entry in entries:
            self.ui.tree.insert(
                "", "end", values=(entry.student_id, entry.status.value, entry.log_details),
            )

    def clear_history(self):
        if not messagebox.askyesno(
            self.ui.tr("confirm_clear_title"), self.ui.tr("confirm_clear")
        ):
            return

        self.ui.tree.delete(*self.ui.tree.get_children())
        self.ui.status_lbl.configure(
            text=self.ui.tr("status_idle"),
            text_color=self.ui.accent_color,
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

        self.ui.status_lbl.configure(
            text=self.ui.tr("status_compiling"),
            text_color="#f1c40f",
        )
        self.ui.tree.delete(*self.ui.tree.get_children())
        if project:
            self.project_manager.clear_results()
        self.root.update_idletasks()

        try:
            entries = self.evaluation_service.evaluate(
                self.ui._zip_path,
                self.ui._output_path,
                configuration,
                runtime_args=self.ui.args_entry.get().strip(),
                timeout=timeout,
            )
        except Exception as exc:
            messagebox.showerror(
                self.ui.tr("start_evaluation"),
                f"{self.ui.tr('err_evaluation')}\n{exc}",
            )
            self.ui.status_lbl.configure(
                text=self.ui.tr("status_idle"),
                text_color=self.ui.accent_color,
            )
            return

        if not entries:
            messagebox.showinfo(
                self.ui.tr("start_evaluation"), self.ui.tr("err_no_students")
            )

        for entry in entries:
            self.ui.tree.insert(
                "", "end", values=(entry.student_id, entry.status.value, entry.log_details)
            )
            self._persist_result(entry)

        project_name = (
            self.current_project_name
            if self.current_project_name
            else "Session"
        )

        self.ui.status_lbl.configure(
            text=f"Evaluation Completed - {project_name}",
            text_color=self.ui.accent_color,
        )

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
        rows = [
            self.ui.tree.item(item, "values")
            for item in self.ui.tree.get_children()
        ]
        if not rows:
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
        self.report_generator.export_txt(path, rows, headers)
        messagebox.showinfo(
            self.ui.tr("export_title"), self.ui.tr("export_success")
        )
