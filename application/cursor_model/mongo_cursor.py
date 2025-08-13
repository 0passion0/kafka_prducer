import os
from os.path import join

from application.config import CURSOR_FILE_PATH
from application.cursor_model.base_cursor import CursorManager


class FileCursorManager(CursorManager):
    """基于文件的游标管理器"""

    def __init__(self, collection, topic, full_amount=False, root_file_path: str = None, ):
        root_file_path = root_file_path or CURSOR_FILE_PATH

        base_dir = join(root_file_path, topic, collection)
        self.file_path = join(base_dir, f'cursor.db')
        self.full_amount = full_amount

    def load(self):
        """
        从文件加载游标
        """
        if not os.path.exists(self.file_path) or self.full_amount:
            return None
        with open(self.file_path) as f:
            try:
                cursor_str = f.read().strip().splitlines()[-1].strip()
                if not cursor_str:
                    raise ValueError
                return cursor_str
            except (IndexError, ValueError):
                # 文件内容异常也退回默认游标
                return None

    def save(self, cursor) -> None:
        """
        将游标保存到文件
        """
        # 确保目录存在
        os.makedirs(os.path.dirname(self.file_path), exist_ok=True)
        with open(self.file_path, "w") as f:
            f.write(str(cursor))
