from json import dumps

class SubSecction(object):
    def __init__(self, title, url, data):
        self.title = title
        self.url = url
        self.data = data
        self.subSecction = []

    def __str__(self):
        return dumps(self, ensure_ascii=False).encode('utf8')

    def addSubSecction(self, subSecction=None, title=None, url=None, data=None):
        if(subSecction == None and title == None and url == None and data == None):
            raise Exception('Parameter missing Error')

        if(subSecction != None):
            self.subSecction.append(subSecction)
        else:
            sect = SubSecction(title, url, data)
            self.subSecction.append(sect)
    

