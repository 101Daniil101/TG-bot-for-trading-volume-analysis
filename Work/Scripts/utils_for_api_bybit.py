import time
import hmac
import hashlib
import json

import Library.utils as utils
from Scripts.logger import log_error, log_warning

URL = "https://api.bybit.com"
RECV_WINDOW = str(5000)
AVAILABLE_INTERVALS = ("1", "3", "5", "15", "30", "60", "120",
                       "240", "360", "720", "D", "W", "M")
AVAILABLE_TRADING_PAIRS = None


def send_request_processing_params(endpoint, method, params):

    url_full = URL + endpoint

    response = utils.send_request(url_full, method, params, headers={})

    return response


def get_trading_candles(category: str, symbol: str,
                               interval: str, start: int = None,
                               end: int = None, limit: int = None):
    """start and end get params in ms"""

    global AVAILABLE_TRADING_PAIRS
    if AVAILABLE_TRADING_PAIRS is None:
        AVAILABLE_TRADING_PAIRS = get_available_trading_pairs()

    if category not in ('spot', 'linear', 'inverse'):
        error_message = f"Типа торгов {category} не существует"
        log_error(error_message)
        return None

    if symbol not in AVAILABLE_TRADING_PAIRS['SPOT'] and \
       symbol not in AVAILABLE_TRADING_PAIRS['FUTURES']:
        error_message = f"Торговой пары {symbol} не существует"
        log_error(error_message)
        return None

    if interval not in AVAILABLE_INTERVALS:
        error_message = f"Интервала {interval} не существует"
        log_error(error_message)
        return None

    endpoint = "/v5/market/kline"
    params = {
        "category": category,
        "symbol": symbol,
        "interval": interval
    }

    if start is not None:
        if start < 0 or start > end:
            error_message = (
                f"Неккоректное значение времени октрытия первой свечи: "
                f"{start}"
            )
            log_error(error_message)
            return None
        params["start"] = start

    if end is not None:
        if end < 0 or end < start:
            error_message = (
                f"Неккоректное значение времени октрытия последней свечи: "
                f"{end}"
            )
            log_error(error_message)
            return None
        params["end"] = end

    if limit is not None:
        if limit < 0:
            error_message = (
                f"Неккоректное значение количества свечей: "
                f"{end}"
            )
            log_error(error_message)
            return None
        params["limit"] = limit

    response = send_request_processing_params(endpoint, "GET", params)

    if "error" in response:
        error_message = (
            f"Network error in get_trading_candles:"
            f"{response['message']}"
        )
        log_error(error_message)
        # ВОТ СЮДА добавь код. ЕСЛИ это условие срабатывает, 
        # то нахер выходим из функции аварийно и в тг-бота пишем мол, ошибка
        # Ее содержание доступно по response["message"]
        ...

    list_of_candles = list()
    for candle in response['result']['list']:
        start_time = candle[0]
        open_price = candle[1]
        high_price = candle[2]
        low_price = candle[3]
        close_price = candle[4]
        volume = candle[5]
        list_of_candles.append(
            (start_time, open_price, high_price,
                low_price, close_price, volume)
            )

    return list_of_candles


def get_available_trading_pairs():
    endpoint = '/v5/market/instruments-info'
    trading_pairs = dict()

    params = {'category': 'spot'}
    response = send_request_processing_params(endpoint, "GET", params)
    trading_pairs['SPOT'] = [
        pair['symbol'] for pair in response['result']['list']
    ]

    params = {'category': 'linear'}
    response = send_request_processing_params(endpoint, "GET", params)
    trading_pairs['FUTURES'] = [
        pair['symbol'] for pair in response['result']['list']
    ]

    return trading_pairs


if __name__ == "__main__":
    endpoint = '/v5/account/wallet-balance'
    params = {"accountType": "UNIFIED"}

    print(get_trading_candles("spot", "BTCUSDT", "15", limit=2))
