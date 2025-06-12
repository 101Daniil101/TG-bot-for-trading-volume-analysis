import Library.utils as utils
from Scripts.logger import log_error, log_warning

# Базовый URL для API Bybit
URL = "https://api.bybit.com"
# Время ожидания ответа в миллисекундах
RECV_WINDOW = str(5000)
# Доступные интервалы таймфреймов
AVAILABLE_INTERVALS = ("1", "3", "5", "15", "30", "60", "120",
                      "240", "360", "720", "D", "W", "M")
# Список доступных торговых пар (инициализируется позже)
AVAILABLE_TRADING_PAIRS = None


def send_request_processing_params(endpoint, method, params):
    # Отправляет HTTP-запрос с обработкой параметров
    url_full = URL + endpoint  # Формирование полного URL
    response = utils.send_request(url_full, method, params, headers={})

    return response


def get_trading_candles(category: str, symbol: str,
                       interval: str, start: int = None,
                       end: int = None, limit: int = None):
    """start and end get params in ms"""
    # Получает данные свечей для указанной категории, символа и интервала
    global AVAILABLE_TRADING_PAIRS
    # Инициализация списка торговых пар, если еще не загружен
    if AVAILABLE_TRADING_PAIRS is None:
        AVAILABLE_TRADING_PAIRS = get_available_trading_pairs()

    # Проверка корректности категории торговли
    if category not in ('spot', 'linear', 'inverse'):
        error_message = f"Типа торгов {category} не существует"
        log_error(error_message)
        return None

    # Проверка существования торговой пары
    if symbol not in AVAILABLE_TRADING_PAIRS['SPOT'] and \
       symbol not in AVAILABLE_TRADING_PAIRS['FUTURES']:
        error_message = f"Торговой пары {symbol} не существует"
        log_error(error_message)
        return None

    # Проверка валидности интервала
    if interval not in AVAILABLE_INTERVALS:
        error_message = f"Интервала {interval} не существует"
        log_error(error_message)
        return None

    endpoint = "/v5/market/kline"  # Эндпоинт для получения свечей
    params = {
        "category": category,
        "symbol": symbol,
        "interval": interval
    }

    if start is not None:
        # Проверка корректности времени начала
        if start < 0 or start > end:
            error_message = (
                f"Неккоректное значение времени октрытия первой свечи: "
                f"{start}"
            )
            log_error(error_message)
            return None
        params["start"] = start

    if end is not None:
        # Проверка корректности времени окончания
        if end < 0 or end < start:
            error_message = (
                f"Неккоректное значение времени октрытия последней свечи: "
                f"{end}"
            )
            log_error(error_message)
            return None
        params["end"] = end

    if limit is not None:
        # Проверка корректности количества свечей
        if limit < 0:
            error_message = (
                f"Неккоректное значение количества свечей: "
                f"{end}"
            )
            log_error(error_message)
            return None
        params["limit"] = limit

    # Отправка запроса к API
    response = send_request_processing_params(endpoint, "GET", params)

    if "error" in response:
        # Обработка сетевой ошибки
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
    # Преобразование данных свечей в список кортежей
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
    # Получает список доступных торговых пар для разных категорий
    endpoint = '/v5/market/instruments-info'
    trading_pairs = dict()

    params = {'category': 'spot'}  # Параметры для спотового рынка
    response = send_request_processing_params(endpoint, "GET", params)
    trading_pairs['SPOT'] = [
        pair['symbol'] for pair in response['result']['list']
    ]

    params = {'category': 'linear'}  # Параметры для линейных фьючерсов
    response = send_request_processing_params(endpoint, "GET", params)
    trading_pairs['FUTURES'] = [
        pair['symbol'] for pair in response['result']['list']
    ]

    return trading_pairs


if __name__ == "__main__":
    # Тест функции получения свечей для спотового рынка
    endpoint = '/v5/account/wallet-balance'
    params = {"accountType": "UNIFIED"}

    print(get_trading_candles("spot", "BTCUSDT", "15", limit=2))
    