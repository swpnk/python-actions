import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_read_root():
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"message": "Hello World", "version": "1.0.0"}


def test_health_check():
    response = client.get("/health")
    assert response.status_code == 200
    assert "status" in response.json()
    assert response.json()["status"] == "healthy"


def test_get_empty_items():
    """Test getting items when database is empty"""
    # Reset first to ensure clean state
    client.post("/reset")

    response = client.get("/items")
    assert response.status_code == 200
    assert response.json() == []


def test_create_and_get_item():
    """Test the full flow: create item, then get it"""
    # Reset first to ensure clean state
    client.post("/reset")

    # Create item
    item_data = {"id": 1, "name": "Test Item", "price": 29.99, "is_available": True}

    # POST the item
    create_response = client.post("/items", json=item_data)
    assert create_response.status_code == 200
    assert create_response.json() == item_data

    # GET the item back
    get_response = client.get("/items/1")
    assert get_response.status_code == 200
    assert get_response.json() == item_data

    # GET all items
    all_items_response = client.get("/items")
    assert all_items_response.status_code == 200
    assert len(all_items_response.json()) == 1
    assert all_items_response.json()[0] == item_data


def test_get_nonexistent_item():
    """Test getting an item that doesn't exist"""
    # Reset first to ensure clean state
    client.post("/reset")

    response = client.get("/items/999")
    assert response.status_code == 404
    assert "detail" in response.json()
    assert response.json()["detail"] == "Item not found"


def test_create_duplicate_item():
    """Test creating item with duplicate ID"""
    # Reset first to ensure clean state
    client.post("/reset")

    item_data = {"id": 1, "name": "Test Item", "price": 29.99, "is_available": True}

    # Create first item
    response1 = client.post("/items", json=item_data)
    assert response1.status_code == 200

    # Try to create duplicate
    response2 = client.post("/items", json=item_data)
    assert response2.status_code == 400
    assert "already exists" in response2.json()["detail"]


def test_create_multiple_items():
    """Test creating multiple items"""
    # Reset first to ensure clean state
    client.post("/reset")

    items = [
        {"id": 1, "name": "Item 1", "price": 10.0, "is_available": True},
        {"id": 2, "name": "Item 2", "price": 20.0, "is_available": False},
        {"id": 3, "name": "Item 3", "price": 30.0, "is_available": True},
    ]

    # Create all items
    for item in items:
        response = client.post("/items", json=item)
        assert response.status_code == 200

    # Get all items
    response = client.get("/items")
    assert response.status_code == 200
    assert len(response.json()) == 3

    # Test getting each item individually
    for item in items:
        response = client.get(f"/items/{item['id']}")
        assert response.status_code == 200
        assert response.json() == item
