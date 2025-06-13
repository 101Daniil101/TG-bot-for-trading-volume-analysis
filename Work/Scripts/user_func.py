import pandas as pd
from datetime import datetime

import Scripts.utils_for_api_bybit as bybit
import Scripts.utils_for_api_okx as okx
import Scripts.utils_for_api_binance as binance
import Scripts.candle_analysis as analysis
import Scripts.create_graphs as graphs


def convert_interval(timeframe: str):
    """ Преобразует строковый таймфрейм в формат, подходящий для разных бирж """
    mapping_bybit = {
        '1': '1', '3': '3', '5': '5', '15': '15', '30': '30',
        '60': '60', '120': '120', '240': '240', '360': '360',
        'Day': 'D', 'Week': 'W', 'Month': 'M'
    }

    mapping_okx = {
        '1': '1m', '3': '3m', '5': '5m', '15': '15m', '30': '30m',
        '60': '1H', '120': '2H', '240': '4H', '360': '6H',
        'Day': '1D', 'Week': '1W', 'Month': '1M'
    }

    mapping_binance = {
        '1': '1m', '3': '3m', '5': '5m', '15': '15m', '30': '30m',
        '60': '1h', '120': '2h', '240': '4h', '360': '6h',
        'Day': '1d', 'Week': '1w', 'Month': '1M'
    }
    # Создание словаря с результатами преобразования для каждой биржи
    result = {"bybit": mapping_bybit[timeframe], "okx": mapping_okx[timeframe],
              "binance": mapping_binance[timeframe]}

    return result


def convert_trading_pair(trading_pair: str, exchange: str, type_of_trade: str):
    """ Преобразует формат торговой пары в зависимости от биржи и типа торговли """
    result = {"bybit": trading_pair.replace('/', ''),
              "okx": trading_pair.replace('/', '-'),
              "binance": trading_pair.replace('/', '')}

    trading_pair = result[exchange]

    months_dict = {
        'JAN': '01', 'FEB': '02', 'MAR': '03', 'APR': '04',
        'MAY': '05', 'JUN': '06', 'JUL': '07', 'AUG': '08',
        'SEP': '09', 'OCT': '10', 'NOV': '11', 'DEC': '12'
    }

    if type_of_trade == "FUTURES":
        # Извлечение дня, месяца и года из торговой пары для фьючерсов
        day = trading_pair[len(trading_pair)-7:len(trading_pair)-5]
        month = trading_pair[len(trading_pair)-5:len(trading_pair)-2]
        year = trading_pair[len(trading_pair)-2:]

        if exchange == 'binance':
            # Форматирование даты для Binance
            trading_pair = trading_pair[:len(trading_pair)-7] + year \
                           + months_dict[month] + day
            trading_pair = trading_pair.replace('-', '_')
            result['binance'] = trading_pair
        elif exchange == 'okx':
            # Форматирование даты для OKX
            trading_pair = trading_pair[:len(trading_pair)-7] + year \
                           + months_dict[month] + day
            result['okx'] = trading_pair

    elif type_of_trade == "PERPETUAL FUTURES" and exchange == "okx":
        # Добавление суффикса для вечных фьючерсов на OKX
        trading_pair = trading_pair + "-SWAP"
        result['okx'] = trading_pair

    return result


def convert_type_of_trade(type_of_trade: str, trading_pair: str = '',
                          exchange: str = ''):
    """ Преобразует тип торговли в формат, подходящий для конкретной биржи """
    mapping_bybit = {
        'SPOT': 'spot',
        'FUTURES': 'linear',
        'PERPETUAL FUTURES': 'linear'
    }

    mapping_binance = {
        'SPOT': 'SPOT',
        'FUTURES': 'FUTURES',
        'PERPETUAL FUTURES': 'FUTURES_PERP'
    }

    result = {
        'binance': mapping_binance[type_of_trade],
        'bybit': mapping_bybit[type_of_trade]
    }

    return result


def fix_some_API_error(df: pd.DataFrame, type_of_trade: str):
    """ Корректирует ошибки в данных, полученных от API, в зависимости от типа торговли """
    if (type_of_trade == "FUTURES"):
        df["volume"] = df["volume"] / 100

    if (type_of_trade == "PERPETUAL FUTURES"):
        for index in df.index:
            if df.loc[index, 'volume'] > 10000:
                df.loc[index, 'volume'] = df.loc[index, 'volume'] / 100
            else:
                df.loc[index, 'volume'] = df.loc[index, 'volume'] * 10

    return df


def candles_to_df(candles, exchange_name):
    """ Преобразует список свечей в DataFrame с указанием биржи """
    df = pd.DataFrame(
        candles,
        columns=['timestamp', 'open', 'high', 'low', 'close', 'volume']
    )
    df['timestamp'] = pd.to_datetime(
        df['timestamp'].astype('int64'), unit='ms'
    )
    df = df.sort_values('timestamp')
    df.set_index('timestamp', inplace=True)
    df = df.astype(float)
    df['exchange'] = exchange_name
    return df


def readable_time_to_ms(time_str) -> int:
    """ Преобразует читаемое время в формате ДД.ММ.ГГГГ ЧЧ:ММ в миллисекунды """
    dt = datetime.strptime(time_str, "%d.%m.%Y %H:%M")
    milliseconds = int(dt.timestamp() * 1000)

    return milliseconds


def analys_based_on_trading_pair_timeframe_numbers_candles(
        trading_pair: str, type_of_trade: str,
        timeframe: str, numbers_of_candles: str
        ):
    """
        Входящие параметры:
            trading_pair: str - торговая пара вида BTC/USDT. ОБЯЗАТЕЛЬНО ТАКОГО
            Монету срочных фьчерсов обязательно в виде:
            <монета>/<монета>-ДД.<первые три заглавные буквы месяца на английском языке>.ГГ
            
            kind_of_trade: str - вид торговли.
            Принимает следующие возможные варианты:
                SPOT, FUTURES, PERPETUAL FUTURES
            
            timeframe: str - таймфрейм (сколько длится одна свеча).
            Принимает следующие возможные варианты (в виде строки):
                1, 3, 5, 15, 30, 60, 120, 240, 360, Day, Week, Month.

            numbers_of_candles: str - кол-во крайних свечей
    """
    # Преобразование таймфрейма для каждой биржи
    timeframe_bybit = convert_interval(timeframe)["bybit"]
    timeframe_okx = convert_interval(timeframe)["okx"]
    timeframe_binance = convert_interval(timeframe)["binance"]

    # Преобразование торговой пары для каждой биржи
    trading_pair_bybit = convert_trading_pair(
        trading_pair, 'bybit', type_of_trade
    )['bybit']
    trading_pair_okx = convert_trading_pair(
        trading_pair, 'okx', type_of_trade
    )['okx']
    trading_pair_binance = convert_trading_pair(
        trading_pair, 'binance', type_of_trade
    )['binance']

    # Преобразование типа торговли для каждой биржи
    type_of_trade_bybit = convert_type_of_trade(type_of_trade)["bybit"]
    type_of_trade_binance = convert_type_of_trade(type_of_trade)["binance"]

    # Получение данных свечей для Bybit
    if ((list_of_candles_bybit := bybit.get_trading_candles(
        type_of_trade_bybit, trading_pair_bybit,
        timeframe_bybit, limit=int(numbers_of_candles)
    )) is None):
        raise ValueError("Ошибка валидации данных от Bybit. Проверьте вводимые данные. Для подробностей обратитесь к админу")

    # Получение данных свечей для OKX
    if ((list_of_candles_okx := okx.get_trading_candles(
        trading_pair_okx, timeframe_okx,
        limit=numbers_of_candles
    )) is None):
        raise ValueError("Ошибка валидации данных от Bybit. Проверьте вводимые данные. Для подробностей обратитесь к админу")

    # Получение данных свечей для Binance
    if ((list_of_candles_binance := binance.get_trading_candles(
        type_of_trade_binance, trading_pair_binance, timeframe_binance,
        limit=int(numbers_of_candles)
    )) is None):
        raise ValueError("Ошибка валидации данных от Bybit. Проверьте вводимые данные. Для подробностей обратитесь к админу")

    # Преобразование свечей в DataFrame для каждой биржи
    df_bybit = candles_to_df(list_of_candles_bybit, 'Bybit')
    df_okx = candles_to_df(list_of_candles_okx, 'OKX')
    df_binance = candles_to_df(list_of_candles_binance, 'Binance')

    # Корректировка ошибок в данных OKX
    df_okx = fix_some_API_error(df_okx, type_of_trade)

    # Расчет индикаторов OBV для всех DataFrame
    df_bybit = analysis.calculate_obv(df_bybit)
    df_okx = analysis.calculate_obv(df_okx)
    df_binance = analysis.calculate_obv(df_binance)

    # Расчет индикаторов VWAP для всех DataFrame
    df_bybit = analysis.calculate_vwap(df_bybit)
    df_okx = analysis.calculate_vwap(df_okx)
    df_binance = analysis.calculate_vwap(df_binance)

    # Расчет объемного профиля для всех DataFrame
    df_volume_profile_bybit = analysis.calculate_volume_profile(df_bybit)
    df_volume_profile_okx = analysis.calculate_volume_profile(df_okx)
    df_volume_profile_binance = analysis.calculate_volume_profile(df_binance)

    # Создание графика объемов
    path_to_volume_plot = graphs.create_volume_plot(
        df_bybit, df_okx, df_binance
    )
    # Создание графика OBV
    path_to_obv_plot = graphs.create_obv_plot(
        df_bybit, df_okx, df_binance
    )
    # Создание графика VWAP
    path_to_plot_vwap = graphs.create_plot_vwap(
        df_bybit, df_okx, df_binance
    )
    # Создание круговой диаграммы объемов
    path_to_volume_pie_chart = graphs.create_volume_pie_chart(
        df_bybit, df_okx, df_binance
    )
    # Создание графика объемного профиля
    path_to_plot_volume_profilies = graphs.create_plot_volume_profiles(
        df_volume_profile_bybit, df_volume_profile_okx,
        df_volume_profile_binance
    )

    # Возвращение путей к созданным графикам
    return (
        path_to_volume_plot, path_to_obv_plot, path_to_plot_vwap,
        path_to_volume_pie_chart, path_to_plot_volume_profilies
    )


def analys_based_on_trading_pair_timeframe_start_end(
        trading_pair: str, type_of_trade: str, timeframe: str,
        start_time: str, end_time: str
        ):
    """
        Входящие параметры:
            trading_pair: str - торговая пара вида BTC/USDT. ОБЯЗАТЕЛЬНО ТАКОГО
            Монету срочных фьчерсов обязательно в виде:
            <монета>/<монета>-ДД.<первые три заглавные буквы месяца на английском языке>.ГГ
            
            kind_of_trade: str - вид торговли.
            Принимает следующие возможные варианты:
                SPOT, FUTURES, PERPETUAL FUTURES
            
            timeframe: str - таймфрейм (сколько длится одна свеча).
            Принимает следующие возможные варианты (в виде строки):
                1, 3, 5, 15, 30, 60, 120, 240, 360, Day, Week, Month.

            start_time: str - время открытия первой свечи в формате
            ИМЕННО ТАКОМ ДД.ММ.ГГГГ ЧЧ:ММ
            (при выборе лучше сделать через календарь конечно)

            end_time: str - время закрытия последней свечи в формате
            ИМЕННО ТАКОМ ДД.ММ.ГГГГ ЧЧ:ММ

            То есть в результат пойдут свечи, время открытия которых больше 
            или равны start_time, но меньше или равны end_time
    """
    # Преобразование таймфрейма для каждой биржи
    timeframe_bybit = convert_interval(timeframe)["bybit"]
    timeframe_okx = convert_interval(timeframe)["okx"]
    timeframe_binance = convert_interval(timeframe)["binance"]

    # Преобразование торговой пары для каждой биржи
    trading_pair_bybit = convert_trading_pair(
        trading_pair, 'bybit', type_of_trade
    )['bybit']
    trading_pair_okx = convert_trading_pair(
        trading_pair, 'okx', type_of_trade
    )['okx']
    trading_pair_binance = convert_trading_pair(
        trading_pair, 'binance', type_of_trade
    )['binance']

    # Преобразование типа торговли для каждой биржи
    type_of_trade_bybit = convert_type_of_trade(type_of_trade)["bybit"]
    type_of_trade_binance = convert_type_of_trade(type_of_trade)["binance"]

    # Преобразование времени начала и конца в миллисекунды
    start = readable_time_to_ms(start_time)
    end = readable_time_to_ms(end_time)

    # Получение данных свечей для Bybit в заданном диапазоне
    if ((list_of_candles_bybit := bybit.get_trading_candles(
        type_of_trade_bybit, trading_pair_bybit,
        timeframe_bybit, start=start, end=end
    )) is None):
        raise ValueError("Ошибка валидации данных от Bybit. Проверьте вводимые данные. Для подробностей обратитесь к админу")

    # Получение данных свечей для OKX в заданном диапазоне
    if ((list_of_candles_okx := okx.get_trading_candles(
        trading_pair_okx, timeframe_okx,
        after=str(end+1), before=str(start-1)
    )) is None):
        raise ValueError("Ошибка валидации данных от Bybit. Проверьте вводимые данные. Для подробностей обратитесь к админу")

    # Получение данных свечей для Binance в заданном диапазоне
    if ((list_of_candles_binance := binance.get_trading_candles(
        type_of_trade_binance, trading_pair_binance, timeframe_binance,
        start=start, end=end
    )) is None):
        raise ValueError("Ошибка валидации данных от Bybit. Проверьте вводимые данные. Для подробностей обратитесь к админу")

    # Преобразование свечей в DataFrame для каждой биржи
    df_bybit = candles_to_df(list_of_candles_bybit, 'Bybit')
    df_okx = candles_to_df(list_of_candles_okx, 'OKX')
    df_binance = candles_to_df(list_of_candles_binance, 'Binance')

    # Корректировка ошибок в данных OKX
    df_okx = fix_some_API_error(df_okx, type_of_trade)

    # Расчет индикаторов OBV для всех DataFrame
    df_bybit = analysis.calculate_obv(df_bybit)
    df_okx = analysis.calculate_obv(df_okx)
    df_binance = analysis.calculate_obv(df_binance)

    # Расчет индикаторов VWAP для всех DataFrame
    df_bybit = analysis.calculate_vwap(df_bybit)
    df_okx = analysis.calculate_vwap(df_okx)
    df_binance = analysis.calculate_vwap(df_binance)

    # Расчет объемного профиля для всех DataFrame
    df_volume_profile_bybit = analysis.calculate_volume_profile(df_bybit)
    df_volume_profile_okx = analysis.calculate_volume_profile(df_okx)
    df_volume_profile_binance = analysis.calculate_volume_profile(df_binance)

    # Создание графика объемов
    path_to_volume_plot = graphs.create_volume_plot(
        df_bybit, df_okx, df_binance
    )
    # Создание графика OBV
    path_to_obv_plot = graphs.create_obv_plot(
        df_bybit, df_okx, df_binance
    )
    # Создание графика VWAP
    path_to_plot_vwap = graphs.create_plot_vwap(
        df_bybit, df_okx, df_binance
    )
    # Создание круговой диаграммы объемов
    path_to_volume_pie_chart = graphs.create_volume_pie_chart(
        df_bybit, df_okx, df_binance
    )
    # Создание графика объемного профиля
    path_to_plot_volume_profilies = graphs.create_plot_volume_profiles(
        df_volume_profile_bybit, df_volume_profile_okx,
        df_volume_profile_binance
    )

    # Возвращение путей к созданным графикам
    return (
        path_to_volume_plot, path_to_obv_plot, path_to_plot_vwap,
        path_to_volume_pie_chart, path_to_plot_volume_profilies
    )


if __name__ == "__main__":
    # Тест выполнения функции с заданными параметрами для фьючерсов
    print(analys_based_on_trading_pair_timeframe_numbers_candles(
        "BTC/USDT-26SEP25", "FUTURES", "15", '4'
    ))
    # Тест выполнения функции с заданными параметрами для спотового рынка
    print(analys_based_on_trading_pair_timeframe_start_end(
        "BTC/USDT", "SPOT", "15", "12.06.2025 09:00", "12.06.2025 09:30"
    ))
    # Тест выполнения функции с заданными параметрами для вечных фьючерсов
    print(analys_based_on_trading_pair_timeframe_numbers_candles(
        "BTC/USDT", "PERPETUAL FUTURES", "60", '5'
    ))
    