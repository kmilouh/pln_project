import requests


class GoogleDriveHelper(object):
    def __init__(self, file_id, destination, logger, size):
        self.logger = logger
        self.file_id = file_id
        self.destination = destination
        self.size = size

    def saveFile(self):
        self.logger.info("Download " + self.file_id + " from Google Drive to " + self.destination)
        self.download(self.file_id, self.destination)

    def download(self, id, destination):
        URL = "https://docs.google.com/uc?export=download"
        self.logger.info("Request Session")
        session = requests.Session()
        self.logger.debug("Get File with id={0}".format(id))
        response = session.get(URL, params={'id': id}, stream=True)
        self.logger.info("Get Confirm Token")
        token = self.getToken(response)

        if token:
            params = {'id': id, 'confirm': token}
            response = session.get(URL, params=params, stream=True)
        else:
            self.logger.error("Request Token Not Found")
        self.logger.info("Save Response")
        self.save_response_content(response, destination)

    def getToken(self, response):
        self.logger.info("Get GoogleDrive Request Token")
        for key, value in response.cookies.items():
            if key.startswith('download_warning'):
                return value
        return None

    def save_response_content(self, response, destination):
        CHUNK_SIZE = 32768
        chunks = response.iter_content(CHUNK_SIZE)
        i = 1
        with open(destination, "wb") as f:
            for chunk in chunks:
                if(i % 10 == 9):
                    self.logger.info("Save chunk {0} Mb of {1}".format(i * CHUNK_SIZE / 1048576, self.size))
                i += 1
                if chunk:
                    f.write(chunk)
