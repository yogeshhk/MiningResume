# Mining Resume

This repository contains programs related to extracting relevant fields from resumes. It (optionally) can build a knowledge graph (KG) from the extraction. On top of KG, it will more effective to build a chatbot for queries releated to all the ingested resumes.

## Phase 0: Rule-based extraction
Extracting certain important fields from a resume like name, email, phone,  etc. based on a `config.xml` which specifies fields to extract along with the patterns to look for those fields, respectively.

### How it works:
* parser.py take the config file as well as the directory having text resumes, as arguments.
* As all the domain (resume, here) is specified in the config file, any changes or addition to logic is done only the the config file. 
* (Ideally) parser logic is independent and thus should not need any change. Atleast thats the idea!!
* Certain field extraction methods are specified in the config file which are used to parse based on the pattern specified.

### How to run:
* Prepare your own config.xml similar to the given one. 
* For command line, run "python parser_by_regex.py"
* For GUI, run "python main.py"


## Phase 1: LLM-based extraction
Open source model from Hugging Face is used as LLM (Large Language Model) and a prompt is used for extraction.

### How to Run:
* Run "python parser_by_llm.py"

## ToDos
- Phase 2: `parser_by_spacy.py`
	- Use spaCy based NER (Named Entity Recognition) models to do the extraction
	- Build custom NER models if necessary.
	- Add spaCy Matcher logic if needed
- Phase 3: `build_kg.py`
	- Build Knowledge Graph (KG) based on the extractions
	- Nodes can be Person, Orgs, Skills, etc and Edges can be 'educated_in', 'programs_in', etc. See if any standard schema is available at schema.org or DBpedia for resume extraction. E.g. One triplet could be ('Yogesh', 'bachelors_degree', 'CoEP'). 'bachelors_degree' can have attributes like 'date_range', 'branch', 'marks' etc. 'Yogesh' can have attributes like 'address', 'mobile', etc.
	- KG can be initially in networkxx form and later can be in Neo4j form.
	- Build Streamlit app to upload a resume and show the KG visually, or in Neo4j
- Phase 4: `resume_chatbot.py`
	- Query language can be SparQL or Cypher ending on KG's residence.
	- LLMs can be used to convert Natural Language English queries in to SparQL or Cypher language
	- A WoW streamlit chatbot can be built
	- It can be deployed on StreamLit-Shares for peeople to try out. Limited to 5 resumes, say.
- Phase 5: Production
	- Build such system, end-to-end along with payments, as a pay-per-use MicroSaaS
	- It can also be native to VertexAI or Azure like cloud also.


## Disclaimer:
* Author (yogeshkulkarni@yahoo.com) gives no guarantee of the results of the program. It is just a fun script. Lot of improvements are still to be made. So, don’t depend on it at all.

Copyright (C) 2017 Yogesh H Kulkarni
