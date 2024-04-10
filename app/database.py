# todo add User
import datetime
import enum
from decimal import Decimal

from sqlalchemy import (
    create_engine,
    ForeignKey,
    String,
    Date,
    DateTime,
    UniqueConstraint,
    Numeric,
)
from sqlalchemy.orm import (
    DeclarativeBase,
    Mapped,
    registry,
    mapped_column,
    relationship,
)
from typing import (
    Optional,
    List,
)
from typing_extensions import Annotated

now = datetime.datetime.now

str_32 = Annotated[str, 32]
str_48 = Annotated[str, 48]
str_64 = Annotated[str, 64]
text = Annotated[str, 5000]
num_10_2 = Annotated[Decimal, 10]


class Base(DeclarativeBase):
    registry = registry(
        type_annotation_map={
            str_32: String(32),
            str_48: String(48),
            str_64: String(64),
            text: String(5000),
            num_10_2: Numeric(10, 2),
        }
    )


class UserRole(enum.Enum):
    SELLER = 'seller'
    CUSTOMER = 'customer'


class ReviewRate(enum.Enum):
    ONE = 1
    TWO = 2
    THREE = 3
    FOUR = 4
    FIVE = 5


class ProductState(enum.Enum):
    NEW = 'new'
    USED = 'used'
    REFURBISHED = 'refurbished'


class OrderStatus(enum.Enum):
    PENDING = 'pending'
    SHIPPED = 'shipped'
    DELIVERED = 'delivered'


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)
    username: Mapped[str_32] = mapped_column(unique=True)
    email: Mapped[str_48] = mapped_column(unique=True)
    name: Mapped[str_32]
    surname: Mapped[str_32]
    birth_date: Mapped[datetime] = mapped_column(Date)
    phone_number: Mapped[Optional[str_64]]
    role: Mapped[UserRole] = mapped_column()
    created_at: Mapped[datetime] = mapped_column(DateTime, default=now)
    modified_at: Mapped[datetime] = mapped_column(DateTime, default=now, onupdate=now)
    __mapper_args__ = {'polymorphic_on': role}
    review: Mapped[List["Review"]] = relationship(back_populates="user")


class Seller(User):
    __tablename__ = "sellers"

    id: Mapped[int] = mapped_column(ForeignKey("users.id"), primary_key=True)
    company_name: Mapped[str_32]
    __mapper_args__ = {'polymorphic_identity': UserRole.SELLER}


class CustomerAddress(Base):
    __tablename__ = "customers_addresses"

    id: Mapped[int] = mapped_column(primary_key=True)
    street: Mapped[str_48]
    city: Mapped[str_32]
    country: Mapped[str_32]
    postal_code: Mapped[str_32]
    address_line1: Mapped[Optional[str_64]]
    address_line2: Mapped[Optional[str_64]]
    customer: Mapped["Customer"] = relationship(back_populates="address")


class Customer(User):
    __tablename__ = "customers"

    id: Mapped[int] = mapped_column(ForeignKey("users.id"), primary_key=True)
    __mapper_args__ = {'polymorphic_identity': UserRole.CUSTOMER}
    address_id: Mapped[int] = mapped_column(ForeignKey("customers_addresses.id"))
    address: Mapped["CustomerAddress"] = relationship(back_populates="customer")
    wishlist: Mapped[List["WishList"]] = relationship(back_populates="customer")
    cart: Mapped["Cart"] = relationship(back_populates="customer")


class Review(Base):
    __tablename__ = "reviews"

    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str_32]
    body: Mapped[Optional[text]]
    rating: Mapped[ReviewRate] = mapped_column()
    created_at: Mapped[datetime] = mapped_column(DateTime, default=now)
    modified_at: Mapped[datetime] = mapped_column(DateTime, default=now, onupdate=now)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))  # should be only related to Customer?
    user: Mapped["User"] = relationship(back_populates="review")

    def __repr__(self) -> str:
        return f"Review(id={self.id!r}, title={self.title!r}, rating={self.rating!r}, " \
               f"created_at={self.created_at!r}, modified_at={self.modified_at!r}, " \
               f"writer={self.user_id})"


class ProductCategory(Base):
    __tablename__ = "product_categories"

    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str_32]
    product: Mapped[List["Product"]] = relationship(back_populates="category")


class Product(Base):
    __tablename__ = "products"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str_48]
    description: Mapped[Optional[text]]
    image_src: Mapped[str_64]  # todo maybe should be longer?
    category_id: Mapped[int] = mapped_column(ForeignKey("product_categories.id"))
    category: Mapped["ProductCategory"] = relationship(back_populates="product")
    listing: Mapped[List["Listing"]] = relationship(back_populates="product")
    wishlist_entry: Mapped[List["WishListEntry"]] = relationship(back_populates="product")


class Listing(Base):
    __tablename__ = "listings"

    id: Mapped[int] = mapped_column(primary_key=True)
    quantity: Mapped[int]
    available: Mapped[bool]
    price: Mapped[num_10_2]
    state: Mapped[ProductState] = mapped_column()
    product_id: Mapped[int] = mapped_column(ForeignKey("products.id"))
    product: Mapped["Product"] = relationship(back_populates="listing")
    cart_entry: Mapped[List["CartEntry"]] = relationship(back_populates="listing")


class Cart(Base):
    __tablename__ = "carts"

    id: Mapped[int] = mapped_column(primary_key=True)
    customer_id: Mapped[int] = mapped_column(ForeignKey("customers.id"))
    customer: Mapped["Customer"] = relationship(back_populates="cart")
    cart_entry: Mapped[List["CartEntry"]] = relationship(back_populates="cart")
    __table_args__ = (UniqueConstraint("customer_id"),)


class CartEntry(Base):
    __tablename__ = "cart_entries"

    id: Mapped[int] = mapped_column(primary_key=True)
    amount: Mapped[int]
    cart_id: Mapped[int] = mapped_column(ForeignKey("carts.id"))
    listing_id: Mapped[int] = mapped_column(ForeignKey("listings.id"))
    cart: Mapped["Cart"] = relationship(back_populates="cart_entry")
    listing: Mapped["Listing"] = relationship(back_populates="cart_entry")


class Order(Base):
    __tablename__ = "orders"

    id: Mapped[int] = mapped_column(primary_key=True)
    price: Mapped[num_10_2]
    status: Mapped[OrderStatus] = mapped_column()

    # purchased_at: Mapped[Optional[datetime]] = mapped_column(DateTime,)

    def __repr__(self) -> str:
        return f"Order(id={self.id!r}, price={self.price!r}, status={self.status!r})"


class OrderEntry(Base):
    __tablename__ = "order_entries"

    id: Mapped[int] = mapped_column(primary_key=True)
    price: Mapped[num_10_2]
    listing_id: Mapped[int] = mapped_column(ForeignKey('listings.id'))
    order_id: Mapped[int] = mapped_column(ForeignKey('orders.id'))

    def __repr__(self) -> str:
        return f"OrderEntry(id={self.id!r}, price={self.price!r}, listing_id={self.listing_id}," \
               f"order_id={self.order_id!r})"


class WishList(Base):
    __tablename__ = "wishlists"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str_32]
    customer_id: Mapped[int] = mapped_column(ForeignKey("customers.id"))
    customer: Mapped["Customer"] = relationship(back_populates="wishlist")
    wishlist_entry: Mapped[List["WishListEntry"]] = relationship(back_populates="wishlist")

    __table_args__ = (UniqueConstraint("customer_id"),)

    def __repr__(self) -> str:
        return f"WishList(id={self.id!r}, name=(id={self.name!r}, customer_id={self.customer_id!r})"


class WishListEntry(Base):
    __tablename__ = "wishlist_entries"

    id: Mapped[int] = mapped_column(primary_key=True)
    wishlist_id: Mapped[int] = mapped_column(ForeignKey("wishlists.id"))
    product_id: Mapped[int] = mapped_column(ForeignKey("products.id"))  # or listing?
    wishlist: Mapped["WishList"] = relationship(back_populates="wishlist_entry")
    product: Mapped["Product"] = relationship(back_populates="wishlist_entry")


engine = create_engine("postgresql+psycopg2://postgres:1234@localhost/",
                       echo=True)

Base.metadata.create_all(bind=engine)
