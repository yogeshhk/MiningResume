import os, PyPDF2, docx2txt
from os import path

BASE_DIR = path.dirname(__file__)

DATA_FOLDER = path.join(BASE_DIR, "data")
CONFIG_FILE = path.join(BASE_DIR, "config.xml")


def read_data(data_folder_path):
    resume_texts = []
    for filename in os.listdir(data_folder_path):
        extension = os.path.splitext(filename)[1]
        resume_text = None
        if extension == ".txt":
            with open(os.path.join(data_folder_path, filename), 'r') as file:
                resume_text = file.read()
        elif extension == ".pdf":
            resume_text = pdf_to_txt(os.path.join(data_folder_path, filename))
        elif extension == ".docx":
            resume_text = docx_to_txt(os.path.join(data_folder_path, filename))

        if resume_text:
            result_dict = {'filename': filename, 'resume_text': resume_text}
            resume_texts.append(result_dict)
    return resume_texts


def docx_to_txt(file_doc_path):
    doc = docx2txt.process(file_doc_path)
    raw = ""
    raw += doc
    return raw


def pdf_to_txt(file_path):
    pdfFile = open(file_path, "rb")  # Open resume.pdf as rb, store it in pdfFile variable
    pdfReader = PyPDF2.PdfReader(pdfFile)  # Reads the file using PdfFileReader from PyPDF2
    raw = ""
    for index in range(len(pdfReader.pages)):
        page = pdfReader.pages[index]  # Get the number of pages
        text = page.extract_text()  # Extract the text on every page
        raw += text
    return raw
