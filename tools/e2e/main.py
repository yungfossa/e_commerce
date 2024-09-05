import json
import time

from admin import Admin
from seller import Seller
from user import User
from utils import assert_eq, before, test


def reset():
    Admin.login("admin@shopsphere.com", "changeme").reset_db()


@test("it should create a user")
@before(reset)
def create_users():
    u = User.signup(f"{time.time()}@gmail.com", "Password1?", "foo", "bar")
    (profile, status_code) = u.profile()
    assert_eq(status_code, 422)

    u = u.verify()
    (profile, status_code) = u.profile()
    assert_eq(status_code, 422)

    u = u.login()
    (profile, status_code) = u.profile()
    assert_eq(status_code, 200)


@test("when creating a fresh account, the cart should be empty")
@before(reset)
def empty_cart():
    u = User.create(f"{time.time()}@gmail.com", "Password1?", "foo", "bar")
    (cart, status_code) = u.cart()
    assert_eq(status_code, 200)
    assert_eq(len(cart["cart_entries"]), 0, "cart must be empty")
    assert_eq(cart["cart_total"], 0, "cart amount must be equal to 0")


@test("it should properly create a new category")
@before(reset)
def create_category():
    admin = Admin.login("admin@shopsphere.com", "changeme")
    u = User.create(f"{time.time()}@gmail.com", "Password1?", "foo", "bar")

    # make sure the admin can create new categories
    (categories, status_code) = u.get_categories()
    assert_eq(status_code, 200)
    assert_eq(len(categories), 3, "number of categories must equal to 3")

    # TODO assert status code
    admin.add_category("Drugs")

    (categories, status_code) = u.get_categories()
    assert_eq(status_code, 200)
    assert_eq(len(categories), 4, "number of categories must equal to 3")


@test("an admin should be able to create a new product")
@before(reset)
def create_product():
    admin = Admin.login("admin@shopsphere.com", "changeme")
    u = User.create(f"{time.time()}@gmail.com", "Password1?", "foo", "bar")

    # initially the products should be empty
    (products, status_code) = u.get_products()
    assert_eq(status_code, 200)
    assert_eq(products, None)

    (product, status_code) = admin.add_product(
        "iPhone 15", "A phone", "http://example.com/image.png", "Tech"
    )
    assert_eq(status_code, 201)

    # we should have a single product
    (products, status_code) = u.get_products()
    assert_eq(status_code, 200)
    assert_eq(len(products), 1)


@test(
    "a seller should be able to add a listing for a product, and it should be visible to a user"
)
@before(reset)
def create_listing():
    admin = Admin.login("admin@shopsphere.com", "changeme")
    seller = Seller.login("sales@amazon.com", "changeme")
    u = User.create(f"{time.time()}@gmail.com", "Password1?", "foo", "bar")

    (product, status_code) = admin.add_product(
        "iPhone 15", "A phone", "http://example.com/image.png", "Tech"
    )
    assert_eq(status_code, 201)

    product_id = product["product_id"]

    (listing, status_code) = seller.create_listing(product_id, 10, 19.99, "new")
    assert_eq(status_code, 201)

    (listings, status_code) = u.get_listings(product_id)
    assert_eq(status_code, 200)

    print(json.dumps(listings, indent=2))
