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

### Phase 2: `parser_by_spacy.py`

- Use spaCy-based Named Entity Recognition (NER) models for extraction.
- Build custom NER models if necessary.
- Add spaCy Matcher logic if needed.

### Phase 3: `build_kg.py`

- Build a Knowledge Graph (KG) based on the extractions.
- Nodes can represent entities like Person, Organizations, Skills, etc., and edges can represent relationships like "educated_in," "programs_in," etc.
- Follow standard schemas like schema.org or DBpedia for resume extraction.
- Represent the KG initially in networkx format and later in Neo4j.
- Build a Streamlit app to upload resumes and visualize the KG or use Neo4j.

### Phase 4: `resume_chatbot.py`

- Use query languages like SPARQL or Cypher, depending on the KG's residence.
- Leverage LLMs to convert natural language English queries into SPARQL or Cypher.
- Build a Streamlit chatbot for querying the KG.
- Deploy the chatbot on Streamlit-Shares for limited (e.g., 5 resumes) public access.

### Phase 5: Production

- Build an end-to-end system with payment integration as a pay-per-use MicroSaaS.
- Consider deploying on cloud platforms like VertexAI or Azure.

## Disclaimer

- The author (yogeshkulkarni@yahoo.com) provides no guarantee for the program's results. It is a fun script with room for improvement. Do not depend on it entirely.

Copyright (C) 2017 Yogesh H Kulkarni
