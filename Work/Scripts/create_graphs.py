import os

import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
from pathlib import Path


Path("Graphics").mkdir(exist_ok=True)


def create_volume_plot(df_bybit, df_okx, df_binance):
    plt.figure(figsize=(14, 7))

    for df in [df_bybit, df_okx, df_binance]:
        if not isinstance(df.index, pd.DatetimeIndex):
            df.index = pd.to_datetime(df.index)

    x = range(len(df_bybit))

    width = 0.25

    plt.bar(
        x, df_bybit['volume'], width, label='Bybit',
        color='#2775ca', alpha=0.8
        )
    plt.bar(
        [i + width for i in x], df_okx['volume'], width,
        label='OKX', color='#0ecb81', alpha=0.8
        )
    plt.bar(
        [i + 2*width for i in x], df_binance['volume'],
        width, label='Binance', color='#f0b90b', alpha=0.8
        )

    plt.title('Сравнение торговых объемов по биржам', pad=20, fontsize=14)
    plt.xlabel('Время', fontsize=12)
    plt.ylabel('Объем торгов', fontsize=12)

    time_labels = [ts.strftime('%H:%M') for ts in df_bybit.index]
    plt.xticks([i + width for i in x], time_labels, rotation=45)

    plt.legend(fontsize=12)
    plt.grid(axis='y', linestyle='--', alpha=0.7)

    plt.tight_layout()

    os.makedirs('plots', exist_ok=True)

    filepath = 'Graphics/volume_plot.png'
    plt.savefig(filepath, bbox_inches='tight', dpi=120)
    plt.close()

    return filepath


def create_obv_plot(df_bybit, df_okx, df_binance):
    plt.figure(figsize=(14, 7))

    for exchange, df in zip(['Bybit', 'OKX', 'Binance'],
                            [df_bybit, df_okx, df_binance]):
        if 'obv' not in df.columns:
            raise ValueError(
                f"DataFrame для {exchange} не содержит колонку 'obv'"
                )

    for df in [df_bybit, df_okx, df_binance]:
        if not isinstance(df.index, pd.DatetimeIndex):
            df.index = pd.to_datetime(df.index)

    plt.plot(
        df_bybit.index, df_bybit['obv'], label='Bybit',
        color='#2775ca', linewidth=2.5
        )
    plt.plot(
        df_okx.index, df_okx['obv'], label='OKX',
        color='#0ecb81', linewidth=2.5
        )
    plt.plot(
        df_binance.index, df_binance['obv'], label='Binance',
        color='#f0b90b', linewidth=2.5
        )

    plt.title(
        'Сравнение On-Balance Volume (OBV) по биржам', pad=20, fontsize=14
        )
    plt.xlabel(
        'Время', fontsize=12
        )
    plt.ylabel(
        'Значение OBV', fontsize=12
        )

    plt.gca().xaxis.set_major_formatter(
        plt.matplotlib.dates.DateFormatter('%H:%M')
        )
    plt.xticks(
        rotation=45
        )

    plt.legend(fontsize=12, loc='upper left')
    plt.grid(True, linestyle='--', alpha=0.7)

    plt.tight_layout()

    os.makedirs('plots', exist_ok=True)

    filepath = 'Graphics/obv_plot.png'
    plt.savefig(filepath, bbox_inches='tight', dpi=120)
    plt.close()

    return filepath


def create_plot_volume_profiles(volume_bybit, volume_okx, volume_binance):
    combined = pd.DataFrame({
        'Bybit': volume_bybit,
        'OKX': volume_okx,
        'Binance': volume_binance
    }).fillna(0)

    def get_mid_price(interval):
        return (interval.left + interval.right) / 2

    combined['mid_price'] = combined.index.map(get_mid_price)
    combined = combined.sort_values('mid_price', ascending=False).head(20)

    fig, ax = plt.subplots(figsize=(12, 8))

    y_labels = [
        f"{round(interval.left)} - {round(interval.right)}" \
        for interval in combined.index
        ]

    bar_height = 0.25
    indices = range(len(combined))

    ax.barh(
        [i + bar_height for i in indices], combined['Bybit'],
        height=bar_height, label='Bybit', color='#2775ca'
        )
    ax.barh(
        indices, combined['OKX'], height=bar_height,
        label='OKX', color='#0ecb81'
        )
    ax.barh(
        [i - bar_height for i in indices], combined['Binance'],
        height=bar_height, label='Binance', color='#f0b90b'
        )

    ax.set_yticks(indices)
    ax.set_yticklabels(y_labels)
    ax.set_xlabel("Объём торгов")
    ax.set_title("Сравнение объёмного профиля по биржам", fontsize=14)
    ax.grid(True, axis='x', linestyle='--', alpha=0.6)
    ax.legend()

    plt.tight_layout()

    os.makedirs('plots', exist_ok=True)
    path = 'Graphics/volume_profile_comparison.png'
    plt.savefig(path, bbox_inches='tight', dpi=120)
    plt.close()

    return path


def create_plot_vwap(df_bybit, df_okx, df_binance):
    plt.figure(figsize=(14, 7))

    for df in [df_bybit, df_okx, df_binance]:
        if 'vwap' not in df.columns:
            typical = (df['high'] + df['low'] + df['close']) / 3
            df['vwap'] = (typical * df['volume']).cumsum() \
                / df['volume'].cumsum()

    plt.plot(
        df_bybit.index, df_bybit['vwap'], label='Bybit VWAP',
        color='#2775ca', linewidth=2
        )
    plt.plot(
        df_okx.index, df_okx['vwap'], label='OKX VWAP',
        color='#0ecb81', linewidth=2
        )
    plt.plot(
        df_binance.index, df_binance['vwap'], label='Binance VWAP',
        color='#f0b90b', linewidth=2
        )

    plt.title('Сравнение VWAP по биржам', fontsize=14)
    plt.xlabel('Время')
    plt.ylabel('VWAP')
    plt.legend()
    plt.grid(True, linestyle='--', alpha=0.7)
    plt.xticks(rotation=45)

    os.makedirs('plots', exist_ok=True)
    path = 'Graphics/vwap_comparison.png'
    plt.savefig(path, bbox_inches='tight', dpi=120)
    plt.close()
    return path


def create_volume_pie_chart(df_bybit, df_okx, df_binance,
                            pair_name="BTC-USDT"):
    total_volumes = {
        'Bybit': df_bybit['volume'].sum(),
        'OKX': df_okx['volume'].sum(),
        'Binance': df_binance['volume'].sum()
    }

    labels = list(total_volumes.keys())
    sizes = list(total_volumes.values())
    colors = ['#2775ca', '#0ecb81', '#f0b90b']

    patches, texts, autotexts = plt.pie(
        sizes, 
        labels=labels, 
        colors=colors,
        autopct='%1.1f%%',
        startangle=90,
        textprops={'fontsize': 12}
    )

    for autotext in autotexts:
        autotext.set_fontsize(14)
        autotext.set_color('white')

    plt.setp(patches, edgecolor='white', linewidth=2)

    plt.title(
        f'Распределение объемов торгов {pair_name}\nпо биржам',
        fontsize=16, pad=20
        )

    legend_labels = [f'{label}: {size:,.1f}' \
                     for label, size in total_volumes.items()]
    plt.legend(
        patches,
        legend_labels,
        loc='upper right',
        bbox_to_anchor=(1.3, 1),
        fontsize=12
    )

    os.makedirs('plots', exist_ok=True)
    filepath = f'Graphics/volume_pie_{pair_name}.png'
    plt.savefig(filepath, bbox_inches='tight', dpi=120, transparent=False)
    plt.close()

    return filepath
