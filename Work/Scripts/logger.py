import logging
from datetime import datetime

LOG_FILENAME = 'Output/error_log.txt'

logging.basicConfig(
    filename=LOG_FILENAME,
    level=logging.ERROR,
    format='%(asctime)s [%(levelname)s] [%(module)s] %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)


def log_error(message: str):
    logging.error(message)
    print(f"[ERROR] {message}")


def log_warning(message: str):
    logging.warning(message)
    print(f"[WARNING] {message}")