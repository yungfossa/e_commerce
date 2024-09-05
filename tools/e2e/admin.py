from dataclasses import dataclass
from typing import Self

import requests
from utils import PREFIX, assert_eq, logged


@dataclass
class Admin:
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
    def reset_db(self):
        s = requests.Session()

        r = s.get(
            f"{PREFIX}/admin/debug/reload",
            headers={"Authorization": f"Bearer {self.access_token}"},
        )

        assert_eq(r.status_code, 200)

        return r.json().get("data")

    @logged()
    def add_category(self, name: str):
        s = requests.Session()

        r = s.put(
            f"{PREFIX}/admin/category",
            headers={"Authorization": f"Bearer {self.access_token}"},
            json={"category_title": name},
        )

        return r.json().get("data")

    @logged()
    def add_product(
        self, name: str, description: str, image_src: str, category: str
    ) -> (any, int):
        s = requests.Session()

        r = s.put(
            f"{PREFIX}/admin/products",
            headers={"Authorization": f"Bearer {self.access_token}"},
            json={
                "name": name,
                "description": description,
                "image_src": image_src,
                "category_title": category,
            },
        )

        return r.json().get("data"), r.status_code
