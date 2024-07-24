import enum
from datetime import datetime
from decimal import Decimal
from typing import Optional, List
from sqlalchemy import (
    Boolean,
    ForeignKey,
    Table,
    Column,
    Integer,
    func,
    String,
    Date,
    DateTime,
    Numeric,
    Text,
    Enum,
    select,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship
from .base_models import BaseModel
from sqlalchemy_utils import create_materialized_view
from sqlalchemy_utils.compat import _select_args


class UserType(enum.Enum):
    USER = "user"
    ADMIN = "admin"
    CUSTOMER = "customer"
    SELLER = "seller"


class ProductState(enum.Enum):
    NEW = "new"
    USED = "used"
    REFURBISHED = "refurbished"


class OrderStatus(enum.Enum):
    PENDING = "pending"
    SHIPPED = "shipped"
    DELIVERED = "delivered"


class ReviewRate(enum.Enum):
    ONE = 1
    TWO = 2
    THREE = 3
    FOUR = 4
    FIVE = 5


# TODO /change-password route
# TODO three endpoint to verify solo admin and from all
# TODO solve the infinity recursion when a relationship is Null


class TokenBlocklist(BaseModel):
    __tablename__ = "tokens_blocklist"
    id: Mapped[int] = mapped_column(primary_key=True)
    jti: Mapped[str] = mapped_column(String(36), index=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    created_at: Mapped[datetime] = mapped_column(DateTime)
    expired_at: Mapped[datetime] = mapped_column(DateTime, index=True)


class User(BaseModel):
    __tablename__ = "users"
    id: Mapped[int] = mapped_column(primary_key=True)
    email: Mapped[str] = mapped_column(String(64), unique=True)
    name: Mapped[str] = mapped_column(String(32))
    surname: Mapped[str] = mapped_column(String(32))
    password: Mapped[Optional[str]] = mapped_column(String(64))
    birth_date: Mapped[Optional[datetime]] = mapped_column(Date)
    phone_number: Mapped[Optional[str]] = mapped_column(String(32))
    user_type: Mapped[str] = mapped_column(Enum(UserType))
    created_at: Mapped[datetime] = mapped_column(DateTime, default=func.now())
    modified_at: Mapped[datetime] = mapped_column(
        DateTime, default=func.now(), onupdate=func.now()
    )
    is_active: Mapped[bool] = mapped_column(Boolean, default=False)

    # TODO solve the infinite recursion when i call the to_dict method due to delete_request relationship

    delete_request: Mapped[Optional["DeleteRequest"]] = relationship(
        back_populates="user"
    )

    __mapper_args__ = {
        "polymorphic_identity": UserType.USER,
        "polymorphic_on": user_type,
    }


class Admin(User):
    __tablename__ = "admins"
    id: Mapped[int] = mapped_column(ForeignKey("users.id"), primary_key=True)

    __mapper_args__ = {"polymorphic_identity": UserType.ADMIN}


class Seller(User):
    __tablename__ = "sellers"
    id: Mapped[int] = mapped_column(ForeignKey("users.id"), primary_key=True)
    company_name: Mapped[str] = mapped_column(String(32))
    rating: Mapped[Optional[Decimal]] = mapped_column(Numeric(4, 2))

    listing: Mapped[Optional[List["Listing"]]] = relationship(back_populates="seller")

    __mapper_args__ = {"polymorphic_identity": UserType.SELLER}


class Customer(User):
    __tablename__ = "customers"
    id: Mapped[int] = mapped_column(ForeignKey("users.id"), primary_key=True)
    address_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey("customer_addresses.id"), nullable=True
    )

    cart: Mapped["Cart"] = relationship(back_populates="customer")
    address: Mapped[Optional["CustomerAddress"]] = relationship(
        back_populates="customer", uselist=False
    )

    wishlist: Mapped[Optional[List["WishList"]]] = relationship(
        back_populates="customer"
    )
    review: Mapped[List["ProductReview"]] = relationship(back_populates="customer")

    __mapper_args__ = {"polymorphic_identity": UserType.CUSTOMER}


class CustomerAddress(BaseModel):
    __tablename__ = "customer_addresses"
    id: Mapped[int] = mapped_column(primary_key=True)
    street: Mapped[str] = mapped_column(String(128))
    city: Mapped[str] = mapped_column(String(64))
    state: Mapped[str] = mapped_column(String(64))
    country: Mapped[str] = mapped_column(String(64))
    postal_code: Mapped[str] = mapped_column(String(32))

    customer: Mapped["Customer"] = relationship(back_populates="address", uselist=False)


class ProductCategory(BaseModel):
    __tablename__ = "product_categories"
    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column(String(32), unique=True)
    product: Mapped[List["Product"]] = relationship(back_populates="category")


ProductWordOccurrence = Table(
    "product_word_occurrences",
    BaseModel.metadata,
    Column("product_id", Integer, ForeignKey("products.id"), primary_key=True),
    Column(
        "word_occurrence_id",
        Integer,
        ForeignKey("word_occurrences.id"),
        primary_key=True,
    ),
)


class Product(BaseModel):
    __tablename__ = "products"
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(32))
    description: Mapped[str] = mapped_column(Text)
    image_src: Mapped[str] = mapped_column(Text)
    category_id: Mapped[int] = mapped_column(ForeignKey("product_categories.id"))

    category: Mapped["ProductCategory"] = relationship(back_populates="product")
    wishlist_entry: Mapped[Optional[List["WishListEntry"]]] = relationship(
        back_populates="product"
    )
    listing: Mapped[Optional[List["Listing"]]] = relationship(back_populates="product")
    words: Mapped[List["WordOccurrence"]] = relationship(
        secondary=ProductWordOccurrence, back_populates="products"
    )


class Listing(BaseModel):
    __tablename__ = "listings"
    id: Mapped[int] = mapped_column(primary_key=True)
    quantity: Mapped[int]
    available: Mapped[bool]
    price: Mapped[Decimal] = mapped_column(Numeric(10, 2))
    product_state: Mapped[ProductState]
    seller_id: Mapped[int] = mapped_column(ForeignKey("sellers.id"))
    product_id: Mapped[int] = mapped_column(ForeignKey("products.id"))

    seller: Mapped["Seller"] = relationship(back_populates="listing")
    product: Mapped["Product"] = relationship(back_populates="listing")
    cart_entry: Mapped[List["CartEntry"]] = relationship(back_populates="listing")
    review: Mapped[List["ProductReview"]] = relationship(back_populates="listing")
    order_entries: Mapped[List["OrderEntry"]] = relationship(back_populates="listing")


class ProductReview(BaseModel):
    __tablename__ = "reviews"
    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column(String(64))
    description: Mapped[Optional[str]] = mapped_column(Text)
    rating: Mapped[ReviewRate]
    created_at: Mapped[datetime] = mapped_column(DateTime, default=func.now())
    modified_at: Mapped[datetime] = mapped_column(
        DateTime, default=func.now(), onupdate=func.now()
    )
    customer_id: Mapped[int] = mapped_column(ForeignKey("customers.id"))
    listing_id: Mapped[int] = mapped_column(ForeignKey("listings.id"))

    customer: Mapped["Customer"] = relationship(back_populates="review")
    listing: Mapped["Listing"] = relationship(back_populates="review")


class CartEntry(BaseModel):
    __tablename__ = "cart_entries"
    id: Mapped[int] = mapped_column(primary_key=True)
    amount: Mapped[Decimal] = mapped_column(Numeric(10, 2))
    cart_id: Mapped[int] = mapped_column(ForeignKey("carts.id"))
    listing_id: Mapped[int] = mapped_column(ForeignKey("listings.id"))

    cart: Mapped["Cart"] = relationship(back_populates="cart_entry")
    listing: Mapped["Listing"] = relationship(back_populates="cart_entry")


class Cart(BaseModel):
    __tablename__ = "carts"
    id: Mapped[int] = mapped_column(primary_key=True)
    customer_id: Mapped[int] = mapped_column(ForeignKey("customers.id"))

    customer: Mapped["Customer"] = relationship(back_populates="cart")
    cart_entry: Mapped[Optional[List["CartEntry"]]] = relationship(
        back_populates="cart"
    )


class WishListEntry(BaseModel):
    __tablename__ = "wishlist_entries"
    id: Mapped[int] = mapped_column(primary_key=True)
    product_id: Mapped[int] = mapped_column(ForeignKey("products.id"))
    wishlist_id: Mapped[int] = mapped_column(ForeignKey("wishlists.id"))

    product: Mapped["Product"] = relationship(back_populates="wishlist_entry")
    wishlist: Mapped["WishList"] = relationship(back_populates="wishlist_entries")


class WishList(BaseModel):
    __tablename__ = "wishlists"
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(32))
    costumer_id: Mapped[int] = mapped_column(ForeignKey("customers.id"))

    customer: Mapped["Customer"] = relationship(back_populates="wishlist")
    wishlist_entries: Mapped[List["WishListEntry"]] = relationship(
        back_populates="wishlist"
    )


class OrderEntry(BaseModel):
    __tablename__ = "order_entries"
    id: Mapped[int] = mapped_column(primary_key=True)
    order_id: Mapped[int] = mapped_column(ForeignKey("orders.id"))
    listing_id: Mapped[int] = mapped_column(ForeignKey("listings.id"))

    order: Mapped["Order"] = relationship(back_populates="order_entries")
    listing: Mapped["Listing"] = relationship(back_populates="order_entries")


class Order(BaseModel):
    __tablename__ = "orders"
    id: Mapped[int] = mapped_column(primary_key=True)
    price: Mapped[Decimal] = mapped_column(Numeric(10, 2))
    order_status: Mapped[OrderStatus]
    purchased_at: Mapped[Optional[datetime]] = mapped_column(DateTime)
    address_street: Mapped[str] = mapped_column(String(128))
    address_city: Mapped[str] = mapped_column(String(64))
    address_state: Mapped[str] = mapped_column(String(64))
    address_country: Mapped[str] = mapped_column(String(64))
    address_postal_code: Mapped[str] = mapped_column(String(32))

    order_entries: Mapped[List["OrderEntry"]] = relationship(back_populates="order")


class DeleteRequest(BaseModel):
    __tablename__ = "delete_requests"
    id: Mapped[int] = mapped_column(primary_key=True)
    reason: Mapped[str] = mapped_column(Text)
    requested_at: Mapped[datetime] = mapped_column(DateTime, default=func.now())
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))

    user: Mapped["User"] = relationship(back_populates="delete_request")


class WordOccurrence(BaseModel):
    __tablename__ = "word_occurrences"
    id: Mapped[int] = mapped_column(primary_key=True)
    word_id: Mapped[int] = mapped_column(ForeignKey("words.id"))
    word: Mapped["Word"] = relationship(back_populates="word_occ")
    products: Mapped[List["Product"]] = relationship(
        secondary=ProductWordOccurrence, back_populates="words"
    )


class Word(BaseModel):
    __tablename__ = "words"
    id: Mapped[int] = mapped_column(primary_key=True)
    word: Mapped[str] = mapped_column(String(32))

    word_occ: Mapped[List["WordOccurrence"]] = relationship(back_populates="word")


# materialized views


class MVProductCategory(BaseModel):
    __table__ = create_materialized_view(
        name="mv_product_categories",
        selectable=select(
            *_select_args(
                Product.id.label("product_id"),
                Product.name.label("product_name"),
                Product.description.label("product_descr"),
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
