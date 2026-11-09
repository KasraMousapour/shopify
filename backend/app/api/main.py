from fastapi import APIRouter

from app.api.routes import cart, collections, items, login, orders, private, products, users, utils
from app.core.config import settings

api_router = APIRouter()
api_router.include_router(login.router)
api_router.include_router(users.router)
api_router.include_router(utils.router)
api_router.include_router(items.router)
api_router.include_router(collections.router)
api_router.include_router(products.router)
api_router.include_router(cart.router)
api_router.include_router(orders.router)

if settings.FASTAPI_ENV == 'development':
    api_router.include_router(private.router)
