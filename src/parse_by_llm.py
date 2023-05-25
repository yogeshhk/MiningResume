import os
from langchain.chains import LLMChain, SimpleSequentialChain  # import LangChain libraries
from langchain.llms import OpenAI, HuggingFaceHub  # import OpenAI model
from langchain.prompts import PromptTemplate  # import PromptTemplate
from file_operations import read_data, DATA_FOLDER
import json
from collections import OrderedDict

# Use any one of the following
llm = HuggingFaceHub(repo_id="bigscience/bloom", model_kwargs={"temperature": 1e-10})

# llm = OpenAI(
#     model_name="text-curie-001",
#     temperature=0,
# )

attributes_list = ["Name", "Email", "Address", "Phone Number", "Objective", "Skills", "Employment History",
                   "Education History", "Accomplishments"]


def parse_document_by_llm(text):
    parsed_items_dict = OrderedDict()
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
        response = chain.run({'resume': text, 'attribute': attr})
        parsed_items_dict[attr] = response.strip()
    return parsed_items_dict


if __name__ == "__main__":
    final_result = []

    docs_dicts = read_data(DATA_FOLDER)

    for doc_dict in docs_dicts:
        result = parse_document_by_llm(doc_dict['resume_text'])
        result['filename'] = doc_dict['filename']
        final_result.append(result)

    jason_result = json.dumps(final_result, indent=4)
    print("Final Result:\n {}".format(jason_result))
