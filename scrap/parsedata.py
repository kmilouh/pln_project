import nltk
import string
from nltk.tokenize import word_tokenize
from log_helper import LogHelper


class Tokenizer(object):
    def __init__(self, logger, language, only_words=True):
        self.language = language
        self.logger = logger
        self.only_words = only_words
        # In some environments if don't put these lines maybe the library throw
        # an Exception
        nltk.data.load('nltk:tokenizers/punkt/spanish.pickle')
        #nltk.data.load('tokenizers/punkt/spanish.pickle')

    def tokenize(self, source):
        try:
            tokens = word_tokenize(source, self.language)
            filtered_tokens = [token for token in tokens if token.isalpha()]
            return list(filtered_tokens)

        except Exception as e:
            self.logger.error("Error parsing the text " + str(e))
            exit(-1)
