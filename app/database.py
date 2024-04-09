import datetime
from sqlalchemy import create_engine
from sqlalchemy import ForeignKey, String, Float, Date, DateTime
from typing import Optional
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column
from sqlalchemy.orm import relationship

now = datetime.datetime.utcnow


class Base(DeclarativeBase):
    pass


class User(Base):
    __tablename__ = "user"
    id: Mapped[int] = mapped_column(primary_key=True)
    username: Mapped[str] = mapped_column(String(32), unique=True)
    email: Mapped[str] = mapped_column(String(128), unique=True)
    name: Mapped[str] = mapped_column(String(32))
    surname: Mapped[str] = mapped_column(String(32))
    phone_number: Mapped[Optional[str]] = mapped_column(String(32))
    birth_date: Mapped[Date]
    role: Mapped[str] = mapped_column(String(32), nullable=False)
    created_at: Mapped[DateTime] = mapped_column(default=now)
    modified_at: Mapped[DateTime] = mapped_column(default=now, onupdate=now)

    __mapper_args__ = {'polymorphic_on': role}

    def __repr__(self) -> str:
        return f"User(id={self.id!r}, username={self.name!r}, role={self.role!r}, created_at={self.created_at!r}, " \
               f"modified_at={self.modified_at!r})"


class Seller(User):
    __tablename__ = "seller"
    id: Mapped[int] = mapped_column(ForeignKey("user.id"), primary_key=True)
    company_name: Mapped[str] = mapped_column(String(32))

    __mapper_args__ = {'polymorphic_identity': 'seller'}


class CustomerAddress(Base):
    __tablename__ = "customer_address"
    id: Mapped[int] = mapped_column(primary_key=True)
    city: Mapped[str] = mapped_column(String(64))
    country: Mapped[str] = mapped_column(String(32))
    postcode: Mapped[str] = mapped_column(String(32))
    street_name: Mapped[str] = mapped_column(String(32))
    street_number: Mapped[str] = mapped_column(String(32))

    customer: Mapped["Customer"] = relationship(back_populates="customer_address")


class Customer(User):
    __tablename__ = "customer"
    id: Mapped[int] = mapped_column(ForeignKey("user.id"), primary_key=True)
    address_id: Mapped[int] = mapped_column(ForeignKey("customer_address.id"))

    __mapper_args__ = {'polymorphic_identity': 'customer'}

    customer_address: Mapped["CustomerAddress"] = relationship(back_populates="customer")


class Review:
    __tablename__ = "review"
    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("user.id"))  # todo should be "costumers.id"?
    title: Mapped[str] = mapped_column(String(124))
    description: Mapped[str] = mapped_column(String(50000))
    rating: Mapped[float] = mapped_column(Float(precision=3, decimal_return_scale=1))
    created_at: Mapped[DateTime] = mapped_column(default=now)
    modified_at: Mapped[DateTime] = mapped_column(default=now, onupdate=now)

    user = relationship(User, back_populates="reviews")


engine = create_engine('sqlite://', echo=True)  # todo: set to SQLite for testing (change in PostgresSQL)

Base.metadata.create_all(engine)
