"""
Timing decorators and utilities for measuring function execution time.
"""

import time
from functools import wraps


def measure_time_async(func):
    """
    Decorator to measure the execution time of async functions.
    
    Args:
        func: The async function to measure
        
    Returns:
        Wrapper function that prints execution time and returns the original result
        
    Example:
        @measure_time_async
        async def my_async_function():
            await asyncio.sleep(1)
            return "done"
    """
    @wraps(func)
    async def wrapper(*args, **kwargs):
        start = time.perf_counter()
        result = await func(*args, **kwargs)
        end = time.perf_counter()
        print(f"{func.__name__} elapsed: {end - start:.4f}s")
        return result
    return wrapper