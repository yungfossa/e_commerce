from datetime import datetime

from .extensions import bcrypt, db
from .models import Admin, Cart, Customer, ProductCategory, Seller


def init_db(init_data):
    """
    Initialize the database with initial data.

    This function populates the database with categories, admin users, sellers, and customers.
    It's typically used when setting up the application for the first time or resetting to a known state.

    Args:
        init_data (dict): A dictionary containing initial data for the database.
                          Expected to have 'categories', 'admins', 'sellers', and 'customers' keys.

    Note:
        - This function commits changes to the database after each set of entities is created.
        - Existing data in the database will not be affected; this function only adds new entries.
    """
    db.session.commit()
    db.drop_all()
    db.create_all()
    db.session.commit()

    categories = init_data.get("categories", [])
    admin = init_data.get("admins", [])
    seller = init_data.get("sellers", [])
    customer = init_data.get("customers", [])

    # Create product categories
    for c in categories:
        ProductCategory.create(title=c)

    # Create admin users
    for a in admin:
        Admin.create(
            email=a["email"],
            name=a["name"],
            surname=a["name"],
            password=bcrypt.generate_password_hash(a["password"], 10).decode("utf-8"),
            birth_date=datetime.now(),
            is_verified=True,
            verified_on=datetime.now(),
        )

    # Create seller accounts
    for s in seller:
        Seller.create(
            email=s["email"],
            name=s["name"],
            surname=s["name"],
            company_name=s["name"],
            password=bcrypt.generate_password_hash(s["password"], 10).decode("utf-8"),
            birth_date=datetime.now(),
            is_verified=True,
            verified_on=datetime.now(),
        )

    # Create customer accounts and associated carts
    for c in customer:
        customer = Customer.create(
            email=c["email"],
            name=c["name"],
            surname=c["surname"],
            password=bcrypt.generate_password_hash(c["password"], 10).decode("utf-8"),
            birth_date=datetime.now(),
            is_verified=True,
            verified_on=datetime.now(),
        )
        Cart.create(customer_id=customer.id)


# This module contains utility functions for database operations and initialization.

# The main function, init_db, is responsible for setting up the initial state of the database.
# It creates categories, admin users, sellers, and customers based on the provided init_data.

# Usage:
# init_db(init_data)
# Where init_data is a dictionary containing lists of categories, admins, sellers, and customers.

# Note:
# - This function will drop all existing tables and recreate them. Use with caution in a production environment.
# - Passwords are hashed using bcrypt before being stored in the database.
# - All users created by this function are set as verified.
# - Each customer automatically gets an associated empty cart.

# Security Considerations:
# - In a production environment, consider using more secure methods for initial user creation.
# - Avoid storing plaintext passwords, even temporarily. Consider using a separate secure method for initial password setting.
