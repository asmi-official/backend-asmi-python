import logging
from sqlalchemy import text
from app.config.database import engine

logger = logging.getLogger(__name__)


def startup_event():
    """
    Event that runs when application starts
    - Test database connection
    - Log PostgreSQL information
    """
    try:
        with engine.connect() as conn:
            result = conn.execute(text("SELECT version()"))
            version_row = result.fetchone()
            if version_row is None:
                raise Exception("Could not retrieve PostgreSQL version")
            version = version_row[0]

        print("=" * 60)
        print("[OK] PostgreSQL CONNECTED SUCCESSFULLY!")
        print(f"   Database: {engine.url.database}")
        print(f"   Host: {engine.url.host}:{engine.url.port}")
        print(f"   User: {engine.url.username}")
        print(f"   Version: {version.split(',')[0]}")
        print("=" * 60)

        logger.info("Database connection established successfully")

    except Exception as e:
        print("=" * 60)
        print("[ERROR] PostgreSQL CONNECTION FAILED!")
        print(f"   Error: {str(e)}")
        print("=" * 60)

        logger.error(f"Database connection failed: {str(e)}")
        raise


def shutdown_event():
    """
    Event that runs when application shuts down
    """
    logger.info("Application shutdown")
    print("Application shutting down...")
