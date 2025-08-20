# Mining Resume

This project provides a powerful toolkit for extracting structured information from resume files. It supports various file formats and offers two distinct parsing methodologies: a highly customizable rule-based approach using Regex, and a modern, AI-driven approach using a Large Language Model (LLM).

The primary objective is to convert unstructured resume text from formats like .pdf, .docx, and .txt into a clean, structured JSON output.

## **✨ Features**

* **Multi-Format Support**: Parses resumes from `.pdf`, `.docx`, and `.txt` files seamlessly.  
* **Dual Parsing Engines**:  
  * **Regex-Based Parser**: Offers granular control over data extraction through a simple and powerful XML configuration. Ideal for resumes with consistent formatting.  
  * **LLM-Based Parser**: Leverages a pre-trained Large Language Model (`google/flan-t5-large`) to intelligently identify and extract information, adapting well to varied resume layouts.  
* **Structured Output**: Consistently outputs extracted data in a clean, easy-to-use JSON format.  
* **Customizable Extraction**:  
  * For the Regex parser, you can define your own extraction rules in regex\_config.xml without changing any Python code.  
  * For the LLM parser, the list of attributes to be extracted can be easily modified in the script.

## **📂 Src Project Structure**
```
.  
├── data/  
│   └── YogeshKulkarniLinkedInProfile.pdf  \# Place your resume files here  
├── llm\_resume\_parser.py                   \# Main script for LLM-based parsing  
├── regex\_resume\_parser.py                 \# Main script for Regex-based parsing  
├── regex\_config.xml                       \# Configuration file for the Regex parser  
└── README.md
```
## **🚀 Getting Started**

Follow these instructions to set up and run the project on your local machine.

### **Prerequisites**

* Python 3.8+  
* For the LLM Parser: A Hugging Face API Token

### **Installation**

1. **Clone the repository:**  
```
   git clone \<your-repository-url\>  
   cd \<your-repository-name\>
```
2. **Create and activate a virtual environment (recommended):**  
```
   \# For Windows  
   python \-m venv venv  
   .\\venv\\Scripts\\activate

   \# For macOS/Linux  
   python3 \-m venv venv  
   source venv/bin/activate
```
3. Install the required dependencies:  
   Create a requirements.txt file with the following content:  
   ```
   PyPDF2  
   docx2txt  
   langchain  
   langchain-community  
   langchain-huggingface  
   transformers  
   torch  
   sentencepiece
   ```

   Then, install the packages: 
```   
   pip install \-r requirements.txt
```

4. Set up Environment Variables (for LLM Parser):  
   The LLM parser requires a Hugging Face API token to interact with the model hub.  
   Create a .env file in the root directory and add your token:  
   ```
   HUGGINGFACEHUB\_API\_TOKEN="your\_hf\_token\_here"
   ```

   The script will load this variable automatically.

## **🏃 How to Run**

Before running either parser, place the resume files you want to process inside the data folder. The scripts are pre-configured to run with a sample file named `YogeshKulkarniLinkedInProfile.pdf`.

### **1\. Regex-Based Parser**

This method uses the patterns defined in regex\_config.xml to extract information.

* **Customize (Optional)**: Open regex\_config.xml to review or modify the regex patterns for each field you want to extract.  
* **Run the script**:  
```
  python regex\_resume\_parser.py
```
  The script will process the sample resume and print the extracted structured data as a JSON object to the console.

### **2\. LLM-Based Parser**

This method uses a Hugging Face model to understand the context and extract the required fields.

* **Ensure your API token is set** as described in the installation steps.  
* **Run the script**:  
```
  python llm\_resume\_parser.py
```
  The script will download the model (on the first run), process the sample resume, and print the extracted data in JSON format to the console.

## **⚙️ Configuration**

The **Regex-Based Parser** is controlled by the regex\_config.xml file. This file allows you to define:

* **Terms**: The specific fields to extract (e.g., Name, Email, PhoneNumber).  
* **Methods**: The extraction logic to use (e.g., univalue\_extractor for single values).  
* **Patterns**: The specific regex patterns used to find the information.

This design allows for easy adaptation to different resume formats or extraction requirements without modifying the Python source code.

## **📜 Disclaimer**

The author provides no guarantee for the program's results. This is a utility script with room for improvement. Do not depend on it entirely for critical applications.

Copyright (C) 2025 Yogesh H Kulkarni