import logging
from sqlalchemy import text
from app.config.database import engine

logger = logging.getLogger(__name__)


def startup_event():
    """
    Event yang dijalankan saat aplikasi startup
    - Test koneksi database
    - Log informasi PostgreSQL
    """
    try:
        with engine.connect() as conn:
            result = conn.execute(text("SELECT version()"))
            version = result.fetchone()[0]

        print("=" * 60)
        print("✅ PostgreSQL CONNECTED SUCCESSFULLY!")
        print(f"   Database: {engine.url.database}")
        print(f"   Host: {engine.url.host}:{engine.url.port}")
        print(f"   User: {engine.url.username}")
        print(f"   Version: {version.split(',')[0]}")
        print("=" * 60)

        logger.info("Database connection established successfully")

    except Exception as e:
        print("=" * 60)
        print("❌ PostgreSQL CONNECTION FAILED!")
        print(f"   Error: {str(e)}")
        print("=" * 60)

        logger.error(f"Database connection failed: {str(e)}")
        raise


def shutdown_event():
    """
    Event yang dijalankan saat aplikasi shutdown
    """
    logger.info("Application shutdown")
    print("👋 Application shutting down...")
