
import functools
import requests


def retryrequest(status_code=None, retries=4):
    if status_code is None:
        status_code = range(500, 600)
    if not isinstance(status_code, (list, tuple)):
        status_code = [status_code]

    def decorator_retry(func):
        @functools.wraps(func)
        def wrapper_retry(*args, **kwargs):
            tries = 0
            while True:
                tries += 1
                try:
                    result = func(*args, **kwargs)
                    break
                except requests.exceptions.HTTPError as e:
                    if e.response.status_code not in status_code:
                        raise
                    if tries >= retries:
                        raise
                    print(e)
                    print("Retrying")
            return result
        return wrapper_retry
    return decorator_retry
