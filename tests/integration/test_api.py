"""API endpoint integration testlari — real DB, real HTTP, async."""

import httpx
import pytest
import pytest_asyncio
from httpx import ASGITransport

from src.presentation.api.app import app

transport = ASGITransport(app=app)


@pytest_asyncio.fixture
async def client():
    async with httpx.AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac


async def _auth(client, telegram_id="integ_test"):
    r = await client.post(
        "/api/v1/auth/telegram",
        json={"telegram_id": telegram_id, "name": "Tester"},
    )
    return {"Authorization": f"Bearer {r.json()['access_token']}"}


class TestHealthAPI:
    @pytest.mark.asyncio
    async def test_health(self, client):
        r = await client.get("/health")
        assert r.status_code == 200
        assert r.json()["status"] == "ok"


class TestAuthAPI:
    @pytest.mark.asyncio
    async def test_create_user(self, client):
        r = await client.post(
            "/api/v1/auth/telegram",
            json={"telegram_id": "auth_create_001", "name": "Auth Test"},
        )
        assert r.status_code == 200
        assert "access_token" in r.json()

    @pytest.mark.asyncio
    async def test_idempotent_auth(self, client):
        await client.post(
            "/api/v1/auth/telegram",
            json={"telegram_id": "auth_idem_001", "name": "Idem"},
        )
        r = await client.post(
            "/api/v1/auth/telegram",
            json={"telegram_id": "auth_idem_001", "name": "Idem"},
        )
        assert r.status_code == 200


class TestGoalsAPI:
    @pytest.mark.asyncio
    async def test_create_goal(self, client):
        h = await _auth(client, "goals_create_001")
        r = await client.post(
            "/api/v1/goals",
            json={"title": "Test Maqsad", "description": "Tavsif"},
            headers=h,
        )
        assert r.status_code == 201
        data = r.json()
        assert data["title"] == "Test Maqsad"
        assert data["status"] == "active"

    @pytest.mark.asyncio
    async def test_create_goal_empty_title(self, client):
        h = await _auth(client, "goals_empty_001")
        r = await client.post("/api/v1/goals", json={"title": ""}, headers=h)
        assert r.status_code in (400, 422)

    @pytest.mark.asyncio
    async def test_list_goals(self, client):
        h = await _auth(client, "goals_list_001")
        await client.post("/api/v1/goals", json={"title": "M1"}, headers=h)
        await client.post("/api/v1/goals", json={"title": "M2"}, headers=h)
        r = await client.get("/api/v1/goals", headers=h)
        assert r.status_code == 200
        assert len(r.json()) >= 2

    @pytest.mark.asyncio
    async def test_get_goal_not_found(self, client):
        from uuid import uuid4

        h = await _auth(client, "goals_404_001")
        r = await client.get(f"/api/v1/goals/{uuid4()}", headers=h)
        assert r.status_code == 404

    @pytest.mark.asyncio
    async def test_unauthenticated(self, client):
        r = await client.get("/api/v1/goals")
        assert r.status_code in (401, 403)


class TestPlansAPI:
    @pytest.mark.asyncio
    async def test_create_plan(self, client):
        h = await _auth(client, "plans_001")
        g = await client.post("/api/v1/goals", json={"title": "Goal"}, headers=h)
        goal_id = g.json()["id"]
        r = await client.post(
            f"/api/v1/goals/{goal_id}/plans",
            json={"source": "manual"},
            headers=h,
        )
        assert r.status_code in (200, 201)
        assert r.json()["source"] == "manual"


class TestTaskTemplatesAPI:
    @pytest.mark.asyncio
    async def test_add_template(self, client):
        h = await _auth(client, "tmpl_001")
        g = await client.post("/api/v1/goals", json={"title": "Goal"}, headers=h)
        p = await client.post(
            f"/api/v1/goals/{g.json()['id']}/plans",
            json={"source": "manual"},
            headers=h,
        )
        r = await client.post(
            f"/api/v1/plans/{p.json()['id']}/task-templates",
            json={"title": "50 so'z", "tolerance_minutes": 15, "task_weight": 0.8},
            headers=h,
        )
        assert r.status_code in (200, 201)
        assert r.json()["title"] == "50 so'z"


class TestAdminAPI:
    @pytest.mark.asyncio
    async def test_stats_requires_auth(self, client):
        r = await client.get("/api/v1/admin/stats")
        assert r.status_code in (401, 403)

    @pytest.mark.asyncio
    async def test_users_requires_auth(self, client):
        r = await client.get("/api/v1/admin/users")
        assert r.status_code in (401, 403)
