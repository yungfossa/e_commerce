from dataclasses import dataclass
from typing import Self

import requests
from utils import PREFIX, assert_eq, logged


@dataclass
class Admin:
    """
    Represents an admin user with methods to interact with the admin API.
    """

    email: str
    password: str

    access_token: str

    @logged()
    @staticmethod
    def login(email: str, password: str) -> Self:
        """
        Authenticates an admin user and returns an Admin instance.

        Args:
            email (str): The admin's email address.
            password (str): The admin's password.

        Returns:
            Admin: An authenticated Admin instance.

        Raises:
            AssertionError: If the login request fails.
        """
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
        """
        Resets the database.

        Returns:
            dict: The response data from the reset operation.

        Raises:
            AssertionError: If the reset request fails.
        """
        s = requests.Session()

        r = s.get(
            f"{PREFIX}/admin/debug/reload",
            headers={"Authorization": f"Bearer {self.access_token}"},
        )

        assert_eq(r.status_code, 200)

        return r.json().get("data")

    @logged()
    def add_category(self, name: str):
        """
        Adds a new category to the system.

        Args:
            name (str): The name of the category to add.

        Returns:
            tuple: A tuple containing the response data and status code.
        """
        s = requests.Session()

        r = s.put(
            f"{PREFIX}/admin/category",
            headers={"Authorization": f"Bearer {self.access_token}"},
            json={"category_title": name},
        )

        return r.json().get("data"), r.status_code

    @logged()
    def add_product(
        self, name: str, description: str, image_src: str, category: str
    ) -> (any, int):
        """
        Adds a new product to the system.

        Args:
            name (str): The name of the product.
            description (str): The product description.
            image_src (str): The URL or path to the product image.
            category (str): The category of the product.

        Returns:
            tuple: A tuple containing the response data and status code.
        """
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
