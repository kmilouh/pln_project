#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""This is the web scraper for Twitter FAQ"""

from bs4 import BeautifulSoup
import requests
import json
import anyjson
from parsedata import SubSecction
from collections import namedtuple

# FAQ urls in different languages
urls = {'es': 'https://help.twitter.com/es', 'en': 'https://help.twitter.com/'}

for language, url in urls.items():
    sec = SubSecction('FAQ language {0!r}'.format(language), url, None)
    response = requests.get(url, timeout=5)
    content = BeautifulSoup(response.content, "html.parser")
    # print(content)
    i = 0
    j = 0

    for tweet in content.findAll('div', attrs={"class": "hp01__content"}):
        print('Secc text i=', i, tweet.p.text.strip())
        mainSecction_item = SubSecction(
            tweet.p.text.strip(), url, tweet.p.text.strip())
        i += 1
        for text in tweet.findAll('li', attrs={"class", "hp01__topic-list-item"}):
            # print(text)
            print('SubSecc text j=', j, text.text.strip())
            print('SubSecc url j=', j, text.a.get('href'))
            j += 1
            sub_response = requests.get(text.a.get('href'), timeout=5)
            sub_content = BeautifulSoup(sub_response.content, "html.parser")
            for sub_text in sub_content.findAll('script', attrs={"type": "application/ld+json"}):
                y = anyjson.deserialize(sub_text.text.strip().replace('@', ''))
                if (y['type'] == 'CollectionPage'):
                    print(y)
                    print(y['mainEntity'])
                # print(y)
            exit()

        sec.addSubSecction(subSecction=mainSecction_item)
    exit()
