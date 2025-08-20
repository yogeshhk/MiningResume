import os
import re
import json
from collections import OrderedDict
from docling.document_converter import DocumentConverter

        
class DoclingResumeParser:
    """
    Resume parser using Docling (no LLMs).
    Extracts structured fields like Name, Email, Phone, Education, etc.
    """

    def __init__(self):
       
        self.converter = DocumentConverter()
        self.attributes_list = [
            "Name", "Email", "Phone Number", "Address",
            "Skills", "Employment History", "Education History", "Accomplishments"
        ]

    def read_single_resume(self, file_path: str):
        """
        Convert a resume file into markdown text.
        Supports PDF, DOCX, and TXT.
        """
        try:
            result = self.converter.convert(file_path)
            text = result.document.export_to_markdown()
            return {"filename": os.path.basename(file_path), "resume_text": text}
        except Exception as e:
            print(f"Error reading file {file_path}: {e}")
            return None

    def read_resumes_from_folder(self, folder_path: str):
        """
        Reads all resumes from a folder and returns list of dicts.
        """
        resumes = []
        if not os.path.isdir(folder_path):
            print(f"Error: Directory not found at {folder_path}")
            return resumes

        for filename in os.listdir(folder_path):
            file_path = os.path.join(folder_path, filename)
            if os.path.isfile(file_path):
                result_dict = self.read_single_resume(file_path)
                if result_dict:
                    resumes.append(result_dict)
        return resumes

    def parse_resume(self, resume_text: str):
        """
        Rule-based parsing of resume text into attributes.
        """
        parsed = OrderedDict()

        # Regex-based extraction
        email_match = re.search(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}", resume_text)
        phone_match = re.search(r"\+?\d[\d\s\-()]{7,}", resume_text)

        parsed["Email"] = email_match.group(0) if email_match else ""
        parsed["Phone Number"] = phone_match.group(0) if phone_match else ""

        # Name heuristic (first line, unless it's an email/phone)
        lines = resume_text.strip().split("\n")
        if lines:
            first_line = lines[0].strip()
            if not re.search(r"[@\d]", first_line):
                parsed["Name"] = first_line
            else:
                parsed["Name"] = ""
        else:
            parsed["Name"] = ""

        # Simple keyword-based sections
        def extract_section(keyword):
            pattern = re.compile(rf"{keyword}.*?(?=\n[A-Z][a-zA-Z ]+:|\Z)", re.DOTALL | re.IGNORECASE)
            match = pattern.search(resume_text)
            return match.group(0).strip() if match else ""

        parsed["Address"] = extract_section("Address")
        parsed["Skills"] = extract_section("Skills")
        parsed["Employment History"] = extract_section("Experience|Work|Employment")
        parsed["Education History"] = extract_section("Education")
        parsed["Accomplishments"] = extract_section("Achievements|Accomplishments")

        return parsed


if __name__ == "__main__":
    base_dir = os.path.dirname(__file__)
    data_folder = os.path.join(base_dir, "data")
    sample_resume_path = os.path.join(data_folder, "YogeshKulkarniLinkedInProfile.pdf")

    parser = DoclingResumeParser()
    resume = parser.read_single_resume(sample_resume_path)

    if resume:
        print(f"\n--- Parsing {resume['filename']} ---")
        parsed_data = parser.parse_resume(resume['resume_text'])
        parsed_data["filename"] = resume["filename"]

        print("\n--- Parsed Result ---")
        print(json.dumps(parsed_data, indent=4))
    else:
        print("Could not extract text from the sample resume.")
