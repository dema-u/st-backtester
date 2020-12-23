import time
import os
import sys
from trader import Trader, TraderController
from strategy import FractalStrategy
from utils import CurrencyPair, Pips
from utils import ConfigHandler, LoggerHandler


DEFAULT_CURRENCY = 'EURUSD'
DEFAULT_FREQUENCY = 'm1'


logger_helper = LoggerHandler('MAIN', "INFO")
logger_helper.add_stream_handler()
logger_helper.add_path_handler()
logger = logger_helper.logger


if __name__ == '__main__':

    env_vars = os.environ

    currency = os.environ.get('currency', DEFAULT_CURRENCY)
    frequency = os.environ.get('frequency', DEFAULT_FREQUENCY)

    config = ConfigHandler()
    trader_section = config.get_trader_settings(currency, frequency)

    target_level = float(trader_section['target_level'])
    back_level = float(trader_section['back_level'])
    break_level = float(trader_section['break_level'])
    sl_extension = float(trader_section['sl_extension'])
    max_width = float(trader_section['max_width'])
    min_width = float(trader_section['min_width'])
    risk = float(trader_section['risk'])

    start_time = str(trader_section['start_time'])
    end_time = str(trader_section['end_time'])

    pair = CurrencyPair(currency)
    jpy_pair: bool = pair.jpy_pair

    strategy = FractalStrategy(currency_pair=pair,
                               target_level=target_level,
                               back_level=back_level,
                               break_level=Pips(break_level, jpy_pair),
                               sl_extension=Pips(sl_extension, jpy_pair),
                               max_width=Pips(max_width, jpy_pair),
                               min_width=Pips(min_width, jpy_pair),
                               risk=risk)

    trader = Trader(currency_pair=pair,
                    strategy=strategy,
                    freq=frequency)

    controller = TraderController(frequency=frequency,
                                  start_time=start_time,
                                  end_time=end_time)

    logger.info(f'trader and controller initialized. trading {currency} on {frequency} frequency...')

    while True:

        # noinspection PyBroadException
        try:

            action = controller.get_action()

            if action == 'trade':
                trader.process_timestep()
            elif action == 'update':
                trader.update_trader()
            elif action == 'shutdown':
                logger.info('trading day finished. terminating')
                trader.terminate()
                break

        except:
            logger.exception('trader unexpectedly raised an error. shutting down.')
            # trader.terminate()
            sys.exit(1)

        finally:
            time.sleep(1.0)

    sys.exit(0)
