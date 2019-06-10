#!/usr/bin/python3
# -*- coding: utf-8 -*-
"""This is Query for Twitter FAQ"""

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
from query import Query
import os
from os import system, name
import pickle


# Logs
loghelper = LogHelper()
logger = loghelper.getLogger("default")
logger.info("Start App")

query = Query("es_data.json",logger, data_file='query_model_es.bin', load_model=False,)
# query.save('query_model_es.bin')


print(query.query("cosas judiciales"))
print(query.query("requerimientos para información"))
print(query.query("información del usuario"))
print(query.query("enviar imágenes"))

