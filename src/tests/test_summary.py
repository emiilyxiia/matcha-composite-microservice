import pytest
from fastapi.testclient import TestClient

from src.main import app

client = TestClient(app)

# --- Dummy client implementations used for monkeypatching --- #

async def _dummy_get_user(user_id: str):
    if user_id == "missing":
        return None
    return {
        "id": user_id,
        "username": "test_user",
        "email": "test@example.com",
    }

async def _dummy_get_expenses(limit: int = 10, offset: int = 0):
    # Two expenses: 5.0 and 7.5 => total 12.5
    return [
        {"id": "e1", "cost": 5.0, "order_name": "Latte"},
        {"id": "e2", "cost": 7.5, "order_name": "Hojicha"},
    ]

async def _dummy_get_rankings_for_user(user_id: str):
    # Two items: ratings 4.0 and 5.0 => avg 4.5
    return [
        {
            "id": "r1",
            "user_id": user_id,
            "items": [
                {"name": "Ikuyo Ippodo Tea", "origin": "home", "rating": 4.0, "cost_per_gram": 0.8},
                {"name": "Matcha Cafe Maiko", "origin": "cafe", "rating": 5.0, "cost_per_gram": 1.2},
            ],
        }
    ]

@pytest.fixture(autouse=True)
def patch_clients(monkeypatch):
    # Patch the *symbols that summary.py imports*
    monkeypatch.setattr("src.routes.summary.get_user", _dummy_get_user)
    monkeypatch.setattr("src.routes.summary.get_expenses", _dummy_get_expenses)
    monkeypatch.setattr("src.routes.summary.get_rankings_for_user", _dummy_get_rankings_for_user)

def test_get_user_summary_ok():
    user_id = "11111111-1111-1111-1111-111111111111"
    resp = client.get(f"/summary/users/{user_id}?limit=10")
    assert resp.status_code == 200

    data = resp.json()
    assert data["user"]["id"] == user_id
    assert len(data["recentExpenses"]) == 2
    assert len(data["rankings"]) == 1

    # Stats
    assert data["stats"]["numExpenses"] == 2
    assert data["stats"]["totalExpenseCost"] == 12.5
    assert pytest.approx(data["stats"]["averageRankingScore"], 0.0001) == 4.5

def test_get_user_summary_user_not_found(monkeypatch):
    # Override get_user just for this test to simulate missing user
    async def _no_user(user_id: str):
        return None

    monkeypatch.setattr("src.routes.summary.get_user", _no_user)

    resp = client.get("/summary/users/missing?limit=5")
    assert resp.status_code == 404
    assert resp.json()["detail"] == "User not found"
