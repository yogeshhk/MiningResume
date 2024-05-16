# Mining Resume

This repository contains programs to extract relevant fields from resumes and optionally build a knowledge graph (KG) for effective querying using a chatbot.

## Features

### Phase 0: Rule-based Extraction

- Extract important fields like name, email, phone, etc. from resumes based on patterns specified in a `config.xml` file.

#### How it works

- `parser.py` takes the config file and a directory containing text resumes as arguments.
- The config file specifies the fields to extract and their respective patterns.
- The parser logic is independent of the domain (resumes in this case), and changes or additions are made in the config file.
- Field extraction methods and patterns are defined in the config file.

#### Usage

- Prepare your own `config.xml` file similar to the provided one.
- For command-line execution, run `python parser_by_regex.py`.
- For a GUI, run `python main.py`.

### Phase 1: LLM-based Extraction

- Uses an open-source model from Hugging Face as a Large Language Model (LLM) and a prompt for extraction.

#### Usage

- Run `python parser_by_llm.py`.

## TODO

### Phase 2: 
- File to be created: `parser_by_spacy.py`
- Use spaCy-based Named Entity Recognition (NER) models for extraction.
- Build custom NER models if necessary. Data from `rijaraju repo` is at `data\rijaraju_repo_resume_ner_training_data.json`
- Add spaCy Matcher logic if needed.
- Output is json of key-value pairs, where Key is NER type and value is specific to the resume-person.
- Also extract relationships values, it `Education` as key and value as say `CoEP`, its date range etc.

### Phase 3: 
- File to be created: `build_kg.py`
- Build a Knowledge Graph (KG) based on the extractions.
- Nodes can represent entities like Person, Organizations, Skills, etc., and edges can represent relationships like "educated_in," "programs_in," etc.
- Central person-node can have person specific attributes, but other nodes like `Autodesk` or `CoEP` should not have, as other resume-person may also refer them. Resume-person specific attributes should be on edge from `Yogesh` to `CoEP` like date range, branch etc.
- Nodes like `Python`, `NLP` will be common and can come from different company nodes, like `Icertis`, `Intuit` etc.
- Schema design is critical as it decides which extractions can be NODES, EDGES and attributes on them.
- Follow standard schema like schema.org or DBpedia for resume extraction.
- Represent the KG initially in networkx format and later in Neo4j.
- Build a Streamlit app to upload resumes and visualize the KG or use Neo4j.

### Phase 4: 
- File to be created: `resume_chatbot.py`
- Use query languages like SPARQL or Cypher, depending on the KG's residence.
- Leverage LLMs to convert natural language English queries into SPARQL or Cypher.
- Build a Streamlit chatbot for querying the KG. See if you can visualize the built KG.
- Deploy the chatbot on Streamlit-Shares for limited (e.g., 5 resumes) public access.

### Phase 5: Production

- Build an end-to-end system with payment integration as a pay-per-use MicroSaaS.
- Consider deploying on cloud platforms like VertexAI or Azure.

## Disclaimer

- The author (yogeshkulkarni@yahoo.com) provides no guarantee for the program's results. It is a fun script with room for improvement. Do not depend on it entirely.

Copyright (C) 2017 Yogesh H Kulkarni
