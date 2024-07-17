from .extensions import db


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
    
    def to_dict(self):
        """Convert model instance to a dictionary"""
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}