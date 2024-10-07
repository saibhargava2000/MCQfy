import os
import PyPDF2
from docx import Document

def read_files_in_directory(directory_path):
    combined_content = ""

    for filename in os.listdir(directory_path):
        if filename.endswith('.txt'):
            with open(os.path.join(directory_path, filename), 'r', encoding='utf-8') as file:
                combined_content += file.read()

        elif filename.endswith('.pdf'):
            with open(os.path.join(directory_path, filename), 'rb') as file:
                pdf_reader = PyPDF2.PdfFileReader(file)
                for page_num in range(pdf_reader.numPages):
                    page = pdf_reader.getPage(page_num)
                    combined_content += page.extractText()

        elif filename.endswith('.docx'):
            doc = Document(os.path.join(directory_path, filename))
            for para in doc.paragraphs:
                combined_content += para.text

    return combined_content


