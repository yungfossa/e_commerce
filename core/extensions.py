from decimal import Decimal
from typing import Annotated
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_bcrypt import Bcrypt
from sqlalchemy import String, Numeric, Date, DateTime, Text
from sqlalchemy.orm import DeclarativeBase, registry

str_32 = Annotated[str, "str_32"]
str_64 = Annotated[str, "str_64"]
str_128 = Annotated[str, "str_128"]
text = Annotated[str, "text"]
num_10_2 = Annotated[Decimal, "num_10_2"]
num_4_2 = Annotated[Decimal, "num_4_2"]
date_t = Annotated[Date, "date"]
datetime_t = Annotated[DateTime, "datetime"]


class Base(DeclarativeBase):
    registry = registry(
        type_annotation_map={
            str_32: String(32),
            str_64: String(64),
            str_128: String(128),
            text: Text,
            num_4_2: Numeric(4, 2),
            num_10_2: Numeric(10, 2),
            date_t: Date,
            datetime_t: DateTime
        }
    )


db = SQLAlchemy(model_class=Base)

bcrypt = Bcrypt()


# bcrypt functions wrappers
def generate_hash(password):
    return bcrypt.generate_password_hash(password, 10).decode('utf-8')


def check_hash(pw_hash, password) -> bool:
    return bcrypt.check_password_hash(pw_hash, password)


login_manager = LoginManager()
