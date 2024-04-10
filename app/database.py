import datetime
import enum
from sqlalchemy import (
    create_engine,
    ForeignKey,
    Text,
    Date,
    DateTime,
)
from sqlalchemy.orm import (
    DeclarativeBase,
    Mapped,
    mapped_column,
    relationship
)
from typing import (
    Optional,
    List
)

now = datetime.datetime.now


class Base(DeclarativeBase):
    type_annotation_map = {
        str: Text
    }


class UserRole(enum.Enum):
    SELLER = 'seller'
    CUSTOMER = 'customer'


class ReviewRate(enum.Enum):
    ONE = 1
    TWO = 2
    THREE = 3
    FOUR = 4
    FIVE = 5


class User(Base):
    __tablename__ = "users"
    id: Mapped[int] = mapped_column(primary_key=True)
    username: Mapped[str] = mapped_column(unique=True)
    email: Mapped[str] = mapped_column(unique=True)
    name: Mapped[str]
    surname: Mapped[str]
    birth_date: Mapped[datetime] = mapped_column(Date)
    phone_number: Mapped[Optional[str]]
    role: Mapped[UserRole] = mapped_column()
    created_at: Mapped[datetime] = mapped_column(DateTime, default=now)
    modified_at: Mapped[datetime] = mapped_column(DateTime, default=now, onupdate=now)
    __mapper_args__ = {'polymorphic_on': role}

    review: Mapped[List["Review"]] = relationship(back_populates="user")


class Seller(User):
    __tablename__ = "sellers"
    id: Mapped[int] = mapped_column(ForeignKey("users.id"), primary_key=True)
    company_name: Mapped[str]
    __mapper_args__ = {'polymorphic_identity': UserRole.SELLER}


class CustomerAddress(Base):
    __tablename__ = "customers_addresses"
    id: Mapped[int] = mapped_column(primary_key=True)
    street: Mapped[str]
    city: Mapped[str]
    country: Mapped[str]
    postal_code: Mapped[str]
    address_line1: Mapped[Optional[str]]
    address_line2: Mapped[Optional[str]]

    customer: Mapped["Customer"] = relationship(back_populates="address")


class Customer(User):
    __tablename__ = "customers"
    id: Mapped[int] = mapped_column(ForeignKey("users.id"), primary_key=True)
    __mapper_args__ = {'polymorphic_identity': UserRole.CUSTOMER}

    address_id: Mapped[int] = mapped_column(ForeignKey("customers_addresses.id"))
    address: Mapped["CustomerAddress"] = relationship(back_populates="customer")


class Review(Base):
    __tablename__ = "reviews"
    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str]
    body: Mapped[Optional[str]]
    rating: Mapped[ReviewRate] = mapped_column()
    created_at: Mapped[datetime] = mapped_column(DateTime, default=now)
    modified_at: Mapped[datetime] = mapped_column(DateTime, default=now, onupdate=now)

    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))  # should be only related to Customer?
    user: Mapped["User"] = relationship(back_populates="review")


engine = create_engine("postgresql+psycopg2://postgres:1234@localhost/",
                       echo=True)

Base.metadata.create_all(bind=engine)
