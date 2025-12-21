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
       - USER INFO
            - username
            - matcha budget
       - RANKINGS INFO
            - average rating score across all ranked items
            - Top 5 most worth matchas (worth = rating / cost_per_gram)
       - BUDGET INFO    
            - total expense cost
            - recent expenses
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
    # Expenses: total expenses and recent expenses
    total_cost = 0.0
    num_expenses = 0
    for e in expenses:
        cost = e.get("cost")
        if isinstance(cost, (int, float)):
            total_cost += cost
        num_expenses += 1

    expenses_sorted = sorted(
        expenses,
        key=lambda e: e.get("expense_date") or "",
        reverse=True
    )

    # Rankings: average rating across all items
    scores: list[float] = []
    for r in rankings:
        for item in r.get("items", []):
            rating = item.get("rating")
            if isinstance(rating, (int, float)):
                scores.append(rating)

    avg_rating = round(sum(scores) / len(scores),2) if scores else None

    worth_items = []
    for r in rankings:
        for item in r.get("items", []):
            name = item.get("name")
            rating = item.get("rating")
            cpg = item.get("cost_per_gram")  # from M3 RankedItem
            origin = item.get("origin")

            if isinstance(rating, (int, float)) and isinstance(cpg, (int, float)) and cpg > 0:
                worth_items.append({
                    "name": name,
                    "origin": origin,
                    "rating": rating,
                    "cost_per_gram": cpg,
                    "worth": round(rating / cpg, 2)
                })
    worth_items.sort(key=lambda x: x["worth"], reverse=True)
    top_worth = worth_items[:5]

    return {
        "username": username,               #from user microservice
        "matcha_budget": matcha_budget,     #from user microservice
        "mostWorthLeaderboard": top_worth,  #from ranking microservice
        "averageRankingScore": avg_rating,  #from ranking microservice
        "totalExpenses": total_cost,        #from budget microservice
        "recentExpenses": expenses_sorted,         #from budget microservice
    }