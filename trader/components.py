import fxcmpy


class Order:

    def __init__(self,
                 trader,
                 order: fxcmpy.fxcmpy_order,
                 back_price):

        self.trader = trader
        self.order = order
        self.back_price = back_price
        self.trader.orders.insert(0, self)

    def update(self, latest_price):

        position = self.order.get_associated_trade()

        if position is not None:
            print('Adding a position to the positions list.')
            Position(trader=self.trader,
                     position=position,
                     back_price=self.back_price)

        elif self.status == 'Canceled':
            print('Order cancelled, removing from orders list.')
            self.trader.orders.remove(self)

    @property
    def status(self):
        return self.order.get_status()


class Position:

    def __init__(self,
                 trader,
                 position: fxcmpy.fxcmpy_open_position,
                 back_price):

        self.trader = trader
        self.position = position
        self.back_price = back_price
        self.trader.positions.insert(0, self)

        self._is_back = False

    def update(self, latest_price):

        if self.position not in self.trader.connection.get_open_trade_ids():
            self.trader.positions.remove(self)

        if self.is_long and latest_price > self.back_price and self._is_back == False:
            self._is_back = True
            self.sl_to_entry()
        elif not self.is_long and latest_price < self.back_price and self._is_back == False:
            self._is_back = True
            self.sl_to_entry()

    def sl_to_entry(self):
        trade_id = self.position.get_tradeId()
        open_price = self.position.get_open()

        self.trader.connection.change_trade_stop_limit(trade_id, is_stop=True, rate=open_price, is_in_pips=False)

    @property
    def is_long(self):
        return bool(self.position.get_isBuy())

    @property
    def is_back(self):
        return self._is_back

    @property
    def sl(self):
        return self.position.get_stop()

    @sl.setter
    def sl(self, new_sl):
        trade_id = self.position.get_tradeId()
        self.trader.connection.change_trade_stop_limit(trade_id, is_stop=True, rate=new_sl, is_in_pips=False)
