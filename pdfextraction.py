import os
import PyPDF2

def extract_text_from_pdf(pdf_filename, input_folder="information_pdf", output_folder="information_txt"):
    # Path to the PDF file
    pdf_path = os.path.join(input_folder, pdf_filename)
    
    # Check if the PDF file exists
    if not os.path.exists(pdf_path):
        # print(f"The file {pdf_filename} does not exist.")
        return

    try:
        print(f"Extracting text from {pdf_filename}")

        # Open the PDF file
        with open(pdf_path, 'rb') as pdf_file:
            pdf_reader = PyPDF2.PdfReader(pdf_file)
            
            # Read each page from the PDF file
            text = []
            for page in pdf_reader.pages:
                text.append(page.extract_text())
        
        # Join all text from all pages
        full_text = '\n'.join(text)

        # Define the output file path
        output_file_path = os.path.join(os.getcwd(), output_folder, f"{pdf_filename.replace('.pdf', '.txt')}")

        # Write the extracted text to a new file
        with open(output_file_path, 'w', encoding='utf-8') as output_file:
            output_file.write(full_text)

        print(f"Text has been extracted and saved to {output_file_path}")

    except Exception as e:
        print(f"An error occurred: {e}")


directory = "information_pdf"
for filename in os.listdir(directory):
    # Construct full file path
    file_path = os.path.join(directory, filename)
    # Check if the file is a PDF
    if os.path.isfile(file_path) and filename.lower().endswith('.pdf') and filename.replace('.pdf', '.txt') not in os.listdir("information_txt"):
        extract_text_from_pdf(filename)
