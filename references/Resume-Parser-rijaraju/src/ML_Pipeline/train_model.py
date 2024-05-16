import spacy
import random
import matplotlib.pyplot as plt
import warnings


def build_spacy_model(train, model):

    if model is not None:
        nlp = spacy.load(model)  # load existing spaCy model
        print("Loaded model '%s'" % model)
    else:
        nlp = spacy.blank("en")  # create blank Language class
        print("Created blank 'en' model")

    TRAIN_DATA = train
    # create the built-in pipeline components and add them to the pipeline
    # nlp.create_pipe works for built-ins that are registered with spaCy
    if "ner" not in nlp.pipe_names:
        ner = nlp.create_pipe("ner")
        # nlp.add_pipe(ner, last=True)
        nlp.add_pipe("ner", last=True)
    else:
        ner = nlp.get_pipe("ner")

    # add labels
    for _, annotations in TRAIN_DATA:
        for ent in annotations.get("entities"):
            ner.add_label(ent[2])

    # get names of other pipes to disable them during training
    other_pipes = [pipe for pipe in nlp.pipe_names if pipe != "ner"]
    with nlp.disable_pipes(*other_pipes), warnings.catch_warnings():  # only train NER
        warnings.filterwarnings("ignore", category=UserWarning, module="spacy")
        if model is None:
            optimizer = nlp.begin_training()
        for itn in range(2):
            # train for 50 iteration
            print("Starting iteration " + str(itn))
            random.shuffle(TRAIN_DATA)
            losses = {}
            for text, annotations in TRAIN_DATA:
                try:
                    nlp.update(
                        [text],  # batch of texts
                        [annotations],  # batch of annotations
                        drop=0.2,  # dropout - make it harder to memorise data
                        sgd=optimizer,  # callable to update weights
                        losses=losses,
                    )
                except Exception as e:
                    pass
            print(losses)
            # plt.scatter(itn, losses["ner"])
            # plt.ylabel("ner_loss")
            # plt.xlabel("Iterations")
            # plt.show()

    nlp.to_disk("nlp_model")
    # plt.savefig("loss.png")
    return nlp
