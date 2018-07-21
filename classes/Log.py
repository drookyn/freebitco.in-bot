import logging

class Log():
    def __init__(self):
        # create logger
        self.logger = logging.getLogger(__name__)
        self.logger.setLevel(logging.DEBUG)

        # create formatter
        formatter = logging.Formatter('%(asctime)s:%(levelname)s:%(message)s')

        # create console handler
        consoleHandler = logging.StreamHandler()
        consoleHandler.setLevel(logging.DEBUG)
        consoleHandler.setFormatter(formatter)

        # create file handler
        fileHandler = logging.FileHandler('info.log')
        fileHandler.setLevel(logging.INFO)
        fileHandler.setFormatter(formatter)

        # add handler to logger
        self.logger.addHandler(consoleHandler)
        self.logger.addHandler(fileHandler)