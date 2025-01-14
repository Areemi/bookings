from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
from starlette.requests import Request
from starlette.responses import Response
from sqladmin import Admin

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware


from fastapi_cache import FastAPICache
from fastapi_cache.backends.redis import RedisBackend
from fastapi_cache.decorator import cache

from redis import asyncio as aioredis


from app.admin.views import BookingsAdmin, HotelsAdmin, RoomsAdmin, UsersAdmin
from app.config import settings
from app.bookings.router import router as router_bookings
from app.pages.router import router as router_pages
from app.images.router import router as router_images
from app.hotels.router import router as router_hotels
from app.database import engine
from app.users.router import router_auth, router_users
from app.admin.auth import authentication_backend


@asynccontextmanager
async def lifespan(_: FastAPI) -> AsyncIterator[None]:
    redis = aioredis.from_url(f"redis://{settings.REDIS_HOST}:{settings.REDIS_PORT}", encoding="utf-8")
    FastAPICache.init(RedisBackend(redis), prefix="cache")
    yield

app = FastAPI(lifespan=lifespan)


@cache()
async def get_cache():
    return 1

app.mount("/static", StaticFiles(directory="app/static"), "static")

# Включение основных роутеров
app.include_router(router_auth)
app.include_router(router_users)
app.include_router(router_hotels)
app.include_router(router_bookings)

# Включение дополнительных роутеров
app.include_router(router_pages)
app.include_router(router_images)



origins = [
    "http://localhost:3000",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "OPTIONS", "DELETE", "PATCH", "PUT"],
    allow_headers=["Content-Type", "Set-Cookie",
                   "Access-Control-Allow-Headers", 
                   "Access-Control-Allow-Origin",
                    "Authorizations"]
)


admin = Admin(app, engine, authentication_backend=authentication_backend)

admin.add_view(UsersAdmin)
admin.add_view(BookingsAdmin)
admin.add_view(RoomsAdmin)
admin.add_view(HotelsAdmin)
