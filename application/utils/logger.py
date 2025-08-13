import logging
import sys
import os
from datetime import datetime

from application.config import LOG_PATH


def get_logger(name: str) -> logging.Logger:
    logger = logging.getLogger(name)
    if logger.handlers:  # 避免重复 addHandler
        return logger
    logger.setLevel(logging.INFO)
    
    # 创建日志目录
    log_dir = LOG_PATH
    os.makedirs(log_dir, exist_ok=True)
    
    # 创建文件处理器，以日期命名日志文件
    log_filename = datetime.now().strftime('%Y-%m-%d') + '.log'
    file_handler = logging.FileHandler(os.path.join(log_dir, log_filename), encoding='utf-8')
    file_formatter = logging.Formatter("[%(asctime)s] [%(levelname)s] [%(name)s] %(message)s")
    file_handler.setFormatter(file_formatter)
    logger.addHandler(file_handler)
    
    # 保留控制台输出
    console_handler = logging.StreamHandler(sys.stdout)
    console_formatter = logging.Formatter("[%(asctime)s] [%(levelname)s] [%(name)s] %(message)s")
    console_handler.setFormatter(console_formatter)
    logger.addHandler(console_handler)
    
    return logger