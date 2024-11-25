import os
from config import LOG_DIR

import logging

logger = logging.getLogger('AppLogger')
logger.setLevel(logging.DEBUG)  # Главный логгер должен улавливать все уровни

def setup_logging():
    """Настройка логирования в папку LOG_DIR"""
    os.makedirs(LOG_DIR, exist_ok=True)  # Создаем папку logs, если ее нет
    
    # формат логов
    log_format = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'

    # Пути для отдельных файлов логов
    info_log_file = os.path.join(LOG_DIR, 'info.log')
    debug_log_file = os.path.join(LOG_DIR, 'debug.log')
    error_log_file = os.path.join(LOG_DIR, 'error.log')

    # Создание главного логгера
    

    # Обработчик для INFO и выше
    info_handler = logging.FileHandler(info_log_file, encoding='utf-8')
    info_handler.setLevel(logging.INFO)  # Логирует INFO, WARNING, ERROR, CRITICAL
    info_handler.setFormatter(logging.Formatter(log_format))

    # Обработчик для DEBUG
    debug_handler = logging.FileHandler(debug_log_file, encoding='utf-8')
    debug_handler.setLevel(logging.DEBUG)  # Логирует DEBUG и выше
    debug_handler.setFormatter(logging.Formatter(log_format))

    # Обработчик для WARNING и выше (включает ERROR и CRITICAL)
    error_handler = logging.FileHandler(error_log_file, encoding='utf-8')
    error_handler.setLevel(logging.WARNING)  # Логирует WARNING, ERROR, CRITICAL
    error_handler.setFormatter(logging.Formatter(log_format))

    # Обработчик для консоли (опционально)
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)  # Логирует INFO и выше
    console_handler.setFormatter(logging.Formatter(log_format))

    # Добавляем обработчики к логгеру
    logger.addHandler(info_handler)
    logger.addHandler(debug_handler)
    logger.addHandler(error_handler)
    logger.addHandler(console_handler)


    logging.info("Логирование настроено")