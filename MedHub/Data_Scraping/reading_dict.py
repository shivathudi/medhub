from collections import defaultdict
import pickle

def dd():
    return defaultdict(str)

def read_dict(file_name):
    return pickle.load(open(file_name, "rb"))

test = read_dict('disease_dictionaries/disease_dict_A_to_z.p')
print test['narcolepsy']