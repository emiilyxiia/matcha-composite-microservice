from fastapi import APIRouter, HTTPException
import asyncio

from src.clients.user_client import get_user
from src.clients.budget_client import get_expenses
from src.clients.ranking_client import get_rankings_for_user

router = APIRouter()

@router.get("/summary/users/{user_id}")
async def get_user_summary(user_id: str, limit: int = 10):
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
       - user
       - rankings
       - recentExpenses
       - stats (totalExpenseCost, numExpenses, averageRankingScore, numRankingEntries)
    """

    # 1. FK check: user must exist
    user = await get_user(user_id)
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")

    # 2. Parallel calls to M2 and M3
    rankings_task = asyncio.create_task(get_rankings_for_user(user_id))
    expenses_task = asyncio.create_task(get_expenses(limit=limit, offset=0))

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

    average_rating = sum(scores) / len(scores) if scores else None

    return {
        "user": user,
        "rankings": rankings,
        "recentExpenses": expenses,
        "stats": {
            "totalExpenseCost": total_cost,
            "numExpenses": num_expenses,
            "averageRankingScore": average_rating,
            "numRankingEntries": len(rankings),
        },
    }