import fxcmpy


class Order:

    def __init__(self,
                 trader,
                 order: fxcmpy.fxcmpy_order,
                 back_price):

        self.trader = trader
        self.fxcm_order = order
        self.back_price = back_price
        self.trader.orders.insert(0, self)

    def update(self, latest_price) -> None:

        position = self.fxcm_order.get_associated_trade()

        if position is not None:
            self.trader.logger.info(f'order {self.id} became a position, removing from orders and adding a position.')

            self.trader.orders.remove(self)

            Position(trader=self.trader,
                     position=position,
                     back_price=self.back_price)

        elif self.status == 'Canceled':
            self.trader.logger.info(f'order {self.id} cancelled, removing from orders list.')
            self.trader.orders.remove(self)

    @property
    def id(self):
        return self.fxcm_order.get_orderId()

    @property
    def status(self):
        return self.fxcm_order.get_status()


class Position:

    def __init__(self,
                 trader,
                 position: fxcmpy.fxcmpy_open_position,
                 back_price):

        self.trader = trader
        self.fxcm_position = position
        self.back_price = back_price

        if self.trader.position is not None:
            self.trader.position.close()

        self.trader.position = self

        self._is_back = False

        self.trader.logger.info(f'initialized a new position position {self.id}')

    def update(self, latest_price):

        if self.id not in self.trader.connection.get_open_trade_ids():
            self.trader.logger.info(f'position not found, removing position')
            self.trader.position = None

        if self.is_long and latest_price > self.back_price and self._is_back == False:
            self.trader.logger.info(f'position {self.id} has reached back level of {self.back_price}')
            self._is_back = True
            self.sl_to_entry()

        elif not self.is_long and latest_price < self.back_price and self._is_back == False:
            self.trader.logger.info(f'position {self.id} has reached back level of {self.back_price}')
            self._is_back = True
            self.sl_to_entry()

    def sl_to_entry(self):
        open_price = self.fxcm_position.get_open()
        self.trader.connection.change_trade_stop_limit(self.id, is_stop=True, rate=open_price, is_in_pips=False)

    def close(self):
        self.trader.position = None
        self.fxcm_position.close()

    @property
    def entry(self):
        return self.fxcm_position.get_open()

    @property
    def id(self):
        return self.fxcm_position.get_tradeId()

    @property
    def is_long(self):
        return bool(self.fxcm_position.get_isBuy())

    @property
    def is_back(self):
        return self._is_back

    @property
    def sl(self):
        return self.fxcm_position.get_stop()

    @sl.setter
    def sl(self, new_sl):
        trade_id = self.fxcm_position.get_tradeId()
        self.trader.connection.change_trade_stop_limit(trade_id, is_stop=True, rate=new_sl, is_in_pips=False)
