from functools import wraps

from termcolor import colored

IS_DEBUG = True
PREFIX = "http://localhost:5000"


def debug(*args, **kwargs):
    if IS_DEBUG:
        print(*args, **kwargs)


def logged(message: str = None, print_args=True, print_ret=True):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            nonlocal message
            if message is None:
                message = func.__name__
            debug(
                colored("running", "green"),
                message,
                colored(f"args={args}" if args else "", "dark_grey"),
                colored(f"kwargs={kwargs}" if kwargs else "", "dark_grey"),
            )
            r = func(*args, **kwargs)
            debug(
                colored("done", "green"),
                message,
                colored(f"return={r}" if r else "", "dark_grey"),
            )
            return r

        return wrapper

    return decorator


def assert_eq(actual: any, expect: any, message: str = None):
    if actual == expect:
        message = colored(message, "white", attrs=["bold"]) if message else None
        debug(colored("assert_eq", "green"), end=" ")
        if message:
            debug(message, end=" ")
        debug(colored(f"{actual} == {expect}", "dark_grey"))
    else:
        message = colored(message, "red", attrs=["bold"]) if message else None
        debug(colored("assert_eq", "red", attrs=["bold"]), end=" ")
        if message:
            debug(message, end=" ")
        debug(colored(f"{actual} == {expect}", "red"))
        raise Exception(f"{actual} != {expect}")


def test(name: str):
    def decorator(func):
        print(name)

    return decorator


def before(before_func):
    def decorator(func):
        before_func()
        func()

    return decorator


def after(after_func):
    def decorator(func):
        func()
        after_func()

    return decorator
