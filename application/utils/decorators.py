import functools
import json

from application.utils.logger import get_logger


def log_execution(func):
    """
    装饰器，用于记录方法执行日志，包括输入参数、输出结果及异常信息
    """
    logger = get_logger(func.__module__)

    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        # 记录输入参数（转为可序列化字符串）
        try:
            args_str = json.dumps(args, ensure_ascii=False, default=str)
            kwargs_str = json.dumps(kwargs, ensure_ascii=False, default=str)
        except Exception:
            args_str, kwargs_str = str(args), str(kwargs)

        logger.info(f"[{func.__name__}] 开始执行，输入参数: args={args_str}, kwargs={kwargs_str}")

        try:
            result = func(*args, **kwargs)

            # 记录输出结果（如果可序列化）
            try:
                result_str = json.dumps(result, ensure_ascii=False, default=str)
            except Exception:
                result_str = str(result)

            logger.info(f"[{func.__name__}] 执行完成，输出结果: {result_str}")
            return result
        except Exception as e:
            logger.exception(f"[{func.__name__}] 执行发生错误: {e}")
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
