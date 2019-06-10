#!/usr/bin/python3
# -*- coding: utf-8 -*-

# --------------------------------------------------------------------------------
# Librerías
from bs4 import BeautifulSoup
import requests
import time
import json
import os
from json import dumps
import anyjson
from datastore import SubSecction
from log_helper import LogHelper
from parsedata import Tokenizer
from collections import namedtuple
import nltk

# --------------------------------------------------------------------------------
# Descargamos nltk punkt
nltk.download('punkt')

# --------------------------------------------------------------------------------
# Archivos de registro
loghelper = LogHelper()
logger = loghelper.getLogger("default")
logger.info("Start App")

# --------------------------------------------------------------------------------
# FAQ urls en diferentes lenguajes, actualmente admitidos: ES, EN

urls = {#'es': 'https://help.twitter.com/es',
        'en': 'https://help.twitter.com/'
       }

languages = { 'es':'spanish', 'en': 'english'}

# --------------------------------------------------------------------------------
# Tiempo limite para las solicitudes
CONST_TIMEOUT = 10

# --------------------------------------------------------------------------------
# Tiempo entre solicitudes
CONST_REQUEST_TIME_DELAY = 0

# --------------------------------------------------------------------------------
# Lista principal de las subsecciones
main_subsection_list = []

# --------------------------------------------------------------------------------
# Diccionario URL
url_dictionary = {}

# --------------------------------------------------------------------------------
for language, url in urls.items():

    # Creación del archivo de registro
    logger.info("Create Language Subsection {0!r} with url {1!r}".format(language,url))
    sec = SubSecction('FAQ language {0}'.format(language), url, '', -1)

    # Cogemos las ayudas principales en el correspondiente lenguaje
    response = requests.get(url, timeout=CONST_TIMEOUT)

    # Creamos el tokenizador para el lenguaje seleccionado
    tokenizer = Tokenizer(logger,languages[language])
    
    # Contenido HTML para analizar
    content = BeautifulSoup(response.content, "html.parser")

    # En esta función trataremos de almacenar en diferentes secciones el contenido 
    # de ayuda de la página, para ello tendremos que explorar todas las posibilidades
    # que nos proporciona la página HTML en donde se puede encontrar dicho contenido
    # cómo puede ser: hp01__content, hp01__topic-list-item, ap04, twtr-component-space--md
    # Así pues el JSON generado, tendrá un título, un ID y contenido para quedar mejor 
    # estructurado a la hora poder trabajar con él
    id = 0
    for tweet in content.findAll('div', attrs={"class": "hp01__content"}):

        title = tweet.p.text.strip()
        logger.info("Create Subsection {0!r}".format(title))
        mainSecction_item = SubSecction(title, url, tweet.p.text.strip(), id)

        id = id + 1
        pid = id
        for text in tweet.findAll('li', attrs={"class", "hp01__topic-list-item"}):

            sub_content_secction_title = text.a.text.strip()
            logger.info("Create Subsection {0!r}".format(sub_content_secction_title))

            if text.a.get('href') in url_dictionary:
                pid = url_dictionary[text.a.get('href')]
                continue
            else:
                url_dictionary[text.a.get('href')] = id

            sub_content_secction = SubSecction(sub_content_secction_title,text.a.get('href'), '', pid)

            sub_response = requests.get(text.a.get('href'), timeout=CONST_TIMEOUT)
            sub_content = BeautifulSoup(sub_response.content, "html.parser")

            for sub_text in sub_content.findAll('script', attrs={"type": "application/ld+json"}):

                y = anyjson.deserialize(sub_text.text.strip().replace('@', ''))
                if (y['type'] == 'CollectionPage'):

                    item_list = y['mainEntity']['itemListElement']
                    for item_text in item_list:

                        id = id +1
                        pid = id
                        if item_text['url'] in url_dictionary:
                            pid = url_dictionary[text.a.get('href')]
                            continue
                        else:
                             url_dictionary[item_text['url']] = id

                        time.sleep(CONST_REQUEST_TIME_DELAY)
                        page_response = requests.get(item_text['url'], timeout=CONST_TIMEOUT)
                        page_content = BeautifulSoup(page_response.content,"html.parser")
                        separator = '  '
                        buffer = ' '
                        
                        data_html = page_content.findAll('div', attrs={"class": "ap04"})
                        data_html2 = page_content.findAll('div', attrs={"class": "twtr-component-space--md"})
                        if(len(data_html) >0):
                            for help_text in page_content.findAll('div', attrs={"class": "ap04"}):
                                data = separator.join(tokenizer.tokenize(help_text.text.strip().replace('@', '')))
                                if data not in buffer:
                                    buffer = '{0} {1}'.format(buffer, data)
                        elif len(data_html2) > 0:
                            for help_text in data_html2:
                                data_text_2 = help_text.text.strip().replace('@', '')
                                if 'BreadcrumbList' not in data_text_2: 
                                    data = separator.join(tokenizer.tokenize(data_text_2))
                                    if data not in buffer:
                                        buffer = '{0} {1}'.format(buffer, data)

                        logger.info("Create Subsection {0!r} -> {1!r}".format(item_text['name'],item_text['url']))
                        item_subSection = SubSecction(item_text['name'],item_text['url'],buffer,pid)
                        sub_content_secction.addSubSecction(subSecction=item_subSection)

            mainSecction_item.addSubSecction(subSecction = sub_content_secction)

        sec.addSubSecction(subSecction=mainSecction_item)

    main_subsection_list.append(sec)

# --------------------------------------------------------------------------------
# Guardamos los datos en español en un JSON 
with open('es_data.json', 'a') as the_file:
    str_data = str(main_subsection_list[0]).replace("\\","")
    the_file.write(str_data)

# --------------------------------------------------------------------------------
# Guardamos los datos en inglés en un JSON
with open('en_data.json', 'a') as the_file:
    str_data = str(main_subsection_list[0]).replace("\\","")
    the_file.write(str_data)