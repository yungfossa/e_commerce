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
        message = colored(message, "white", attrs=["bold"]) if message else None
        print(colored("assert_eq", "green"), end=" ")
        if message:
            print(message, end=" ")
        print(colored(f"{actual} == {expect}", "dark_grey"))
    else:
        message = colored(message, "red", attrs=["bold"]) if message else None
        print(colored("assert_eq", "red", attrs=["bold"]), end=" ")
        if message:
            print(message, end=" ")
        print(colored(f"{actual} == {expect}", "red"))


@dataclass
class Admin:
    # TODO as it is now, the assertions are mixed between the client classes and the unit tests, this should be decoupled
    email: str
    password: str

    access_token: str

    @logged()
    @staticmethod
    def login(email: str, password: str) -> Self:
        s = requests.Session()

        r = s.post(
            f"{PREFIX}/login",
            json={
                "email": email,
                "password": password,
            },
        )

        assert_eq(r.status_code, 200)

        return Admin(
            email,
            password,
            r.json()["data"]["access_token"],
        )

    @logged()
    def add_category(self, name: str):
        s = requests.Session()

        r = s.put(
            f"{PREFIX}/admin/category",
            headers={"Authorization": f"Bearer {self.access_token}"},
            json={"category_title": name},
        )

        assert_eq(r.status_code, 200)

        return r.json()["data"]


@dataclass
class User:
    # TODO each method should check whether verification is a prerequisite
    # TODO allow to refresh access token, this is also missing in the backend

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

    @logged()
    def profile(self):
        s = requests.Session()
        r = s.get(
            f"{PREFIX}/profile",
            headers={"Authorization": f"Bearer {self.access_token}"},
        )

        assert_eq(r.status_code, 200)

        return r.json()["data"]

    @logged()
    def cart(self):
        s = requests.Session()
        r = s.get(
            f"{PREFIX}/cart",
            headers={"Authorization": f"Bearer {self.access_token}"},
        )

        assert_eq(r.status_code, 200)

        return r.json()["data"]

    @logged()
    def get_categories(self):
        s = requests.Session()
        r = s.get(
            f"{PREFIX}/categories",
            headers={"Authorization": f"Bearer {self.access_token}"},
        )

        assert_eq(r.status_code, 200)

        return r.json()["data"]


# TODO these tests should be named and chunked

admin = Admin.login("admin@shopsphere.com", "changeme")

# create 3 users, we are not testing for failures here
users = [
    User.signup(f"{time.time()}@gmail.com", "Password1?", "foo", "bar")
    .verify()
    .login(),
    User.signup(f"{time.time()}@gmail.com", "Password1?", "foo", "bar")
    .verify()
    .login(),
    User.signup(f"{time.time()}@gmail.com", "Password1?", "foo", "bar")
    .verify()
    .login(),
]

u = users[0]

# make sure the cart is empty
cart = u.cart()
assert_eq(len(cart["cart_entries"]), 0, "cart must be empty")
assert_eq(cart["cart_total"], 0, "cart amount must be equal to 0")

# make sure the admin can create new categories
categories = u.get_categories()
assert_eq(len(categories), 3, "number of categories must equal to 3")

admin.add_category("Drugs")

categories = u.get_categories()
assert_eq(len(categories), 4, "number of categories must equal to 3")
