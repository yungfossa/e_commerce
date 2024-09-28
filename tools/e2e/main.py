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

    (categories, status_code) = admin.add_category("Drugs")
    assert_eq(status_code, 201)

    (categories, status_code) = u.get_categories()
    assert_eq(status_code, 200)
    assert_eq(len(categories), 4, "number of categories must equal to 4")


@test("an admin should be able to create a new product")
@before(reset)
def create_product():
    admin = Admin.login("admin@shopsphere.com", "changeme")
    u = User.create(f"{time.time()}@gmail.com", "Password1?", "foo", "bar")

    # initially the products should be empty
    (products, status_code) = u.get_products()
    assert_eq(status_code, 200)
    assert_eq(products, [])

    (product, status_code) = admin.add_product(
        "iPhone 15",
        "A phone",
        "https://upload.wikimedia.org/wikipedia/commons/7/70/Example.png",
        "Tech",
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
        "iPhone 15",
        "A phone",
        "https://upload.wikimedia.org/wikipedia/commons/7/70/Example.png",
        "Tech",
    )
    assert_eq(status_code, 201)

    product_id = product["id"]

    (listing, status_code) = seller.create_listing(product_id, 10, 19.99, "new")
    assert_eq(status_code, 201)

    (listings, status_code) = u.get_listings(product_id)
    assert_eq(status_code, 200)

    print(json.dumps(listings, indent=2))


@test("a user should be able to create an order")
@before(reset)
def create_order():
    admin = Admin.login("admin@shopsphere.com", "changeme")
    seller = Seller.login("sales@amazon.com", "changeme")
    u = User.create(f"{time.time()}@gmail.com", "Password1?", "foo", "bar")

    (product, status_code) = admin.add_product(
        "iPhone 15",
        "A phone",
        "https://upload.wikimedia.org/wikipedia/commons/7/70/Example.png",
        "Tech",
    )
    assert_eq(status_code, 201)

    (listing, status_code) = seller.create_listing(product["id"], 10, 19.99, "new")
    assert_eq(status_code, 201)

    (listings, status_code) = u.get_listings(product["id"])
    assert_eq(status_code, 200)

    print(json.dumps(listings, indent=2))

    (cart, status_code) = u.cart()
    assert_eq(status_code, 200)
    assert_eq(len(cart["cart_entries"]), 0, "cart must be empty")
    assert_eq(cart["cart_total"], 0, "cart amount must be equal to 0")

    (cart, status_code) = u.upsert_cart(listing["id"], 1)
    assert_eq(status_code, 200)

    (cart, status_code) = u.cart()
    assert_eq(status_code, 200)
    assert_eq(len(cart["cart_entries"]), 1, "cart must have 1 entry")
    assert_eq(cart["cart_total"], 19.99, "cart amount must be equal to 19.99")

    (order, status_code) = u.create_order(
        address_street="Via Genova 2",
        address_city="San Martino di Lupari",
        address_state="Padova",
        address_country="Italy",
        address_postal_code="35018",
    )
    assert_eq(status_code, 201)

    (orders, status_code) = u.get_orders()
    assert_eq(status_code, 200)
    assert_eq(orders["pagination"]["total_items"], 1, "user must have 1 order")

    print(json.dumps(orders, indent=2))

    (order, status_code) = u.get_order(order["id"])
    assert_eq(status_code, 200)
    assert_eq(order["total_amount"], 19.99)
    assert_eq(order["status"], "pending")
    assert_eq(order["address"]["street"], "Via Genova 2")
    assert_eq(order["address"]["city"], "San Martino di Lupari")
    assert_eq(order["address"]["state"], "Padova")
    assert_eq(order["address"]["country"], "Italy")
    assert_eq(order["address"]["postal_code"], "35018")

    (cart, status_code) = u.cart()
    assert_eq(status_code, 200)
    assert_eq(len(cart["cart_entries"]), 0, "cart must be empty")
    assert_eq(cart["cart_total"], 0, "cart amount must be equal to 0")
