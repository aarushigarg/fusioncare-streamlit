from openai import OpenAI
import datetime
import streamlit as st
import os

class FileManager:
    def __init__(self):
        open_api_key=st.secrets["OPENAI_API_KEY"]
        self.client = OpenAI(api_key=open_api_key)
        self.vector_store_id = st.secrets["VECTOR_STORE_ID"]

        # Initialize the OpenAI client
        self.client = OpenAI(api_key=open_api_key)

    def list_files(self):
        response = self.client.files.list(purpose="assistants")
        if len(response.data) == 0:
            print("No files found.")
            return
        file_names = []
        for file in response.data:
            created_date = datetime.datetime.utcfromtimestamp(file.created_at).strftime('%Y-%m-%d')
            file_names.append(file.filename)
            print(f" - {file.filename} [{file.id}], Created: {created_date}")
        print()
        return file_names

    def upload_new_files(self, directory="information_pdf"):
        added_files = self.list_files()
        for filename in os.listdir(directory):
            # Construct full file path
            file_path = os.path.join(directory, filename)
            # Check if the file is a PDF file and not already uploaded
            if os.path.isfile(file_path) and filename.lower().endswith('.pdf') and filename not in added_files:
                print(f"Uploading {filename}...")
                # Upload the file to OpenAI
                try:
                    with open(file_path, "rb") as file:
                        response = self.client.files.create(file=file, purpose="assistants")
                        print(f"File uploaded successfully: {response.filename} [{response.id}]")

                        file = self.client.beta.vector_stores.files.create_and_poll(
                            vector_store_id=self.vector_store_id,
                            file_id=response.id
                        )
                        print(f"File uploaded to vector store: {file.status}")  
                except FileNotFoundError:
                    print("File not found. Please make sure the filename and path are correct.")
                except Exception as e:
                    print(f"An error occurred while uploading {filename}: {e}")

    def list_and_delete_file(self):
        while True:
            response = self.client.files.list(purpose="assistants")
            files = list(response.data)
            if len(files) == 0:
                print("No files found.")
                return
            for i, file in enumerate(files, start=1):
                created_date = datetime.datetime.utcfromtimestamp(file.created_at).strftime('%Y-%m-%d')
                print(f"[{i}] {file.filename} [{file.id}], Created: {created_date}")
            choice = input("Enter a file number to delete, or any other input to return to menu: ")
            if not choice.isdigit() or int(choice) < 1 or int(choice) > len(files):
                return
            selected_file = files[int(choice) - 1]
            self.client.files.delete(selected_file.id)
            print(f"File deleted: {selected_file.filename}")

    def delete_all_files(self):
        confirmation = input("This will delete all OpenAI files with purpose 'assistants'.\n Type 'YES' to confirm: ")
        if confirmation == "YES":
            response = self.client.files.list(purpose="assistants")
            num_files = 0
            for file in response.data:
                self.client.files.delete(file.id)
                num_files += 1
            print(num_files + " files with purpose 'assistants' have been deleted.")
        else:
            print("Operation cancelled.")

def main():
    vector_store = FileManager()
    while True:
        print("\n== Assistants file utility ==")
        print("[1] List all files")
        print("[2] Upload all unadded files")
        print("[3] List all and delete one of your choice")
        print("[4] Delete all assistant files (confirmation required)")
        print("[9] Exit")
        choice = input("Enter your choice: ")

        if choice == "1":
            vector_store.list_files()
        elif choice == "2":
            vector_store.upload_new_files()
        elif choice == "3":
            vector_store.list_and_delete_file()
        elif choice == "4":
            vector_store.delete_all_files()
        elif choice == "9":
            break
        else:
            print("Invalid choice. Please try again.")

if __name__ == "__main__":
    main()