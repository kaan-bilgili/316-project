import os
import zipfile


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

        os.makedirs(folder_path, exist_ok=True)

        return folder_path


    def process_zip_files(self):

        zip_files = self.get_zip_files()

        for zip_file in zip_files:

            student_id = zip_file.replace(".zip", "")

            zip_path = os.path.join(self.submissions_folder, zip_file)

            try:

                extract_folder = self.create_student_folder(student_id)

                self.extract_zip(zip_path, extract_folder)

                print(f"{student_id} processed successfully.")

            except Exception as e:

                print(f"Error processing {student_id}: {e}")

                continue 
