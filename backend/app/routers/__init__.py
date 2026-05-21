from fastapi import APIRouter

from app.routers import (
    auth,
    hotspots,
    locations,
    match,
    offer_requests,
    offers,
    request_actions,
    requests,
    users,
)

api_router = APIRouter()
api_router.include_router(auth.router)
api_router.include_router(users.router)
api_router.include_router(locations.router)
api_router.include_router(hotspots.router)
api_router.include_router(match.router)  # /offers/match before /offers/{id}
api_router.include_router(offers.router)
api_router.include_router(request_actions.router)  # before /requests/{id} GET only
api_router.include_router(requests.router)
api_router.include_router(offer_requests.router)
