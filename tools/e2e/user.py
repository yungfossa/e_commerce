from dataclasses import dataclass
from typing import Self

import requests
from utils import PREFIX, assert_eq, logged


@dataclass
class User:
    """
    Represents a user in the e-commerce system.

    This class provides methods for user operations such as signup, login,
    profile management, cart operations, and order placement.
    """

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
        """
        Create a new user account, verify it, and log in.

        Args:
            email (str): User's email address.
            password (str): User's password.
            name (str): User's first name.
            surname (str): User's last name.

        Returns:
            User: A fully authenticated User instance.
        """
        return User.signup(email, password, name, surname).verify().login()

    @logged()
    @staticmethod
    def signup(
        email: str,
        password: str,
        name: str,
        surname: str,
    ) -> Self:
        """
        Sign up a new user.

        Args:
            email (str): User's email address.
            password (str): User's password.
            name (str): User's first name.
            surname (str): User's last name.

        Returns:
            User: A User instance with a verification token.

        Raises:
            AssertionError: If the signup request fails.
        """
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
        """
        Verify the user's account using the verification token.

        Returns:
            User: A User instance with the verification token cleared.

        Raises:
            AssertionError: If the verification request fails.
        """
        s = requests.Session()

        r = s.get(f"{PREFIX}/verify/{self.verification_token}")

        assert_eq(r.status_code, 200)

        return User(self.email, self.password, self.name, self.surname, None, None)

    @logged()
    def login(
        self,
    ) -> Self:
        """
        Log in the user.

        Returns:
            User: A User instance with an access token.

        Raises:
            AssertionError: If the login request fails.
        """
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
        """
        Force login a user without going through the signup and verification process.

        Args:
            email (str): User's email address.
            password (str): User's password.

        Returns:
            User: A User instance with an access token.

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
        """
        Retrieve the user's profile information.

        Returns:
            tuple: A tuple containing the profile data and status code.
        """
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
        """
        Retrieve the user's cart information.

        Returns:
            tuple: A tuple containing the cart data and status code.
        """
        s = requests.Session()

        r = s.get(
            f"{PREFIX}/cart",
            headers={"Authorization": f"Bearer {self.access_token}"},
        )

        print(r.text)

        return r.json().get("data"), r.status_code

    @logged()
    def upsert_cart(self, listing_id: str, quantity: int) -> tuple[any, int]:
        """
        Add or update an item in the user's cart.

        Args:
            listing_id (str): The ID of the listing to add or update.
            quantity (int): The quantity of the item.

        Returns:
            tuple: A tuple containing the updated cart data and status code.
        """
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
        """
        Remove items from the user's cart.

        Args:
            cart_item_ids (list[str]): A list of cart item IDs to remove.

        Returns:
            tuple: A tuple containing the updated cart data and status code.
        """
        s = requests.Session()

        r = s.delete(
            f"{PREFIX}/cart",
            headers={"Authorization": f"Bearer {self.access_token}"},
            json={"cart_item_ids": cart_item_ids},
        )

        return r.json().get("data"), r.status_code

    @logged()
    def get_categories(self) -> tuple[any, int]:
        """
        Retrieve the list of product categories.

        Returns:
            tuple: A tuple containing the categories data and status code.
        """
        s = requests.Session()

        r = s.get(
            f"{PREFIX}/categories",
            headers={"Authorization": f"Bearer {self.access_token}"},
        )

        return r.json().get("data"), r.status_code

    @logged()
    def get_products(self) -> tuple[any, int]:
        """
        Retrieve the list of products.

        Returns:
            tuple: A tuple containing the products data and status code.
        """
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
        """
        Retrieve the listings for a specific product.

        Args:
            product_id (str): The ID of the product to get listings for.

        Returns:
            tuple: A tuple containing the listings data and status code.
        """
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
        """
        Create a review for a product listing.

        Args:
            product_id (str): The ID of the product.
            listing_id (str): The ID of the listing.
            title (str): The title of the review.
            description (str): The description of the review.
            rating (int): The rating given in the review.

        Returns:
            tuple: A tuple containing the review data and status code.
        """
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
        """
        Create an order with the items in the user's cart.

        Args:
            address_street (str): Street address for shipping.
            address_city (str): City for shipping.
            address_state (str): State for shipping.
            address_country (str): Country for shipping.
            address_postal_code (str): Postal code for shipping.

        Returns:
            tuple: A tuple containing the order data and status code.
        """
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
        """
        Retrieve the user's orders with optional filtering and pagination.

        Args:
            status (str, optional): Filter orders by status.
            order_by (str, optional): Field to order by. Defaults to "purchased_at".
            order_direction (str, optional): Order direction ("asc" or "desc"). Defaults to "desc".
            offset (int, optional): Pagination offset. Defaults to 0.
            limit (int, optional): Pagination limit. Defaults to 10.

        Returns:
            tuple: A tuple containing the orders data and status code.
        """
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
        """
        Retrieve details of a specific order.

        Args:
            order_ulid (str): The ULID of the order to retrieve.

        Returns:
            tuple: A tuple containing the order data and status code.
        """
        s = requests.Session()

        r = s.get(
            f"{PREFIX}/orders/{order_ulid}",
            headers={"Authorization": f"Bearer {self.access_token}"},
        )

        print(r.text)

        return r.json().get("data"), r.status_code
