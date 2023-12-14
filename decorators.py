from datetime import datetime, time
import logging
from typing import Callable


def within_time_interval(start_time: str, end_time: str) -> Callable:
    def decorator(func: Callable) -> Callable:
        def wrapper(*args, **kwargs):
            current_time = datetime.now().time()
            start = time(*map(int, start_time.split(':')))
            end = time(*map(int, end_time.split(':')))
            if start <= current_time <= end:
                result = func(*args, **kwargs)
                return result
            else:
                logging.info(f"Function '{func.__name__}' is not executed outside the time interval.")
        return wrapper
    return decorator
