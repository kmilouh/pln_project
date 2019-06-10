# --------------------------------------------------------------------------------
# Librerías
import nltk
import string
from nltk.tokenize import word_tokenize
from log_helper import LogHelper

# --------------------------------------------------------------------------------
# Clase que parsea el texto con nltk haciendolo usable para otras tareas
class Tokenizer(object):
    def __init__(self, logger, language, only_words=True):
        self.language = language
        self.logger = logger
        self.only_words = only_words
        # Necesario en algunos entornos para no crear una excepción
        nltk.data.load('nltk:tokenizers/punkt/spanish.pickle')

    def tokenize(self, source):
        try:
            tokens = word_tokenize(source, self.language)
            filtered_tokens = [token for token in tokens if token.isalpha()]
            return list(filtered_tokens)

        except Exception as e:
            self.logger.error("Error parsing the text " + str(e))
            exit(-1)
