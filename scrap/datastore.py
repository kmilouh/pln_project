from json import dumps

class SubSecction(object):
    '''
    SubSecction class.
    This class store the data from the twitter help.
    '''
    def __init__(self, title, url, data):
        '''
        Constructor. 
        '''
        self.title = title
        self.url = url
        self.data = data
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
        
        return "{ 'title' : '" + self.title + "' , 'url': '" + self.url + "' , 'data': '" + self.data + "' , 'subSecction': [" + str(buffer) + "]  }".replace("\\"," ")

    def addSubSecction(self, subSecction=None, title=None, url=None, data=None):
        '''
        Add SubSection
        '''
        if(subSecction == None and title == None and url == None and data == None):
            raise Exception('Parameter missing Error')

        if(subSecction != None):
            self.subSecction.append(subSecction)
        else:
            sect = SubSecction(title, url, data)
            self.subSecction.append(sect)
    

