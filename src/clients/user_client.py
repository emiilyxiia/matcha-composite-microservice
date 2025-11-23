import httpx
from src.config import USER_SERVICE_BASE_URL

async def get_user(user_id: str) -> dict | None:
    """
    Fetch a user by UUID from the User Service.

    Assumes User Service exposes:
      GET /users/{user_id}
    and returns 404 if not found.
    """
    url = f"{USER_SERVICE_BASE_URL}/users/{user_id}"
    async with httpx.AsyncClient() as client:
        resp = await client.get(url)

    if resp.status_code == 404:
        return None

    resp.raise_for_status()
    return resp.json()
