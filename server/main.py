from contextlib import asynccontextmanager
from typing import Annotated, List
from fastapi import FastAPI, Depends, HTTPException
from fastapi_mcp import FastApiMCP
from sqlalchemy.ext.asyncio import AsyncSession

from .database import get_db, async_engine
from .models import Base
from .schemas import (
    ShoppingListCreate, ShoppingListResponse, ShoppingListUpdate, ShoppingListWithItems,
    ShoppingItemCreate, ShoppingItemResponse, ShoppingItemUpdate
)
from .crud import (
    create_shopping_list, get_shopping_list, get_shopping_lists, update_shopping_list, delete_shopping_list,
    create_shopping_item, get_shopping_item, get_shopping_items, update_shopping_item, delete_shopping_item, toggle_item_completion
)

@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Function that handles startup and shutdown events.
    """
    yield
    await async_engine.dispose()
        
app = FastAPI(description="REST api for managing shopping lists.", lifespan=lifespan)

db_dependency = Annotated[AsyncSession, Depends(get_db)]

@app.post("/shopping-lists/", response_model=ShoppingListResponse, operation_id="create_shopping_list", summary="Create a new shopping list")
async def create_list(shopping_list: ShoppingListCreate, db: db_dependency):
    """Create a new shopping list with the given name and description."""
    return await create_shopping_list(db=db, shopping_list=shopping_list)

@app.get("/shopping-lists/", response_model=List[ShoppingListResponse], operation_id="get_shopping_lists", summary="Get all shopping lists")
async def read_lists(db: db_dependency,skip: int = 0, limit: int = 100):
    """Retrieve all shopping lists with optional pagination."""
    shopping_lists = await get_shopping_lists(db, skip=skip, limit=limit)
    return shopping_lists

@app.get("/shopping-lists/{shopping_list_id}", response_model=ShoppingListWithItems, operation_id="get_shopping_list", summary="Get a specific shopping list with items")
async def read_list(shopping_list_id: int, db: db_dependency):
    """Retrieve a specific shopping list by ID along with all its items."""
    db_shopping_list = await get_shopping_list(db, shopping_list_id=shopping_list_id)
    if db_shopping_list is None:
        raise HTTPException(status_code=404, detail="Shopping list not found")
    return db_shopping_list

@app.put("/shopping-lists/{shopping_list_id}", response_model=ShoppingListResponse, operation_id="update_shopping_list", summary="Update a shopping list")
async def update_list(shopping_list_id: int, shopping_list: ShoppingListUpdate, db: db_dependency):
    """Update an existing shopping list's name and/or description."""
    db_shopping_list = await update_shopping_list(db, shopping_list_id=shopping_list_id, shopping_list=shopping_list)
    if db_shopping_list is None:
        raise HTTPException(status_code=404, detail="Shopping list not found")
    return db_shopping_list

@app.delete("/shopping-lists/{shopping_list_id}", operation_id="delete_shopping_list", summary="Delete a shopping list")
async def delete_list(shopping_list_id: int, db: db_dependency):
    """Delete a shopping list and all its items."""
    success = await delete_shopping_list(db, shopping_list_id=shopping_list_id)
    if not success:
        raise HTTPException(status_code=404, detail="Shopping list not found")
    return {"message": "Shopping list deleted successfully"}

@app.post("/shopping-items/", response_model=ShoppingItemResponse, operation_id="create_shopping_item", summary="Add an item to a shopping list")
async def create_item(shopping_item: ShoppingItemCreate, db: db_dependency):
    """Add a new item to a shopping list."""
    shopping_list = await get_shopping_list(db, shopping_item.shopping_list_id)
    if not shopping_list:
        raise HTTPException(status_code=404, detail="Shopping list not found")
    return await create_shopping_item(db=db, shopping_item=shopping_item)

@app.get("/shopping-items/", response_model=List[ShoppingItemResponse], operation_id="get_shopping_items", summary="Get all shopping items")
async def read_items(db: db_dependency, skip: int = 0, limit: int = 100, shopping_list_id: int = None):
    """Retrieve all shopping items with optional filtering by shopping list."""
    items = await get_shopping_items(db, shopping_list_id=shopping_list_id, skip=skip, limit=limit)
    return items

@app.get("/shopping-items/{item_id}", response_model=ShoppingItemResponse, operation_id="get_shopping_item", summary="Get a specific shopping item")
async def read_item(item_id: int, db: db_dependency):
    """Retrieve a specific shopping item by ID."""
    db_item = await get_shopping_item(db, item_id=item_id)
    if db_item is None:
        raise HTTPException(status_code=404, detail="Shopping item not found")
    return db_item

@app.put("/shopping-items/{item_id}", response_model=ShoppingItemResponse, operation_id="update_shopping_item", summary="Update a shopping item")
async def update_item(item_id: int, shopping_item: ShoppingItemUpdate, db: db_dependency):
    """Update an existing shopping item's details."""
    db_item = await update_shopping_item(db, item_id=item_id, shopping_item=shopping_item)
    if db_item is None:
        raise HTTPException(status_code=404, detail="Shopping item not found")
    return db_item

@app.delete("/shopping-items/{item_id}", operation_id="delete_shopping_item", summary="Delete a shopping item")
async def delete_item(item_id: int, db: db_dependency):
    """Delete a shopping item from its list."""
    success = await delete_shopping_item(db, item_id=item_id)
    if not success:
        raise HTTPException(status_code=404, detail="Shopping item not found")
    return {"message": "Shopping item deleted successfully"}

@app.patch("/shopping-items/{item_id}/toggle", response_model=ShoppingItemResponse, operation_id="toggle_item_completion", summary="Toggle item completion status")
async def toggle_completion(item_id: int, db: db_dependency):
    """Toggle the completion status of a shopping item (mark as completed/uncompleted)."""
    db_item = await toggle_item_completion(db, item_id=item_id)
    if db_item is None:
        raise HTTPException(status_code=404, detail="Shopping item not found")
    return db_item 

# Turn FastAPI app into an MCP server - must call after route declarations:
mcp = FastApiMCP(app)
mcp.mount()
mcp.setup_server()