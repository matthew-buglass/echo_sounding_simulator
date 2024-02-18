from functools import wraps
import time
from typing import Callable, Any


def timed(func: Callable) -> Callable:
    """
    Function decorator for monitoring execution time

    Args:
        func: The function to time

    Returns:
        result: the result of the function
    """
    @wraps(func)
    def timed_wrapper(*args, **kwargs) -> (Any, float):
        start_time = time.perf_counter()
        result = func(*args, **kwargs)
        end_time = time.perf_counter()
        total_time = end_time - start_time
        print(f'Function {func.__name__}{args} {kwargs} Took {total_time:.5f} seconds')
        return result
    return timed_wrapper
