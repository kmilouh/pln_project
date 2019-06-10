import nltk
import math
from nltk.tokenize import RegexpTokenizer
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords
from nltk.stem.porter import PorterStemmer
from nltk.stem import SnowballStemmer
from math import log10, sqrt
from collections import Counter
from datastore import DataIterator
from log_helper import LogHelper
import os
from os import system, name
import pickle


class Query:

    def __init__(self, str_json_file, logger: LogHelper, language='spanish', data_file='query_model.bin', load_model=False):
        self.logger = logger
        nltk.download("stopwords")
        nltk.download('punkt')
        nltk.data.load('nltk:tokenizers/punkt/spanish.pickle')
        if load_model:
            self.load(data_file)
            return

        self.stopWords = stopwords.words('spanish')

        if language == 'spanish':
            self.stemmer = SnowballStemmer('spanish')
        else:
            self.stemmer = PorterStemmer()

        self.tokenizer = RegexpTokenizer(r'[a-zA-Z]+')


        self.iterator = DataIterator(str_json_file) # Data.
        self.vectors = {}  # tf-idf vectors for all documents
        self.df = Counter()  # storage for document frequency
        self.tfs = {}  # permanent storage for tfs of all tokens in all documents
        self.lengths = Counter()  # used for calculating lengths of documents
        self.postings_list = {}  # posting list storage for each token in the corpus
        self.st_tokens = []
        for _id, _url, doc in self.iterator.data:
            doc = doc.lower()  # given code for reading files and converting the case
            tokens = self.tokenizer.tokenize(doc)  # tokenizing each document
            # removing stopwords and performing stemming
            tokens = [self.stemmer.stem(token)
                      for token in tokens if token not in self.stopWords]
            tf = Counter(tokens)
            self.df += Counter(list(set(tokens)))
            # making a copy of tf into tfs for that filename
            self.tfs[_id] = tf.copy()
            tf.clear()  # clearing tf so that the next document will have an empty tf

        # loop for calculating tf-idf vectors and lengths of documents
        for id in self.tfs:
            # initializing the tf-idf vector for each doc
            self.vectors[id] = Counter()
            length = 0
            for token in self.tfs[id]:
                # get_weigth calculates the weight of a token in a doc without normalization
                weight = self.get_weigth(id, token)
               # this is the weight of a token in a file
                self.vectors[id][token] = weight
                length += weight**2  # calculating length for normalizing later
            self.lengths[id] = math.sqrt(length)

        # loop for normalizing the weights
        for id in self.vectors:
            for token in self.vectors[id]:
                self.vectors[id][token] = self.vectors[id][token] / \
                    self.lengths[id]  # dividing weights by the document's length
                if token not in self.postings_list:
                    self.postings_list[token] = Counter()
                # copying the normalized value into the posting list
                self.postings_list[token][id] = self.vectors[id][token]

    # returns the weight of a token in a document without normalizing
    def get_weigth(self, id, token):
        idf = self.get_idf(token)
        # tfs has the logs of term frequencies of all docs in a multi-level dict
        return (1+log10(self.tfs[id][token]))*idf

    def get_idf(self, token):
        if self.df[token] == 0:
            return -1
        # len(tfs) returns no. of docs; df[token] returns the token's document frequency
        return log10(len(self.tfs)/self.df[token])



    def load(self, filename):
        try:
            with open(filename, "rb") as file:
                store_memory = pickle.load(file)
 
                self.stopWords = store_memory["stopWords"]
                self.stemmer = store_memory["stemmer"]
                self.tokenizer = store_memory["tokenizer"]
                self.iterator = store_memory["iterator"]
                self.vectors = store_memory["vectors"]
                self.df = store_memory["df"]
                self.tfs = store_memory["tfs"]
                self.lengths = store_memory["lengths"]
                self.postings_list = store_memory["postings_list"]
                self.st_tokens = store_memory["st_tokens"]
        except Exception as error:
            self.logger.error("Error Load Model {0}".format(str(error)))

    def save(self, filename):
        try:
            # self.logger.info("ModelBase {0} save to {1} ".format(
            #    self.message, filename))
            store_memory = {}
            store_memory["stopWords"] = self.stopWords
            store_memory["stemmer"] = self.stemmer
            store_memory["tokenizer"] = self.tokenizer
            store_memory["iterator"] = self.iterator
            store_memory["vectors"] = self.vectors
            store_memory["df"] = self.df
            store_memory["tfs"] = self.tfs
            store_memory["lengths"] = self.lengths
            store_memory["postings_list"] = self.postings_list
            store_memory["st_tokens"] = self.st_tokens

            with open(filename, "wb") as file:
                pickle.dump(store_memory, file)
        except Exception as error:
            self.logger.error("Error Save Model {0}".format(str(error)))

    def query(self, qstring):  # function that returns the best match for a query
        self.logger.info(" Query {0}".format(qstring))
        qstring = qstring.lower()  # converting the words to lower case
        qtf = {}
        qlength = 0
        flag = 0
        loc_docs = {}
        tenth = {}
        # initializing a counter for calculating cosine similarity b/w a token and a doc
        cos_sims = Counter()
        for token in qstring.split():
            if token in self.stopWords:
                continue
            # stemming the token using PorterStemmer
            token = self.stemmer.stem(token)
            # if the token doesn't exist in vocabulary,ignore it (this includes stopwords removal)
            if token not in self.postings_list:
                continue
            # if a token has idf = 0, all values in its postings list are zero. max 10 will be chosen randomly
            if self.get_idf(token) == 0:
                # to avoid that, we store all docs
                loc_docs[token], weights = zip(
                    *self.postings_list[token].most_common())
            else:
                # taking top 10 in postings list
                loc_docs[token], weights = zip(
                    *self.postings_list[token].most_common(50))
            tenth[token] = weights[-1]  # storing the upper bound of each token
            if flag == 1:
                # commondocs keeps track of docs that have all tokens
                commondocs = set(loc_docs[token]) & commondocs
            else:
                commondocs = set(loc_docs[token])
                flag = 1
            # updating term freq of token in query
            qtf[token] = 1+log10(qstring.count(token))
            # calculating length for normalizing the query tf later
            qlength += qtf[token]**2
        qlength = sqrt(qlength)
        for doc in self.vectors:
            cos_sim = 0
            for token in qtf:
                if doc in loc_docs[token]:
                    # calculate actual score if document is in top 10
                    cos_sim = cos_sim + (qtf[token] / qlength) * \
                        self.postings_list[token][doc]
                else:
                    # otherwise, calculate its upper bound score
                    cos_sim = cos_sim + (qtf[token] / qlength) * tenth[token]
            cos_sims[doc] = cos_sim
        max = cos_sims.most_common(50)  # seeing which doc has the max value
        ans, wght = zip(*max)
        try:
            if ans[0] in commondocs:
                answer = []
                # if doc has actual score, return score
                answer.append((ans[0], wght[0]))
                if len(ans) > 5:
                    for i in range(1, 5):
                        if ans[i] in commondocs:
                            answer.append((ans[i], wght[i]))

                return answer
            else:

                # if upperbound score is greater, return fetch more
                # return [("fetch more", 0)]
                answer = []
                answer.append((ans[0], wght[0]))
                if len(ans) > 5:
                    for i in range(1, 5):
                        answer.append((ans[i], wght[i]))
                return answer

        except UnboundLocalError:  # if none of the tokens are in vocabulary, return none
            return [("None", 0)]



#query = Query("es_data.json", data_file='query_model_es.bin', load_model=True,)
## query.save('query_model_es.bin')
#
#
#print(query.query("cosas judiciales"))
#print(query.query("requerimientos para información"))
