from functools import wraps

from termcolor import colored

IS_DEBUG = True
PREFIX = "http://localhost:5000"


def debug(*args, **kwargs):
    """
    Print debug information if IS_DEBUG is True.

    This function acts as a wrapper around the built-in print function,
    but only outputs if the global IS_DEBUG flag is set to True.

    Args:
        *args: Variable length argument list to be printed.
        **kwargs: Arbitrary keyword arguments to be passed to the print function.
    """
    if IS_DEBUG:
        print(*args, **kwargs)


def logged(message: str = None, print_args=True, print_ret=True):
    """
    A decorator that logs the execution of a function.

    This decorator prints information about the function call, including
    the function name, arguments, and return value.

    Args:
        message (str, optional): A custom message to print. If None, the function name is used.
        print_args (bool): Whether to print the function arguments. Defaults to True.
        print_ret (bool): Whether to print the function return value. Defaults to True.

    Returns:
        function: The decorated function.
    """

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
    """
    Assert that two values are equal and print the result.

    This function compares two values and raises an exception if they are not equal.
    It also prints colored output indicating whether the assertion passed or failed.

    Args:
        actual (any): The actual value to compare.
        expect (any): The expected value to compare against.
        message (str, optional): A custom message to print with the assertion.

    Raises:
        Exception: If the actual value does not equal the expected value.
    """
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
    """
    A decorator that prints the name of a test function.

    This decorator is used to label and identify test functions.

    Args:
        name (str): The name of the test to be printed.

    Returns:
        function: The decorated function.
    """

    def decorator(func):
        print(name)

    return decorator


def before(before_func):
    """
    A decorator that runs a function before the decorated function.

    This decorator is typically used in testing to set up preconditions.

    Args:
        before_func (function): The function to run before the decorated function.

    Returns:
        function: The decorated function.
    """

    def decorator(func):
        before_func()
        func()

    return decorator


def after(after_func):
    """
    A decorator that runs a function after the decorated function.

    This decorator is typically used in testing to clean up after a test.

    Args:
        after_func (function): The function to run after the decorated function.

    Returns:
        function: The decorated function.
    """

    def decorator(func):
        func()
        after_func()

    return decorator
