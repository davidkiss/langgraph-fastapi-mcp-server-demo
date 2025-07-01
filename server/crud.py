from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional
from .models import ShoppingList, ShoppingItem
from .schemas import ShoppingListCreate, ShoppingListUpdate, ShoppingItemCreate, ShoppingItemUpdate

# Shopping List CRUD operations
async def create_shopping_list(db: AsyncSession, shopping_list: ShoppingListCreate) -> ShoppingList:
    db_shopping_list = ShoppingList(**shopping_list.model_dump())
    db.add(db_shopping_list)
    await db.commit()
    await db.refresh(db_shopping_list)
    return db_shopping_list

async def get_shopping_list(db: AsyncSession, shopping_list_id: int) -> Optional[ShoppingList]:
    result = await db.execute(
        select(ShoppingList).where(ShoppingList.id == shopping_list_id)
    )
    return result.scalars().first()

async def get_shopping_lists(db: AsyncSession, skip: int = 0, limit: int = 100) -> List[ShoppingList]:
    result = await db.execute(select(ShoppingList).offset(skip).limit(limit))
    return result.scalars().all()

async def update_shopping_list(db: AsyncSession, shopping_list_id: int, shopping_list: ShoppingListUpdate) -> Optional[ShoppingList]:
    result = await db.execute(select(ShoppingList).filter(ShoppingList.id == shopping_list_id))
    db_shopping_list = result.scalars().first()
    if db_shopping_list:
        update_data = shopping_list.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            setattr(db_shopping_list, key, value)
        await db.commit()
        await db.refresh(db_shopping_list)
        return db_shopping_list
    return None

async def delete_shopping_list(db: AsyncSession, shopping_list_id: int) -> bool:
    result = await db.execute(select(ShoppingList).filter(ShoppingList.id == shopping_list_id))
    db_shopping_list = result.scalars().first()
    if db_shopping_list:
        await db.delete(db_shopping_list)
        await db.commit()
        return True
    return False

# Shopping Item CRUD operations
async def create_shopping_item(db: AsyncSession, shopping_item: ShoppingItemCreate) -> ShoppingItem:
    db_shopping_item = ShoppingItem(**shopping_item.model_dump())
    db.add(db_shopping_item)
    await db.commit()
    await db.refresh(db_shopping_item)
    return db_shopping_item

async def get_shopping_item(db: AsyncSession, item_id: int) -> Optional[ShoppingItem]:
    result = await db.execute(select(ShoppingItem).filter(ShoppingItem.id == item_id))
    return result.scalars().first()

async def get_shopping_items(db: AsyncSession, shopping_list_id: Optional[int] = None, skip: int = 0, limit: int = 100) -> List[ShoppingItem]:
    query = select(ShoppingItem).offset(skip).limit(limit)
    if shopping_list_id:
        query = query.filter(ShoppingItem.shopping_list_id == shopping_list_id)
    result = await db.execute(query)
    return result.scalars().all()

async def update_shopping_item(db: AsyncSession, item_id: int, shopping_item: ShoppingItemUpdate) -> Optional[ShoppingItem]:
    result = await db.execute(select(ShoppingItem).filter(ShoppingItem.id == item_id))
    db_shopping_item = result.scalars().first()
    if db_shopping_item:
        update_data = shopping_item.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(db_shopping_item, field, value)
        await db.commit()
        await db.refresh(db_shopping_item)
        return db_shopping_item
    return None

async def delete_shopping_item(db: AsyncSession, item_id: int) -> bool:
    result = await db.execute(select(ShoppingItem).filter(ShoppingItem.id == item_id))
    db_shopping_item = result.scalars().first()
    if db_shopping_item:
        await db.delete(db_shopping_item)
        await db.commit()
        return True
    return False

async def toggle_item_completion(db: AsyncSession, item_id: int) -> Optional[ShoppingItem]:
    result = await db.execute(select(ShoppingItem).filter(ShoppingItem.id == item_id))
    db_shopping_item = result.scalars().first()
    if db_shopping_item:
        db_shopping_item.is_completed = not db_shopping_item.is_completed
        await db.commit()
        await db.refresh(db_shopping_item)
        return db_shopping_item
    return None 