from typing import Optional, List
from datetime import datetime
from pydantic import BaseModel, Field

# Shopping List Schemas
class ShoppingListBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=255, description="Name of the shopping list")
    description: Optional[str] = Field(None, description="Optional description of the shopping list")

class ShoppingListCreate(ShoppingListBase):
    pass

class ShoppingListUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = None

class ShoppingListResponse(ShoppingListBase):
    id: int
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True

# Shopping Item Schemas
class ShoppingItemBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=255, description="Name of the item")
    quantity: int = Field(1, ge=1, description="Quantity of the item")
    unit: Optional[str] = Field(None, max_length=50, description="Unit of measurement (e.g., kg, pieces)")
    notes: Optional[str] = Field(None, description="Additional notes about the item")
    is_completed: bool = Field(False, description="Whether the item has been purchased")

class ShoppingItemCreate(ShoppingItemBase):
    shopping_list_id: int = Field(..., description="ID of the shopping list this item belongs to")

class ShoppingItemUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    quantity: Optional[int] = Field(None, ge=1)
    unit: Optional[str] = Field(None, max_length=50)
    notes: Optional[str] = None
    is_completed: Optional[bool] = None

class ShoppingItemResponse(ShoppingItemBase):
    id: int
    shopping_list_id: int
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True

# Combined Response Schemas
class ShoppingListWithItems(ShoppingListResponse):
    items: List[ShoppingItemResponse] = []
    
    class Config:
        from_attributes = True 