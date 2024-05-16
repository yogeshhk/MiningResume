import json
import random
import spacy

# function to check the existing model
def check_existing_model(model_name): # take model name as an input
# pass this in a try except block
    try: 
        nlp=spacy.load(model_name)
        print("Model Exists. Updating the model")
        return model_name
    except Exception as e: # exception
        print("Model by this name does not exist. Building a new one")
        return None




