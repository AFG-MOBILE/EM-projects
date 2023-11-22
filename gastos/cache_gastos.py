import functools
import datetime
import os

def get_cache_filename(func_name):
    return f"{func_name}_cache_clear.txt"

def daily_cache_clear(func):
    cache_file = get_cache_filename(func.__name__)

    if os.path.exists(cache_file):
        with open(cache_file, 'r') as f:
            last_cleared_str = f.read().strip()
            last_cleared = datetime.datetime.fromisoformat(last_cleared_str)
    else:
        last_cleared = datetime.datetime.now()

    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        nonlocal last_cleared
        current_time = datetime.datetime.now()
        delta = current_time - last_cleared

        if delta.days >= 1:
            func.cache_clear()  # Limpa o cache
            last_cleared = current_time
            with open(cache_file, 'w') as f:
                f.write(current_time.isoformat())

        return func(*args, **kwargs)

    return wrapper