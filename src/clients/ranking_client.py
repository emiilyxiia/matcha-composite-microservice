import httpx
from src.config import RANKING_SERVICE_BASE_URL


async def get_rankings_for_user(user_id: str) -> list[dict]:
    """
    Fetch rankings for a specific user from the Rankings service.

    Matches M3's GET /ranking:
    - GET /ranking?user_id=<uuid>[&min_rating=&max_rating=&max_cost=&origin=]

    Returns a JSON array of readRank objects.
    """
    url = f"{RANKING_SERVICE_BASE_URL}/ranking"
    params = {"user_id": user_id}

    async with httpx.AsyncClient() as client:
        resp = await client.get(url, params=params)

    resp.raise_for_status()
    return resp.json()