import pytest
from httpx import AsyncClient
from app.main import app
from app.core.database import init_db, get_db

@pytest.fixture
async def client():
    await init_db()
    async with AsyncClient(app=app, base_url="http://test") as ac:
        yield ac

@pytest.mark.asyncio
async def test_register_user(client):
    response = await client.post("/api/v1/auth/register", json={
        "email": "test@example.com",
        "username": "testuser",
        "password": "password123"
    })
    
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert "refresh_token" in data
    assert "user" in data
    assert data["user"]["email"] == "test@example.com"
    assert data["user"]["username"] == "testuser"

@pytest.mark.asyncio
async def test_register_duplicate_email(client):
    # Register first user
    await client.post("/api/v1/auth/register", json={
        "email": "test@example.com",
        "username": "testuser1",
        "password": "password123"
    })
    
    # Try to register with same email
    response = await client.post("/api/v1/auth/register", json={
        "email": "test@example.com",
        "username": "testuser2",
        "password": "password123"
    })
    
    assert response.status_code == 400
    assert "Email already registered" in response.json()["detail"]

@pytest.mark.asyncio
async def test_login_user(client):
    # Register user first
    await client.post("/api/v1/auth/register", json={
        "email": "test@example.com",
        "username": "testuser",
        "password": "password123"
    })
    
    # Login
    response = await client.post("/api/v1/auth/login", json={
        "email": "test@example.com",
        "password": "password123"
    })
    
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert "refresh_token" in data
    assert "user" in data

@pytest.mark.asyncio
async def test_login_invalid_credentials(client):
    response = await client.post("/api/v1/auth/login", json={
        "email": "nonexistent@example.com",
        "password": "wrongpassword"
    })
    
    assert response.status_code == 401
    assert "Incorrect email or password" in response.json()["detail"]

@pytest.mark.asyncio
async def test_get_current_user(client):
    # Register and login to get token
    register_response = await client.post("/api/v1/auth/register", json={
        "email": "test@example.com",
        "username": "testuser",
        "password": "password123"
    })
    
    token = register_response.json()["access_token"]
    
    # Get current user
    response = await client.get(
        "/api/v1/auth/me",
        headers={"Authorization": f"Bearer {token}"}
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["email"] == "test@example.com"
    assert data["username"] == "testuser"

@pytest.mark.asyncio
async def test_get_current_user_invalid_token(client):
    response = await client.get(
        "/api/v1/auth/me",
        headers={"Authorization": "Bearer invalid_token"}
    )
    
    assert response.status_code == 401 