from dataclasses import dataclass
from typing import Self

import requests
from utils import PREFIX, assert_eq, logged


@dataclass
class Seller:
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

        return Seller(
            email,
            password,
            r.json()["data"]["access_token"],
        )

    @logged()
    def create_listing(
        self, product_id: str, quantity: int, price: float, product_state: str
    ) -> (any, int):
        s = requests.Session()

        r = s.post(
            f"{PREFIX}/seller/listings",
            headers={"Authorization": f"Bearer {self.access_token}"},
            json={
                "id": product_id,
                "quantity": quantity,
                "price": price,
                "product_state": product_state,
            },
        )

        return r.json().get("data"), r.status_code
