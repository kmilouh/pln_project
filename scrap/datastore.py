from json import dumps
import anyjson
import os
import json

class SubSecction(object):
    '''
    SubSecction class.
    This class store the data from the twitter help.
    '''
    def __init__(self, title, url, data, id):
        '''
        Constructor. 
        '''
        self.title = title
        self.url = url
        self.data = data
        self.id = id
        self.subSecction = []

    def __str__(self):
        '''
        To Str. 
        '''
        buffer = ""
        for x in self.subSecction:
            str_data = str(x).replace("\\","")
            buffer = buffer + " , " + str_data
            
        buffer = buffer.strip().strip("'").strip(",")
        
        return "{ 'title' : '" + self.title + "' , 'url': '" + self.url +  "' , 'id': '" + str(self.id) +   "' , 'data': '" + self.data + "' , 'subSecction': [" + str(buffer) + "]  }".replace("\\"," ")

    def addSubSecction(self, subSecction=None, title=None, url=None, data=None, id=0):
        '''
        Add SubSection
        '''
        if(subSecction == None and title == None and url == None and data == None):
            raise Exception('Parameter missing Error')

        if(subSecction != None):
            self.subSecction.append(subSecction)
        else:
            sect = SubSecction(title, url, data,id)
            self.subSecction.append(sect)
    

class DataIterator:
    def __init__(self, jsonfile):
        self.data = []
        self.ids = {}
        self.num = 0
        # Read JSON data into the datastore variable
        if jsonfile:
            with open(jsonfile, 'r') as f:
                datastore = json.load(f)

        sections = datastore['subSecction']

        for section in sections:
            self.save_data(section)
    
    def save_data(self,section):
        if len(section['data']) > 0:
            if not  section['id'] in self.ids:
                self.ids[section['id']] = section['url']
                self.data.append((section['id'], section['url'],  section['data'] + ' ' + section['title']))

        sections = section['subSecction']
        if len(sections) > 0:
            for _section in sections:
                self.save_data(_section)
