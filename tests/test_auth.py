import pytest
from httpx import AsyncClient

@pytest.mark.asyncio
async def test_register(client: AsyncClient):
    response = await client.post(
        "/api/v1/auth/register",
        json={
            "email": "owner@example.com",
            "password": "StrongPassword123",
            "name": "Alice Owner",
            "organization_name": "Acme Inc"
        }
    )
    assert response.status_code == 201
    data = response.json()
    assert "access_token" in data
    assert "refresh_token" in data
    assert data["token_type"] == "bearer"

@pytest.mark.asyncio
async def test_register_duplicate_email(client: AsyncClient):
    # First registration
    await client.post(
        "/api/v1/auth/register",
        json={
            "email": "test@example.com",
            "password": "Password123",
            "name": "Test User",
            "organization_name": "Test Org"
        }
    )
    
    # Duplicate registration
    response = await client.post(
        "/api/v1/auth/register",
        json={
            "email": "test@example.com",
            "password": "Password123",
            "name": "Test User 2",
            "organization_name": "Test Org 2"
        }
    )
    assert response.status_code == 409

@pytest.mark.asyncio
async def test_login(client: AsyncClient):
    # Register first
    await client.post(
        "/api/v1/auth/register",
        json={
            "email": "login@example.com",
            "password": "Password123",
            "name": "Login User",
            "organization_name": "Login Org"
        }
    )
    
    # Login
    response = await client.post(
        "/api/v1/auth/login",
        json={
            "email": "login@example.com",
            "password": "Password123"
        }
    )
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data

@pytest.mark.asyncio
async def test_login_wrong_password(client: AsyncClient):
    # Register
    await client.post(
        "/api/v1/auth/register",
        json={
            "email": "user@example.com",
            "password": "CorrectPassword",
            "name": "User",
            "organization_name": "Org"
        }
    )
    
    # Wrong password
    response = await client.post(
        "/api/v1/auth/login",
        json={
            "email": "user@example.com",
            "password": "WrongPassword"
        }
    )
    assert response.status_code == 401

@pytest.mark.asyncio
async def test_get_me(client: AsyncClient):
    # Register and get token
    reg_response = await client.post(
        "/api/v1/auth/register",
        json={
            "email": "me@example.com",
            "password": "Password123",
            "name": "Me User",
            "organization_name": "My Org"
        }
    )
    token = reg_response.json()["access_token"]
    
    # Get me
    response = await client.get(
        "/api/v1/auth/me",
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["email"] == "me@example.com"
    assert data["name"] == "Me User"
