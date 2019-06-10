#!/usr/bin/python3
# -*- coding: utf-8 -*-

# --------------------------------------------------------------------------------
# Librerías
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
from json import dumps
from os import system, name
import pickle
from bottle import route, response, static_file, run, debug
from pathlib import Path
import nltk

# --------------------------------------------------------------------------------
nltk.download("stopwords")
nltk.download('punkt')
nltk.data.load('nltk:tokenizers/punkt/spanish.pickle')

# --------------------------------------------------------------------------------
# Archivos de registro
loghelper = LogHelper()
logger = loghelper.getLogger("default")
logger.info("Start App")

# --------------------------------------------------------------------------------
# Cargamos el modelo de español e inglés que vamos a usar, si es la primera vez
# que se ejecuta se crea automáticamente
if os.path.exists('query_model_es.bin'):
    query_es = Query("es_data.json",logger, data_file='query_model_es.bin', load_model=True)
else:
    query_es = Query("es_data.json",logger, data_file='query_model_es.bin', load_model=False)
    query_es.save('query_model_es.bin')
if os.path.exists('query_model_en.bin'):
    query_en = Query("en_data.json",logger,language='english', data_file='query_model_en.bin', load_model=True)
else:
    query_en = Query("en_data.json",logger,language='english', data_file='query_model_en.bin', load_model=False)
    query_en.save('query_model_en.bin')

model = []
model.append(query_es)
model.append(query_en)

info = [{"name": "Modelo en Español", "value": "Modelo en Español, datos..."},
        {"name": "Modelo en Ingles", "value": "Modelo en Ingles, datos Eng..."},
        ]

# --------------------------------------------------------------------------------
# Función usada para crear un servidor local y ejecutar la aplicación diseñada
def runServer(httpPort=9000):

    debug(True)
    global logger

    @route('/')
    def send_static_index():
        logger.info("Request index.html")
        return static_file("index.html", root='./static/')

    @route('/models')
    def send_models():
        return dumps(info, ensure_ascii=False).encode('utf8')

    @route('/query/<modelbase>/<length>/<end>/<words>')
    def send_autocomplete(modelbase, length, end, words):
        response.content_type = 'application/json'
        modelbase = int(modelbase)
        end = int(end)

        if modelbase < 0 or modelbase > len(model):
            message_error = "ModelBase Number {0} not exist".format(modelbase)
            logger.error(message_error)
            ret = {"Error": message_error}
            return dumps(ret, ensure_ascii=False).encode('utf8')
        try:
            wordList = words.split("$")
            query_str = " ".join(wordList)
            ret = model[modelbase].query(query_str)
            return dumps({"items": ret}, ensure_ascii=False).encode('utf8')
        except Exception as ex:
            logger.exception("Exception: {0}".format(str(ex)))
            ret = {"Error": str(ex)}
            return dumps(ret, ensure_ascii=False).encode('utf8')

    @route('/<filename:path>')
    def send_static(filename):
        logger.info("Request {0}".format(filename))
        return static_file(filename, root='./static/')

    run(host='localhost', port=httpPort)

# --------------------------------------------------------------------------------
runServer()
