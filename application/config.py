import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent  # 根路径
RUNTIME_PATH = os.path.join(BASE_DIR, 'runtime')  # 运行环境目录
LOG_PATH = os.path.join(RUNTIME_PATH, 'log')  # 日志目录
CURSOR_FILE_PATH = os.path.join(RUNTIME_PATH, 'cursors')  # 游标缓存文件目录
TEMP_PATH = os.path.join(RUNTIME_PATH, 'temp')  # 临时文件路径
UPLOAD_PATH = os.path.join(RUNTIME_PATH, 'upload')  # 上传文件路径
EXTEND_PATH = os.path.join(BASE_DIR, 'extend')  # 依赖文件路径
ES_MAPPING_PATH = os.path.join(EXTEND_PATH, 'elastic_db', 'mapping')
