"""Locust load test — API endpoint'larni yuklama bilan tekshirish.

Ishga tushirish:
    locust -f tests/load/locustfile.py --host=http://localhost:8000

Dashboard: http://localhost:8089
"""

import random
from uuid import uuid4

from locust import HttpUser, between, events, task


class DisiplApiUser(HttpUser):
    """Disipl API foydalanuvchi simulyatsiyasi."""

    wait_time = between(1, 3)  # Har bir task orasida 1-3 soniya kutish

    def on_start(self):
        """Foydalanuvchi boshlanganda — register/login."""
        self.user_id = str(uuid4())
        self.token = None

        # Register
        response = self.client.post(
            "/api/v1/auth/register",
            json={
                "email": f"loadtest_{self.user_id[:8]}@test.uz",
                "password": "Test1234!",
                "full_name": "Load Test User",
            },
        )
        if response.status_code in (200, 201):
            data = response.json()
            self.token = data.get("access_token")

        # Agar register bo'lmasa — login qilishga urinib ko'rish
        if not self.token:
            response = self.client.post(
                "/api/v1/auth/login",
                json={
                    "email": f"loadtest_{self.user_id[:8]}@test.uz",
                    "password": "Test1234!",
                },
            )
            if response.status_code == 200:
                self.token = response.json().get("access_token")

    def _auth_headers(self) -> dict:
        """Auth header yaratish."""
        if self.token:
            return {"Authorization": f"Bearer {self.token}"}
        return {}

    @task(10)
    def health_check(self):
        """Health check endpoint — eng ko'p chaqiriladi."""
        self.client.get("/health")

    @task(8)
    def readiness_check(self):
        """Readiness check — DB va Redis tekshirish."""
        self.client.get("/health/ready")

    @task(5)
    def list_goals(self):
        """Maqsadlar ro'yxatini olish."""
        self.client.get(
            "/api/v1/goals",
            headers=self._auth_headers(),
            name="/api/v1/goals [GET]",
        )

    @task(3)
    def create_goal(self):
        """Yangi maqsad yaratish."""
        self.client.post(
            "/api/v1/goals",
            json={
                "title": f"Load Test Goal {random.randint(1, 1000)}",
                "description": "Automated load test goal",
                "target_date": "2026-12-31",
            },
            headers=self._auth_headers(),
            name="/api/v1/goals [POST]",
        )

    @task(4)
    def list_checkins(self):
        """Check-in'lar ro'yxatini olish."""
        self.client.get(
            "/api/v1/checkins",
            headers=self._auth_headers(),
            name="/api/v1/checkins [GET]",
        )

    @task(2)
    def create_checkin(self):
        """Yangi check-in yaratish."""
        self.client.post(
            "/api/v1/checkins",
            json={
                "task_id": str(uuid4()),
                "status": random.choice(["completed", "skipped", "partial"]),
                "note": "Load test check-in",
            },
            headers=self._auth_headers(),
            name="/api/v1/checkins [POST]",
        )

    @task(2)
    def list_insights(self):
        """Insight'lar ro'yxatini olish."""
        self.client.get(
            "/api/v1/insights",
            headers=self._auth_headers(),
            name="/api/v1/insights [GET]",
        )

    @task(1)
    def get_limits(self):
        """Limitlar haqida ma'lumot olish."""
        self.client.get(
            "/api/v1/goals/limits/info",
            headers=self._auth_headers(),
            name="/api/v1/goals/limits/info [GET]",
        )

    @task(1)
    def list_plans(self):
        """Rejalar ro'yxatini olish."""
        self.client.get(
            "/api/v1/plans",
            headers=self._auth_headers(),
            name="/api/v1/plans [GET]",
        )


@events.test_start.add_listener
def on_test_start(environment, **kwargs):
    """Test boshlanishi."""
    print("=" * 50)
    print("DISIPL API LOAD TEST — BOSHLANDI")
    print("=" * 50)


@events.test_stop.add_listener
def on_test_stop(environment, **kwargs):
    """Test tugashi."""
    print("=" * 50)
    print("DISIPL API LOAD TEST — TUGADI")
    print("=" * 50)
