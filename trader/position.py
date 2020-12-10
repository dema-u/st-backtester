from utils import LoggerHandler


logger_helper = LoggerHandler(__name__, "INFO")
logger_helper.add_stream_handler()
logger_helper.add_path_handler()
logger = logger_helper.logger


class FXCMPosition:

    def __init__(self,
                 trader,
                 broker,
                 fxcm_position,
                 back_price):

        self._trader = trader
        self._broker = broker
        self._fxcm_position = fxcm_position
        self._id = fxcm_position.get_tradeId()

        self._trader.logger.info(f'initializing position {self.id}')

        if self._trader.position is not None:
            self._trader.logger.info(f'found pre-existing position {self._trader.position.id}, closing')
            self._trader.position.close()

        self._open_price = self._fxcm_position.get_open()
        self._id = self._fxcm_position.get_tradeId()
        self._sl = self._fxcm_position.get_stop()
        self._is_long = self._fxcm_position.get_isBuy()
        self._is_back = False
        self._back_price = back_price

        self._trader.position = self

        self._trader.logger.info(f'{self.direction} position {self.id} initialized')

    def update(self, latest_price):

        if self.id not in self._broker.open_position_ids:
            self._trader.logger.info(f'{self.direction} position {self.id} not found, removing position')
            self._trader.position = None

        if self.is_long and latest_price > self._back_price and self._is_back == False:
            self.flag_back_price()
        elif not self.is_long and latest_price < self._back_price and self._is_back == False:
            self.flag_back_price()

    def flag_back_price(self):
        self._trader.logger.info(f'{self.direction} position {self.id} has reached back level of {self._back_price}')
        self._is_back = True
        self.sl = self.open_price

    def close(self):
        self._trader.position = None
        self._fxcm_position.close()

    @property
    def direction(self):
        return 'long' if self.is_long else 'short'

    @property
    def open_price(self):
        return self._open_price

    @property
    def sl(self):
        return self._sl

    @sl.setter
    def sl(self, new_sl):
        self._broker.change_position_sl(self.id, new_sl)

    @property
    def is_long(self):
        return self._is_long

    @property
    def is_back(self):
        return self._is_back

    @property
    def id(self):
        return self._id
