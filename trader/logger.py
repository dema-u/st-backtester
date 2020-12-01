import os
import logging


class Logger:

    filepath_log = os.path.abspath('logs/trader.log')
    logging_format = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')

    def __init__(self):

        self._logger = logging.getLogger('trader')
        self._logger.setLevel(logging.INFO)

        self._add_null_handler()

    def add_stream_handler(self) -> None:
        stream_handler = logging.StreamHandler()
        stream_handler.setFormatter(Logger.logging_format)
        self._logger.addHandler(stream_handler)

    def add_path_handler(self) -> None:
        file_handler = logging.FileHandler(filename=Logger.abspath_log)
        file_handler.setFormatter(Logger.logging_format)
        self._logger.addHandler(file_handler)

    def _add_null_handler(self) -> None:
        null_handler = logging.NullHandler()
        null_handler.setFormatter(Logger.logging_format)
        self._logger.addHandler(null_handler)


    @property
    def logger(self):
        return self._logger
