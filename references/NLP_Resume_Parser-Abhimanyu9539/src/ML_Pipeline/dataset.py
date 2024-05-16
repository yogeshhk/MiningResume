import utils

# function to read the data
def read_data():
    train=utils.convert_json_to_spacy("") # train file

    test=utils.convert_json_to_spacy("")     # test file

    return train,test
