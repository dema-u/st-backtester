from trader.position import FXCMPosition


class Order:

    def __init__(self, trader, is_long: bool, entry: float, tp: float, sl: float, size: int, back_price: float):

        self._trader = trader

        self._is_long = is_long
        self._entry = entry
        self._tp = tp
        self._sl = sl
        self._size = size
        self._back_price = back_price

    def get_fxcm_order(self, connection, order):
        return FXCMOrder(trader=self._trader,
                         is_long=self._is_long,
                         entry=self._entry,
                         tp=self._tp,
                         sl=self._sl,
                         size=self.size,
                         back_price=self._back_price,
                         connection=connection,
                         fxcm_order=order)

    @property
    def is_long(self) -> bool:
        return self._is_long

    @property
    def size(self) -> int:
        return self._size

    @property
    def entry(self) -> float:
        return self._entry

    @property
    def tp(self) -> float:
        return self._tp

    @property
    def sl(self) -> float:
        return self._sl


class FXCMOrder(Order):

    def __init__(self, connection, fxcm_order, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self._connection = connection
        self._fxcm_order = fxcm_order
        self._trader.orders.insert(0, self)

        self._is_long = fxcm_order.get_isBuy()
        self._tp = fxcm_order.get_limit()
        self._sl = fxcm_order.get_stop()
        self._size = fxcm_order.get_amount()

        self._trader.logger.info(f'order {self.id} initialized')

    def update(self) -> None:

        position = self._fxcm_order.get_associated_trade()

        if position is not None:
            self._trader.logger.info(f'order {self.id} became a position, removing from orders and adding a position.')
            self._trader.orders.remove(self)
            self._initialize_position(position)

        elif self.status == 'Canceled':
            self._trader.logger.info(f'order {self.id} cancelled, removing from orders list.')
            self._trader.orders.remove(self)

    def _initialize_position(self, position):
        FXCMPosition(trader=self._trader,
                     connection=self._connection,
                     fxcm_position=position,
                     back_price=self._back_price)

    @property
    def id(self) -> int:
        return self._fxcm_order.get_orderId()

    @property
    def status(self) -> str:
        return self._fxcm_order.get_status()
