import os
import re
import json
from pathlib import Path

import PyPDF2
import docx2txt
import xml.etree.cElementTree as ET
from collections import OrderedDict

class RegexResumeParser:
    """
    A class to parse resumes using regex configurations.
    """
    def __init__(self, config_content):
        """
        Initializes the ResumeParser with the regex configuration.
        
        :param config_content: A string containing the XML configuration.
        """
        self.config = self._read_config_from_string(config_content)
        self.resume_text = ""
        self.parsed_data = None

    def _read_config_from_string(self, config_content):
        """
        Reads the XML configuration from a string.
        
        :param config_content: String containing the XML configuration.
        :return: A list of ordered dictionaries with the configuration.
        """
        root = ET.fromstring(config_content)
        config_element = []
        for child in root:
            term = OrderedDict()
            term["Term"] = child.get('name', "")
            for level1 in child:
                term["Method"] = level1.get('name', "")
                term["Section"] = level1.get('section', "")
                for level2 in level1:
                    term[level2.tag] = term.get(level2.tag, []) + [level2.text]
            config_element.append(term)
        return config_element

    def _docx_to_txt(self, file_doc_path):
        """
        Converts a .docx file to text.
        
        :param file_doc_path: Path to the .docx file.
        :return: Extracted text from the .docx file.
        """
        try:
            return docx2txt.process(file_doc_path)
        except Exception as e:
            print(f"Error processing docx file {file_doc_path}: {e}")
            return ""

    def _pdf_to_txt(self, file_path):
        """
        Converts a .pdf file to text.
        
        :param file_path: Path to the .pdf file.
        :return: Extracted text from the .pdf file.
        """
        raw_text = ""
        try:
            with open(file_path, "rb") as pdf_file:
                pdf_reader = PyPDF2.PdfReader(pdf_file)
                for page in pdf_reader.pages:
                    raw_text += page.extract_text() if page.extract_text() else ""
        except Exception as e:
            print(f"Error processing pdf file {file_path}: {e}")
        return raw_text

    def read_resume_file(self, file_path):
        """
        Reads a resume file (.txt, .pdf, .docx) and extracts the text.
        
        :param file_path: The full path to the resume file.
        :return: A dictionary containing the filename and the extracted text.
        """
        filename = os.path.basename(file_path)
        extension = os.path.splitext(filename)[1]
        resume_text = ""

        if extension == ".txt":
            try:
                with open(file_path, 'r', encoding='utf-8') as file:
                    resume_text = file.read()
            except Exception as e:
                print(f"Error reading txt file {file_path}: {e}")
        elif extension == ".pdf":
            resume_text = self._pdf_to_txt(file_path)
        elif extension == ".docx":
            resume_text = self._docx_to_txt(file_path)
        else:
            print(f"Unsupported file format for: {filename}")

        self.resume_text = resume_text
        if self.resume_text:
            return {'filename': filename, 'resume_text': self.resume_text}
        return None

    def _univalue_extractor(self, section, sub_terms_dict, parsed_items_dict):
        """
        Extracts single value items from a given section of the resume.
        """
        retval = OrderedDict()
        # Use the full resume text if no section is specified
        text_to_search = self.resume_text
        if section and "Sections" in parsed_items_dict and parsed_items_dict["Sections"].get(section):
             get_section_lines = parsed_items_dict["Sections"].get(section)
             text_to_search = "\n".join(get_section_lines)

        for node_tag, pattern_list in sub_terms_dict.items():
            for pattern in pattern_list:
                try:
                    regex_pattern = re.compile(r"{}".format(pattern), re.IGNORECASE | re.MULTILINE)
                    match = regex_pattern.search(text_to_search)
                    if match:
                        # Find the first non-empty group
                        result = next((g for g in match.groups() if g), None)
                        if result:
                            retval[node_tag] = result.strip()
                            break 
                except re.error as e:
                    print(f"Regex error for pattern '{pattern}': {e}")
            if node_tag in retval:
                break
        return retval


    def _section_value_extractor(self, section, sub_terms_dict, parsed_items_dict):
        """
        Extracts values from a specific section based on keywords.
        """
        retval = OrderedDict()
        single_section_lines = parsed_items_dict.get("Sections", {}).get(section)

        if not single_section_lines:
            #print(f"Warning: Section '{section}' not found or is empty.")
            return retval

        for line in single_section_lines:
            for node_tag, pattern_string_list in sub_terms_dict.items():
                pattern_string = pattern_string_list[0]
                pattern_list = [p.strip() for p in re.split(r',|:', pattern_string)]
                
                # Use word boundaries for more accurate matching
                matches = [pattern for pattern in pattern_list if re.search(r'\b' + re.escape(pattern) + r'\b', line, re.IGNORECASE)]
                
                if matches:
                    info_string = ", ".join(matches)
                    # Improved regex for years, handles YYYY-YYYY, YYYY-YY, YYYY-Present etc.
                    year_matches = re.findall(r'(\b\d{4}\b)\s*(?:-|to|–)\s*(\b\d{2,4}\b|Present|Current)', line, re.IGNORECASE)
                    if year_matches:
                        start_year, end_year = year_matches[0]
                        info_string += f" ({start_year}-{end_year})"
                    elif re.search(r'\b\d{4}\b', line): # Find standalone year
                        year = re.search(r'\b\d{4}\b', line).group()
                        info_string += f" ({year})"

                    retval[node_tag] = retval.get(node_tag, []) + [info_string]
                    break 
        return retval


    def _is_new_section(self, line, sub_terms_dict):
        """
        Determines if a line indicates the start of a new section.
        """
        line = line.strip()
        if not line:
            return ""
            
        # A section header is typically short, and often ends with a colon, or is just a word or two.
        if len(line.split()) > 4:
            return ""

        for node_tag, pattern_list in sub_terms_dict.items():
            for pattern in pattern_list[0].split(','):
                pattern = pattern.strip()
                # Match if the line starts with the pattern, case-insensitive
                if re.match(r'^\s*' + re.escape(pattern) + r'\b.*:?$', line, re.IGNORECASE):
                    return node_tag
        return ""

    def _section_extractor(self, section, sub_terms_dict, parsed_items_dict):
        """
        Segments the resume text into predefined sections.
        """
        retval = OrderedDict()
        if self.resume_text:
            current_section = "Header" 
            retval[current_section] = []
            lines = self.resume_text.splitlines()
            
            for line in lines:
                line = line.strip()
                if not line:
                    continue
                
                new_section = self._is_new_section(line, sub_terms_dict)
                if new_section and new_section != current_section:
                    current_section = new_section
                    retval[current_section] = [line] # Include section header line
                elif current_section:
                    retval.get(current_section, []).append(line)
        return retval


    def parse(self):
        """
        Parses the resume text based on the loaded configuration.
        """
        if not self.resume_text:
            print("Error: Resume text not loaded. Call read_resume_file() first.")
            return None

        parsed_items_dict = OrderedDict()
        
        # A map to allow calling methods by name
        extraction_methods = {
            "univalue_extractor": self._univalue_extractor,
            "section_value_extractor": self._section_value_extractor,
            "section_extractor": self._section_extractor
        }

        for term in self.config:
            term_name = term.get('Term')
            extraction_method_name = term.get('Method')
            extraction_method_ref = extraction_methods.get(extraction_method_name)
            
            if not extraction_method_ref:
                print(f"Warning: Method '{extraction_method_name}' not found.")
                continue

            section = term.get("Section")
            sub_term_dict = OrderedDict((k, v) for k, v in term.items() if k not in ["Term", "Method", "Section"])
            
            parsed_items_dict[term_name] = extraction_method_ref(section, sub_term_dict, parsed_items_dict)
        
        # Clean up the final output
        if "Sections" in parsed_items_dict:
            del parsed_items_dict["Sections"]
        
        self.parsed_data = parsed_items_dict
        return self.parsed_data

# --- Main execution block ---
if __name__ == "__main__":
    # 1. Define and create the regex_config.xml file
    # This makes the script self-contained and ensures the config is available.
    config_file_path = "regex_config.xml"

    # 2. Set up paths and check for the resume file
    # Create a 'data' directory if it doesn't exist
    data_path = Path(__file__).resolve().parent.parent.parent / "data"
    if not os.path.exists(data_path):
        os.makedirs(data_path)
        print("Created 'data' directory.")

    resume_file_path = os.path.join(data_path, "YogeshKulkarniLinkedInProfile.pdf")

    if not os.path.exists(resume_file_path):
        print(f"\nERROR: Resume file not found at '{resume_file_path}'")
        print("Please make sure the PDF file is in the 'data' directory before running.")
    else:
        # 3. Read config, instantiate the parser, and run the parsing process
        try:
            with open(config_file_path, 'r') as f:
                config_content = f.read()

            # Initialize the parser with the XML configuration content
            resume_parser = RegexResumeParser(config_content=config_content)
            
            # Read the content of the sample resume
            print(f"\n--- Reading Resume: {os.path.basename(resume_file_path)} ---")
            resume_data = resume_parser.read_resume_file(resume_file_path)

            if resume_data and resume_data['resume_text'].strip():
                print("--- Parsing Resume ---")
                # Parse the resume content
                parsed_result = resume_parser.parse()
                
                if parsed_result:
                    # Add the filename to the result for context
                    parsed_result['filename'] = resume_data['filename']
                    
                    # Pretty print the final JSON result
                    final_json_result = json.dumps(parsed_result, indent=4)
                    print("\n--- Final Parsed Result ---")
                    print(final_json_result)
                else:
                    print("Parsing failed: No data could be extracted.")
            else:
                print(f"Could not read resume file or the file is empty: {resume_file_path}")
        except Exception as e:
            print(f"An unexpected error occurred: {e}")

