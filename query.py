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
import os
from os import system, name
import pickle

# --------------------------------------------------------------------------------
# Clase que nos permite obtener la respuesta a la consulta deseada
class Query:
    def __init__(self, str_json_file, logger: LogHelper, language='spanish', data_file='query_model.bin', load_model=False):
        self.logger = logger

        # True si vamos a cargar y usar un modelo creado
        if load_model:
            self.load(data_file)
            return

        # Diferentes configuraciones en función del lenguaje a usar
        if language == 'spanish':
            self.stopWords = stopwords.words('spanish')
            self.stemmer = SnowballStemmer('spanish')
        else:
            self.stopWords = stopwords.words('english')
            self.stemmer = PorterStemmer()

        # Cargamos el tokenizador a usar
        self.tokenizer = RegexpTokenizer(r'[a-zA-Z]+')

        # Iterador que nos servirá para recorrer el archivo JSON
        self.iterator = DataIterator(str_json_file) 

        # Vector TF-IDF para todos los documentos
        self.vectors = {} 

        # Contador de frecuencia para el documento
        self.df = Counter() 

        # Almacenamiento permanente en todos los documentos para todos
        #  los TF-IDF de todos los tokens 
        self.tfs = {} 

        # Se usara para obtener la longitud de los documentos
        self.lengths = Counter()

        # Lista de publicaciones para cada token del corpus del escrito
        self.postings_list = {} 

        self.st_tokens = []

        for _id, _url, doc in self.iterator.data:
            # Convertimos a minúsculas el documento leido
            doc = doc.lower() 

            # Obtenemos los tokens de dicho documento
            tokens = self.tokenizer.tokenize(doc)  

            # Eliminamos las "stopwords" y derivaciones
            tokens = [self.stemmer.stem(token)
                      for token in tokens if token not in self.stopWords]

            tf = Counter(tokens)
            self.df += Counter(list(set(tokens)))

            # Hacemos una copia del TF-IDF en el almacenador permanente
            # de TF-IDF para este archivo
            self.tfs[_id] = tf.copy()

            # Limpiamos los TF-IDF para el siguiente documento
            tf.clear()

        # Bucle para calcular los vectores TF-IDF y sus longitudes de los documentos
        for id in self.tfs:
            # Inicializamos el vector TF-IDF para cada documento
            self.vectors[id] = Counter()

            length = 0
            for token in self.tfs[id]:
                # Calculamos los pesos de un token en el documento sin normalización
                weight = self.get_weigth(id, token)
                self.vectors[id][token] = weight

                # Guardarmos la longitud para normalizar el peso posteriormente
                length += weight**2 

            self.lengths[id] = math.sqrt(length)

        # Bucle para normalizar los pesos
        for id in self.vectors:
            for token in self.vectors[id]:
                # Dividimos los pesos por la longitud del documento
                self.vectors[id][token] = self.vectors[id][token] / self.lengths[id]

                if token not in self.postings_list:
                    self.postings_list[token] = Counter()
                
                # Finalmente, copiamos el valor normalizado en la lista de publicaciones
                self.postings_list[token][id] = self.vectors[id][token]

    # Este método, devuelve el peso de un token en un documento sin normalización
    def get_weigth(self, id, token):
        idf = self.get_idf(token)

        # TFS contiene un archivo de registro de las frecuencias de los términos en todos 
        # los doscumentos en un diccionario multi nivel
        return (1+log10(self.tfs[id][token]))*idf

    # Método que devuelve IDF
    def get_idf(self, token):
        if self.df[token] == 0:
            return -1

        # len(tfs) devuelve el número de documentos
        # df[token] devuelve la frecuencia del token en el documento
        return log10(len(self.tfs)/self.df[token])

    # Método para cargar el modelo
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

    # Método para guardar el modelo
    def save(self, filename):
        try:
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

    # Método que devuelve la respuesta con la mejor concordancia a la consulta aplicada
    def query(self, qstring): 
        self.logger.info(" Query {0}".format(qstring))

        # Convertimos las palabras de la consulta a minúsculas
        qstring = qstring.lower()
        qtf = {}
        qlength = 0
        flag = 0
        loc_docs = {}
        tenth = {}

        # Inicializamos el contador para calcular el coseno de b/w de un token en el documento
        cos_sims = Counter()
        for token in qstring.split():
            if token in self.stopWords:
                continue

            # Obtenemos la raiz de la palabra
            token = self.stemmer.stem(token)

            # Si no existe en el vocabulario, la ignoramos y continuamos
            if token not in self.postings_list:
                continue
            
            # Si el token tiene idf = 0 , todos los valores en sus listas de 
            # publicaciones son cero, en caso contrario como máximo 50 son 
            # elegidas arbitrariamente
            if self.get_idf(token) == 0:

                # para conseguirlo, almacenamos todos los documentos
                loc_docs[token], weights = zip(
                    *self.postings_list[token].most_common())
            else:

                # Cogemos 50 listas de publicaciones
                loc_docs[token], weights = zip(
                    *self.postings_list[token].most_common(50))

            # Guardamos el límite superior de cada token
            tenth[token] = weights[-1]  
            if flag == 1:
                
                # Nos mantiene el rastro de los documentos que tienen tokens
                commondocs = set(loc_docs[token]) & commondocs
            else:
                commondocs = set(loc_docs[token])
                flag = 1

            # Actualizamos la frecuencia de cada término en la consulta
            qtf[token] = 1+log10(qstring.count(token))

            # Calculamos la longitud para normalizar después
            qlength += qtf[token]**2

        qlength = sqrt(qlength)
        for doc in self.vectors:
            cos_sim = 0
            for token in qtf:
                if doc in loc_docs[token]:

                    # Calculamos la puntuación actual si el documento está en el top 10
                    cos_sim = cos_sim + (qtf[token] / qlength) * \
                        self.postings_list[token][doc]
                else:

                    # En otro caso, calculamos la puntuación del límite superior
                    cos_sim = cos_sim + (qtf[token] / qlength) * tenth[token]

            cos_sims[doc] = cos_sim

        # Vemos que documento tiene la puntuación mayor
        max = cos_sims.most_common(50)
        ans, wght = zip(*max)
        try:
            if ans[0] in commondocs:

                # Si el documento tiene puntuación, la devolvemos
                answer = []
                answer.append((self.iterator.ids[ans[0]], ans[0], wght[0], self.iterator.title[ans[0]]))
                if len(ans) > 5:
                    for i in range(1, 5):
                        if ans[i] in commondocs:
                            answer.append((self.iterator.ids[ans[i]],ans[i], wght[i],self.iterator.title[ans[i]]))
                return answer
            else:
                
                answer = []
                answer.append((self.iterator.ids[ans[0]],ans[0], wght[0],self.iterator.title[ans[0]]))
                if len(ans) > 5:
                    for i in range(1, 5):
                        answer.append((self.iterator.ids[ans[i]],ans[i], wght[i],self.iterator.title[ans[i]]))
                return answer

        # Si ningún token está en el vocabulario devolvemos None
        except UnboundLocalError: 
            return [("None", 0)]
