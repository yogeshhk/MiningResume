import os
import json
from collections import OrderedDict
import PyPDF2
import docx2txt
from langchain.chains import LLMChain
from langchain_community.llms import HuggingFaceHub
from langchain.prompts import PromptTemplate
from langchain_huggingface import HuggingFaceEndpoint
from langchain.prompts import PromptTemplate
from langchain.schema.runnable import RunnableSequence
from transformers import pipeline
from langchain_community.llms import HuggingFacePipeline

class LLMResumeParser:
    """
    A class to parse resumes using a Large Language Model (LLM).
    It handles reading text from various file formats (.txt, .pdf, .docx)
    and extracts specified attributes from the resume content.
    """

    def __init__(self, model_name="google/flan-t5-large", temperature=1e-10):
        print(os.environ.get("HUGGINGFACEHUB_API_TOKEN"))
        print(os.environ.get("HF_API_TOKEN"))

        # self.llm = HuggingFaceEndpoint(
        #     repo_id="google/flan-t5-large",   # ✅ works with free inference API
        #     temperature=0.1,
        #     huggingfacehub_api_token=os.environ.get("HUGGINGFACEHUB_API_TOKEN")
        # )      
        # Load the model locally
        pipe = pipeline(
            "text2text-generation",   # for seq2seq models like flan-t5
            model=model_name,
            tokenizer=model_name,
            max_new_tokens=2048,
            token=False  # ✅ Correct and explicit way to force no token
        )
        self.llm = HuggingFacePipeline(pipeline=pipe)        
        self.attributes_list = [
            "Name", "Email", "Address", "Phone Number", "Objective", "Skills",
            "Employment History", "Education History", "Accomplishments"
        ]
        prompt = """You are an expert recruiter skilled at extracting relevant information from a resume.
        Please extract {attribute} from the resume text given as {resume}. The output should be crisp and exact with no
        extra words, not even the attribute name in the completion.

        Extracted value:
        """
        prompt_template = PromptTemplate(
            input_variables=["resume", "attribute"],
            template=prompt
        )
        # self.chain = LLMChain(llm=self.llm, prompt=prompt_template)
        self.chain = prompt_template | self.llm

    def _docx_to_txt(self, file_path):
        try:
            return docx2txt.process(file_path)
        except Exception as e:
            print(f"Error reading DOCX file {file_path}: {e}")
            return None

    def _pdf_to_txt(self, file_path):
        raw_text = ""
        try:
            with open(file_path, "rb") as pdf_file:
                pdf_reader = PyPDF2.PdfReader(pdf_file)
                for page in pdf_reader.pages:
                    raw_text += page.extract_text()
            return raw_text
        except Exception as e:
            print(f"Error reading PDF file {file_path}: {e}")
            return None

    def read_single_resume(self, file_path):
        """
        Reads a single resume file and extracts its text.

        Args:
            file_path (str): Path to the resume file.

        Returns:
            dict or None: {'filename': ..., 'resume_text': ...} if successful, else None.
        """
        extension = os.path.splitext(file_path)[1].lower()
        resume_text = None
        if extension == ".txt":
            try:
                with open(file_path, 'r', encoding='utf-8') as file:
                    resume_text = file.read()
            except Exception as e:
                print(f"Error reading TXT file {file_path}: {e}")
        elif extension == ".pdf":
            resume_text = self._pdf_to_txt(file_path)
        elif extension == ".docx":
            resume_text = self._docx_to_txt(file_path)

        if resume_text:
            return {"filename": os.path.basename(file_path), "resume_text": resume_text}
        return None

    def read_resumes_from_folder(self, folder_path):
        """
        Reads all resume files (.txt, .pdf, .docx) from a specified folder.
        """
        resume_texts = []
        if not os.path.isdir(folder_path):
            print(f"Error: Directory not found at {folder_path}")
            return resume_texts

        for filename in os.listdir(folder_path):
            file_path = os.path.join(folder_path, filename)
            result_dict = self.read_single_resume(file_path)
            if result_dict:
                resume_texts.append(result_dict)
        return resume_texts

    def parse_resume(self, resume_text):
        # print(f"DEBUG: Inside parse_resume -> {resume_text}")
        parsed_items_dict = OrderedDict()
        for attr in self.attributes_list:
            try:
                response = self.chain.invoke({'resume': resume_text, 'attribute': attr})
                if isinstance(response, dict) and "text" in response:
                    response_text = response["text"]
                else:
                    response_text = str(response)
                print(f"DEBUG: LLM raw response for {attr} -> {response_text}")
                parsed_items_dict[attr] = response_text.strip()
            except Exception as e:
                print(f"Error parsing attribute '{attr}': {e}")
                parsed_items_dict[attr] = "Error during parsing"
        return parsed_items_dict


if __name__ == "__main__":
    # --- End-to-End Testing ---

    base_dir = os.path.dirname(__file__)
    data_folder = os.path.join(base_dir, "data")
    sample_resume_path = os.path.join(data_folder, "YogeshKulkarniLinkedInProfile.pdf")
    print(f"A sample resume is at: {sample_resume_path}")

    try:
        parser = LLMResumeParser()

        # Read only the sample resume
        resume = parser.read_single_resume(sample_resume_path)
        if resume:
            print(f"\n--- Parsing {resume['filename']} ---")
            parsed_data = parser.parse_resume(resume['resume_text'])
            parsed_data['filename'] = resume['filename']

            json_result = json.dumps(parsed_data, indent=4)
            print("\n--- Parsed Result ---")
            print(json_result)
        else:
            print("\nCould not extract text from the sample resume.")

    except Exception as e:
        print(f"\nAn error occurred during the parsing process: {e}")
        print("Please ensure your HUGGINGFACEHUB_API_TOKEN environment variable is set correctly.")
