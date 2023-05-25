import os, PyPDF2, docx2txt
from langchain.chains import LLMChain, SimpleSequentialChain  # import LangChain libraries
from langchain.llms import OpenAI, HuggingFaceHub  # import OpenAI model
from langchain.prompts import PromptTemplate  # import PromptTemplate

# Use any one of the following
# llm = HuggingFaceHub(repo_id="bigscience/bloom", model_kwargs={"temperature": 1e-10})

llm = OpenAI(
    model_name="text-curie-001",
    temperature=0,
)

attributes_list = ["Name", "Email", "Address", "Phone Number", "Objective", "Skills", "Employment History",
                   "Education History", "Accomplishments"]


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


def main(file_path):
    parsed_resumes = []
    for filename in os.listdir(file_path):
        extension = os.path.splitext(filename)[1]
        resume_text = None
        if extension == ".txt":
            with open(os.path.join(file_path, filename), 'r') as file:
                resume_text = file.read()
        elif extension == ".pdf":
            resume_text = pdf_to_txt(os.path.join(file_path, filename))
        elif extension == ".docx":
            resume_text = docx_to_txt(os.path.join(file_path, filename))  # Pass the full file path to docx_to_txt()

        if resume_text:
            parsed_info = parse_resume_by_llm(resume_text)
            parsed_resumes.append(parsed_info)
    return parsed_resumes

def parse_resume_by_llm(text):
    parsed_info = []
    prompt = """You are an expert recruiter skilled at extracting relevant information from a resume.
    Please extract {attribute} from the resume text given as {resume}. The output should be crisp and exact with no 
    extra words, not even the attribute name in the completion.

    Extracted value:
    """
    prompt_template = PromptTemplate(
        input_variables=["resume", "attribute"],
        template=prompt
    )
    chain = LLMChain(llm=llm,
                     prompt=prompt_template)
    for attr in attributes_list:
        result = chain.run({'resume': text, 'attribute': attr})
        parsed_info.append({attr: result.strip()})
    return parsed_info


if __name__ == "__main__":
    resume_folder = "data"
    results = main(resume_folder)
    print("Final Result:\n {}".format(results))

