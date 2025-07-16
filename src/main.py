from contextlib import asynccontextmanager
from pathlib import Path
import logging
import sys

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

sys.path.append(str(Path(__file__).parent.parent))
logging.basicConfig(level=logging.INFO)

from src.api.auth import router as router_auth  # noqa: E402
from src.config import settings  # noqa: E402
from src.init import redis_manager  # noqa: E402
from src.utils.db_manager import DBManager  # noqa: E402


@asynccontextmanager
async def lifespan(app: FastAPI):
    await redis_manager.connect()
    async with DBManager(settings.DB_URL, settings.DB_NAME) as db:
        await db.init_indexes()
    yield
    await redis_manager.close()


app = FastAPI(lifespan=lifespan)
app.include_router(router_auth)

app.add_middleware(CORSMiddleware, allow_origins=["*"])

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", reload=True)
