import json
import random
import spacy

def check_existing_model(model_name):

    try: 
        nlp=spacy.load(model_name)
        print("Model Exists. Updating the model")
        return model_name
    except Exception as e:
        print("Model by this name does not exist. Building a new one")
        return None




