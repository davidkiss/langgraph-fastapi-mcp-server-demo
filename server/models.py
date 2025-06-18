from datetime import datetime, timezone
from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

Base = declarative_base()

class ShoppingList(Base):
    __tablename__ = "shopping_lists"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False, index=True)
    description = Column(Text, nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))
    
    # Relationship to items
    items = relationship("ShoppingItem", back_populates="shopping_list", cascade="all, delete-orphan")

class ShoppingItem(Base):
    __tablename__ = "shopping_items"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    quantity = Column(Integer, default=1)
    unit = Column(String(50), nullable=True)  # e.g., "kg", "pieces", "bottles"
    notes = Column(Text, nullable=True)
    is_completed = Column(Boolean, default=False)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))
    
    # Foreign key to shopping list
    shopping_list_id = Column(Integer, ForeignKey("shopping_lists.id"), nullable=False)
    shopping_list = relationship("ShoppingList", back_populates="items") 