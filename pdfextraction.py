import os
from pdf2docx import Converter

def extract_text_from_pdf(pdf_filename, input_folder="information_pdf", output_folder="information_docx"):
    # Path to the PDF file
    pdf_path = os.path.join(input_folder, pdf_filename)
    
    # Check if the PDF file exists
    if not os.path.exists(pdf_path):
        print(f"The file {pdf_filename} does not exist.")
        return

    try:
        print(f"Extracting text from {pdf_filename}")

        # Create a PDF converter object
        cv = Converter(pdf_path)
    
        # Define the output file path
        output_file_path = os.path.join(os.getcwd(), output_folder, f"{pdf_filename.replace('.pdf', '.docx')}")

        # Convert all pages of the PDF to a Word file
        cv.convert(output_file_path, start=0, end=None)

        # Close the converter object
        cv.close()

        print(f"Text has been extracted and saved to {output_file_path}")

    except Exception as e:
        print(f"An error occurred: {e}")


directory = "information_pdf"
for filename in os.listdir(directory):
    # Construct full file path
    file_path = os.path.join(directory, filename)
    # Check if the file is a PDF file and if the corresponding DOCX file does not exist
    if os.path.isfile(file_path) and filename.lower().endswith('.pdf') and filename.replace('.pdf', '.docx') not in os.listdir("information_docx"):
        extract_text_from_pdf(filename)
