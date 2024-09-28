from sqlalchemy_serializer import SerializerMixin

from .extensions import db


class CRUDMixin(object):
    """
    Mixin that adds convenience methods for CRUD (Create, Read, Update, Delete) operations.

    This mixin is used to provide common database operations to all models,
    reducing code duplication and standardizing data manipulation across the application.
    """

    @classmethod
    def create(cls, **kwargs):
        """
        Create a new record and save it to the database.

        Args:
            **kwargs: Arbitrary keyword arguments corresponding to model fields.

        Returns:
            The newly created and saved record instance.
        """
        record = cls(**kwargs)
        return record.save()

    def update(self, commit=True, **kwargs):
        """
        Update specific fields of a record.

        Args:
            commit (bool): Whether to commit the changes immediately.
            **kwargs: Arbitrary keyword arguments corresponding to model fields to update.

        Returns:
            The updated record instance.
        """
        for attr, value in kwargs.items():
            setattr(self, attr, value)
        if commit:
            return self.save()
        return self

    def save(self, commit=True):
        """
        Save the record to the database.

        Args:
            commit (bool): Whether to commit the changes immediately.

        Returns:
            The saved record instance.
        """
        db.session.add(self)
        if commit:
            db.session.commit()
        return self

    def delete(self, commit=True) -> None:
        """
        Remove the record from the database.

        Args:
            commit (bool): Whether to commit the changes immediately.

        Returns:
            None
        """
        db.session.delete(self)
        if commit:
            return db.session.commit()


class BaseModel(db.Model, CRUDMixin, SerializerMixin):
    """
    Base model class that includes CRUD convenience methods and serialization capabilities.

    This class serves as the base for all other models in the application. By inheriting from
    this class, all models gain:
    1. SQLAlchemy's ORM capabilities (from db.Model)
    2. CRUD operations (from CRUDMixin)
    3. Serialization methods (from SerializerMixin)

    All models defined in models.py should inherit from this BaseModel class to ensure
    consistent behavior and reduce code duplication.
    """

    __abstract__ = True


# This module defines the base classes used for all models in the application.

# Key components:
# 1. CRUDMixin: Provides Create, Read, Update, and Delete operations that can be
#    reused across all models. This significantly reduces code duplication and
#    ensures consistent data manipulation methods throughout the application.

# 2. BaseModel: Combines SQLAlchemy's db.Model, our custom CRUDMixin, and
#    SerializerMixin from sqlalchemy_serializer. This class serves as the
#    foundation for all other models in the application.

# Usage:
# All models defined in models.py should inherit from BaseModel. This ensures that
# every model has access to:
# - SQLAlchemy ORM features
# - CRUD operations (create, update, save, delete)
# - Serialization capabilities

# By inheriting from BaseModel, the User class automatically gains all CRUD
# methods and can be easily serialized to JSON or other formats.

# This approach promotes DRY (Don't Repeat Yourself) principles and helps maintain
# consistency across the application's data layer.
