from datetime import datetime

from .extensions import bcrypt, db
from .models import Admin, Customer, ProductCategory, Seller


def init_db(init_data):
    db.session.commit()
    db.drop_all()
    db.create_all()
    db.session.commit()

    categories = init_data.get("categories", [])
    admin = init_data.get("admins", [])
    seller = init_data.get("sellers", [])
    customer = init_data.get("customers", [])

    for c in categories:
        ProductCategory.create(title=c)

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

    for c in customer:
        Customer.create(
            email=c["email"],
            name=c["name"],
            surname=c["surname"],
            password=bcrypt.generate_password_hash(c["password"], 10).decode("utf-8"),
            birth_date=datetime.now(),
            is_verified=True,
            verified_on=datetime.now(),
        )

    for s in seller:
        Seller.create(
            email=s["email"],
            name=s["name"],
            surname=s["name"],
            company_name=s["name"],
            password=bcrypt.generate_password_hash(a["password"], 10).decode("utf-8"),
            birth_date=datetime.now(),
            is_verified=True,
            verified_on=datetime.now(),
        )
