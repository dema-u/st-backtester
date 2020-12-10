from trader.orders import FXCMOrder


def test_callback_insertion(mocked_broker):

    mocked_broker.subscribe_data()
    mocked_broker._connection.subscribe_market_data.assert_called_once_with(mocked_broker._pair.fxcm_name)


def test_entry_replace(mocked_broker, mocked_fxcm_order, simple_order):

    mocked_broker._connection.create_entry_order.return_value = mocked_fxcm_order
    mocked_broker._connection.get_order_ids.return_value = []

    fxcm_order = mocked_broker.place_entry_order(simple_order, replace=True)

    assert isinstance(fxcm_order, FXCMOrder)
    assert simple_order.back_price == fxcm_order.back_price
