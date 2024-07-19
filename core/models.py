from datetime import datetime
from decimal import Decimal
from typing import Optional, List
from sqlalchemy import ForeignKey, Table, Column, Integer, func, String, Date, DateTime, Numeric, Text, Enum
from sqlalchemy.orm import Mapped, mapped_column, relationship
from .base_models import BaseModel
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
    
class TokenBlocklist(BaseModel):
    id: Mapped[int] = mapped_column(primary_key=True)
    jti: Mapped[str] = mapped_column(String(36), index=True)
    created_at: Mapped[DateTime] = mapped_column(DateTime)
    
class User(BaseModel):
    __tablename__ = 'users'
    
    id: Mapped[int] = mapped_column(primary_key=True)
    email: Mapped[str] = mapped_column(String(64), unique=True)
    name: Mapped[str] = mapped_column(String(32))
    surname: Mapped[str] = mapped_column(String(32))
    password: Mapped[Optional[str]] = mapped_column(String(64))
    birth_date: Mapped[datetime] = mapped_column(Date)
    phone_number: Mapped[Optional[str]] = mapped_column(String(32))
    user_type: Mapped[UserType] = mapped_column(Enum(UserType))
    created_at: Mapped[datetime] = mapped_column(DateTime, default=func.now())
    modified_at: Mapped[datetime] = mapped_column(DateTime, default=func.now(), onupdate=func.now())

    delete_request: Mapped[Optional['DeleteRequest']] = relationship(back_populates="user")

    __mapper_args__ = {
        'polymorphic_identity': "user",
        'polymorphic_on': user_type
    }
    
    def to_dict(self):
        return {
            'id': self.id,
            'email': self.email,
            'name': self.name,
            'surname': self.surname,
            'birth_date': self.birth_date.isoformat() if self.birth_date else None,
            'phone_number': self.phone_number,
            'user_type': self.user_type.value,
            'created_at': self.created_at.isoformat(),
            'modified_at': self.modified_at.isoformat(),
        }

class Admin(User):
    __tablename__ = "admins"
    id: Mapped[int] = mapped_column(ForeignKey("users.id"), primary_key=True)
    
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
    
    def to_dict(self):
        seller_dict = super().to_dict()
        seller_dict.update({
            'company_name': self.company_name,
            'rating': float(self.rating) if self.rating is not None else None
        })
        return seller_dict
    
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

class ProductCategory(BaseModel):
    __tablename__ = "product_categories"
    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column(String(32))

    product: Mapped[List["Product"]] = relationship(back_populates="category")

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
    modified_at: Mapped[datetime] = mapped_column(DateTime, default=func.now(), onupdate=func.now())
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
    cart_entry: Mapped[List["CartEntry"]] = relationship(back_populates="cart")

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
    wishlist_entries: Mapped[List["WishListEntry"]] = relationship(back_populates="wishlist")
    
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
    products: Mapped[List["Product"]] = relationship(secondary=ProductWordOccurrence, back_populates="words")

class Word(BaseModel):
    __tablename__ = "words"
    id: Mapped[int] = mapped_column(primary_key=True)
    word: Mapped[str] = mapped_column(String(32))

    word_occ: Mapped[List["WordOccurrence"]] = relationship(back_populates="word")