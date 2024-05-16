import spacy
from ML_Pipeline import text_extractor

# function for prediction
def predict(path):
    #output={}
    nlp=spacy.load("model") # load the model
    test_text=text_extractor.convert_pdf_to_text(path) # convert
    for text in test_text:
        text=text.replace('\n',' ') # replace
        doc = nlp(text)
        for ent in doc.ents:
            print(f'{ent.label_.upper():{30}}-{ent.text}')
            #output[ent.label_.upper()]=ent.text
    #return output
        
