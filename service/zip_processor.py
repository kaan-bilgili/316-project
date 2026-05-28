import os
import zipfile
import shutil


class ZipProcessor:

    def __init__(self, submissions_folder):

        self.submissions_folder = submissions_folder


    def get_zip_files(self):

        zip_files = []

        for file in os.listdir(self.submissions_folder):

            if file.endswith(".zip"):

                zip_files.append(file)

        return zip_files


    def extract_zip(self, zip_path, extract_folder):

        with zipfile.ZipFile(zip_path, 'r') as zip_ref:

            zip_ref.extractall(extract_folder)

        print(f"{zip_path} extracted.")


    def create_student_folder(self, student_id):

        folder_path = os.path.join(self.submissions_folder, student_id)

        if os.path.exists(folder_path):
            shutil.rmtree(folder_path)

        os.makedirs(folder_path, exist_ok=True)

        return folder_path


    def process_zip_files(self):

        zip_files = self.get_zip_files()

        results = [] 
        
        for zip_file in zip_files:
            student_id = os.path.splitext(zip_file)[0] 
            zip_path = os.path.join(self.submissions_folder, zip_file) 
            try: 
                extract_folder = self.create_student_folder(student_id) 
                self.extract_zip(zip_path, extract_folder) 
                result = {
                     "student_id": student_id, 
                     "status": "SUCCESS", 
                     "path": extract_folder 
                } 
                
                results.append(result) 
                print(f"{student_id} processed successfully.") 
            except zipfile.BadZipFile: 
                result = {
                    "student_id": student_id, 
                    "status": "BAD_ZIP", 
                    "path": None 
                } 
                
                results.append(result) 
                
                print(f"{student_id} contains an invalid ZIP file.") 
                
            except FileNotFoundError:
                result = {
                    "student_id": student_id, 
                    "status": "FILE_NOT_FOUND", 
                    "path": None 
                } 
                
                results.append(result) 
                print(f"{student_id} file could not be found.") 
                
            except Exception as e: 
                result = {
                    "student_id": student_id, 
                    "status": "ERROR", 
                    "error": str(e), 
                    "path": None 
                } 
                
                results.append(result) 
                print(f"Error processing {student_id}: {e}") 
                 
        return results
