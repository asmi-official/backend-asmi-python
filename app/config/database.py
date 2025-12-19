from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker, declarative_base
from sqlalchemy.exc import OperationalError
from app.config.config import DATABASE_URL, DB_HOST, DB_PORT, DB_NAME, DB_USER

try:
    engine = create_engine(
        DATABASE_URL,
        pool_pre_ping=True
    )

    # Test koneksi
    with engine.connect() as conn:
        conn.execute(text("SELECT 1"))

except OperationalError as e:
    error_msg = str(e.orig) if hasattr(e, 'orig') else str(e)

    if "password authentication failed" in error_msg:
        raise ConnectionError(
            f"❌ ERROR: Password PostgreSQL salah!\n"
            f"Database: {DB_NAME}\n"
            f"User: {DB_USER}\n"
            f"Pastikan password di file .env sesuai dengan PostgreSQL"
        ) from e

    elif "database" in error_msg and "does not exist" in error_msg:
        raise ConnectionError(
            f"❌ ERROR: Database '{DB_NAME}' tidak ditemukan!\n"
            f"Jalankan command ini untuk membuat database:\n"
            f"  psql -U {DB_USER}\n"
            f"  CREATE DATABASE {DB_NAME};"
        ) from e

    elif "Connection refused" in error_msg or "connect" in error_msg.lower():
        raise ConnectionError(
            f"❌ ERROR: Tidak bisa koneksi ke PostgreSQL!\n"
            f"Host: {DB_HOST}:{DB_PORT}\n"
            f"Pastikan PostgreSQL sudah running:\n"
            f"  Windows: Get-Service postgresql*\n"
            f"  Linux/Mac: sudo systemctl status postgresql"
        ) from e

    elif "role" in error_msg and "does not exist" in error_msg:
        raise ConnectionError(
            f"❌ ERROR: User PostgreSQL '{DB_USER}' tidak ada!\n"
            f"Jalankan command ini untuk membuat user:\n"
            f"  psql -U postgres\n"
            f"  CREATE USER {DB_USER} WITH PASSWORD 'your_password';\n"
            f"  GRANT ALL PRIVILEGES ON DATABASE {DB_NAME} TO {DB_USER};"
        ) from e

    else:
        raise ConnectionError(
            f"❌ ERROR: Koneksi database gagal!\n"
            f"Host: {DB_HOST}:{DB_PORT}\n"
            f"Database: {DB_NAME}\n"
            f"User: {DB_USER}\n"
            f"Detail error: {error_msg}"
        ) from e

except Exception as e:
    raise ConnectionError(
        f"❌ ERROR: Unexpected error saat koneksi database!\n"
        f"Detail: {str(e)}"
    ) from e

SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)

Base = declarative_base()
