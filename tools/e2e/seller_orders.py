import time

from admin import Admin
from seller import Seller
from user import User
from utils import assert_eq, before, test


def reset():
    """Reset the database to a clean state."""
    Admin.login("admin@shopsphere.com", "changeme").reset_db()


@test("seller should be able to manage orders")
@before(reset)
def seller_order_management():
    """
    Test the seller's ability to manage orders.

    This test covers the following scenarios:
    1. Creating a product and listing
    2. Creating an order as a user
    3. Retrieving orders as a seller
    4. Testing order filters
    5. Retrieving a specific order
    6. Updating order status
    """
    # Set up test users
    admin = Admin.login("admin@shopsphere.com", "changeme")
    seller = Seller.login("sales@amazon.com", "changeme")
    u = User.create(f"{time.time()}@gmail.com", "Password1?", "foo", "bar")

    # Create a product and listing
    (product, status_code) = admin.add_product(
        "iPhone 15",
        "A phone",
        "https://upload.wikimedia.org/wikipedia/commons/7/70/Example.png",
        "Tech",
    )
    assert_eq(status_code, 201)

    (listing, status_code) = seller.create_listing(product["id"], 10, 19.99, "new")
    assert_eq(status_code, 201)

    # Create an order
    (cart, status_code) = u.upsert_cart(listing["id"], 1)
    assert_eq(status_code, 200)

    (order, status_code) = u.create_order(
        address_street="Via Genova 4",
        address_city="San Martino di Lupari",
        address_state="Padova",
        address_country="Italy",
        address_postal_code="35018",
    )
    assert_eq(status_code, 201)

    # Test get_orders
    (data, status_code) = seller.get_orders()
    assert_eq(status_code, 200)
    assert "orders" in data
    assert "pagination" in data

    # Test with custom filters
    filters = {
        "status": "pending",
        "offset": 0,
        "limit": 5,
        "order_by": "purchased_at",
        "order_direction": "desc",
    }
    (data, status_code) = seller.get_orders(filters)
    assert_eq(status_code, 200)
    assert "orders" in data
    assert "pagination" in data
    assert data["pagination"]["limit"] == 5

    # Test with invalid filters
    (data, status_code) = seller.get_orders({"status": "invalid_status"})
    assert_eq(status_code, 400)

    (data, status_code) = seller.get_orders({"order_by": "invalid_field"})
    assert_eq(status_code, 400)

    # Make a valid get_orders call
    (data, status_code) = seller.get_orders()
    assert_eq(status_code, 200)

    # Now we can safely access the order data
    order_id = data["orders"][0]["order_id"]

    # Test get_order
    (order_data, status_code) = seller.get_order(order_id)
    assert_eq(status_code, 200)
    assert "order_id" in order_data
    assert "status" in order_data
    assert "customer_info" in order_data
    assert "shipping_address" in order_data
    assert "product_details" in order_data

    (invalid_order_data, status_code) = seller.get_order("invalid_order_id")
    assert_eq(status_code, 404)

    # Test update_order_status
    (update_data, status_code) = seller.update_order_status(order_id, "shipped")
    assert_eq(status_code, 200)
    assert update_data["new_status"] == "shipped"

    (invalid_update_data, status_code) = seller.update_order_status(
        order_id, "invalid_status"
    )
    assert_eq(status_code, 400)

    (non_existent_update_data, status_code) = seller.update_order_status(
        "invalid_order_id", "shipped"
    )
    assert_eq(status_code, 404)

    (invalid_transition_data, status_code) = seller.update_order_status(
        order_id, "pending"
    )
    assert_eq(status_code, 400)

    print("All seller order management tests passed successfully!")
