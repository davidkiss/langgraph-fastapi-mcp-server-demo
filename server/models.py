from datetime import datetime
from typing import Optional
from sqlalchemy import Integer, String, Boolean, DateTime, ForeignKey, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship, Mapped, mapped_column

Base = declarative_base()

class ShoppingList(Base):
    __tablename__ = "shopping_lists"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String(255), index=True)
    description: Mapped[Optional[str]] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=func.now(), onupdate=func.now())
    
    # Relationship to items
    items: Mapped[list["ShoppingItem"]] = relationship("ShoppingItem", back_populates="shopping_list", cascade="all, delete-orphan", lazy="selectin")

class ShoppingItem(Base):
    __tablename__ = "shopping_items"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String(255))
    quantity: Mapped[int] = mapped_column(Integer, default=1)
    unit: Mapped[Optional[str]] = mapped_column(String(50))  # e.g., "kg", "pieces", "bottles"
    notes: Mapped[Optional[str]] = mapped_column(Text)
    is_completed: Mapped[bool] = mapped_column(Boolean, default=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=func.now(), onupdate=func.now())
    
    # Foreign key to shopping list
    shopping_list_id: Mapped[int] = mapped_column(Integer, ForeignKey("shopping_lists.id"))
    shopping_list: Mapped[ShoppingList] = relationship("ShoppingList", back_populates="items") 