from .extensions import (
    db,
    str_64,
    str_32,
    str_128,
    num_10_2,
    num_4_2,
    text,
    datetime_t,
    date_t,
    generate_hash
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
    Table,
    Column,
    Integer,
    func
)

from flask_login import UserMixin

import enum


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


class Admin(db.Model):
    __tablename__ = "admins"
    id: Mapped[int] = mapped_column(primary_key=True)
    nickname: Mapped[str_32]
    password_hash: Mapped[str_64]

    def __init__(self, nickname, password):
        self.nickname = nickname
        self.password_hash = generate_hash(password)

    def __repr__(self) -> str:
        return f"Admin(id={self.id!r}, nickname={self.nickname!r})"


class User(UserMixin, db.Model):
    __tablename__ = "users"
    id: Mapped[int] = mapped_column(primary_key=True)
    email: Mapped[str_64] = mapped_column(unique=True)
    name: Mapped[str_32]
    surname: Mapped[str_32]
    password_hash: Mapped[str_64]
    birth_date: Mapped[Optional[date_t]]
    phone_number: Mapped[Optional[str_32]]
    user_type: Mapped[str_32]
    created_at: Mapped[datetime_t] = mapped_column(default=func.now())
    modified_at: Mapped[datetime_t] = mapped_column(default=func.now(), onupdate=func.now())

    delete_request: Mapped[Optional["DeleteRequest"]] = relationship(back_populates="user")

    __mapper_args__ = {
        'polymorphic_identity': "user",
        'polymorphic_on': "user_type"
    }

    def __init__(self, email, name, surname, password, birth_date, phone_number, user_type):
        self.email = email
        self.name = name
        self.surname = surname
        self.password_hash = generate_hash(password)
        self.birth_date = birth_date
        self.phone_number = phone_number
        self.user_type = user_type

    def __repr__(self) -> str:
        return f"<User(id={self.id!r}, email={self.email!r}, " \
               f"user_type={self.user_type!r}, created_at={self.created_at!r}, " \
               f"modified_at={self.modified_at!r})>"


class Customer(User):
    __tablename__ = "customers"
    id: Mapped[int] = mapped_column(ForeignKey("users.id"), primary_key=True)
    address_id: Mapped[int] = mapped_column(ForeignKey("customer_addresses.id"))

    address: Mapped["CustomerAddress"] = relationship(back_populates="customer")
    wishlist: Mapped[List["WishList"]] = relationship(back_populates="customer")
    cart: Mapped["Cart"] = relationship(back_populates="customer")
    review: Mapped[List["Review"]] = relationship(back_populates="customer")

    __table_args__ = (UniqueConstraint("address_id"),)

    __mapper_args__ = {
        'polymorphic_identity': "customer",
    }

    def __init__(self, **kwargs):
        super(Customer, self).__init__(**kwargs)


class Seller(User):
    __tablename__ = "sellers"
    id: Mapped[int] = mapped_column(ForeignKey("users.id"), primary_key=True)
    company_name: Mapped[str_32]
    rating: Mapped[Optional[num_4_2]]

    listing: Mapped[List["Listing"]] = relationship(back_populates="seller")

    __mapper_args__ = {
        'polymorphic_identity': "seller",
    }

    def __init__(self, company_name, **kwargs):
        super(Seller, self).__init__(**kwargs)
        self.company_name = company_name

    def __repr__(self) -> str:
        return f"<Seller(id={self.id!r}, email={self.email!r}, " \
               f"company_name={self.company_name!r}, user_type={self.user_type!r}," \
               f"created_at={self.created_at!r}, modified_at={self.modified_at!r})>"


class CustomerAddress(db.Model):
    __tablename__ = "customer_addresses"
    id: Mapped[int] = mapped_column(primary_key=True)
    street: Mapped[str_128]
    city: Mapped[str_64]
    state: Mapped[str_64]
    country: Mapped[str_64]
    postal_code: Mapped[str_32]

    customer: Mapped["Customer"] = relationship(back_populates="address")

    def __repr__(self):
        return f"<CustomerAddress(id={self.id}, customer_id={self.customer_id}, " \
               f"street='{self.street}', city='{self.city}', " \
               f"state='{self.state}, country='{self.country}', " \
               f"postal_code='{self.postal_code}')>"


class ProductCategory(db.Model):
    __tablename__ = "product_categories"
    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str_32]

    word_occ: Mapped[List["WordOccurrence"]] = relationship(back_populates="category")

    def __repr__(self) -> str:
        return f"<ProductCategory(id={self.id!r}, title={self.title!r})>"


ProductWordOccurrence = Table(
    "product_word_occurrences",
    db.Model.metadata,
    Column("product_id", Integer, ForeignKey("products.id"), primary_key=True),
    Column("word_occurrence_id", Integer, ForeignKey("word_occurrences.id"), primary_key=True)
)


class Product(db.Model):
    __tablename__ = "products"
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str_32]
    description: Mapped[text]
    image_src: Mapped[text]
    category_id: Mapped[int] = mapped_column(ForeignKey("product_categories.id"))

    category: Mapped["ProductCategory"] = relationship(back_populates="product")
    wishlist_entry: Mapped[List["WishListEntry"]] = relationship(back_populates="product")
    listing: Mapped[List["Listing"]] = relationship(back_populates="product")
    words: Mapped[List["WordOccurrence"]] = relationship(secondary=ProductWordOccurrence, back_populates="products")

    def __repr__(self) -> str:
        return f"<Product(id={self.id!r}, name={self.name!r}, " \
               f"image_src={self.image_src}, category={self.category_id!r})>"


class Listing(db.Model):
    __tablename__ = "listings"
    id: Mapped[int] = mapped_column(primary_key=True)
    quantity: Mapped[int]
    available: Mapped[bool]
    price: Mapped[num_10_2]
    product_state: Mapped[ProductState]
    seller_id: Mapped[int] = mapped_column(ForeignKey("sellers.id"))
    product_id: Mapped[int] = mapped_column(ForeignKey("products.id"))

    seller: Mapped["Seller"] = relationship(back_populates="listing")
    product: Mapped["Product"] = relationship(back_populates="listing")
    cart_entry: Mapped[List["CartEntry"]] = relationship(back_populates="listing")
    review: Mapped[List["Review"]] = relationship(back_populates="listing")
    order_entries: Mapped[List["OrderEntry"]] = relationship(back_populates="listing")

    def __repr__(self) -> str:
        return f"<Listing(id={self.id!r}, quantity={self.quantity!r}, " \
               f"available={self.available}, price={self.price!r}, " \
               f"product_state={self.product_state!r}, seller_id={self.seller_id!r}" \
               f"product_id={self.product_id!r})>"


class Review(db.Model):
    __tablename__ = "reviews"
    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str_64]
    description: Mapped[Optional[text]]
    rating: Mapped[ReviewRate]
    created_at: Mapped[datetime_t] = mapped_column(default=func.now())
    modified_at: Mapped[datetime_t] = mapped_column(default=func.now(), onupdate=func.now())
    customer_id: Mapped[int] = mapped_column(ForeignKey("customers.id"))
    listing_id: Mapped[int] = mapped_column(ForeignKey("listings.id"))

    customer: Mapped["Customer"] = relationship(back_populates="review")
    listing: Mapped["Listing"] = relationship(back_populates="review")

    def __repr__(self) -> str:
        return f"<Review(id={self.id!r}, title={self.title!r}, " \
               f"rating={self.rating!r}, created_at={self.created_at!r}, " \
               f"modified_at={self.modified_at!r}, customer_id={self.customer_id!r}, " \
               f"listing_id={self.listing_id!r})>"


class CartEntry(db.Model):
    __tablename__ = "cart_entries"
    id: Mapped[int] = mapped_column(primary_key=True)
    amount: Mapped[num_10_2]
    cart_id: Mapped[int] = mapped_column(ForeignKey("carts.id"))
    listing_id: Mapped[int] = mapped_column(ForeignKey("listings.id"))

    cart: Mapped["Cart"] = relationship(back_populates="cart_entry")
    listing: Mapped["Listing"] = relationship(back_populates="cart_entry")

    def __repr__(self) -> str:
        return f"<CartEntry(id={self.id!r}, amount={self.amount!r}, " \
               f"cart_id={self.cart_id!r}, listing_id={self.listing_id!r})>"


class Cart(db.Model):
    __tablename__ = "carts"
    id: Mapped[int] = mapped_column(primary_key=True)
    customer_id: Mapped[int] = mapped_column(ForeignKey("customers.id"))

    customer: Mapped["Customer"] = relationship(back_populates="cart")
    cart_entry: Mapped[List["CartEntry"]] = relationship(back_populates="cart")

    __table_args__ = (UniqueConstraint("customer_id"),)

    def __repr__(self) -> str:
        return f"<Cart(id={self.id!r}, customer_id={self.customer_id!r})>"


class WishListEntry(db.Model):
    __tablename__ = "wishlist_entries"
    id: Mapped[int] = mapped_column(primary_key=True)
    product_id: Mapped[int] = mapped_column(ForeignKey("products.id"))
    wishlist_id: Mapped[int] = mapped_column(ForeignKey("wishlists.id"))

    product: Mapped["Product"] = relationship(back_populates="wishlist_entry")
    wishlist: Mapped["WishList"] = relationship(back_populates="wishlist_entries")

    def __repr__(self) -> str:
        return f"WishListEntry(id={self.id!r}, product_id={self.product_id}, " \
               f"wishlist_id={self.wishlist_id!r})>"


class WishList(db.Model):
    __tablename__ = "wishlists"
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str_32]
    costumer_id: Mapped[int] = mapped_column(ForeignKey("customers.id"))

    customer: Mapped["Customer"] = relationship(back_populates="wishlist")
    wishlist_entries: Mapped[List["WishListEntry"]] = relationship(back_populates="wishlist")

    def __repr__(self) -> str:
        return f"<WishList(id={self.id!r}, name={self.name!r}, " \
               f"customer_id={self.customer_id!r})>"


class OrderEntry(db.Model):
    __tablename__ = "order_entries"
    id: Mapped[int] = mapped_column(primary_key=True)
    order_id: Mapped[int] = mapped_column(ForeignKey("orders.id"))
    listing_id: Mapped[int] = mapped_column(ForeignKey("listings.id"))

    order: Mapped["Order"] = relationship(back_populates="order_entries")
    listing: Mapped["Listing"] = relationship(back_populates="order_entries")

    def __repr__(self) -> str:
        return f"<OrderEntry(id={self.id!r}, order_id={self.order_id!r}, " \
               f"listing_id={self.listing_id!r})>"


class Order(db.Model):
    __tablename__ = "orders"
    id: Mapped[int] = mapped_column(primary_key=True)
    price: Mapped[num_10_2]
    order_status: Mapped[OrderStatus]
    purchased_at: Mapped[Optional[datetime_t]]
    address_street: Mapped[str_128]
    address_city: Mapped[str_64]
    address_state: Mapped[str_64]
    address_country: Mapped[str_64]
    address_postal_code: Mapped[str_32]

    order_entries: Mapped[List["OrderEntry"]] = relationship(back_populates="order")

    def __repr__(self) -> str:
        return f"<Order(id={self.id!r}, price={self.price!r}, " \
               f"order_status={self.order_status!r}, purchased_at={self.purchased_at!r}, a" \
               f"address={self.address_street}, city={self.address_city}, " \
               f"state={self.address_state}, country={self.address_country}," \
               f"postal_code={self.address_postal_code})>"


class DeleteRequest(db.Model):
    __tablename__ = "delete_requests"
    id: Mapped[int] = mapped_column(primary_key=True)
    reason: Mapped[text]
    requested_at: Mapped[datetime_t] = mapped_column(default=func.now())
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))

    user: Mapped["User"] = relationship(back_populates="delete_request")

    __table_args__ = (UniqueConstraint("user_id"),)

    def __repr__(self) -> str:
        return f"<DeleteRequest(id={self.id}, reason='{self.reason}', " \
               f"requested_at={self.requested_at}, user_id={self.user_id})>"

    # todo ADD CHECK CONSTRAINT (if now - requested_at > 30 -> delete). This check must be executed once a day


class WordOccurrence(db.Model):
    __tablename__ = "word_occurrences"
    id: Mapped[int] = mapped_column(primary_key=True)
    word_id: Mapped[int] = mapped_column(ForeignKey("words.id"))

    word: Mapped["Word"] = relationship(back_populates="word_occ")
    products: Mapped[List["Product"]] = relationship(secondary=ProductWordOccurrence, back_populates="words")

    def __repr__(self) -> str:
        return f"<Word(id={self.id!r}, word_id={self.word_id!r})>"


class Word(db.Model):
    __tablename__ = "words"
    id: Mapped[int] = mapped_column(primary_key=True)
    word: Mapped[str_32]

    word_occ: Mapped[List["WordOccurrence"]] = relationship(back_populates="word")

    def __repr__(self) -> str:
        return f"<Word(id={self.id!r}, word={self.word!r})>"
