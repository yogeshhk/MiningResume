import spacy
import random
from spacy.util import minibatch, compounding

# function to train the model
def build_spacy_model(train,model):

    if model is not None:
        nlp = spacy.load(model)  # load existing spaCy model
        print("Loaded model '%s'" % model)
    else:
        nlp = spacy.blank("en")  # create blank Language class
        print("Created blank 'en' model")

    TRAIN_DATA =train
    #nlp = spacy.blank('en')  # create blank Language class
    # create the built-in pipeline components and add them to the pipeline
    # nlp.create_pipe works for built-ins that are registered with spaCy
    if 'ner' not in nlp.pipe_names:
        ner = nlp.create_pipe('ner')
        nlp.add_pipe('ner', last=True)
    else:
        ner = nlp.get_pipe("ner")
       

    # add labels
    for _, annotations in TRAIN_DATA:
         for ent in annotations.get('entities'):
            ner.add_label(ent[2])

    # get names of other pipes to disable them during training
    other_pipes = [pipe for pipe in nlp.pipe_names if pipe != 'ner']
    with nlp.disable_pipes(*other_pipes):  # only train NER
        if model is None:
            optimizer = nlp.begin_training()
        for itn in range(2):
            print("Starting iteration " + str(itn))
            # random.shuffle(TRAIN_DATA)
            # losses = {}
            # batches = minibatch(TRAIN_DATA, size=compounding(8., 32., 1.001))
            # for batch in batches:
            #     texts, annotations = zip(*batch)
            #     nlp.update(texts, annotations, sgd=optimizer, 
            #                losses=losses)
            # print('Losses', losses)
            random.shuffle(TRAIN_DATA)
            losses = {}
            for text, annotations in TRAIN_DATA:
                    try:
                        nlp.update(
                            [text],  # batch of texts
                            [annotations],  # batch of annotations
                            drop=0.2,  # dropout - make it harder to memorise data
                            sgd=optimizer,  # callable to update weights
                            losses=losses)
                    except Exception as e:
                        pass
            print(losses)
    
    nlp.to_disk("model")
    return nlp