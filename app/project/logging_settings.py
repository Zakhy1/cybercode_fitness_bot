import logging
import os
import glob
import time
from logging.handlers import TimedRotatingFileHandler
from datetime import datetime

# Папка для логов
log_dir = "logs"

os.makedirs(log_dir, exist_ok=True)
os.makedirs(os.path.join(log_dir, "error"), exist_ok=True)
os.makedirs(os.path.join(log_dir, "info"), exist_ok=True)

# Количество дней для хранения логов
log_retention_days = 60

# Формат логов
log_format = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
date_format = "%Y-%m-%d %H:%M:%S"

# Получаем текущую дату для имени файла
current_date = datetime.now().strftime("%Y-%m-%d")


# Функция для удаления старых логов
def cleanup_old_logs(log_directory, retention_days):
    cutoff_time = time.time() - (retention_days * 86400)  # Время отсечения
    for log_file in glob.glob(os.path.join(log_directory, "*.log*")):
        if os.path.isfile(log_file) and os.path.getmtime(
                log_file) < cutoff_time:
            os.remove(log_file)
            print(f"Удален старый лог: {log_file}")


# Настройка логирования
def setup_logger(name, level, filename):
    handler = TimedRotatingFileHandler(
        filename=os.path.join(log_dir, filename),
        when="midnight",
        interval=1,
        backupCount=30,  # Хранение ротации логов
        encoding="utf-8",
        utc=True  # Использовать UTC время для ротации
    )
    handler.setLevel(level)
    handler.setFormatter(logging.Formatter(log_format, date_format))

    logger = logging.getLogger(name)
    logger.setLevel(level)
    logger.addHandler(handler)
    return logger


# Создание логгеров
info_logger = setup_logger("info_logger", logging.INFO, "info/info.log")
error_logger = setup_logger("error_logger", logging.ERROR, "error/error.log")

# Удаляем старые логи
cleanup_old_logs(log_dir, log_retention_days)

# Тест логов
# info_logger.info("Это информационное сообщение")
# error_logger.error("Это сообщение об ошибке")
