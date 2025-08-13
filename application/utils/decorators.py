import functools
from application.utils.logger import get_logger


def log_execution(func):
    """
    装饰器，用于记录方法执行日志
    """
    logger = get_logger(func.__module__)
    
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        logger.info(f"开始执行 {func.__name__}")
        try:
            result = func(*args, **kwargs)
            logger.info(f"执行 {func.__name__} 完成")
            return result
        except Exception as e:
            logger.error(f"执行 {func.__name__} 时发生错误: {e}")
            raise
    return wrapper


def monitor_performance(func):
    """
    装饰器，用于监控方法执行性能
    """
    logger = get_logger(func.__module__)
    
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        import time
        start_time = time.time()
        try:
            result = func(*args, **kwargs)
            return result
        finally:
            end_time = time.time()
            logger.info(f"{func.__name__} 执行耗时: {end_time - start_time:.2f}秒")
    return wrapper