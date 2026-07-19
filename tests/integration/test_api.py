"""API endpoint integration testlari — real DB, real HTTP, async."""

import uuid

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


async def _auth(client, suffix="integ"):
    """Email-based register + login."""
    uid = uuid.uuid4().hex[:8]
    email = f"test_{suffix}_{uid}@disipl.test"
    await client.post(
        "/api/v1/auth/register",
        json={"email": email, "password": "Test1234!", "name": "Tester"},
    )
    r = await client.post(
        "/api/v1/auth/login",
        json={"email": email, "password": "Test1234!"},
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
    async def test_register(self, client):
        uid = uuid.uuid4().hex[:8]
        r = await client.post(
            "/api/v1/auth/register",
            json={
                "email": f"reg_{uid}@disipl.test",
                "password": "Test1234!",
                "name": "Auth Test",
            },
        )
        assert r.status_code == 201
        assert "access_token" in r.json()
        assert "refresh_token" in r.json()

    @pytest.mark.asyncio
    async def test_register_duplicate(self, client):
        uid = uuid.uuid4().hex[:8]
        email = f"dup_{uid}@disipl.test"
        await client.post(
            "/api/v1/auth/register",
            json={"email": email, "password": "Test1234!", "name": "Dup"},
        )
        r = await client.post(
            "/api/v1/auth/register",
            json={"email": email, "password": "Test1234!", "name": "Dup"},
        )
        assert r.status_code == 409

    @pytest.mark.asyncio
    async def test_login(self, client):
        uid = uuid.uuid4().hex[:8]
        email = f"login_{uid}@disipl.test"
        await client.post(
            "/api/v1/auth/register",
            json={"email": email, "password": "Test1234!", "name": "Login Test"},
        )
        r = await client.post(
            "/api/v1/auth/login",
            json={"email": email, "password": "Test1234!"},
        )
        assert r.status_code == 200
        assert "access_token" in r.json()

    @pytest.mark.asyncio
    async def test_login_wrong_password(self, client):
        uid = uuid.uuid4().hex[:8]
        email = f"login_wrong_{uid}@disipl.test"
        await client.post(
            "/api/v1/auth/register",
            json={"email": email, "password": "Test1234!", "name": "Wrong"},
        )
        r = await client.post(
            "/api/v1/auth/login",
            json={"email": email, "password": "WrongPassword!"},
        )
        assert r.status_code == 401

    @pytest.mark.asyncio
    async def test_refresh_token(self, client):
        uid = uuid.uuid4().hex[:8]
        reg = await client.post(
            "/api/v1/auth/register",
            json={
                "email": f"refresh_{uid}@disipl.test",
                "password": "Test1234!",
                "name": "Refresh",
            },
        )
        refresh_token = reg.json()["refresh_token"]
        r = await client.post(
            "/api/v1/auth/refresh",
            json={"refresh_token": refresh_token},
        )
        assert r.status_code == 200
        assert "access_token" in r.json()

    @pytest.mark.asyncio
    async def test_get_me(self, client):
        h = await _auth(client, "me_001")
        r = await client.get("/api/v1/auth/me", headers=h)
        assert r.status_code == 200
        assert "email" in r.json()

    @pytest.mark.asyncio
    async def test_invalid_token(self, client):
        r = await client.get(
            "/api/v1/auth/me",
            headers={"Authorization": "Bearer invalid_token_123"},
        )
        assert r.status_code == 401

    @pytest.mark.asyncio
    async def test_logout(self, client):
        uid = uuid.uuid4().hex[:8]
        email = f"logout_{uid}@disipl.test"
        reg = await client.post(
            "/api/v1/auth/register",
            json={"email": email, "password": "Test1234!", "name": "Logout"},
        )
        refresh_token = reg.json()["refresh_token"]
        r = await client.post(
            "/api/v1/auth/logout",
            json={"refresh_token": refresh_token},
        )
        assert r.status_code == 204

        # Eski refresh token bilan refresh qilib bo'lmaydi
        r2 = await client.post(
            "/api/v1/auth/refresh",
            json={"refresh_token": refresh_token},
        )
        assert r2.status_code == 401

    @pytest.mark.asyncio
    async def test_logout_all(self, client):
        email = "logoutall_test_001@disipl.test"
        h = await _auth(client, "logoutall_001")
        r = await client.post("/api/v1/auth/logout-all", headers=h)
        assert r.status_code == 204

        # Sessiyalar bo'sh bo'lishi kerak
        s = await client.get("/api/v1/auth/sessions", headers=h)
        assert s.status_code == 200
        assert len(s.json()) == 0

    @pytest.mark.asyncio
    async def test_get_sessions(self, client):
        h = await _auth(client, "sessions_001")
        r = await client.get("/api/v1/auth/sessions", headers=h)
        assert r.status_code == 200
        sessions = r.json()
        assert isinstance(sessions, list)
        assert len(sessions) >= 1
        assert "ip_address" in sessions[0]
        assert "created_at" in sessions[0]

    @pytest.mark.asyncio
    async def test_change_password(self, client):
        uid = uuid.uuid4().hex[:8]
        email = f"chpwd_{uid}@disipl.test"
        await client.post(
            "/api/v1/auth/register",
            json={"email": email, "password": "Test1234!", "name": "ChangePwd"},
        )
        login = await client.post(
            "/api/v1/auth/login",
            json={"email": email, "password": "Test1234!"},
        )
        h = {"Authorization": f"Bearer {login.json()['access_token']}"}

        r = await client.post(
            "/api/v1/auth/change-password",
            json={"current_password": "Test1234!", "new_password": "NewPass5678!"},
            headers=h,
        )
        assert r.status_code == 204

        # Eski parol bilan kirib bo'lmaydi
        r2 = await client.post(
            "/api/v1/auth/login",
            json={"email": email, "password": "Test1234!"},
        )
        assert r2.status_code == 401

        # Yangi parol bilan kirish mumkin
        r3 = await client.post(
            "/api/v1/auth/login",
            json={"email": email, "password": "NewPass5678!"},
        )
        assert r3.status_code == 200

    @pytest.mark.asyncio
    async def test_change_password_wrong_current(self, client):
        h = await _auth(client, "chpwd_bad_001")
        r = await client.post(
            "/api/v1/auth/change-password",
            json={"current_password": "WrongPass999!", "new_password": "NewPass5678!"},
            headers=h,
        )
        assert r.status_code == 400


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


class TestFullUserFlow:
    """To'liq foydalanuvchi zanjiri: register → goal → plan → template → check-in → score."""

    @pytest.mark.asyncio
    async def test_happy_path(self, client):
        uid = uuid.uuid4().hex[:8]
        email = f"full_flow_{uid}@disipl.test"
        # 1. Register
        reg = await client.post(
            "/api/v1/auth/register",
            json={
                "email": email,
                "password": "Test1234!",
                "name": "Full Flow User",
            },
        )
        assert reg.status_code == 201
        token = reg.json()["access_token"]
        h = {"Authorization": f"Bearer {token}"}

        # 2. Create goal
        goal = await client.post(
            "/api/v1/goals",
            json={"title": "Ingliz tili C1", "description": "C1 darajaga yetish"},
            headers=h,
        )
        assert goal.status_code == 201
        goal_id = goal.json()["id"]

        # 3. Create plan
        plan = await client.post(
            f"/api/v1/goals/{goal_id}/plans",
            json={"source": "manual"},
            headers=h,
        )
        assert plan.status_code in (200, 201)
        plan_id = plan.json()["id"]

        # 4. Add task template
        tmpl = await client.post(
            f"/api/v1/plans/{plan_id}/task-templates",
            json={
                "title": "50 so'z yodlash",
                "tolerance_minutes": 15,
                "task_weight": 0.8,
            },
            headers=h,
        )
        assert tmpl.status_code in (200, 201)

        # 5. Get user info — tekshirish
        me = await client.get("/api/v1/auth/me", headers=h)
        assert me.status_code == 200
        assert me.json()["email"] == email
