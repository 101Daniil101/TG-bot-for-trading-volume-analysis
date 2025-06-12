import numpy as np
import pandas as pd


def calculate_obv(df):
    # Вычисляет индикатор OBV (On-Balance Volume) на основе данных свечей
    df['obv'] = (np.sign(df['close'].diff()) * df['volume']).cumsum()
    return df


def calculate_vwap(df):
    # Вычисляет индикатор VWAP (Volume Weighted Average Price)
    df['typical_price'] = (df['high'] + df['low'] + df['close']) / 3
    df['vwap'] = (df['typical_price'] * df['volume']).cumsum() / \
        df['volume'].cumsum()
    return df


def calculate_volume_profile(df, price_bins=20):
    # Вычисляет профиль объема для ценовых диапазонов
    df['price_bin'] = pd.cut(df['close'], bins=price_bins)
    volume_profile = df.groupby('price_bin', observed=False)['volume'].sum() \
        .sort_values(ascending=False)
    return volume_profile

