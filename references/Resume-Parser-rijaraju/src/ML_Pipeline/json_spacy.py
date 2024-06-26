import json
import os
import json
import random
import logging
from sklearn.metrics import classification_report
from sklearn.metrics import precision_recall_fscore_support
# from spacy.gold import GoldParse
from spacy.scorer import Scorer


def convert_data_to_spacy(JSON_FilePath):
    try:
        training_data = []
        lines = []
        with open(JSON_FilePath, "r", encoding="utf-8") as f:
            lines = f.readlines()

        for line in lines:
            data = json.loads(line)
            text = data["content"]
            entities = []
            for annotation in data["annotation"]:
                # only a single point in text annotation.
                point = annotation["points"][0]
                labels = annotation["label"]
                # handle both list of labels or a single label.
                if not isinstance(labels, list):
                    labels = [labels]

                for label in labels:
                    entities.append((point["start"], point["end"] + 1, label))

            training_data.append((text, {"entities": entities}))

        return training_data
    except Exception as e:
        logging.exception(
            "Unable to process " + JSON_FilePath + "\n" + "error = " + str(e)
        )
        return None

