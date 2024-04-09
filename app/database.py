from datetime import datetime, date
from sqlalchemy import create_engine
from sqlalchemy import ForeignKey
from typing import Optional
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column
from sqlalchemy.orm import relationship


class Base(DeclarativeBase):
    pass


class User(Base):
    __tablename__ = "user"
    id: Mapped[int] = mapped_column(
        primary_key=True)
    username: Mapped[str] = mapped_column(unique=True)
    email: Mapped[str] = mapped_column(unique=True)
    name: Mapped[str]
    surname: Mapped[str]  # not null column
    phone_number: Mapped[Optional[str]]  # nullable column
    birth_date: Mapped[date]
    role: Mapped[str]
    created_at: Mapped[datetime] = mapped_column(default=datetime.utcnow)
    modified_at: Mapped[datetime] = mapped_column(default=datetime.utcnow)

    def __repr__(self) -> str:
        return f"User(id={self.id!r}, username={self.name!r}, role={self.role!r}, created_at={self.created_at!r}, " \
               f"modified_at={self.modified_at!r})"


class Seller(User):
    __tablename__ = "seller"
    id: Mapped[int] = mapped_column(ForeignKey("user.id"), primary_key=True)
    company_name: Mapped[str]


class CustomerAddress(Base):
    __tablename__ = "customer_address"
    id: Mapped[int] = mapped_column(primary_key=True)
    customer: Mapped["Customer"] = relationship(back_populates="customer_address")


class Customer(User):
    __tablename__ = "customer"
    id: Mapped[int] = mapped_column(ForeignKey("user.id"), primary_key=True)
    address_id: Mapped[int] = mapped_column(ForeignKey("customer_address.id"))
    customer_address: Mapped["CustomerAddress"] = relationship(back_populates="customer")


engine = create_engine('sqlite://', echo=True)  # todo: set to SQLite for testing (change in PostgreSQL)

Base.metadata.create_all(engine)
