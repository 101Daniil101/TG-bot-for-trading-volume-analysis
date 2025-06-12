from datetime import datetime
import Library.utils as utils
from Scripts.logger import log_error, log_warning

# Базовый URL для API OKX
URL = "https://www.okx.com"
# Доступные интервалы таймфреймов (внимание: возможно UTC +8)
AVAILABLE_INTERVALS = ("1m", "3m", "5m", "15m", "30m", "1H", "2H", "4H",
                      "6H", "12H", "1D", "2D", "3D", "1W", "1M", "3M")
# Список доступных торговых пар (инициализируется позже)
AVAILABLE_TRADING_PAIRS = None


def get_okx_timestamp() -> str:
    # Получает текущую временную метку в формате OKX (UTC)
    now = datetime.utcnow()
    return now.strftime("%Y-%m-%dT%H:%M:%S.%f")[:-3] + "Z"


def send_request_processing_params(endpoint, method, params):
    # Отправляет HTTP-запрос с обработкой параметров
    url_full = URL + endpoint  # Формирование полного URL
    response = utils.send_request(url_full, method, params, headers={})

    return response


def get_trading_candles(instId: str, bar: str,
                       after: str = None,
                       before: str = None, limit: str = None):
    # Получает данные свечей для указанного инструмента и интервала
    global AVAILABLE_TRADING_PAIRS
    # Инициализация списка торговых пар, если еще не загружен
    if AVAILABLE_TRADING_PAIRS is None:
        AVAILABLE_TRADING_PAIRS = get_available_trading_pairs()

    # Проверка существования торговой пары в зависимости от типа
    if "SWAP" in instId:
        if instId not in AVAILABLE_TRADING_PAIRS["SWAP"]:
            error_message = f"Торговой пары {instId} не существует"
            log_error(error_message)
            return None
    elif instId.count("-") == 2:
        if instId not in AVAILABLE_TRADING_PAIRS["FUTURES"]:
            error_message = f"Торговой пары {instId} не существует"
            log_error(error_message)
            return None
    else:
        if instId not in AVAILABLE_TRADING_PAIRS["SPOT"]:
            error_message = f"Торговой пары {instId} не существует"
            log_error(error_message)
            return None

    # Проверка валидности интервала
    if bar not in AVAILABLE_INTERVALS:
        error_message = f"Интервала {bar} не существует"
        log_error(error_message)
        return None

    endpoint = "/api/v5/market/candles"  # Эндпоинт для получения свечей
    params = {
        "instId": instId,
        "bar": bar
    }

    if after is not None:
        # Проверка корректности времени начала
        if int(after) < 0 or int(after) < int(before):
            error_message = (
                f"Неккоректное значение времени октрытия последней свечи: "
                f"{after}"
            )
            log_error(error_message)
            return None
        params["after"] = str(after)

    if before is not None:
        # Проверка корректности времени окончания
        if int(before) < 0 or int(before) > int(after):
            error_message = (
                f"Неккоректное значение времени октрытия первой свечи: "
                f"{after}"
            )
            log_error(error_message)
            return None
        params["before"] = str(before)

    if limit is not None:
        # Проверка корректности количества свечей
        if int(limit) < 0:
            error_message = (
                f"Неккоректное значение количества свечей: "
                f"{limit}"
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
    for candle in response["data"]:
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
    # Получает список доступных торговых пар для разных типов инструментов
    endpoint = "/api/v5/public/instruments"
    trading_pairs = dict()

    params = {"instType": "SPOT"}  # Параметры для спотового рынка
    response = send_request_processing_params(endpoint, "GET", params)
    trading_pairs["SPOT"] = [
        trading_pair["instId"] for trading_pair in response["data"]
    ]

    params = {"instType": "SWAP"}  # Параметры для свопов
    response = send_request_processing_params(endpoint, "GET", params)
    trading_pairs["SWAP"] = [
        trading_pair["instId"] for trading_pair in response["data"]
    ]

    params = {"instType": "FUTURES"}  # Параметры для фьючерсов
    response = send_request_processing_params(endpoint, "GET", params)
    trading_pairs["FUTURES"] = [
        trading_pair["instId"] for trading_pair in response["data"]
    ]

    return trading_pairs
