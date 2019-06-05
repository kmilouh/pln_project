import logging
import logging.config
import datetime
import os

class LogHelper(object):
    def __init__(self):
        now = datetime.datetime.now()


        if not os.path.exists("./logs/"):
            os.makedirs("./logs/")

        filename = "./logs/log_{0}_{1}_{2}.log".format(now.year, now.month, now.day)
        
        file_exists = os.path.isfile(filename) 
 
        if not file_exists:
            pass
            with open(filename,"a+") as f:
                print('Creating Log File.')        

        logging.config.fileConfig('./logging.conf', defaults={'logfilename': filename})  
    
    def getLogger(self, name):
        return logging.getLogger(name)
