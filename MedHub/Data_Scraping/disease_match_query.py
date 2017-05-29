
# coding: utf-8

# In[87]:

from sklearn.feature_extraction.text import *
import numpy as np
from scipy.sparse import *
import cPickle
from sklearn.metrics.pairwise import linear_kernel
import re, string
import nltk
from sklearn.feature_extraction.stop_words import *
from collections import Counter


# In[88]:

# We need to import the same functions we used to vectorize, in order to repeat the process.

def gettext(text):

    """
    Parse text and remove JavaScript and references
    """
    return text.replace("To use the sharing features on this page, please enable JavaScript.", '').split("References")[0]

def tokenize_custom(text):
    """
    Tokenize text and return a non-unique list of tokenized words
    found in the text. Normalize to lowercase, strip punctuation,
    remove stop words, drop words of length < 3.
    """
    text = text.lower()
    subs = re.compile('[' + re.escape(string.punctuation) + '0-9\\r\\t\\n' + ']')
    processed_text = subs.sub(' ', text)
    words = nltk.word_tokenize(processed_text)
    words = [word for word in words if len(word) >=3 and word not in ENGLISH_STOP_WORDS]
    return words

def stemwords(words):
    """
    Given a list of tokens/words, return a new list with each word
    stemmed using a PorterStemmer.
    """
    stemmer = nltk.stem.porter.PorterStemmer()
    stemmed_list = [stemmer.stem_word(word) for word in words]
    return stemmed_list

def tokenizer_custom(text):
    return stemwords(tokenize_custom(text))


# In[89]:

# We have to write the user query to a text file because the transform function in tfidf expects RAW text documents. 

def write_query(query, file_dest = "Data_Scraping/user_query.txt"):
    f = open(file_dest, 'w')
    f.write(query)
    f.close()


# In[90]:

def load_vectorizer(filename):
    fp = open(filename, 'rb')
    clf = cPickle.load(fp)
    fp.close()
    return clf


# In[91]:

def load_sparse_csr(filename):
    loader = np.load(filename)
    return csr_matrix((  loader['data'], loader['indices'], loader['indptr']),
                         shape = loader['shape'])


# In[92]:

def load_disease_names(filename):
    f = open(filename, 'r')
    diseases = f.readlines()
    f.close()
    
    diseases = [disease.strip() for disease in diseases]
    
    return diseases


# In[93]:

def disease_match(query_file = "Data_Scraping/user_query.txt",
                  vectorizer_loc = "Data_Scraping/diseases_data/vectorizer.pk",
                  disease_matrix_loc = "Data_Scraping/diseases_data/disease_matrix.npz",
                 disease_names_loc = "Data_Scraping/diseases_data/diseases.txt"):
    
    diseases = load_disease_names(disease_names_loc)
    tfidf = load_vectorizer(vectorizer_loc)
    disease_matrix = load_sparse_csr(disease_matrix_loc)
    
    query_vector = tfidf.transform([query_file])
    cosine_similarities = linear_kernel(query_vector, disease_matrix).flatten()
    
    # Get the top 5 matches to diseases
    related_docs_indices = cosine_similarities.argsort()[:-6:-1]
    
    return [(diseases[idx].split('/')[-1], diseases[idx].split('/')[-2], round(cosine_similarities[idx],2)) for idx in related_docs_indices]





