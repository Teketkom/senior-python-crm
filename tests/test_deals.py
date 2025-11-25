import pytest
from httpx import AsyncClient
from decimal import Decimal

async def register_and_get_token(client: AsyncClient, email: str) -> tuple[str, int]:
    response = await client.post(
        "/api/v1/auth/register",
        json={
            "email": email,
            "password": "Password123",
            "name": "Test User",
            "organization_name": "Test Org"
        }
    )
    data = response.json()
    token = data["access_token"]
    
    # Get org ID
    orgs_response = await client.get(
        "/api/v1/auth/organizations/me",
        headers={"Authorization": f"Bearer {token}"}
    )
    org_id = orgs_response.json()[0]["id"]
    
    return token, org_id

@pytest.mark.asyncio
async def test_create_deal(client: AsyncClient):
    token, org_id = await register_and_get_token(client, "deal@example.com")
    
    response = await client.post(
        "/api/v1/deals/",
        headers={
            "Authorization": f"Bearer {token}",
            "X-Organization-Id": str(org_id)
        },
        json={
            "title": "Website redesign",
            "amount": "10000.0",
            "currency": "EUR"
        }
    )
    assert response.status_code == 201
    data = response.json()
    assert data["title"] == "Website redesign"
    assert data["status"] == "new"
    assert data["stage"] == "qualification"

@pytest.mark.asyncio
async def test_update_deal_to_won_with_zero_amount(client: AsyncClient):
    token, org_id = await register_and_get_token(client, "won@example.com")
    
    # Create deal with zero amount
    create_response = await client.post(
        "/api/v1/deals/",
        headers={
            "Authorization": f"Bearer {token}",
            "X-Organization-Id": str(org_id)
        },
        json={
            "title": "Zero deal",
            "amount": "0",
            "currency": "USD"
        }
    )
    deal_id = create_response.json()["id"]
    
    # Try to set status to won
    response = await client.patch(
        f"/api/v1/deals/{deal_id}",
        headers={
            "Authorization": f"Bearer {token}",
            "X-Organization-Id": str(org_id)
        },
        json={
            "status": "won"
        }
    )
    assert response.status_code == 400

@pytest.mark.asyncio
async def test_list_deals(client: AsyncClient):
    token, org_id = await register_and_get_token(client, "list@example.com")
    
    # Create multiple deals
    for i in range(3):
        await client.post(
            "/api/v1/deals/",
            headers={
                "Authorization": f"Bearer {token}",
                "X-Organization-Id": str(org_id)
            },
            json={
                "title": f"Deal {i}",
                "amount": str(1000 * (i + 1)),
                "currency": "USD"
            }
        )
    
    # List deals
    response = await client.get(
        "/api/v1/deals/",
        headers={
            "Authorization": f"Bearer {token}",
            "X-Organization-Id": str(org_id)
        }
    )
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 3
