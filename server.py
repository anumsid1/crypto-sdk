# server.py

import uvicorn
from fastapi import FastAPI
from api.routes import router

app = FastAPI(
    title="Crypto SDK API",
    description="Live crypto market data via CoinGecko",
    version="1.0.0",
)

app.include_router(router, prefix="/api/v1")


if __name__ == "__main__":
    uvicorn.run("server:app", host="0.0.0.0", port=8000, reload=True)
