import logging

# Имя файла для сохранения логов ошибок
LOG_FILENAME = 'Output/error_log.txt'

# Настройка конфигурации логирования
logging.basicConfig(
    filename=LOG_FILENAME,
    level=logging.ERROR,
    format='%(asctime)s [%(levelname)s] [%(module)s] %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)


def log_error(message: str):
    # Логирование ошибки и вывод в консоль
    logging.error(message)
    print(f"[ERROR] {message}")


def log_warning(message: str):
    # Логирование предупреждения и вывод в консоль
    logging.warning(message)
    print(f"[WARNING] {message}")
    