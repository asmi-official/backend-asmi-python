from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker, declarative_base
from sqlalchemy.exc import OperationalError
from app.config.config import DATABASE_URL, DB_HOST, DB_PORT, DB_NAME, DB_USER

try:
    engine = create_engine(
        DATABASE_URL,
        pool_pre_ping=True
    )

    # Test connection
    with engine.connect() as conn:
        conn.execute(text("SELECT 1"))

except OperationalError as e:
    error_msg = str(e.orig) if hasattr(e, 'orig') else str(e)

    if "password authentication failed" in error_msg:
        raise ConnectionError(
            f"❌ ERROR: PostgreSQL password is incorrect!\n"
            f"Database: {DB_NAME}\n"
            f"User: {DB_USER}\n"
            f"Make sure the password in .env file matches PostgreSQL"
        ) from e

    elif "database" in error_msg and "does not exist" in error_msg:
        raise ConnectionError(
            f"❌ ERROR: Database '{DB_NAME}' not found!\n"
            f"Run this command to create the database:\n"
            f"  psql -U {DB_USER}\n"
            f"  CREATE DATABASE {DB_NAME};"
        ) from e

    elif "Connection refused" in error_msg or "connect" in error_msg.lower():
        raise ConnectionError(
            f"❌ ERROR: Cannot connect to PostgreSQL!\n"
            f"Host: {DB_HOST}:{DB_PORT}\n"
            f"Make sure PostgreSQL is running:\n"
            f"  Windows: Get-Service postgresql*\n"
            f"  Linux/Mac: sudo systemctl status postgresql"
        ) from e

    elif "role" in error_msg and "does not exist" in error_msg:
        raise ConnectionError(
            f"❌ ERROR: PostgreSQL user '{DB_USER}' does not exist!\n"
            f"Run this command to create the user:\n"
            f"  psql -U postgres\n"
            f"  CREATE USER {DB_USER} WITH PASSWORD 'your_password';\n"
            f"  GRANT ALL PRIVILEGES ON DATABASE {DB_NAME} TO {DB_USER};"
        ) from e

    else:
        raise ConnectionError(
            f"❌ ERROR: Database connection failed!\n"
            f"Host: {DB_HOST}:{DB_PORT}\n"
            f"Database: {DB_NAME}\n"
            f"User: {DB_USER}\n"
            f"Detail error: {error_msg}"
        ) from e

except Exception as e:
    raise ConnectionError(
        f"❌ ERROR: Unexpected error during database connection!\n"
        f"Detail: {str(e)}"
    ) from e

SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)

Base = declarative_base()
