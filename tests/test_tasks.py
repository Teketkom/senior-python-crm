import pytest
from httpx import AsyncClient
from datetime import datetime, timedelta

async def setup_deal(client: AsyncClient) -> tuple[str, int, int]:
    response = await client.post(
        "/api/v1/auth/register",
        json={
            "email": "task@example.com",
            "password": "Password123",
            "name": "Task User",
            "organization_name": "Task Org"
        }
    )
    token = response.json()["access_token"]
    
    orgs_response = await client.get(
        "/api/v1/auth/organizations/me",
        headers={"Authorization": f"Bearer {token}"}
    )
    org_id = orgs_response.json()[0]["id"]
    
    # Create a deal
    deal_response = await client.post(
        "/api/v1/deals/",
        headers={"Authorization": f"Bearer {token}", "X-Organization-Id": str(org_id)},
        json={"title": "Test Deal", "amount": "5000", "currency": "USD"}
    )
    deal_id = deal_response.json()["id"]
    
    return token, org_id, deal_id

@pytest.mark.asyncio
async def test_create_task(client: AsyncClient):
    token, org_id, deal_id = await setup_deal(client)
    
    due_date = (datetime.utcnow() + timedelta(days=7)).isoformat()
    response = await client.post(
        "/api/v1/tasks/",
        headers={"Authorization": f"Bearer {token}", "X-Organization-Id": str(org_id)},
        json={
            "deal_id": deal_id,
            "title": "Call client",
            "description": "Discuss proposal",
            "due_date": due_date
        }
    )
    assert response.status_code == 201
    data = response.json()
    assert data["title"] == "Call client"
    assert data["is_done"] is False

@pytest.mark.asyncio
async def test_create_task_past_due_date(client: AsyncClient):
    token, org_id, deal_id = await setup_deal(client)
    
    past_date = (datetime.utcnow() - timedelta(days=1)).isoformat()
    response = await client.post(
        "/api/v1/tasks/",
        headers={"Authorization": f"Bearer {token}", "X-Organization-Id": str(org_id)},
        json={
            "deal_id": deal_id,
            "title": "Past task",
            "due_date": past_date
        }
    )
    assert response.status_code == 400

@pytest.mark.asyncio
async def test_mark_task_done(client: AsyncClient):
    token, org_id, deal_id = await setup_deal(client)
    
    # Create task
    create_response = await client.post(
        "/api/v1/tasks/",
        headers={"Authorization": f"Bearer {token}", "X-Organization-Id": str(org_id)},
        json={"deal_id": deal_id, "title": "Task to complete"}
    )
    task_id = create_response.json()["id"]
    
    # Mark done
    response = await client.patch(
        f"/api/v1/tasks/{task_id}/mark-done",
        headers={"Authorization": f"Bearer {token}", "X-Organization-Id": str(org_id)}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["is_done"] is True
