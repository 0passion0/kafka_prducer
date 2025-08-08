import os
from datetime import datetime

from config import DEFAULT_CURSOR_FILE_PATH
from cursor_model.base_cursor import CursorManager


class FileCursorManager(CursorManager):
    """基于文件的游标管理器"""

    def __init__(self, collection, topic, key, file_path: str = None, ):
        self.file_path = file_path or DEFAULT_CURSOR_FILE_PATH + collection + '_' + topic + '_' + key + '.cursor'

    def load(self, full_amount=False):
        """
        从文件加载游标
        """
        if not os.path.exists(self.file_path) or full_amount:
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

# class StateRepository:
#     """本地增量游标持久化"""

#     def __init__(self, file_path: str = None):
#         self.file_path = file_path or DEFAULT_CURSOR_FILE_PATH
#         self.last_min_id = '000000000000000000000000'

#     def load(self) -> datetime:
#         return self.last_min_id
#         # if not os.path.exists(self.file_path):
#         #     return ObjectId(self.last_min_id)
#         # with open(self.file_path) as f:
#         #     try:
#         #         ts_str = f.read().strip().splitlines()[-1].strip()
#         #         if not ts_str:
#         #             raise ValueError
#         #         return ObjectId(ts_str)
#         #     except (IndexError, ValueError):
#         #         # 文件内容异常也退回最小日期
#         #         return ObjectId(self.last_min_id)

#     def save(self, max_id) -> None:
#         with open(self.file_path, "w") as f:
#             f.write("\n" + str(max_id))
