# server.py

import uvicorn
from contextlib import asynccontextmanager
from fastapi import FastAPI
from api.routes import router
from crypto_sdk.database import init_db
from crypto_sdk.scheduler import start_scheduler
from crypto_sdk.logger import setup_logger

logger = setup_logger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Runs on startup and shutdown.
    This is the FastAPI way of managing resources — similar to
    start/stop hooks in a Phoenix application.
    """
    # Startup
    logger.info("Server starting up...")
    init_db()
    scheduler = start_scheduler(interval_seconds=60)

    yield  # server is running

    # Shutdown
    logger.info("Server shutting down...")
    scheduler.shutdown()


app = FastAPI(
    title="Crypto SDK API",
    description="Live crypto market data via CoinGecko",
    version="1.0.0",
    lifespan=lifespan,
)

app.include_router(router, prefix="/api/v1")


if __name__ == "__main__":
    uvicorn.run("server:app", host="0.0.0.0", port=8000, reload=True)
