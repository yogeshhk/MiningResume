# NLP_Resume_ParserNLP Project to Build a Resume Parser in Python using Spacy


## NLP Tools and Techniques Used:
### Tokenization

It is the process of splitting textual data into different pieces called tokens. One can either break a sentence into tokens of words or characters; the choice depends on the problem one is interested in solving. It is usually the first step that is performed in any NLP project, and the same will be the case with this resume parser using NLP project. Tokenization helps in further steps of an NLP pipeline which usually involves evaluating the weights of all the words depending on their significance in the corpus.



### Lemmatization

The larger goal of this resume parsing python application is to decode the semantics of the text. For that, the form of the verb that is used does not have a significant impact. Therefore, lemmatization is used to convert all the words into their root form, called 'lemma.' For example, 'drive,' 'driving, 'drove' all have the same lemma 'drive.'



### Parts-of-Speech Tagging

If you consider the word "Apple," it can have two meanings in a sentence. Depending on whether it has been used as a proper noun or a common noun, you will understand whether one is discussing the multinational tech company or the fruit. This CV parser python project will understand how POS Tagging is implemented in Python.



### Stopwords Elimination

Stopwords are the words like 'a', 'the,' 'am', 'is', etc., that hardly add any meaning to a sentence. These words are usually deleted to save on processing power and time. In their CV, an applicant may submit their work experience in long paragraphs with many stopwords. For such cases, it becomes essential to know how to extract experience from a resume in python, which you will learn in this project.



### SpaCy

SpaCy is a library in Python that is widely used in many NLP-based projects by data scientists as it offers quick implementation of techniques mentioned above. Additionally, one can use SpaCy to visualize different entities in text data through its built-in visualizer called displacy. Furthermore, SpaCy supports the implementation of rule-based matching, shallow parsing, dependency parsing, etc. This NLP resume parser project will guide you on using SpaCy for Named Entity Recognition (NER).



### #OCR using TIKA

Used Apache Tika, an open-source library for implementing OCR in this project. OCR stands for optical character recognition. It involves converting images into text and will be used in this resume extraction python project for decoding text information from the PDF files. The textual data is processed using various NLP methods to extract meaningful information.

