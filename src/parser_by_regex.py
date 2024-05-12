import json
import re
import xml.etree.cElementTree as ET
from collections import OrderedDict

from file_operations import read_data, DATA_FOLDER, CONFIG_FILE


def univalue_extractor(resume_text, section, sub_terms_dict, parsed_items_dict):
    retval = OrderedDict()
    get_section_lines = parsed_items_dict["Sections"].get(section)
    section_doc = "\n".join(get_section_lines)
    if section_doc != "NA":
        for node_tag, pattern_list in sub_terms_dict.items():
            for pattern in pattern_list:
                regex_pattern = re.compile(r"{}".format(pattern))
                match = regex_pattern.search(section_doc)
                if match is not None and len(match.groups()) > 0 and match.group(1) != "":
                    retval[node_tag] = match.group(1)
                    break
    return retval


# Section Information value extractor
def section_value_extractor(resume_text, section, sub_terms_dict, parsed_items_dict):
    retval = OrderedDict()
    single_section_lines = parsed_items_dict["Sections"].get(section)
    for line in single_section_lines:
        for node_tag, pattern_string in sub_terms_dict.items():
            pattern_list = re.split(r",|:", pattern_string[0])
            matches = [pattern for pattern in pattern_list if pattern in line]
            if len(matches):
                info_string = ", ".join(list(matches)) + " "
                numeric_values = re.findall(r"([\d']{4})\s?-?(\d{2}[^\w+])?", line)
                if len(numeric_values):
                    value_list = list(numeric_values[0])
                    info_string = info_string + "-".join([value for value in value_list if value != ""])
                retval[node_tag] = info_string
                break
    return retval


# Find if new section has started
def is_new_section(line, sub_terms_dict):
    new_section = ""
    first_word_of_line = ""
    regex_pattern = re.compile(r"^[\s]?(\w+)?[:|\s]")
    match = regex_pattern.search(line)
    if match is not None and len(match.groups()) > 0 and match.group(1) != "":
        first_word_of_line = match.group(1)
        if first_word_of_line is not None:
            for node_tag, pattern_list in sub_terms_dict.items():
                for pattern in pattern_list:
                    if first_word_of_line in pattern:
                        new_section = node_tag
    return new_section


# Segmentation into sections, a sentence collector
'''
Read line by line
Get first token, send it to section_finder(token, sub_term_dict),returns section node_tag or ""
Once section is found, make it current_section, and add sentences to it till, a next section is found
'''


def section_extractor(resume_text, section, sub_terms_dict, parsed_items_dict):
    retval = OrderedDict()
    if resume_text != "NA":
        current_section = ""
        lines = re.split(r'[\n\r]+', resume_text)
        for line in lines:
            new_section = is_new_section(line, sub_terms_dict)
            if new_section != "":
                current_section = new_section
                continue
            retval[current_section] = retval.get(current_section, []) + [line]

    return retval


# read config and store in equivalent internal list-of-dictionaries structure. No processing-parsing.
def read_config(configfile):
    tree = ET.parse(configfile)
    root = tree.getroot()

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
    jason_result = json.dumps(config_element, indent=4)
    # print("Specifications:\n {}".format(jason_result))
    return config_element


# Processes document as per specifications in config and returns result in dictionary
def parse_document(resume_text, resume_config):
    parsed_items_dict = OrderedDict()

    for term in resume_config:
        term_name = term.get('Term')
        extraction_method = term.get('Method')
        extraction_method_ref = globals()[extraction_method]
        section = term.get("Section")  # Optional
        sub_term_dict = OrderedDict()
        list_of_paras = list(term.items())
        for node_tag, pattern_list in list_of_paras[3:]:
            sub_term_dict[node_tag] = pattern_list
        parsed_items_dict[term_name] = extraction_method_ref(resume_text, section, sub_term_dict, parsed_items_dict)

    # key of section extractors is not to be printed
    del parsed_items_dict["Sections"]
    return parsed_items_dict


if __name__ == "__main__":

    final_result = []

    config = read_config(CONFIG_FILE)
    docs_dicts = read_data(DATA_FOLDER)

    for doc_dict in docs_dicts:
        result = parse_document(doc_dict['resume_text'], config)
        result['filename'] = doc_dict['filename']
        final_result.append(result)

    jason_result = json.dumps(final_result, indent=4)
    print("Final Result:\n {}".format(jason_result))
