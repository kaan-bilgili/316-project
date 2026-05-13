class error_handler:

    def handle_compile_error(self, student_id, error):
        print(f"[COMPILE ERROR] {student_id}: {error}")
    
    def handle_runtime_error(self, student_id, error):
        print(f"[RUNTIME ERROR] {student_id}: {error}")

    def log_error(self, student_id, message):
        print(f"[ERROR LOG] {student_id}: {message}")
    