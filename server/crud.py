from sqlalchemy.orm import Session
from typing import List, Optional
from .models import ShoppingList, ShoppingItem
from .schemas import ShoppingListCreate, ShoppingListUpdate, ShoppingItemCreate, ShoppingItemUpdate

# Shopping List CRUD operations
def create_shopping_list(db: Session, shopping_list: ShoppingListCreate) -> ShoppingList:
    db_shopping_list = ShoppingList(**shopping_list.model_dump())
    db.add(db_shopping_list)
    db.commit()
    db.refresh(db_shopping_list)
    return db_shopping_list

def get_shopping_list(db: Session, shopping_list_id: int) -> Optional[ShoppingList]:
    return db.query(ShoppingList).filter(ShoppingList.id == shopping_list_id).first()

def get_shopping_lists(db: Session, skip: int = 0, limit: int = 100) -> List[ShoppingList]:
    return db.query(ShoppingList).offset(skip).limit(limit).all()

def update_shopping_list(db: Session, shopping_list_id: int, shopping_list: ShoppingListUpdate) -> Optional[ShoppingList]:
    db_shopping_list = get_shopping_list(db, shopping_list_id)
    if db_shopping_list:
        update_data = shopping_list.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(db_shopping_list, field, value)
        db.commit()
        db.refresh(db_shopping_list)
    return db_shopping_list

def delete_shopping_list(db: Session, shopping_list_id: int) -> bool:
    db_shopping_list = get_shopping_list(db, shopping_list_id)
    if db_shopping_list:
        db.delete(db_shopping_list)
        db.commit()
        return True
    return False

# Shopping Item CRUD operations
def create_shopping_item(db: Session, shopping_item: ShoppingItemCreate) -> ShoppingItem:
    db_shopping_item = ShoppingItem(**shopping_item.model_dump())
    db.add(db_shopping_item)
    db.commit()
    db.refresh(db_shopping_item)
    return db_shopping_item

def get_shopping_item(db: Session, item_id: int) -> Optional[ShoppingItem]:
    return db.query(ShoppingItem).filter(ShoppingItem.id == item_id).first()

def get_shopping_items(db: Session, shopping_list_id: Optional[int] = None, skip: int = 0, limit: int = 100) -> List[ShoppingItem]:
    query = db.query(ShoppingItem)
    if shopping_list_id:
        query = query.filter(ShoppingItem.shopping_list_id == shopping_list_id)
    return query.offset(skip).limit(limit).all()

def update_shopping_item(db: Session, item_id: int, shopping_item: ShoppingItemUpdate) -> Optional[ShoppingItem]:
    db_shopping_item = get_shopping_item(db, item_id)
    if db_shopping_item:
        update_data = shopping_item.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(db_shopping_item, field, value)
        db.commit()
        db.refresh(db_shopping_item)
    return db_shopping_item

def delete_shopping_item(db: Session, item_id: int) -> bool:
    db_shopping_item = get_shopping_item(db, item_id)
    if db_shopping_item:
        db.delete(db_shopping_item)
        db.commit()
        return True
    return False

def toggle_item_completion(db: Session, item_id: int) -> Optional[ShoppingItem]:
    db_shopping_item = get_shopping_item(db, item_id)
    if db_shopping_item:
        db_shopping_item.is_completed = not db_shopping_item.is_completed
        db.commit()
        db.refresh(db_shopping_item)
    return db_shopping_item 