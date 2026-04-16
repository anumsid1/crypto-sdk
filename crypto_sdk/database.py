# crypto_sdk/database.py
#
# SQLAlchemy database setup and models.
# SQLAlchemy is the standard ORM in Python — similar to Ecto in Elixir.
# We use SQLite here (a local file-based database) — easy to swap to
# Postgres in production by changing the DATABASE_URL in .env.

import os
from datetime import datetime
from sqlalchemy import create_engine, Column, String, Float, DateTime, Integer
from sqlalchemy.orm import DeclarativeBase, Session

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///crypto_sdk.db")

engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})


class Base(DeclarativeBase):
    pass


class PriceSnapshot(Base):
    """
    One row per coin per job run.
    Builds up a history of prices over time.
    """
    __tablename__ = "price_snapshots"

    id = Column(Integer, primary_key=True, autoincrement=True)
    coin_id = Column(String, nullable=False)
    symbol = Column(String, nullable=False)
    name = Column(String, nullable=False)
    price = Column(Float, nullable=False)
    market_cap = Column(Float, nullable=False)
    price_change_24h = Column(Float, nullable=False)
    captured_at = Column(DateTime, default=datetime.utcnow, nullable=False)


class PriceAlert(Base):
    """
    Logged when a coin moves more than the alert threshold in a single job run.
    """
    __tablename__ = "price_alerts"

    id = Column(Integer, primary_key=True, autoincrement=True)
    coin_id = Column(String, nullable=False)
    symbol = Column(String, nullable=False)
    price_change_24h = Column(Float, nullable=False)
    price_at_alert = Column(Float, nullable=False)
    triggered_at = Column(DateTime, default=datetime.utcnow, nullable=False)


def init_db():
    """Create all tables if they don't exist."""
    Base.metadata.create_all(engine)


def get_session() -> Session:
    """Return a new database session."""
    return Session(engine)
