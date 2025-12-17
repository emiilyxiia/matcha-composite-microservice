import httpx
from src.config import BUDGET_SERVICE_BASE_URL

#no actual url for budget yet since it is on VM
async def get_expenses(limit: int = 10, offset: int = 0) -> list[dict]:
    """
    Fetch a page of expenses from the Budget service.

    Matches M2's GET /expenses:
      - Query params: limit, offset
      - Response: JSON array of expense objects, each may include "links".
    """
    url = f"{BUDGET_SERVICE_BASE_URL}/expenses"
    params = {"limit": limit, "offset": offset}
    async with httpx.AsyncClient() as client:
        resp = await client.get(url, params=params, timeout=5.0)
    resp.raise_for_status()
    return resp.json()