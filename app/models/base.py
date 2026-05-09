"""
BaxtiyorAiTest - Base Model
Common base class for all database models with shared functionality
"""

from datetime import datetime
from sqlalchemy import Column, Integer, DateTime
from sqlalchemy.ext.declarative import declared_attr
from app.extensions import db


class BaseModel(db.Model):
    """Base model with common fields and methods for all models"""
    
    __abstract__ = True  # This is a base class, not a real table
    
    @declared_attr
    def __tablename__(cls):
        """Automatically generate table name from class name"""
        return cls.__name__.lower()
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, 
                       onupdate=datetime.utcnow, nullable=False)
    
    def save(self):
        """Save the current object to database"""
        db.session.add(self)
        db.session.commit()
        return self
    
    def delete(self):
        """Delete the current object from database"""
        db.session.delete(self)
        db.session.commit()
    
    def to_dict(self):
        """Convert model instance to dictionary"""
        result = {}
        for column in self.__table__.columns:
            value = getattr(self, column.name)
            if isinstance(value, datetime):
                value = value.isoformat()
            result[column.name] = value
        return result
    
    def __repr__(self):
        return f'<{self.__class__.__name__} {self.id}>'