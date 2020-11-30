import os
import fxcmpy
import configparser


class Trader:

    def __init__(self, strategy):

        self._strategy = strategy
        self._connection = Trader._initialize_connection()

    def run(self):
        pass

    @staticmethod
    def _initialize_connection():
        abspath_api = os.path.abspath('configs/api.ini')
        config = configparser.ConfigParser()
        config.read(abspath_api)

        fxcm_section = config['FXCM']

        access_token = fxcm_section['access_token']
        log_file = fxcm_section['log_file']
        log_level = fxcm_section['log_level']

        return fxcmpy.fxcmpy(access_token=access_token, log_file=log_file, log_level=log_level)
