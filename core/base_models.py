import enum
from sqlalchemy import inspect
from sqlalchemy.orm import Mapped, mapped_column
from .extensions import db
from datetime import datetime


class CRUDMixin(object):
    """Mixin that adds convenience methods for CRUD (Create, Read, Update, Delete) database operations"""

    @classmethod
    def create(cls, **kwargs):
        """Create a new record and save it the database"""
        record = cls(**kwargs)
        return record.save()

    def update(self, commit=True, **kwargs):
        """Update specific fields of a record."""
        for attr, value in kwargs.items():
            setattr(self, attr, value)
        if commit:
            return self.save()
        return self

    def save(self, commit=True):
        """Save the record"""
        db.session.add(self)
        if commit:
            db.session.commit()
        return self

    def delete(self, commit=True) -> None:
        """Remove the record from the database"""
        db.session.delete(self)
        if commit:
            return db.session.commit()
        return


class BaseModel(CRUDMixin, db.Model):
    """Base model class the includes CRUD convenience methods."""

    __abstract__ = True

    id: Mapped[int] = mapped_column(primary_key=True)

    @classmethod
    def row_to_dict(cls, row, fields=None):
        def serialize_value(value):
            if isinstance(value, datetime):
                return value.isoformat()
            elif isinstance(value, enum.Enum):
                return value.value
            return str(value)

        mapper = inspect(row.__class__)
        columns = mapper.columns.keys()

        result = {}
        for key in columns:
            if fields is None or key in fields:
                value = getattr(row, key)
                result[key] = serialize_value(value)

        return result

    def to_dict(self):
        return self.row_to_dict(self)
