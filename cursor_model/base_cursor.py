import logging
import os
import sys
import time
from datetime import datetime
from abc import ABC, abstractmethod


class CursorManager(ABC):
    """
    游标管理抽象基类
    """
    @abstractmethod
    def load(self):
        pass

    @abstractmethod
    def save(self, cursor):
        pass
