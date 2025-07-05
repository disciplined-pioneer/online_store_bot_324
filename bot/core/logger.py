import os
import logging
from logging.handlers import RotatingFileHandler


LOG_DIR = "logs"
os.makedirs(LOG_DIR, exist_ok=True)

# Общая функция для создания логгеров
def create_logger(name: str, log_file: str, level=logging.INFO):
    log_path = os.path.join(LOG_DIR, log_file)
    handler = RotatingFileHandler(log_path, maxBytes=5*1024*1024, backupCount=3)
    formatter = logging.Formatter('[%(asctime)s] [%(levelname)s] %(message)s')
    handler.setFormatter(formatter)

    logger = logging.getLogger(name)
    logger.setLevel(level)
    logger.addHandler(handler)
    logger.propagate = False
    return logger

# Логгер для YooKassa
yookassa_logger = create_logger("yookassa", "yookassa.log")
