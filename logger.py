import logging
import os
import sys
import time
from datetime import datetime

from config import DEFAULT_CURSOR_FILE_PATH


class StateRepository:
    """本地增量游标持久化"""
    def __init__(self, file_path: str = None):
        self.file_path = file_path or DEFAULT_CURSOR_FILE_PATH
        self.last_min_id = '000000000000000000000000'
    def load(self) -> datetime:
        return self.last_min_id
        # if not os.path.exists(self.file_path):
        #     return ObjectId(self.last_min_id)
        # with open(self.file_path) as f:
        #     try:
        #         ts_str = f.read().strip().splitlines()[-1].strip()
        #         if not ts_str:
        #             raise ValueError
        #         return ObjectId(ts_str)
        #     except (IndexError, ValueError):
        #         # 文件内容异常也退回最小日期
        #         return ObjectId(self.last_min_id)

    def save(self, max_id) -> None:
        with open(self.file_path, "w") as f:
            f.write("\n" + str(max_id))


def get_logger(name: str) -> logging.Logger:
    logger = logging.getLogger(name)
    if logger.handlers:  # 避免重复 addHandler
        return logger
    logger.setLevel(logging.INFO)
    handler = logging.StreamHandler(sys.stdout)
    fmt = "[%(asctime)s] [%(levelname)s] [%(name)s] %(message)s"
    handler.setFormatter(logging.Formatter(fmt))
    logger.addHandler(handler)
    return logger
