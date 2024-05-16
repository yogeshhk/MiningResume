import spacy
from ML_Pipeline import text_extractor


def predict(path):
    output = {}
    nlp = spacy.load("nlp_model")
    test_text = text_extractor.convert_pdf_to_text(path)
    for text in test_text:
        text = text.replace("\n", " ")
        doc = nlp(text)
        print("extraction: ", doc.ents)
        for ent in doc.ents:
            print(f"{ent.label_.upper():{30}}-{ent.text}")
            output[ent.label_.upper()] = ent.text
    return output
