from Scripts.user_func import analys_based_on_trading_pair_timeframe_numbers_candles, analys_based_on_trading_pair_timeframe_start_end


if __name__ == "__main__":
    print(analys_based_on_trading_pair_timeframe_numbers_candles(
        "BTC/USDT-26SEP25", "FUTURES", "15", '4'
        ))
    print(analys_based_on_trading_pair_timeframe_start_end(
        "BTC/USDT", "SPOT", "15", "12.06.2025 09:00", "12.06.2025 09:30"
        ))
    print(analys_based_on_trading_pair_timeframe_numbers_candles(
        "BTC/USDT", "PERPETUAL FUTURES", "60", '5'
        ))
