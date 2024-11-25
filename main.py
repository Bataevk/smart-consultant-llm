import os
import argparse

# local import
from config import LOG_DIR
from server import *

from utils.logs_module import setup_logging, logger


def parse_arguments():
    """Создает и возвращает парсер аргументов командной строки."""
    parser = argparse.ArgumentParser(description="Запуск веб-сервера")
    parser.add_argument("--host", type=str, default="0.0.0.0", help="Хост для запуска (по умолчанию: 0.0.0.0)")
    parser.add_argument("--port", type=int, default=5000, help="Порт для запуска (по умолчанию: 5000)")
    parser.add_argument("--logs", type=bool, default=True, help="Логирование приложения")
    return parser.parse_args()

def main():
    """Главная точка входа в приложение."""
    # Парсинг аргументов
    args = parse_arguments()

    if args.logs:
        # Настройка логирования
        setup_logging()

    # Запуск приложения
    logger.info(f"Запуск приложения на {args.host}:{args.port}")
    start_server(host=args.host, port=args.port)

if __name__ == "__main__":
    main()

