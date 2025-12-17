from fastapi import APIRouter, HTTPException, Depends
import asyncio
import httpx
from src.clients.user_client import get_user
from src.clients.budget_client import get_expenses
from src.clients.ranking_client import get_rankings_for_user
from src.auth.deps import require_jwt

router = APIRouter()

async def safe(coro, default):
    """Prevents one downstream failure from crashing the whole summary."""
    try:
        return await coro
    except (httpx.HTTPError, Exception):
        return default

@router.get("/summary/users/{user_id}")
async def get_user_summary(
    user_id: str,
    limit: int = 10,
    _auth=Depends(require_jwt)  #Enforce JWT
):
    """
    Composite summary for a user.

    Steps:
    1. Logical foreign key check:
       - Call User Service: GET /users/{user_id}
       - If user not found -> 404 and DO NOT call other services.

    2. Parallel calls:
       - Rankings Service: GET /ranking?user_id={user_id}
       - Budget Service:   GET /expenses?limit={limit}&offset=0

    3. Aggregate response:
       - username
       - rankings
       - recentExpenses
       - stats (totalExpenseCost, numExpenses, averageRankingScore, numRankingEntries)
    """

    # 1. FK check: user must exist
    user = await get_user(user_id)
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")

    username = user.get("username")
    matcha_budget = user.get("matcha_budget")  # this is in your M1 payload

    # 2. parallel calls (M2 + M3)
    rankings_task = asyncio.create_task(safe(get_rankings_for_user(user_id), []))
    expenses_task = asyncio.create_task(safe(get_expenses(limit=limit, offset=0), []))

    rankings, expenses = await asyncio.gather(rankings_task, expenses_task)

    # 3. Compute stats
    # Expenses: total cost & count
    total_cost = 0.0
    num_expenses = 0
    for e in expenses:
        cost = e.get("cost")
        if isinstance(cost, (int, float)):
            total_cost += cost
        num_expenses += 1

    # Rankings: average rating across all items
    scores: list[float] = []
    for r in rankings:
        for item in r.get("items", []):
            rating = item.get("rating")
            if isinstance(rating, (int, float)):
                scores.append(rating)

    avg_rating = sum(scores) / len(scores) if scores else None

    return {
        "username": username,
        "matcha_budget": matcha_budget,
        "rankings": rankings,
        "totalExpenseCost": total_cost,
        "numExpenses": num_expenses,
        "averageRankingScore": avg_rating,
    }