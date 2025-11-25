import pytest
from httpx import AsyncClient

async def setup_user_and_org(client: AsyncClient, email: str) -> tuple[str, int]:
    response = await client.post(
        "/api/v1/auth/register",
        json={
            "email": email,
            "password": "Password123",
            "name": "Test User",
            "organization_name": "Test Org"
        }
    )
    token = response.json()["access_token"]
    
    orgs_response = await client.get(
        "/api/v1/auth/organizations/me",
        headers={"Authorization": f"Bearer {token}"}
    )
    org_id = orgs_response.json()[0]["id"]
    return token, org_id

@pytest.mark.asyncio
async def test_create_contact(client: AsyncClient):
    token, org_id = await setup_user_and_org(client, "contact@example.com")
    
    response = await client.post(
        "/api/v1/contacts/",
        headers={
            "Authorization": f"Bearer {token}",
            "X-Organization-Id": str(org_id)
        },
        json={
            "name": "John Doe",
            "email": "john.doe@example.com",
            "phone": "123456789"
        }
    )
    assert response.status_code == 201
    data = response.json()
    assert data["name"] == "John Doe"
    assert data["email"] == "john.doe@example.com"

@pytest.mark.asyncio
async def test_list_contacts_with_search(client: AsyncClient):
    token, org_id = await setup_user_and_org(client, "search@example.com")
    
    # Create contacts
    await client.post(
        "/api/v1/contacts/",
        headers={"Authorization": f"Bearer {token}", "X-Organization-Id": str(org_id)},
        json={"name": "Alice Smith", "email": "alice@example.com"}
    )
    await client.post(
        "/api/v1/contacts/",
        headers={"Authorization": f"Bearer {token}", "X-Organization-Id": str(org_id)},
        json={"name": "Bob Johnson", "email": "bob@example.com"}
    )
    
    # Search for Alice
    response = await client.get(
        "/api/v1/contacts/?search=Alice",
        headers={"Authorization": f"Bearer {token}", "X-Organization-Id": str(org_id)}
    )
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["name"] == "Alice Smith"
