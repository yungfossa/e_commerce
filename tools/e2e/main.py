import time
from dataclasses import dataclass
from functools import wraps
from typing import Self

import requests
from termcolor import colored

PREFIX = "http://localhost:5000"


def logged(message: str = None, print_args=True, print_ret=True):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            nonlocal message
            if message is None:
                message = func.__name__
            print(
                colored("running", "green"),
                message,
                colored(f"args={args}" if args else "", "dark_grey"),
                colored(f"kwargs={kwargs}" if kwargs else "", "dark_grey"),
            )
            r = func(*args, **kwargs)
            print(
                colored("done", "green"),
                message,
                colored(f"return={r}" if r else "", "dark_grey"),
            )
            return r

        return wrapper

    return decorator

def assert_eq(actual: any, expect: any, message: str = None):
    if actual == expect:
        print(colored('assert_eq', 'green'), colored(f'{actual} == {expect}', 'dark_grey'))
    else:
        print(colored('assert_eq', 'red', attrs=['bold']), colored(f'{actual} == {expect}', 'red'))

# TODO each method should check whether verification is a prerequisite
# TODO allow to refresh access token, this is also missing in the backend


@dataclass
class User:
    email: str
    password: str
    name: str
    surname: str

    verification_token: str
    access_token: str

    @logged()
    @staticmethod
    def signup(email: str, password: str, name: str, surname: str) -> Self:
        s = requests.Session()

        r = s.post(
            f"{PREFIX}/signup",
            json={
                "email": email,
                "password": password,
                "name": name,
                "surname": surname,
            },
        )

        assert_eq(r.status_code, 201)

        return User(
            email, password, name, surname, r.json()["data"]["verification_token"], None
        )

    @logged()
    def verify(self):
        s = requests.Session()

        r = s.get(f"{PREFIX}/verify/{self.verification_token}")

        assert_eq(r.status_code, 200)

        return User(self.email, self.password, self.name, self.surname, None, None)

    @logged()
    def login(self) -> Self:
        s = requests.Session()

        r = s.post(
            f"{PREFIX}/login",
            json={
                "email": self.email,
                "password": self.password,
            },
        )

        assert_eq(r.status_code, 200)

        return User(
            self.email,
            self.password,
            self.name,
            self.surname,
            None,
            r.json()["data"]["access_token"],
        )


user_1 = (
    User.signup(f"{time.time()}@gmail.com", "Password1?", "foo", "bar").verify().login()
)

user_2 = (
    User.signup(f"{time.time()}@gmail.com", "Password1?", "foo", "bar").verify().login()
)
