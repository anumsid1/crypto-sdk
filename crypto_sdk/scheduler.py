# crypto_sdk/scheduler.py
#
# APScheduler job definitions.
# The scheduler runs alongside the FastAPI server in the same process.
# In production this would typically be a separate worker process,
# but running together is common for smaller services.

from datetime import datetime, timezone
from apscheduler.schedulers.background import BackgroundScheduler
from .adapters.coingecko import CoinGeckoAdapter
from .analytics import biggest_gainer, average_price, top_movers
from .database import PriceSnapshot, PriceAlert, get_session
from .logger import setup_logger

logger = setup_logger(__name__)

ALERT_THRESHOLD = 5.0  # percent — log an alert if a coin moves more than this
adapter = CoinGeckoAdapter()


def price_monitor_job():
    """
    Core background job — runs on a schedule.

    1. Fetch latest market data
    2. Store price snapshots in the database
    3. Detect coins that moved beyond the alert threshold
    4. Calculate and log a rolling summary
    """
    logger.info("--- Price monitor job started ---")

    try:
        assets = adapter.get_market_data(currency="usd", limit=10)
    except Exception as e:
        logger.error(f"Failed to fetch market data: {e}")
        return

    session = get_session()

    try:
        # 1. Store a snapshot for every coin
        for asset in assets:
            snapshot = PriceSnapshot(
                coin_id=asset.id,
                symbol=asset.symbol,
                name=asset.name,
                price=asset.current_price,
                market_cap=asset.market_cap,
                price_change_24h=asset.price_change_percentage_24h,
                captured_at=datetime.now(timezone.utc),
            )
            session.add(snapshot)

        # 2. Detect and store price alerts
        movers = top_movers(assets, threshold=ALERT_THRESHOLD)
        for asset in movers:
            alert = PriceAlert(
                coin_id=asset.id,
                symbol=asset.symbol,
                price_change_24h=asset.price_change_percentage_24h,
                price_at_alert=asset.current_price,
                triggered_at=datetime.now(timezone.utc),
            )
            session.add(alert)
            logger.warning(
                f"PRICE ALERT | {asset.name} ({asset.symbol.upper()}) "
                f"moved {asset.price_change_percentage_24h:+.2f}% | "
                f"Current price: ${asset.current_price:,.2f}"
            )

        session.commit()

        # 3. Log a structured summary
        gainer = biggest_gainer(assets)
        avg = average_price(assets)

        logger.info(f"Stored {len(assets)} snapshots | {len(movers)} alert(s) triggered")
        logger.info(f"Average price (top 10): ${avg:,.2f}")
        if gainer:
            logger.info(
                f"Biggest gainer: {gainer.name} at {gainer.price_change_percentage_24h:+.2f}%"
            )

    except Exception as e:
        session.rollback()
        logger.error(f"Database error in price monitor job: {e}")
    finally:
        session.close()

    logger.info("--- Price monitor job complete ---")


def start_scheduler(interval_seconds: int = 60) -> BackgroundScheduler:
    """
    Start the background scheduler and return it.
    Called once when the server starts up.
    """
    scheduler = BackgroundScheduler()

    scheduler.add_job(
        price_monitor_job,
        trigger="interval",
        seconds=interval_seconds,
        id="price_monitor",
        next_run_time=datetime.now(timezone.utc),  # run immediately on startup
    )

    scheduler.start()
    logger.info(f"Scheduler started — price_monitor_job running every {interval_seconds}s")
    return scheduler
