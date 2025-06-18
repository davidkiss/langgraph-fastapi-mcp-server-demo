from typing import List
from fastapi import FastAPI, Depends, HTTPException
from fastapi_mcp import FastApiMCP
from sqlalchemy.orm import Session

from .database import get_db, engine
from .models import Base
from .schemas import (
    ShoppingListCreate, ShoppingListResponse, ShoppingListUpdate, ShoppingListWithItems,
    ShoppingItemCreate, ShoppingItemResponse, ShoppingItemUpdate
)
from .crud import (
    create_shopping_list, get_shopping_list, get_shopping_lists, update_shopping_list, delete_shopping_list,
    create_shopping_item, get_shopping_item, get_shopping_items, update_shopping_item, delete_shopping_item, toggle_item_completion
)

Base.metadata.create_all(bind=engine)

app = FastAPI(description="REST api for managing shopping lists.")
# Turn FastAPI app into an MCP server:

@app.post("/shopping-lists/", response_model=ShoppingListResponse, operation_id="create_shopping_list", summary="Create a new shopping list")
def create_list(shopping_list: ShoppingListCreate, db: Session = Depends(get_db)):
    """Create a new shopping list with the given name and description."""
    return create_shopping_list(db=db, shopping_list=shopping_list)

@app.get("/shopping-lists/", response_model=List[ShoppingListResponse], operation_id="get_shopping_lists", summary="Get all shopping lists")
def read_lists(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """Retrieve all shopping lists with optional pagination."""
    shopping_lists = get_shopping_lists(db, skip=skip, limit=limit)
    return shopping_lists

@app.get("/shopping-lists/{shopping_list_id}", response_model=ShoppingListWithItems, operation_id="get_shopping_list", summary="Get a specific shopping list with items")
def read_list(shopping_list_id: int, db: Session = Depends(get_db)):
    """Retrieve a specific shopping list by ID along with all its items."""
    db_shopping_list = get_shopping_list(db, shopping_list_id=shopping_list_id)
    if db_shopping_list is None:
        raise HTTPException(status_code=404, detail="Shopping list not found")
    return db_shopping_list

@app.put("/shopping-lists/{shopping_list_id}", response_model=ShoppingListResponse, operation_id="update_shopping_list", summary="Update a shopping list")
def update_list(shopping_list_id: int, shopping_list: ShoppingListUpdate, db: Session = Depends(get_db)):
    """Update an existing shopping list's name and/or description."""
    db_shopping_list = update_shopping_list(db, shopping_list_id=shopping_list_id, shopping_list=shopping_list)
    if db_shopping_list is None:
        raise HTTPException(status_code=404, detail="Shopping list not found")
    return db_shopping_list

@app.delete("/shopping-lists/{shopping_list_id}", operation_id="delete_shopping_list", summary="Delete a shopping list")
def delete_list(shopping_list_id: int, db: Session = Depends(get_db)):
    """Delete a shopping list and all its items."""
    success = delete_shopping_list(db, shopping_list_id=shopping_list_id)
    if not success:
        raise HTTPException(status_code=404, detail="Shopping list not found")
    return {"message": "Shopping list deleted successfully"}

@app.post("/shopping-items/", response_model=ShoppingItemResponse, operation_id="create_shopping_item", summary="Add an item to a shopping list")
def create_item(shopping_item: ShoppingItemCreate, db: Session = Depends(get_db)):
    """Add a new item to a shopping list."""
    shopping_list = get_shopping_list(db, shopping_item.shopping_list_id)
    if not shopping_list:
        raise HTTPException(status_code=404, detail="Shopping list not found")
    return create_shopping_item(db=db, shopping_item=shopping_item)

@app.get("/shopping-items/", response_model=List[ShoppingItemResponse], operation_id="get_shopping_items", summary="Get all shopping items")
def read_items(skip: int = 0, limit: int = 100, shopping_list_id: int = None, db: Session = Depends(get_db)):
    """Retrieve all shopping items with optional filtering by shopping list."""
    items = get_shopping_items(db, shopping_list_id=shopping_list_id, skip=skip, limit=limit)
    return items

@app.get("/shopping-items/{item_id}", response_model=ShoppingItemResponse, operation_id="get_shopping_item", summary="Get a specific shopping item")
def read_item(item_id: int, db: Session = Depends(get_db)):
    """Retrieve a specific shopping item by ID."""
    db_item = get_shopping_item(db, item_id=item_id)
    if db_item is None:
        raise HTTPException(status_code=404, detail="Shopping item not found")
    return db_item

@app.put("/shopping-items/{item_id}", response_model=ShoppingItemResponse, operation_id="update_shopping_item", summary="Update a shopping item")
def update_item(item_id: int, shopping_item: ShoppingItemUpdate, db: Session = Depends(get_db)):
    """Update an existing shopping item's details."""
    db_item = update_shopping_item(db, item_id=item_id, shopping_item=shopping_item)
    if db_item is None:
        raise HTTPException(status_code=404, detail="Shopping item not found")
    return db_item

@app.delete("/shopping-items/{item_id}", operation_id="delete_shopping_item", summary="Delete a shopping item")
def delete_item(item_id: int, db: Session = Depends(get_db)):
    """Delete a shopping item from its list."""
    success = delete_shopping_item(db, item_id=item_id)
    if not success:
        raise HTTPException(status_code=404, detail="Shopping item not found")
    return {"message": "Shopping item deleted successfully"}

@app.patch("/shopping-items/{item_id}/toggle", response_model=ShoppingItemResponse, operation_id="toggle_item_completion", summary="Toggle item completion status")
def toggle_completion(item_id: int, db: Session = Depends(get_db)):
    """Toggle the completion status of a shopping item (mark as completed/uncompleted)."""
    db_item = toggle_item_completion(db, item_id=item_id)
    if db_item is None:
        raise HTTPException(status_code=404, detail="Shopping item not found")
    return db_item 

mcp = FastApiMCP(app)
mcp.mount()
mcp.setup_server()