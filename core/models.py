from .extensions import (
    db,
    str_64,
    str_32,
    num_10_2,
    num_4_2,
    text,
    datetime_t,
    date_t
)

from typing import (
    Optional,
    List,
)

from sqlalchemy.orm import (
    Mapped,
    mapped_column,
    relationship
)

from sqlalchemy import (
    ForeignKey,
    UniqueConstraint,
)

from flask_login import UserMixin

import datetime

import enum

current_tmp = datetime.datetime.now


class UserRole(enum.Enum):
    ADMIN = 'admin'
    CUSTOMER = 'customer'
    SELLER = 'seller'


class ProductState(enum.Enum):
    NEW = 'new'
    USED = 'used'
    REFURBISHED = 'refurbished'


class OrderStatus(enum.Enum):
    PENDING = 'pending'
    SHIPPED = 'shipped'
    DELIVERED = 'delivered'


class ReviewRate(enum.Enum):
    ONE = 1
    TWO = 2
    THREE = 3
    FOUR = 4
    FIVE = 5


class User(UserMixin, db.Model):
    __tablename__ = "users"
    id: Mapped[int] = mapped_column(primary_key=True)
    email: Mapped[str_64] = mapped_column(unique=True)
    name: Mapped[str_32]
    surname: Mapped[str_32]
    birth_date: Mapped[Optional[date_t]]
    phone_number: Mapped[Optional[str_32]]
    user_role: Mapped[UserRole]
    created_at: Mapped[datetime_t] = mapped_column(default=current_tmp)
    modified_at: Mapped[datetime_t] = mapped_column(default=current_tmp, onupdate=current_tmp)

    def __repr__(self) -> str:
        return f"User(id={self.id!r}, email={self.email!r}, user_role={self.user_role!r}," \
               f"created_at={self.created_at!r}, modified_at={self.modified_at!r})"


class Admin(User):
    __tablename__ = "admins"
    id: Mapped[int] = mapped_column(ForeignKey("users.id"), primary_key=True)


class Customer(User):
    __tablename__ = "customers"
    id: Mapped[int] = mapped_column(ForeignKey("users.id"), primary_key=True)
    cart_id: Mapped[int]
    wishlist: Mapped[List["WishList"]] = relationship(back_populates="customer")
    cart: Mapped["Cart"] = relationship(back_populates="customer")
    review: Mapped[List["Review"]] = relationship(back_populates="customer")


class SellerListing(db.Model):
    __tablename__ = "seller_listings"
    seller_id: Mapped[int] = mapped_column(ForeignKey("sellers.id"), primary_key=True)
    listing_id: Mapped[int] = mapped_column(ForeignKey("listings.id"), primary_key=True)
    seller: Mapped["Seller"] = relationship(back_populates="seller_listing")
    listing: Mapped["Listing"] = relationship(back_populates="seller_listing")


class Seller(User):
    __tablename__ = "sellers"
    id: Mapped[int] = mapped_column(ForeignKey("users.id"), primary_key=True)
    company_name: Mapped[str_32]
    rating: Mapped[Optional[num_4_2]]
    listings: Mapped[List["SellerListing"]] = relationship(back_populates="seller")


class ProductCategory(db.Model):
    __tablename__ = "product_categories"
    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str_32]
    product: Mapped[List["Product"]] = relationship(back_populates="category")


class Product(db.Model):
    __tablename__ = "products"
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str_32]
    description: Mapped[Optional[text]]
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
    sellers: Mapped["SellerListing"] = relationship(back_populates="listing")
    product_id: Mapped[int] = mapped_column(ForeignKey("products.id"))
    product: Mapped["Product"] = relationship(back_populates="listing")
    cart_entry: Mapped[List["CartEntry"]] = relationship(back_populates="listing")
    review: Mapped[List["Review"]] = relationship(back_populates="listing")
    order_entries: Mapped[List["OrderEntry"]] = relationship(back_populates="listing")


class Review(db.Model):
    __tablename__ = "reviews"

    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str_64]
    description: Mapped[Optional[text]]
    created_at: Mapped[datetime_t] = mapped_column(default=current_tmp)
    modified_at: Mapped[datetime_t] = mapped_column(default=current_tmp, onupdate=current_tmp)
    rating: Mapped[ReviewRate]
    customer_id: Mapped[int] = mapped_column(ForeignKey("customers.id"))
    customer: Mapped["Customer"] = relationship(back_populates="review")
    listing_id: Mapped[int] = mapped_column(ForeignKey("listings.id"))
    listing: Mapped["Listing"] = relationship(back_populates="review")


class CartEntry(db.Model):
    __tablename__ = "cart_entries"
    id: Mapped[int] = mapped_column(primary_key=True)
    amount: Mapped[num_10_2]
    cart_id: Mapped[int] = mapped_column(ForeignKey("carts.id"))
    cart: Mapped["Cart"] = relationship(back_populates="cart_entry")
    listing_id: Mapped[int] = mapped_column(ForeignKey("listings.id"))
    listing: Mapped["Listing"] = relationship(back_populates="cart_entry")


class Cart(db.Model):
    __tablename__ = "carts"
    id: Mapped[int] = mapped_column(primary_key=True)
    customer_id: Mapped[int] = mapped_column(ForeignKey("customers.id"))
    customer: Mapped["Customer"] = relationship(back_populates="cart")
    cart_entry: Mapped[List["CartEntry"]] = relationship(back_populates="cart")
    __table_args__ = (UniqueConstraint("customer_id"),)


class WishListEntry(db.Model):
    __tablename__ = "wishlist_entries"
    id: Mapped[int] = mapped_column(primary_key=True)
    product_id: Mapped[int] = mapped_column(ForeignKey("products.id"))
    product: Mapped["Product"] = relationship(back_populates="wishlist_entry")
    wishlist_id: Mapped[int] = mapped_column(ForeignKey("wishlists.id"))
    wishlist: Mapped["WishList"] = relationship(back_populates="wishlist_entries")


class WishList(db.Model):
    __tablename__ = "wishlists"
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str_32]
    costumer_id: Mapped[int] = mapped_column(ForeignKey("customers.id"))
    customer: Mapped["Customer"] = relationship(back_populates="wishlist")
    wishlist_entries: Mapped[List["WishListEntry"]] = relationship(back_populates="wishlist")


class OrderEntry(db.Model):
    __tablename__ = "order_entries"
    id: Mapped[int] = mapped_column(primary_key=True)
    order_id: Mapped[int] = mapped_column(ForeignKey("orders.id"))
    order: Mapped["Order"] = relationship(back_populates="order_entries")
    listing_id: Mapped[int] = mapped_column(ForeignKey("listings.id"))
    listing: Mapped["Listing"] = relationship(back_populates="order_entries")


class Order(db.Model):
    __tablename__ = "orders"
    id: Mapped[int] = mapped_column(primary_key=True)
    price: Mapped[num_10_2]
    purchased_at: Mapped[Optional[datetime_t]]
    # todo add address field (copy?)
    order_status: Mapped[OrderStatus]
    order_entries: Mapped[List["OrderEntry"]] = relationship(back_populates="order")

# todo missing CustomerAddress, TokenOccurence, Token, DeleteRequest
