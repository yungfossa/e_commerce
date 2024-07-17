from datetime import datetime
from decimal import Decimal

from .base_models import BaseModel

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
    Table,
    Column,
    Integer,
    func, String, Date, DateTime, Numeric, Text
)

import enum


class UserType(enum.Enum):
    CUSTOMER = 'customer'
    SELLER = 'seller'
    ADMIN = 'admin'
    

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
    
    
class UserRole(BaseModel):
    __tablename__ = 'user_roles'
    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey('users.id'))
    role: Mapped[str] = mapped_column(String(32))
    
    user: Mapped["User"] = relationship(back_populates="user_roles")
 
class Role(BaseModel):
    _tablename__ = 'roles'
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(32), unique=True)
        
    def __repr__(self) -> str:
        return f"<Role(id={self.id!r}, name={self.name!r})>"
    
    
class User(BaseModel):
    __tablename__ = 'users'
    id: Mapped[int] = mapped_column(primary_key=True)
    email: Mapped[str] = mapped_column(String(64), unique=True)
    name: Mapped[str] = mapped_column(String(32))
    surname: Mapped[str] = mapped_column(String(32))
    password: Mapped[Optional[str]] = mapped_column(String(64))
    birth_date: Mapped[datetime] = mapped_column(Date)
    phone_number: Mapped[Optional[str]] = mapped_column(String(32))
    user_type: Mapped[str] = mapped_column(String(32))
    created_at: Mapped[datetime] = mapped_column(DateTime, default=func.now())
    modified_at: Mapped[datetime] = mapped_column(DateTime, default=func.now(), onupdate=func.now())

    user_roles: Mapped[List["UserRole"]] = relationship(back_populates="user", cascade="all, delete-orphan")
    delete_request: Mapped[Optional['DeleteRequest']] = relationship(back_populates="user")

    __mapper_args__ = {
        'polymorphic_identity': "user",
        'polymorphic_on': "user_type"
    }

    def __repr__(self) -> str:
        return f"<User(id={self.id!r}, email={self.email!r}, " \
               f"user_type={self.user_type!r}, created_at={self.created_at!r}, " \
               f"modified_at={self.modified_at!r})>"
    
    def assign_role(self):
        if self.user_type not in ["customer", "seller", "admin"]:
            raise ValueError("Invalid user type")
        user_role = UserRole(role=self.user_type)
        self.user_roles.append(user_role)
            
    @classmethod
    def create(cls, **kwargs):
        user = super().create(**kwargs)
        user.assign_role()
        return user.save()


class Admin(User):
    __tablename__ = "admins"
    id: Mapped[int] = mapped_column(ForeignKey("users.id"), primary_key=True)

    def __repr__(self) -> str:
        return f"Admin(id={self.id!r})"

    __mapper_args__ = {
        'polymorphic_identity': UserType.ADMIN,
    }
    
    
class Seller(User):
    __tablename__ = "sellers"
    id: Mapped[int] = mapped_column(ForeignKey("users.id"), primary_key=True)
    company_name: Mapped[str] = mapped_column(String(32))
    rating: Mapped[Optional[Decimal]] = mapped_column(Numeric(4, 2))

    listing: Mapped[Optional[List["Listing"]]] = relationship(back_populates="seller")

    __mapper_args__ = {
        'polymorphic_identity': UserType.SELLER,
    }

    def __repr__(self) -> str:
        return f"<Seller(id={self.id!r}, email={self.email!r}, " \
               f"company_name={self.company_name!r}, user_type={self.user_type!r}," \
               f"created_at={self.created_at!r}, modified_at={self.modified_at!r})>"


class Customer(User):
    __tablename__ = "customers"
    id: Mapped[int] = mapped_column(ForeignKey("users.id"), primary_key=True)
    address_id: Mapped[int] = mapped_column(ForeignKey("customer_addresses.id"))

    address: Mapped["CustomerAddress"] = relationship(back_populates="customer")
    wishlist: Mapped[Optional[List["WishList"]]] = relationship(back_populates="customer")
    cart: Mapped["Cart"] = relationship(back_populates="customer")
    review: Mapped[Optional[List["ProductReview"]]] = relationship(back_populates="customer")

    __mapper_args__ = {
        'polymorphic_identity': UserType.CUSTOMER,
    }


class CustomerAddress(BaseModel):
    __tablename__ = "customer_addresses"
    id: Mapped[int] = mapped_column(primary_key=True)
    street: Mapped[str] = mapped_column(String(128))
    city: Mapped[str] = mapped_column(String(64))
    state: Mapped[str] = mapped_column(String(64))
    country: Mapped[str] = mapped_column(String(64))
    postal_code: Mapped[str] = mapped_column(String(32))

    customer: Mapped["Customer"] = relationship(back_populates="address")

    def __repr__(self):
        return f"<CustomerAddress(id={self.id}, customer_id={self.customer_id}, " \
               f"street='{self.street}', city='{self.city}', " \
               f"state='{self.state}, country='{self.country}', " \
               f"postal_code='{self.postal_code}')>"


class ProductCategory(BaseModel):
    __tablename__ = "product_categories"
    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column(String(32))

    product: Mapped[List["Product"]] = relationship(back_populates="category")

    def __repr__(self) -> str:
        return f"<ProductCategory(id={self.id!r}, title={self.title!r})>"


ProductWordOccurrence = Table(
    "product_word_occurrences",
    BaseModel.metadata,
    Column("product_id", Integer, ForeignKey("products.id"), primary_key=True),
    Column("word_occurrence_id", Integer, ForeignKey("word_occurrences.id"), primary_key=True)
)


class Product(BaseModel):
    __tablename__ = "products"
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(32))
    description: Mapped[str] = mapped_column(Text)
    image_src: Mapped[str] = mapped_column(Text)
    category_id: Mapped[int] = mapped_column(ForeignKey("product_categories.id"))

    category: Mapped["ProductCategory"] = relationship(back_populates="product")
    wishlist_entry: Mapped[Optional[List["WishListEntry"]]] = relationship(back_populates="product")
    listing: Mapped[Optional[List["Listing"]]] = relationship(back_populates="product")
    words: Mapped[List["WordOccurrence"]] = relationship(secondary=ProductWordOccurrence, back_populates="products")

    def __repr__(self) -> str:
        return f"<Product(id={self.id!r}, name={self.name!r}, " \
               f"image_src={self.image_src}, category={self.category_id!r})>"


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

    def __repr__(self) -> str:
        return f"<Listing(id={self.id!r}, quantity={self.quantity!r}, " \
               f"available={self.available}, price={self.price!r}, " \
               f"product_state={self.product_state!r}, seller_id={self.seller_id!r}" \
               f"product_id={self.product_id!r})>"


class ProductReview(BaseModel):
    __tablename__ = "reviews"
    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column(String(64))
    description: Mapped[Optional[str]] = mapped_column(Text)
    rating: Mapped[ReviewRate]
    created_at: Mapped[datetime] = mapped_column(DateTime, default=func.now())
    modified_at: Mapped[datetime] = mapped_column(DateTime, default=func.now(), onupdate=func.now())
    customer_id: Mapped[int] = mapped_column(ForeignKey("customers.id"))
    listing_id: Mapped[int] = mapped_column(ForeignKey("listings.id"))

    customer: Mapped["Customer"] = relationship(back_populates="review")
    listing: Mapped["Listing"] = relationship(back_populates="review")

    def __repr__(self) -> str:
        return f"<Review(id={self.id!r}, title={self.title!r}, " \
               f"rating={self.rating!r}, created_at={self.created_at!r}, " \
               f"modified_at={self.modified_at!r}, customer_id={self.customer_id!r}, " \
               f"listing_id={self.listing_id!r})>"


class CartEntry(BaseModel):
    __tablename__ = "cart_entries"
    id: Mapped[int] = mapped_column(primary_key=True)
    amount: Mapped[Decimal] = mapped_column(Numeric(10, 2))
    cart_id: Mapped[int] = mapped_column(ForeignKey("carts.id"))
    listing_id: Mapped[int] = mapped_column(ForeignKey("listings.id"))

    cart: Mapped["Cart"] = relationship(back_populates="cart_entry")
    listing: Mapped["Listing"] = relationship(back_populates="cart_entry")

    def __repr__(self) -> str:
        return f"<CartEntry(id={self.id!r}, amount={self.amount!r}, " \
               f"cart_id={self.cart_id!r}, listing_id={self.listing_id!r})>"


class Cart(BaseModel):
    __tablename__ = "carts"
    id: Mapped[int] = mapped_column(primary_key=True)
    customer_id: Mapped[int] = mapped_column(ForeignKey("customers.id"))

    customer: Mapped["Customer"] = relationship(back_populates="cart")
    cart_entry: Mapped[List["CartEntry"]] = relationship(back_populates="cart")

    def __repr__(self) -> str:
        return f"<Cart(id={self.id!r}, customer_id={self.customer_id!r})>"


class WishListEntry(BaseModel):
    __tablename__ = "wishlist_entries"
    id: Mapped[int] = mapped_column(primary_key=True)
    product_id: Mapped[int] = mapped_column(ForeignKey("products.id"))
    wishlist_id: Mapped[int] = mapped_column(ForeignKey("wishlists.id"))

    product: Mapped["Product"] = relationship(back_populates="wishlist_entry")
    wishlist: Mapped["WishList"] = relationship(back_populates="wishlist_entries")

    def __repr__(self) -> str:
        return f"WishListEntry(id={self.id!r}, product_id={self.product_id}, " \
               f"wishlist_id={self.wishlist_id!r})>"


class WishList(BaseModel):
    __tablename__ = "wishlists"
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(32))
    costumer_id: Mapped[int] = mapped_column(ForeignKey("customers.id"))

    customer: Mapped["Customer"] = relationship(back_populates="wishlist")
    wishlist_entries: Mapped[List["WishListEntry"]] = relationship(back_populates="wishlist")

    def __repr__(self) -> str:
        return f"<WishList(id={self.id!r}, name={self.name!r}, " \
               f"customer_id={self.customer_id!r})>"


class OrderEntry(BaseModel):
    __tablename__ = "order_entries"
    id: Mapped[int] = mapped_column(primary_key=True)
    order_id: Mapped[int] = mapped_column(ForeignKey("orders.id"))
    listing_id: Mapped[int] = mapped_column(ForeignKey("listings.id"))

    order: Mapped["Order"] = relationship(back_populates="order_entries")
    listing: Mapped["Listing"] = relationship(back_populates="order_entries")

    def __repr__(self) -> str:
        return f"<OrderEntry(id={self.id!r}, order_id={self.order_id!r}, " \
               f"listing_id={self.listing_id!r})>"


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

    def __repr__(self) -> str:
        return f"<Order(id={self.id!r}, price={self.price!r}, " \
               f"order_status={self.order_status!r}, purchased_at={self.purchased_at!r}, a" \
               f"address={self.address_street}, city={self.address_city}, " \
               f"state={self.address_state}, country={self.address_country}," \
               f"postal_code={self.address_postal_code})>"


class DeleteRequest(BaseModel):
    __tablename__ = "delete_requests"
    id: Mapped[int] = mapped_column(primary_key=True)
    reason: Mapped[str] = mapped_column(Text)
    requested_at: Mapped[datetime] = mapped_column(DateTime, default=func.now())
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))

    user: Mapped["User"] = relationship(back_populates="delete_request")

    def __repr__(self) -> str:
        return f"<DeleteRequest(id={self.id}, reason='{self.reason}', " \
               f"requested_at={self.requested_at}, user_id={self.user_id})>"


class WordOccurrence(BaseModel):
    __tablename__ = "word_occurrences"
    id: Mapped[int] = mapped_column(primary_key=True)
    word_id: Mapped[int] = mapped_column(ForeignKey("words.id"))
    word: Mapped["Word"] = relationship(back_populates="word_occ")
    products: Mapped[List["Product"]] = relationship(secondary=ProductWordOccurrence, back_populates="words")

    def __repr__(self) -> str:
        return f"<Word(id={self.id!r}, word_id={self.word_id!r})>"


class Word(BaseModel):
    __tablename__ = "words"
    id: Mapped[int] = mapped_column(primary_key=True)
    word: Mapped[str] = mapped_column(String(32))

    word_occ: Mapped[List["WordOccurrence"]] = relationship(back_populates="word")

    def __repr__(self) -> str:
        return f"<Word(id={self.id!r}, word={self.word!r})>"
