import os, sys
import xml.etree.cElementTree as ET
import re
from collections import OrderedDict
import json

## Reader: ToDo: use another file reader.py to import various formats, convert to txt and clean docs, here, below
def read_document(filepath):
    f = open(filepath)
    raw = f.read()
    f.close()
    return raw

### Extraction Methods, called by string "name" as specified in config

# Regex based single value extractor
def univalue_extractor( document, section, subterms_dict, parsed_items_dict ):
    retval = OrderedDict()
    get_section_lines = parsed_items_dict["Sections"].get(section)
    section_doc = "\n".join(get_section_lines)
    if section_doc != "NA":
        for node_tag, pattern_list in subterms_dict.items():
            for pattern in pattern_list:
                regex_pattern = re.compile(r"{}".format(pattern))
                match = regex_pattern.search(section_doc)
                if match != None and len(match.groups()) > 0 and match.group(1) != "":
                    retval[node_tag] = match.group(1)
                    break
    return retval

# Section Information value extractor
def section_value_extractor( document, section, subterms_dict, parsed_items_dict ):
    retval = OrderedDict()
    single_section_lines = parsed_items_dict["Sections"].get(section)
    for line in single_section_lines:
        for node_tag, pattern_string in subterms_dict.items():
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
def is_new_section(line,subterms_dict):
    new_section = ""
    first_word_of_line = ""
    regex_pattern = re.compile(r"^[\s]?(\w+)?[:|\s]")
    match = regex_pattern.search(line)
    if match != None and len(match.groups()) > 0 and match.group(1) != "":
        first_word_of_line = match.group(1)
        if first_word_of_line != None:
            for node_tag, pattern_list in subterms_dict.items():
                for pattern in pattern_list:
                    if first_word_of_line in pattern:
                        new_section = node_tag
    return new_section

# Segementation into sections, a sentence collector
'''
Read line by line
Get first token, send it to section_finder(token, subterm_dict),returns section node_tag or ""
Once section is found, make it current_section, and add sentences to it till, a next section is found
'''
def section_extractor( document, section, subterms_dict,parsed_items_dict ):
    retval = OrderedDict()
    if document != "NA":
        current_section = ""
        lines = re.split(r'[\n\r]+', document)
        for line in lines:
            new_section = is_new_section(line, subterms_dict)
            if new_section != "":
                current_section = new_section
                continue
            retval[current_section] = retval.get(current_section, []) + [line]

    return retval

#read config and store in equivalent internal list-of-dictionaries structure. No processing-parsing.
def read_config( configfile ):

    tree = ET.parse(configfile)
    root = tree.getroot()

    config = []
    for child in root:
        term = OrderedDict()
        term["Term"] = child.get('name', "")
        for level1 in child:
            term["Method"] = level1.get('name', "")
            term["Section"] = level1.get('section', "")
            for level2 in level1:
                term[level2.tag] = term.get(level2.tag, []) + [level2.text]

        config.append(term)
    jason_result = json.dumps(config, indent=4)
    # print("Specifications:\n {}".format(jason_result))
    return config

# Processes docuemtn as per specifications in config and returns result in dictionary
def parse_document(document, config):
    parsed_items_dict = OrderedDict()

    for term in config:
        term_name = term.get('Term')
        extraction_method = term.get('Method')
        extraction_method_ref = globals()[extraction_method]
        section = term.get("Section") # Optional
        subterms_dict = OrderedDict()
        for node_tag, pattern_list in term.items()[3:]:
            subterms_dict[node_tag] = pattern_list
        parsed_items_dict[term_name] = extraction_method_ref(document, section, subterms_dict, parsed_items_dict)

    # key of section extractors is not to be printed
    del parsed_items_dict["Sections"]
    return parsed_items_dict

###### MAIN ##############

if len(sys.argv) != 3:
    print("Usage: parser <configfile> <datafilesfolder>")
    sys.exit(0)

final_result = []

configfile = "./" + sys.argv[1]
config = read_config(configfile)

datafilesdir = "./" + sys.argv[2] + "/"
docs = os.listdir(datafilesdir)

for filename in docs:
    if os.path.isfile(datafilesdir + filename):
        document = read_document(datafilesdir + filename)
        result = parse_document(document, config)
        final_result.append(result)

jason_result = json.dumps(final_result, indent=4)
print("Final Result:\n {}".format(jason_result))


