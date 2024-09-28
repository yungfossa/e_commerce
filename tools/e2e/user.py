from dataclasses import dataclass
from typing import Self

import requests
from utils import PREFIX, assert_eq, logged


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
    def create(
        email: str,
        password: str,
        name: str,
        surname: str,
    ) -> Self:
        return User.signup(email, password, name, surname).verify().login()

    @logged()
    @staticmethod
    def signup(
        email: str,
        password: str,
        name: str,
        surname: str,
    ) -> Self:
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
    def verify(
        self,
    ):
        s = requests.Session()

        r = s.get(f"{PREFIX}/verify/{self.verification_token}")

        assert_eq(r.status_code, 200)

        return User(self.email, self.password, self.name, self.surname, None, None)

    @logged()
    def login(
        self,
    ) -> Self:
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

    @staticmethod
    @logged()
    def force_login(
        email: str,
        password: str,
    ) -> Self:
        s = requests.Session()

        r = s.post(
            f"{PREFIX}/login",
            json={
                "email": email,
                "password": password,
            },
        )

        assert_eq(r.status_code, 200)

        return User(
            email,
            password,
            None,
            None,
            None,
            r.json()["data"]["access_token"],
        )

    @logged()
    def profile(
        self,
    ) -> tuple[any, int]:
        s = requests.Session()

        r = s.get(
            f"{PREFIX}/profile",
            headers={"Authorization": f"Bearer {self.access_token}"},
        )

        return r.json().get("data"), r.status_code

    @logged()
    def cart(
        self,
    ) -> tuple[any, int]:
        s = requests.Session()

        r = s.get(
            f"{PREFIX}/cart",
            headers={"Authorization": f"Bearer {self.access_token}"},
        )

        print(r.text)

        return r.json().get("data"), r.status_code

    @logged()
    def upsert_cart(self, listing_id: str, quantity: int) -> tuple[any, int]:
        s = requests.Session()

        r = s.post(
            f"{PREFIX}/cart",
            headers={"Authorization": f"Bearer {self.access_token}"},
            json={"listing_id": listing_id, "quantity": quantity},
        )

        print(r.text)

        return r.json().get("data"), r.status_code

    @logged()
    def remove_cart_item(
        self,
        cart_item_ids: list[str],
    ) -> tuple[any, int]:
        s = requests.Session()

        r = s.delete(
            f"{PREFIX}/cart",
            headers={"Authorization": f"Bearer {self.access_token}"},
            json={"cart_item_ids": cart_item_ids},
        )

        return r.json().get("data"), r.status_code

    @logged()
    def get_categories(self) -> tuple[any, int]:
        s = requests.Session()

        r = s.get(
            f"{PREFIX}/categories",
            headers={"Authorization": f"Bearer {self.access_token}"},
        )

        return r.json().get("data"), r.status_code

    @logged()
    def get_products(self) -> tuple[any, int]:
        s = requests.Session()

        r = s.post(
            f"{PREFIX}/products",
            headers={"Authorization": f"Bearer {self.access_token}"},
            json={"offset": 0, "limit": 10},
        )

        return r.json().get("data"), r.status_code

    @logged()
    def get_listings(
        self,
        product_id: str,
    ) -> tuple[any, int]:
        s = requests.Session()

        r = s.post(
            f"{PREFIX}/products/{product_id}",
            headers={"Authorization": f"Bearer {self.access_token}"},
            json={"offset": 0, "limit": 10},
        )

        return r.json().get("data"), r.status_code

    @logged()
    def create_review(
        self,
        product_id: str,
        listing_id: str,
        title: str,
        description: str,
        rating: int,
    ) -> tuple[any, int]:
        s = requests.Session()

        r = s.post(
            f"{PREFIX}/products/{product_id}/{listing_id}/review",
            headers={"Authorization": f"Bearer {self.access_token}"},
            json={"title": title, "description": description, "rating": rating},
        )

        return r.json().get("data"), r.status_code

    @logged()
    def create_order(
        self,
        address_street,
        address_city,
        address_state,
        address_country,
        address_postal_code,
    ) -> tuple[any, int]:
        s = requests.Session()

        r = s.post(
            f"{PREFIX}/orders",
            headers={"Authorization": f"Bearer {self.access_token}"},
            json={
                "address_street": address_street,
                "address_city": address_city,
                "address_state": address_state,
                "address_country": address_country,
                "address_postal_code": address_postal_code,
            },
        )

        print(r.text)

        return r.json().get("data"), r.status_code

    @logged()
    def get_orders(
        self,
        status: str = None,
        order_by: str = "purchased_at",
        order_direction: str = "desc",
        offset: int = 0,
        limit: int = 10,
    ) -> tuple[any, int]:
        s = requests.Session()

        payload = {
            "order_by": order_by,
            "order_direction": order_direction,
            "offset": offset,
            "limit": limit,
        }
        if status:
            payload["status"] = status

        r = s.get(
            f"{PREFIX}/orders/summary",
            headers={"Authorization": f"Bearer {self.access_token}"},
            json=payload,
        )

        print(r.text)

        return r.json().get("data"), r.status_code

    @logged()
    def get_order(
        self,
        order_ulid: str,
    ) -> tuple[any, int]:
        s = requests.Session()

        r = s.get(
            f"{PREFIX}/orders/{order_ulid}",
            headers={"Authorization": f"Bearer {self.access_token}"},
        )

        print(r.text)

        return r.json().get("data"), r.status_code
