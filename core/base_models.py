from .extensions import db, bcrypt


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


class CRUDAuthModel(CRUDMixin, db.Model):

    def get_id(self):
        return self.id

    def get_password(self):
        return self._password

    def set_password(self, value):
        self._password = bcrypt.generate_password_hash(value, 10).decode('utf-8')

    def check_password(self, value):
        return bcrypt.check_password_hash(self._password, value)

    __abstract__ = True


class BaseModel(CRUDMixin, db.Model):
    """Base model class the includes CRUD convenience methods."""

    __abstract__ = True
