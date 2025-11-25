import pytest
from httpx import AsyncClient

async def setup_deals_for_analytics(client: AsyncClient) -> tuple[str, int]:
    response = await client.post(
        "/api/v1/auth/register",
        json={
            "email": "analytics@example.com",
            "password": "Password123",
            "name": "Analytics User",
            "organization_name": "Analytics Org"
        }
    )
    token = response.json()["access_token"]
    
    orgs_response = await client.get(
        "/api/v1/auth/organizations/me",
        headers={"Authorization": f"Bearer {token}"}
    )
    org_id = orgs_response.json()[0]["id"]
    
    # Create deals
    for i in range(5):
        await client.post(
            "/api/v1/deals/",
            headers={"Authorization": f"Bearer {token}", "X-Organization-Id": str(org_id)},
            json={"title": f"Deal {i}", "amount": str(1000 * (i + 1)), "currency": "USD"}
        )
    
    # Mark some as won
    deals_response = await client.get(
        "/api/v1/deals/",
        headers={"Authorization": f"Bearer {token}", "X-Organization-Id": str(org_id)}
    )
    deals = deals_response.json()
    
    for deal in deals[:2]:
        await client.patch(
            f"/api/v1/deals/{deal['id']}",
            headers={"Authorization": f"Bearer {token}", "X-Organization-Id": str(org_id)},
            json={"status": "won"}
        )
    
    return token, org_id

@pytest.mark.asyncio
async def test_deals_summary(client: AsyncClient):
    token, org_id = await setup_deals_for_analytics(client)
    
    response = await client.get(
        "/api/v1/analytics/deals/summary?days=30",
        headers={"Authorization": f"Bearer {token}", "X-Organization-Id": str(org_id)}
    )
    assert response.status_code == 200
    data = response.json()
    assert "total_deals_count" in data
    assert "won_deals_count" in data
    assert data["total_deals_count"] == 5
    assert data["won_deals_count"] == 2

@pytest.mark.asyncio
async def test_deals_funnel(client: AsyncClient):
    token, org_id = await setup_deals_for_analytics(client)
    
    response = await client.get(
        "/api/v1/analytics/deals/funnel",
        headers={"Authorization": f"Bearer {token}", "X-Organization-Id": str(org_id)}
    )
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) > 0
    assert all("stage" in item and "count" in item for item in data)
