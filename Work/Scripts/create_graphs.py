import os
import pandas as pd
import matplotlib.pyplot as plt
from pathlib import Path


Path("Graphics").mkdir(exist_ok=True)  # Создание папки Graphics, если она не существует


def create_volume_plot(df_bybit, df_okx, df_binance):
    # Функция для создания графика сравнения торговых объемов по трем биржам
    # Инициализация фигуры графика с заданными размерами
    plt.figure(figsize=(14, 7))

    # Проверка и преобразование индекса каждого DataFrame в формат DatetimeIndex
    # Это необходимо для корректного отображения времени на оси X
    for df in [df_bybit, df_okx, df_binance]:
        if not isinstance(df.index, pd.DatetimeIndex):
            df.index = pd.to_datetime(df.index)

    # Создание списка индексов для оси X на основе длины данных Bybit
    x = range(len(df_bybit))

    # Определение ширины столбцов для гистограммы
    width = 0.25

    # Построение столбца для объемов Bybit с заданным цветом и прозрачностью
    plt.bar(
        x, df_bybit['volume'], width, label='Bybit',
        color='#2775ca', alpha=0.8
        )
    # Построение столбца для объемов OKX, сдвинутого вправо на ширину
    plt.bar(
        [i + width for i in x], df_okx['volume'], width,
        label='OKX', color='#0ecb81', alpha=0.8
        )
    # Построение столбца для объемов Binance, сдвинутого еще на одну ширину
    plt.bar(
        [i + 2*width for i in x], df_binance['volume'],
        width, label='Binance', color='#f0b90b', alpha=0.8
        )

    # Установка заголовка графика с отступом и размером шрифта
    plt.title('Сравнение торговых объемов по биржам', pad=20, fontsize=14)
    # Установка подписи для оси X
    plt.xlabel('Время', fontsize=12)
    # Установка подписи для оси Y
    plt.ylabel('Объем торгов', fontsize=12)

    # Форматирование меток времени для оси X из индекса Bybit
    time_labels = [ts.strftime('%H:%M') for ts in df_bybit.index]
    # Установка меток времени на оси X с поворотом для читаемости
    plt.xticks([i + width for i in x], time_labels, rotation=45)

    # Добавление легенды с указанным размером шрифта
    plt.legend(fontsize=12)
    # Добавление сетки по оси Y для улучшения читаемости
    plt.grid(axis='y', linestyle='--', alpha=0.7)

    # Автоматическая корректировка макета для предотвращения наложения элементов
    plt.tight_layout()

    # Создание папки plots, если она не существует
    os.makedirs('plots', exist_ok=True)

    # Определение пути для сохранения графика
    filepath = 'Graphics/volume_plot.png'
    # Сохранение графика в файл с заданными параметрами
    plt.savefig(filepath, bbox_inches='tight', dpi=120)
    # Закрытие фигуры для освобождения памяти
    plt.close()

    # Возвращение пути к сохраненному файлу
    return filepath


def create_obv_plot(df_bybit, df_okx, df_binance):
    # Функция для создания графика сравнения индикатора OBV по трем биржам
    # Инициализация фигуры графика с заданными размерами
    plt.figure(figsize=(14, 7))

    # Проверка наличия колонки 'obv' в каждом DataFrame
    for exchange, df in zip(['Bybit', 'OKX', 'Binance'],
                            [df_bybit, df_okx, df_binance]):
        if 'obv' not in df.columns:
            raise ValueError(
                f"DataFrame для {exchange} не содержит колонку 'obv'"
                )

    # Проверка и преобразование индекса каждого DataFrame в формат DatetimeIndex
    for df in [df_bybit, df_okx, df_binance]:
        if not isinstance(df.index, pd.DatetimeIndex):
            df.index = pd.to_datetime(df.index)

    # Построение линии для OBV Bybit с заданным цветом и толщиной
    plt.plot(
        df_bybit.index, df_bybit['obv'], label='Bybit',
        color='#2775ca', linewidth=2.5
        )
    # Построение линии для OBV OKX с заданным цветом и толщиной
    plt.plot(
        df_okx.index, df_okx['obv'], label='OKX',
        color='#0ecb81', linewidth=2.5
        )
    # Построение линии для OBV Binance с заданным цветом и толщиной
    plt.plot(
        df_binance.index, df_binance['obv'], label='Binance',
        color='#f0b90b', linewidth=2.5
        )

    # Установка заголовка графика с отступом и размером шрифта
    plt.title(
        'Сравнение On-Balance Volume (OBV) по биржам', pad=20, fontsize=14
        )
    # Установка подписи для оси X
    plt.xlabel(
        'Время', fontsize=12
        )
    # Установка подписи для оси Y
    plt.ylabel(
        'Значение OBV', fontsize=12
        )

    # Настройка формата времени на оси X
    plt.gca().xaxis.set_major_formatter(
        plt.matplotlib.dates.DateFormatter('%H:%M')
        )
    # Поворот меток оси X для улучшения читаемости
    plt.xticks(
        rotation=45
        )

    # Добавление легенды с указанным размером шрифта и позицией
    plt.legend(fontsize=12, loc='upper left')
    # Добавление сетки для улучшения визуального восприятия
    plt.grid(True, linestyle='--', alpha=0.7)

    # Автоматическая корректировка макета
    plt.tight_layout()

    # Создание папки plots, если она не существует
    os.makedirs('plots', exist_ok=True)

    # Определение пути для сохранения графика
    filepath = 'Graphics/obv_plot.png'
    # Сохранение графика в файл с заданными параметрами
    plt.savefig(filepath, bbox_inches='tight', dpi=120)
    # Закрытие фигуры для освобождения памяти
    plt.close()

    # Возвращение пути к сохраненному файлу
    return filepath


def create_plot_volume_profiles(volume_bybit, volume_okx, volume_binance):
    # Функция для создания горизонтального графика объемного профиля по биржам
    # Объединение данных в один DataFrame и заполнение пропусков нулями
    combined = pd.DataFrame({
        'Bybit': volume_bybit,
        'OKX': volume_okx,
        'Binance': volume_binance
    }).fillna(0)

    # Определение функции для вычисления средней цены интервала
    def get_mid_price(interval):
        return (interval.left + interval.right) / 2

    # Добавление столбца с средней ценой для каждого интервала
    combined['mid_price'] = combined.index.map(get_mid_price)
    # Сортировка данных по средней цене и выбор топ-20
    combined = combined.sort_values('mid_price', ascending=False).head(20)

    # Создание фигуры и осей для графика
    fig, ax = plt.subplots(figsize=(12, 8))

    # Форматирование меток для оси Y на основе границ интервалов
    y_labels = [
        f"{round(interval.left)} - {round(interval.right)}"
        for interval in combined.index
        ]

    # Определение высоты столбцов для горизонтальной гистограммы
    bar_height = 0.25
    # Создание списка индексов для построения столбцов
    indices = range(len(combined))

    # Построение горизонтального столбца для Bybit с заданным цветом
    ax.barh(
        [i + bar_height for i in indices], combined['Bybit'],
        height=bar_height, label='Bybit', color='#2775ca'
        )
    # Построение горизонтального столбца для OKX с заданным цветом
    ax.barh(
        indices, combined['OKX'], height=bar_height,
        label='OKX', color='#0ecb81'
        )
    # Построение горизонтального столбца для Binance с заданным цветом
    ax.barh(
        [i - bar_height for i in indices], combined['Binance'],
        height=bar_height, label='Binance', color='#f0b90b'
        )

    # Установка меток по оси Y
    ax.set_yticks(indices)
    # Присвоение отформатированных меток оси Y
    ax.set_yticklabels(y_labels)
    # Установка подписи для оси X
    ax.set_xlabel("Объём торгов")
    # Установка заголовка графика
    ax.set_title("Сравнение объёмного профиля по биржам", fontsize=14)
    # Добавление сетки по оси X для улучшения читаемости
    ax.grid(True, axis='x', linestyle='--', alpha=0.6)
    # Добавление легенды
    ax.legend()

    # Автоматическая корректировка макета
    plt.tight_layout()

    # Создание папки plots, если она не существует
    os.makedirs('plots', exist_ok=True)
    # Определение пути для сохранения графика
    path = 'Graphics/volume_profile_comparison.png'
    # Сохранение графика в файл с заданными параметрами
    plt.savefig(path, bbox_inches='tight', dpi=120)
    # Закрытие фигуры для освобождения памяти
    plt.close()

    # Возвращение пути к сохраненному файлу
    return path


def create_plot_vwap(df_bybit, df_okx, df_binance):
    # Функция для создания графика сравнения VWAP по биржам
    # Инициализация фигуры графика с заданными размерами
    plt.figure(figsize=(14, 7))

    # Проверка наличия колонки 'vwap' и вычисление ее, если отсутствует
    for df in [df_bybit, df_okx, df_binance]:
        if 'vwap' not in df.columns:
            typical = (df['high'] + df['low'] + df['close']) / 3
            df['vwap'] = (typical * df['volume']).cumsum() \
                / df['volume'].cumsum()

    # Построение линии для VWAP Bybit с заданным цветом и толщиной
    plt.plot(
        df_bybit.index, df_bybit['vwap'], label='Bybit VWAP',
        color='#2775ca', linewidth=2
        )
    # Построение линии для VWAP OKX с заданным цветом и толщиной
    plt.plot(
        df_okx.index, df_okx['vwap'], label='OKX VWAP',
        color='#0ecb81', linewidth=2
        )
    # Построение линии для VWAP Binance с заданным цветом и толщиной
    plt.plot(
        df_binance.index, df_binance['vwap'], label='Binance VWAP',
        color='#f0b90b', linewidth=2
        )

    # Установка заголовка графика
    plt.title('Сравнение VWAP по биржам', fontsize=14)
    # Установка подписи для оси X
    plt.xlabel('Время')
    # Установка подписи для оси Y
    plt.ylabel('VWAP')
    # Добавление легенды
    plt.legend()
    # Добавление сетки для улучшения визуального восприятия
    plt.grid(True, linestyle='--', alpha=0.7)
    # Поворот меток оси X для улучшения читаемости
    plt.xticks(rotation=45)

    # Создание папки plots, если она не существует
    os.makedirs('plots', exist_ok=True)
    # Определение пути для сохранения графика
    path = 'Graphics/vwap_comparison.png'
    # Сохранение графика в файл с заданными параметрами
    plt.savefig(path, bbox_inches='tight', dpi=120)
    # Закрытие фигуры для освобождения памяти
    plt.close()
    # Возвращение пути к сохраненному файлу
    return path


def create_volume_pie_chart(df_bybit, df_okx, df_binance,
                            pair_name="BTC-USDT"):
    # Функция для создания круговой диаграммы распределения торговых объемов
    # Вычисление суммарных объемов для каждой биржи
    total_volumes = {
        'Bybit': df_bybit['volume'].sum(),
        'OKX': df_okx['volume'].sum(),
        'Binance': df_binance['volume'].sum()
    }

    # Извлечение меток и значений для диаграммы
    labels = list(total_volumes.keys())
    sizes = list(total_volumes.values())
    # Определение цветов для каждого сектора диаграммы
    colors = ['#2775ca', '#0ecb81', '#f0b90b']

    # Построение круговой диаграммы с настройками отображения
    patches, texts, autotexts = plt.pie(
        sizes,
        labels=labels,
        colors=colors,
        autopct='%1.1f%%',
        startangle=90,
        textprops={'fontsize': 12}
    )

    # Настройка стиля текста процентных значений
    for autotext in autotexts:
        autotext.set_fontsize(14)
        autotext.set_color('white')

    # Установка границ секторов с белой линией
    plt.setp(patches, edgecolor='white', linewidth=2)

    # Установка заголовка с учетом имени торговой пары
    plt.title(
        f'Распределение объемов торгов {pair_name}\nпо биржам',
        fontsize=16, pad=20
        )

    # Форматирование меток для легенды с объемами
    legend_labels = [f'{label}: {size:,.1f}'
                     for label, size in total_volumes.items()]
    # Добавление легенды с расширенными метками
    plt.legend(
        patches,
        legend_labels,
        loc='upper right',
        bbox_to_anchor=(1.3, 1),
        fontsize=12
    )

    # Создание папки plots, если она не существует
    os.makedirs('plots', exist_ok=True)
    # Определение пути для сохранения графика с учетом имени пары
    filepath = f'Graphics/volume_pie_{pair_name}.png'
    # Сохранение графика в файл с заданными параметрами
    plt.savefig(filepath, bbox_inches='tight', dpi=120, transparent=False)
    # Закрытие фигуры для освобождения памяти
    plt.close()

    # Возвращение пути к сохраненному файлу
    return filepath
