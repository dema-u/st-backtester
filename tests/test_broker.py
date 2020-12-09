from trader.orders import FXCMOrder


def test_callback_insertion(mocked_broker):

    def test_function():
        pass

    mocked_broker.add_callback(test_function)
    mocked_broker._connection.subscribe_market_data.assert_called_once_with(mocked_broker._pair.fxcm_name,
                                                                            (test_function, ))


def test_entry_replace(mocked_broker, mocked_fxcm_order, simple_order):

    mocked_broker._connection.create_entry_order.return_value = mocked_fxcm_order
    mocked_broker._connection.get_order_ids.return_value = []

    fxcm_order = mocked_broker.place_entry_order(simple_order, replace=True)

    assert isinstance(fxcm_order, FXCMOrder)
    assert simple_order.back_price == fxcm_order.back_price


# def test_entry_no_replace(mocked_broker, mocked_fxcm_order, simple_order):
#
#     orders_property_mock = PropertyMock()
#     orders_property_mock.return_value
#
#     mocked_broker.cancel_all_orders.return_value = None
#
#     mocked_broker.orders.return_value = [mocked_fxcm_order]


