from .extensions import db

from typing import (
    Annotated,
    Optional,
    List,
)

from sqlalchemy.orm import (
    Mapped,
    mapped_column,
)

from sqlalchemy import (
    Date,
    DateTime,
    ForeignKey,
    relationship,
    UniqueConstraint
)

from decimal import Decimal

import datetime

import enum

current_tmp = datetime.datetime.now

str_32 = Annotated[str, 32]
str_64 = Annotated[str, 64]
text = Annotated[str, 5000]
num_10_2 = Annotated[Decimal, 10]
num_4_2 = Annotated[Decimal, 2]


class UserRole(enum.Enum):
    ADMIN = 'admin'
    CUSTOMER = 'customer'
    SELLER = 'seller'


class ProductState(enum.Enum):
    NEW = 'new'
    USED = 'used'
    REFURBISHED = 'refurbished'


class ReviewRate(enum.Enum):
    ONE = 1
    TWO = 2
    THREE = 3
    FOUR = 4
    FIVE = 5


class User(db.Model):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)
    email: Mapped[str_64] = mapped_column(unique=True)
    name: Mapped[str_32]
    surname: Mapped[str_32]
    birth_date: Mapped[datetime] = mapped_column(Date)
    phone_number: Mapped[Optional[str_32]]
    user_role: Mapped[UserRole]
    created_at: Mapped[datetime] = mapped_column(DateTime, default=current_tmp)
    modified_at: Mapped[datetime] = mapped_column(DateTime, default=current_tmp,
                                                  onupdate=current_tmp)


class Customer(User):
    __tablename__ = "customers"

    id: Mapped[int] = mapped_column(ForeignKey("users.id"), primary_key=True)
    cart_id: Mapped[int]
    wishlist: Mapped[List["WishList"]] = relationship(back_populates="customer")
    cart: Mapped["Cart"] = relationship(back_populates="customer")
    review: Mapped[List["Review"]] = relationship(back_populates="customer")


class Seller(User):
    __tablename__ = "sellers"

    id: Mapped[int] = mapped_column(ForeignKey("users.id"), primary_key=True)
    company_name: Mapped[str_32]
    rating: Mapped[Optional[num_4_2]]  # todo idk ?
    # todo relationship with Listing (N:M)


class Admin(User):
    __tablename__ = "admins"

    id: Mapped[int] = mapped_column(ForeignKey("users.id"), primary_key=True)


class ProductCategory(db.Model):
    __tablename__ = "product_categories"

    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str_32]
    product: Mapped[List["Product"]] = relationship(back_populates="category")


class Product(db.Model):
    __tablename__ = "products"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str_32]
    description: Mapped[text]
    image_src: Mapped[Optional[str]]  # must be not null?
    category_id: Mapped[int] = mapped_column(ForeignKey("product_categories.id"))
    category: Mapped["ProductCategory"] = relationship(back_populates="product")
    wishlist_entry: Mapped[List["WishListEntry"]] = relationship(back_populates="product")
    listing: Mapped[List["Listing"]] = relationship(back_populates="product")


class Listing(db.Model):
    __tablename__ = "listings"

    id: Mapped[int] = mapped_column(primary_key=True)
    quantity: Mapped[int]
    available: Mapped[bool]
    price: Mapped[num_10_2]
    product_state: Mapped[ProductState]
    seller_id: Mapped[int] = mapped_column(ForeignKey("sellers.id"))
    # todo relationship with Seller (N:M)
    product_id: Mapped[int] = mapped_column(ForeignKey("products.id"))
    product: Mapped["Product"] = relationship(back_populates="listing")
    cart_entry: Mapped[List["CartEntry"]] = relationship(back_populates="listing")
    review: Mapped[List["Review"]] = relationship(back_populates="listing")


class Review(db.Model):
    __tablename__ = "reviews"

    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str_64]
    description: Mapped[Optional[text]]
    created_at: Mapped[datetime] = mapped_column(DateTime, default=current_tmp)
    modified_at: Mapped[datetime] = mapped_column(DateTime, onupdate=current_tmp)  # todo idk
    rating: Mapped[ReviewRate]
    customer_id: Mapped[int] = mapped_column(ForeignKey("customers.id"))
    customer: Mapped["Customer"] = mapped_column(back_populates="review")
    listing_id: Mapped[int] = mapped_column(ForeignKey("listings.id"))
    listing: Mapped["Listing"] = mapped_column(back_populates="review")


class Cart(db.Model):
    __tablename__ = "carts"

    id: Mapped[int] = mapped_column(primary_key=True)
    customer_id: Mapped[int] = mapped_column(ForeignKey("customers.id"))
    customer: Mapped["Customer"] = relationship(back_populates="cart")
    cart_entry: Mapped[List["CartEntry"]] = relationship(back_populates="cart")

    __table_args__ = (UniqueConstraint("customer_id"),)


class CartEntry(db.Model):
    __tablename__ = "cart_entries"

    id: Mapped[int] = mapped_column(primary_key=True)
    amount: Mapped[num_10_2]  # todo price?
    cart_id: Mapped[int] = mapped_column(ForeignKey("carts.id"))
    cart: Mapped["Cart"] = relationship(back_populates="cart_entry")
    listing_id: Mapped[int] = mapped_column(ForeignKey("listings.id"))
    listing: Mapped["Listing"] = relationship(back_populates="cart_entry")


class WishList(db.Model):
    __tablename__ = "wishlists"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str_32]
    costumer_id: Mapped[int] = mapped_column(ForeignKey("customers.id"))
    customer: Mapped["Customer"] = relationship(back_populates="wishlist")
    wishlist_entry: Mapped[List["WishListEntry"]] = relationship(back_populates="wishlist")


class WishListEntry(db.Model):
    __tablename__ = "wishlist_entries"

    product_id: Mapped[int] = mapped_column(ForeignKey("products.id"))
    product: Mapped["Product"] = relationship(back_populates="wishlist_entry")
    wishlist_id: Mapped[int] = mapped_column(ForeignKey("wishlists.id"))
    wishlist: Mapped["WishList"] = relationship(back_populates="wishlist_entry")


class Order(db.Model):
    __tablename__ = "orders"
    # todo arrivato qua


class OrderEntry(db.Model):
    __tablename__ = "order_entries"
