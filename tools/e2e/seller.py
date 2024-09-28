from dataclasses import dataclass
from typing import Self

import requests
from utils import PREFIX, assert_eq, logged


@dataclass
class Seller:
    """
    Represents a seller in the e-commerce system.

    This class provides methods for seller operations such as login,
    creating listings, and managing orders.
    """

    email: str
    password: str
    access_token: str

    @logged()
    @staticmethod
    def login(email: str, password: str) -> Self:
        """
        Authenticate a seller and create a Seller instance.

        Args:
            email (str): The seller's email address.
            password (str): The seller's password.

        Returns:
            Seller: An authenticated Seller instance.

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

        return Seller(
            email,
            password,
            r.json()["data"]["access_token"],
        )

    @logged()
    def create_listing(
        self, product_id: str, quantity: int, price: float, product_state: str
    ) -> (any, int):
        """
        Create a new listing for a product.

        Args:
            product_id (str): The ID of the product to list.
            quantity (int): The quantity available for sale.
            price (float): The price of the product.
            product_state (str): The condition of the product (e.g., "new", "used").

        Returns:
            tuple: A tuple containing the response data and status code.
        """
        s = requests.Session()

        r = s.post(
            f"{PREFIX}/seller/listings",
            headers={"Authorization": f"Bearer {self.access_token}"},
            json={
                "product_id": product_id,
                "quantity": quantity,
                "price": price,
                "product_state": product_state,
            },
        )

        return r.json().get("data"), r.status_code

    @logged()
    def get_orders(self, filters=None):
        """
        Retrieve orders for the seller, with optional filtering.

        Args:
            filters (dict, optional): A dictionary of filter parameters.

        Returns:
            tuple: A tuple containing the response data and status code.
        """
        s = requests.Session()

        if filters is None:
            filters = {}

        r = s.get(
            f"{PREFIX}/seller/orders",
            headers={"Authorization": f"Bearer {self.access_token}"},
            json=filters,
        )

        print(r.text)

        return r.json().get("data"), r.status_code

    @logged()
    def get_order(self, order_id: str):
        """
        Retrieve details of a specific order.

        Args:
            order_id (str): The ID of the order to retrieve.

        Returns:
            tuple: A tuple containing the response data and status code.
        """
        s = requests.Session()

        r = s.get(
            f"{PREFIX}/seller/orders/{order_id}",
            headers={"Authorization": f"Bearer {self.access_token}"},
        )

        print(r.text)

        return r.json().get("data"), r.status_code

    @logged()
    def update_order_status(self, order_id: str, new_status: str):
        """
        Update the status of a specific order.

        Args:
            order_id (str): The ID of the order to update.
            new_status (str): The new status to set for the order.

        Returns:
            tuple: A tuple containing the response data and status code.
        """
        s = requests.Session()

        r = s.post(
            f"{PREFIX}/seller/orders/{order_id}",
            headers={"Authorization": f"Bearer {self.access_token}"},
            json={"status": new_status},
        )

        print(r.text)

        return r.json().get("data"), r.status_code
