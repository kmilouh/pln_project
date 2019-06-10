#!/usr/bin/python3
# -*- coding: utf-8 -*-
"""This is the web scraper for Twitter FAQ"""

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
# First download nltk punkt.
nltk.download('punkt')


# Logs
loghelper = LogHelper()
logger = loghelper.getLogger("default")
logger.info("Start App")



# FAQ urls in different languages
# Currently support: ES, EN
urls = {#'es': 'https://help.twitter.com/es',
        'en': 'https://help.twitter.com/'
       }
languages = { 'es':'spanish', 'en': 'english'}
# Timeout for request
CONST_TIMEOUT = 10
# Time between request
CONST_REQUEST_TIME_DELAY = 0

# Main subsection list
main_subsection_list = []


#URL dictionary
url_dictionary = {}



for language, url in urls.items():
    # Create Main Language Subsection.
    logger.info("Create Language Subsection {0!r} with url {1!r}".format(language,url))
    sec = SubSecction('FAQ language {0}'.format(language), url, '', -1)
    # Get the Main Help twitter in the correspond language.
    response = requests.get(url, timeout=CONST_TIMEOUT)
    # create tokenizer for the selected language.
    tokenizer = Tokenizer(logger,languages[language])
    
    content = BeautifulSoup(response.content, "html.parser")

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
                        #item_text.url
                        #item_text.description
                        #item_text.name
                        # Delay.
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

                        #if(item_text['url']== 'https://help.twitter.com/es/using-twitter/types-of-tweets'):
                        #    print('w')

                        # print(page_content.text.strip().replace('@', ''))
                        #break
                    # print(y)
                    #break
            mainSecction_item.addSubSecction(subSecction = sub_content_secction)
            #break

        sec.addSubSecction(subSecction=mainSecction_item)
        #break
    main_subsection_list.append(sec)


#print(main_subsection_list)
#with open('es_data.json', 'a') as the_file:
#    str_data = str(main_subsection_list[0]).replace("\\","")
#    the_file.write(str_data)

# TODO falta ejecutar para ingles.

with open('en_data.json', 'a') as the_file:
    str_data = str(main_subsection_list[0]).replace("\\","")
    the_file.write(str_data)