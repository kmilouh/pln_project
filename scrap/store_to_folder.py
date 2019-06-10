#!/usr/bin/python3
# -*- coding: utf-8 -*-

# Tool for store all data into different txt files

from json import dumps
import anyjson
from datastore import SubSecction
from log_helper import LogHelper
import os
import json


def save_data(section):
    if len(section['data']) > 0:
        if not os.path.exists(folder + os.sep + section['id']):
            with open(folder + os.sep + section['id'] + '.txt', 'a') as the_file:
                the_file.write(section['data'] + ' ' + section['title'])

    sections = section['subSecction']
    if len(sections) > 0:
        for _section in sections:
            save_data(_section)


filename = 'es_data.json'
folder = './corpusfolder/'

if not os.path.exists(folder):
    os.mkdir(folder)

# Read JSON data into the datastore variable
if filename:
    with open(filename, 'r') as f:
        datastore = json.load(f)


sections = datastore['subSecction']

for section in sections:
    save_data(section)
