import enum
from datetime import UTC, datetime
from decimal import Decimal
from time import time
from typing import List, Optional

import jwt
from flask import current_app
from sqlalchemy import (
    CHAR,
    Boolean,
    Column,
    Date,
    DateTime,
    ForeignKey,
    Numeric,
    String,
    Table,
    Text,
    TypeDecorator,
    func,
    select,
)
from sqlalchemy import (
    Enum as SQLAlchemyEnum,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy_utils import create_materialized_view
from sqlalchemy_utils.compat import _select_args

from . import db
from .base_models import BaseModel

USERS_ID_FK = "users.id"
CUSTOMERS_ID = "customers.id"
LISTINGS_ID = "listings.id"
PRODUCTS_ID = "products.id"
CASCADE_ALL_DELETE_ORPHAN = "all, delete-orphan"


class ULID(TypeDecorator):
    """
    Custom type for ULID (Universally Unique Lexicographically Sortable Identifier).

    This type is used as a primary key for most models, providing a sortable,
    URL-safe alternative to UUIDs.
    """

    impl = CHAR(26)
    cache_ok = True

    def load_dialect_impl(self, dialect):
        return dialect.type_descriptor(CHAR(26))

    def process_bind_param(self, value, dialect):
        if value is None:
            return value
        return str(value)

    def process_result_value(self, value, dialect):
        return value


class UserType(enum.Enum):
    """Enum representing different types of users in the system."""

    USER = "user"
    ADMIN = "admin"
    CUSTOMER = "customer"
    SELLER = "seller"


class ProductState(enum.Enum):
    """Enum representing different states a product can be in."""

    NEW = "new"
    USED = "used"
    REFURBISHED = "refurbished"


class OrderStatus(enum.Enum):
    """Enum representing different statuses an order can have."""

    PENDING = "pending"
    SHIPPED = "shipped"
    DELIVERED = "delivered"
    CANCELLED = "cancelled"


class ReviewRate(enum.Enum):
    """Enum representing possible ratings for a review."""

    ONE = 1
    TWO = 2
    THREE = 3
    FOUR = 4
    FIVE = 5


class TokenBlocklist(BaseModel):
    """Model for storing blocked JWT tokens."""

    __tablename__ = "tokens_blocklist"
    id: Mapped[str] = mapped_column(
        ULID, primary_key=True, server_default=func.gen_ulid()
    )
    jti: Mapped[str] = mapped_column(String(36), index=True)
    user_id: Mapped[str] = mapped_column(ULID, ForeignKey(USERS_ID_FK))
    created_at: Mapped[datetime] = mapped_column(DateTime)
    expired_at: Mapped[datetime] = mapped_column(DateTime, index=True)


class User(BaseModel):
    """
    Base User model representing common attributes for all user types.

    This model uses SQLAlchemy's joined table inheritance to create
    specialized user types (Admin, Customer, Seller).
    """

    __tablename__ = "users"
    id: Mapped[str] = mapped_column(
        ULID, primary_key=True, server_default=func.gen_ulid()
    )
    email: Mapped[str] = mapped_column(String(64), unique=True)
    name: Mapped[str] = mapped_column(String(32))
    surname: Mapped[str] = mapped_column(String(32))
    password: Mapped[Optional[str]] = mapped_column(String(64))
    birth_date: Mapped[Optional[datetime]] = mapped_column(Date)
    phone_number: Mapped[Optional[str]] = mapped_column(String(32))
    profile_img: Mapped[Optional[str]] = mapped_column(Text)
    user_type: Mapped[UserType] = mapped_column(SQLAlchemyEnum(UserType))
    is_verified: Mapped[bool] = mapped_column(Boolean, default=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.now(UTC))
    modified_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.now(UTC), onupdate=datetime.now(UTC)
    )
    verified_on: Mapped[Optional[datetime]] = mapped_column(DateTime)

    delete_request: Mapped[Optional["DeleteRequest"]] = relationship(
        back_populates="user",
        cascade=CASCADE_ALL_DELETE_ORPHAN,
        single_parent=True,
        uselist=False,
    )

    __mapper_args__ = {
        "polymorphic_identity": UserType.USER,
        "polymorphic_on": user_type,
    }

    def get_reset_password_token(self, expires_in=1200):
        """Generate a password reset token for the user."""
        return jwt.encode(
            {"reset_password": self.id, "exp": time() + expires_in},
            current_app.config["SECRET_KEY"],
            algorithm="HS256",
        )

    @staticmethod
    def verify_reset_password_token(token):
        """Verify a password reset token and return the associated user."""
        try:
            _id = jwt.decode(
                token, current_app.config["SECRET_KEY"], algorithms=["HS256"]
            )["reset_password"]
        except Exception:
            return
        return db.session.get(User, _id)

    def get_account_verification_token(self, expires_in=86400):  # 24 hours
        """Generate an account verification token for the user."""
        return jwt.encode(
            {"verify_account": self.id, "exp": time() + expires_in},
            current_app.config["SECRET_KEY"],
            algorithm="HS256",
        )

    @staticmethod
    def verify_account_verification_token(token):
        """Verify an account verification token and return the associated user."""
        try:
            _id = jwt.decode(
                token, current_app.config["SECRET_KEY"], algorithms=["HS256"]
            )["verify_account"]
        except Exception:
            return
        return db.session.get(User, _id)


class Admin(User):
    """Admin user model, inheriting from User."""

    __tablename__ = "admins"
    id: Mapped[str] = mapped_column(
        ULID,
        ForeignKey(USERS_ID_FK, ondelete="cascade"),
        primary_key=True,
        server_default=func.gen_ulid(),
    )

    __mapper_args__ = {"polymorphic_identity": UserType.ADMIN}


class Seller(User):
    """Seller user model, inheriting from User."""

    __tablename__ = "sellers"
    id: Mapped[str] = mapped_column(
        ULID,
        ForeignKey(USERS_ID_FK, ondelete="cascade"),
        primary_key=True,
        server_default=func.gen_ulid(),
    )
    company_name: Mapped[str] = mapped_column(String(32))
    rating: Mapped[Optional[Decimal]] = mapped_column(Numeric(4, 2))

    listing: Mapped[Optional[List["Listing"]]] = relationship(
        back_populates="seller",
        cascade=CASCADE_ALL_DELETE_ORPHAN,
    )

    __mapper_args__ = {"polymorphic_identity": UserType.SELLER}


class Customer(User):
    """Customer user model, inheriting from User."""

    __tablename__ = "customers"
    id: Mapped[str] = mapped_column(
        ULID,
        ForeignKey(USERS_ID_FK, ondelete="cascade"),
        primary_key=True,
        server_default=func.gen_ulid(),
    )

    cart: Mapped["Cart"] = relationship(back_populates="customer")
    order: Mapped[Optional[List["Order"]]] = relationship(
        back_populates="customer",
        uselist=False,
        cascade=CASCADE_ALL_DELETE_ORPHAN,
    )
    address: Mapped[Optional[List["CustomerAddress"]]] = relationship(
        back_populates="customer",
        uselist=False,
        cascade=CASCADE_ALL_DELETE_ORPHAN,
    )

    wishlist: Mapped[Optional[List["WishList"]]] = relationship(
        back_populates="customer",
        cascade=CASCADE_ALL_DELETE_ORPHAN,
        single_parent=True,
    )
    review: Mapped[List["ListingReview"]] = relationship(
        back_populates="customer",
        cascade=CASCADE_ALL_DELETE_ORPHAN,
        single_parent=True,
    )

    __mapper_args__ = {"polymorphic_identity": UserType.CUSTOMER}


class CustomerAddress(BaseModel):
    """Model representing a customer's address."""

    __tablename__ = "customer_addresses"
    id: Mapped[str] = mapped_column(
        ULID, primary_key=True, server_default=func.gen_ulid()
    )
    street: Mapped[str] = mapped_column(String(128))
    city: Mapped[str] = mapped_column(String(64))
    state: Mapped[str] = mapped_column(String(64))
    country: Mapped[str] = mapped_column(String(64))
    postal_code: Mapped[str] = mapped_column(String(32))
    customer_id: Mapped[Optional[str]] = mapped_column(
        ULID, ForeignKey(CUSTOMERS_ID), nullable=True
    )

    customer: Mapped["Customer"] = relationship(back_populates="address", uselist=False)


class ProductCategory(BaseModel):
    """Model representing a product category."""

    __tablename__ = "product_categories"
    id: Mapped[str] = mapped_column(
        ULID, primary_key=True, server_default=func.gen_ulid()
    )
    title: Mapped[str] = mapped_column(String(32), unique=True)
    product: Mapped[List["Product"]] = relationship(back_populates="category")


ProductWordOccurrence = Table(
    "product_word_occurrences",
    BaseModel.metadata,
    Column(
        "product_id",
        ULID,
        ForeignKey(PRODUCTS_ID),
        primary_key=True,
        server_default=func.gen_ulid(),
    ),
    Column(
        "word_occurrence_id",
        ULID,
        ForeignKey("word_occurrences.id"),
        primary_key=True,
        server_default=func.gen_ulid(),
    ),
)


class Product(BaseModel):
    """Model representing a product."""

    __tablename__ = "products"
    id: Mapped[str] = mapped_column(
        ULID, primary_key=True, server_default=func.gen_ulid()
    )
    name: Mapped[str] = mapped_column(String(32))
    description: Mapped[str] = mapped_column(Text)
    image_src: Mapped[str] = mapped_column(Text)
    category_id: Mapped[str] = mapped_column(ULID, ForeignKey("product_categories.id"))

    category: Mapped["ProductCategory"] = relationship(back_populates="product")
    listing: Mapped[Optional[List["Listing"]]] = relationship(back_populates="product")
    words: Mapped[List["WordOccurrence"]] = relationship(
        secondary=ProductWordOccurrence, back_populates="products"
    )


class Listing(BaseModel):
    """Model representing a product listing by a seller."""

    __tablename__ = "listings"

    id: Mapped[str] = mapped_column(
        ULID, primary_key=True, server_default=func.gen_ulid()
    )
    quantity: Mapped[int]
    is_available: Mapped[bool] = mapped_column(default=False)
    price: Mapped[Decimal] = mapped_column(Numeric(10, 2))
    product_state: Mapped[ProductState] = mapped_column(SQLAlchemyEnum(ProductState))
    purchase_count: Mapped[int] = mapped_column(default=0)
    view_count: Mapped[int] = mapped_column(default=0)
    seller_id: Mapped[str] = mapped_column(ULID, ForeignKey("sellers.id"))
    product_id: Mapped[str] = mapped_column(ULID, ForeignKey(PRODUCTS_ID))

    seller: Mapped["Seller"] = relationship(back_populates="listing")
    product: Mapped["Product"] = relationship(back_populates="listing")
    cart_entry: Mapped[List["CartEntry"]] = relationship(back_populates="listing")
    review: Mapped[List["ListingReview"]] = relationship(
        back_populates="listing", cascade=CASCADE_ALL_DELETE_ORPHAN
    )
    order_entries: Mapped[Optional[List["OrderEntry"]]] = relationship(
        back_populates="listing"
    )
    wishlist_entry: Mapped[Optional[List["WishListEntry"]]] = relationship(
        back_populates="listing"
    )


class ListingReview(BaseModel):
    """Model representing a review for a product listing."""

    __tablename__ = "reviews"
    id: Mapped[str] = mapped_column(
        ULID, primary_key=True, server_default=func.gen_ulid()
    )
    title: Mapped[str] = mapped_column(String(64))
    description: Mapped[Optional[str]] = mapped_column(Text)
    rating: Mapped[ReviewRate] = mapped_column(SQLAlchemyEnum(ReviewRate))
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.now(UTC))
    modified_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.now(UTC), onupdate=datetime.now(UTC)
    )
    customer_id: Mapped[str] = mapped_column(ULID, ForeignKey(CUSTOMERS_ID))
    listing_id: Mapped[str] = mapped_column(ULID, ForeignKey(LISTINGS_ID))

    customer: Mapped["Customer"] = relationship(back_populates="review")
    listing: Mapped["Listing"] = relationship(back_populates="review")


class CartEntry(BaseModel):
    """Model representing an item in a customer's cart."""

    __tablename__ = "cart_entries"
    id: Mapped[str] = mapped_column(
        ULID, primary_key=True, server_default=func.gen_ulid()
    )
    quantity: Mapped[int]
    cart_id: Mapped[str] = mapped_column(ULID, ForeignKey("carts.customer_id"))
    listing_id: Mapped[str] = mapped_column(ULID, ForeignKey(LISTINGS_ID))

    cart: Mapped["Cart"] = relationship(back_populates="cart_entry")
    listing: Mapped["Listing"] = relationship(back_populates="cart_entry")


class Cart(BaseModel):
    """Model representing a customer's shopping cart."""

    __tablename__ = "carts"
    customer_id: Mapped[str] = mapped_column(
        ULID, ForeignKey(CUSTOMERS_ID), primary_key=True
    )

    customer: Mapped["Customer"] = relationship(back_populates="cart")
    cart_entry: Mapped[Optional[List["CartEntry"]]] = relationship(
        back_populates="cart",
        uselist=False,
        cascade=CASCADE_ALL_DELETE_ORPHAN,
    )


class WishListEntry(BaseModel):
    """
    Model representing an item in a customer's wishlist.

    This model creates a many-to-many relationship between WishList and Listing.
    """

    __tablename__ = "wishlist_entries"
    id: Mapped[str] = mapped_column(
        ULID, primary_key=True, server_default=func.gen_ulid()
    )
    product_id: Mapped[str] = mapped_column(ULID, ForeignKey("listings.id"))
    wishlist_id: Mapped[str] = mapped_column(ULID, ForeignKey("wishlists.id"))
    listing_id: Mapped["Listing"] = relationship(back_populates="wishlist_entry")

    wishlist: Mapped["WishList"] = relationship(back_populates="wishlist_entries")
    listing: Mapped["Listing"] = relationship(back_populates="wishlist_entry")


class WishList(BaseModel):
    """
    Model representing a customer's wishlist.

    A customer can have multiple wishlists, each with a unique name.
    """

    __tablename__ = "wishlists"
    id: Mapped[str] = mapped_column(
        ULID, primary_key=True, server_default=func.gen_ulid()
    )
    name: Mapped[str] = mapped_column(String(32))
    customer_id: Mapped[str] = mapped_column(ULID, ForeignKey(CUSTOMERS_ID))

    customer: Mapped["Customer"] = relationship(back_populates="wishlist")
    wishlist_entries: Mapped[Optional[List["WishListEntry"]]] = relationship(
        back_populates="wishlist", cascade=CASCADE_ALL_DELETE_ORPHAN
    )


class OrderEntry(BaseModel):
    """
    Model representing an individual item in an order.

    Each entry corresponds to a specific listing and quantity ordered.
    """

    __tablename__ = "order_entries"
    id: Mapped[str] = mapped_column(
        ULID, primary_key=True, server_default=func.gen_ulid()
    )
    quantity: Mapped[int]
    order_id: Mapped[str] = mapped_column(ULID, ForeignKey("orders.id"))
    listing_id: Mapped[str] = mapped_column(ULID, ForeignKey(LISTINGS_ID))

    order: Mapped["Order"] = relationship(back_populates="order_entries")
    listing: Mapped["Listing"] = relationship(back_populates="order_entries")


class Order(BaseModel):
    """
    Model representing a customer's order.

    Includes order details, status, and shipping address information.
    """

    __tablename__ = "orders"
    id: Mapped[str] = mapped_column(
        ULID, primary_key=True, server_default=func.gen_ulid()
    )
    price: Mapped[Decimal] = mapped_column(Numeric(10, 2))
    order_status: Mapped[OrderStatus] = mapped_column(SQLAlchemyEnum(OrderStatus))
    purchased_at: Mapped[Optional[datetime]] = mapped_column(DateTime)
    address_street: Mapped[str] = mapped_column(String(128))
    address_city: Mapped[str] = mapped_column(String(64))
    address_state: Mapped[str] = mapped_column(String(64))
    address_country: Mapped[str] = mapped_column(String(64))
    address_postal_code: Mapped[str] = mapped_column(String(32))
    customer_id: Mapped[str] = mapped_column(ULID, ForeignKey(CUSTOMERS_ID))

    order_entries: Mapped[List["OrderEntry"]] = relationship(back_populates="order")
    customer: Mapped["Customer"] = relationship(back_populates="order")


class DeleteRequest(BaseModel):
    """
    Model representing a user's request to delete their account.

    Includes the reason for deletion and scheduled deletion time.
    """

    __tablename__ = "delete_requests"
    id: Mapped[str] = mapped_column(
        ULID, primary_key=True, server_default=func.gen_ulid()
    )
    reason: Mapped[Optional[str]] = mapped_column(Text)
    requested_at: Mapped[datetime] = mapped_column(DateTime, default=func.now())
    to_be_removed_at: Mapped[datetime] = mapped_column(DateTime)
    user_id: Mapped[str] = mapped_column(ULID, ForeignKey(USERS_ID_FK))

    user: Mapped["User"] = relationship(back_populates="delete_request")


class WordOccurrence(BaseModel):
    """
    Model representing the occurrence of words in product descriptions.

    This model creates a many-to-many relationship between Word and Product.
    """

    __tablename__ = "word_occurrences"
    id: Mapped[str] = mapped_column(
        ULID, primary_key=True, server_default=func.gen_ulid()
    )
    word_id: Mapped[str] = mapped_column(ULID, ForeignKey("words.id"))
    word: Mapped["Word"] = relationship(back_populates="word_occ")
    products: Mapped[List["Product"]] = relationship(
        secondary=ProductWordOccurrence, back_populates="words"
    )


class Word(BaseModel):
    """
    Model representing individual words used in product descriptions.

    This model is used for efficient text search and analysis.
    """

    __tablename__ = "words"
    id: Mapped[str] = mapped_column(
        ULID, primary_key=True, server_default=func.gen_ulid()
    )
    word: Mapped[str] = mapped_column(String(32))

    word_occ: Mapped[List["WordOccurrence"]] = relationship(back_populates="word")


# materialized views


class MVProductCategory(BaseModel):
    """
    Materialized view combining product and category information.

    This view is used to optimize queries that frequently join Product and ProductCategory tables.
    """

    __table__ = create_materialized_view(
        name="mv_product_categories",
        selectable=select(
            *_select_args(
                Product.id.label("product_id"),
                Product.name.label("product_name"),
                Product.description.label("product_description"),
                Product.image_src.label("product_img"),
                ProductCategory.title.label("product_category"),
            )
        ).select_from(
            Product.__table__.join(
                ProductCategory, Product.category_id == ProductCategory.id
            )
        ),
        metadata=BaseModel.metadata,
    )


# This module defines additional models for the e-commerce application.
# All models inherit from BaseModel, which provides CRUD operations and serialization capabilities.

# Key features:
# - Use of ULID for primary keys, providing sortable, URL-safe identifiers
# - Complex relationships between models, including many-to-many relationships
# - Use of materialized views for query optimization
# - Detailed tracking of user deletion requests
# - Word occurrence tracking for advanced product search capabilities

# These models extend the core functionality of the e-commerce platform,
# enabling features like wishlists, detailed order tracking, and efficient text search.
