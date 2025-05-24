from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List
import uvicorn

app = FastAPI(title="Demo API", version="1.0.0")

class Item(BaseModel):
    id: int
    name: str
    price: float
    is_available: bool = True

# IMPORTANT: Start with empty list for each app restart
items_db: List[Item] = []

@app.get("/")
def read_root():
    return {"message": "Hello World", "version": "1.0.0"}

@app.get("/items", response_model=List[Item])
def get_items():
    return items_db

@app.post("/items", response_model=Item)
def create_item(item: Item):
    # Check if item with same ID already exists
    for existing_item in items_db:
        if existing_item.id == item.id:
            raise HTTPException(status_code=400, detail=f"Item with ID {item.id} already exists")
    
    items_db.append(item)
    return item

@app.get("/items/{item_id}", response_model=Item)
def get_item(item_id: int):
    for item in items_db:
        if item.id == item_id:
            return item
    # This HTTPException is OUTSIDE the response_model validation
    raise HTTPException(status_code=404, detail="Item not found")

@app.get("/health")
def health_check():
    return {"status": "healthy", "items_count": len(items_db)}

# Reset endpoint for testing
@app.post("/reset")
def reset_items():
    global items_db
    items_db = []
    return {"message": "Items reset", "count": 0}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)
