import os
from dotenv import load_dotenv
from urllib.parse import quote_plus

load_dotenv()

DB_HOST = os.getenv("DB_HOST")
DB_PORT = os.getenv("DB_PORT")
DB_NAME = os.getenv("DB_NAME")
DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")

# Validasi environment variables
missing_vars = []
if not DB_HOST:
    missing_vars.append("DB_HOST")
if not DB_PORT:
    missing_vars.append("DB_PORT")
if not DB_NAME:
    missing_vars.append("DB_NAME")
if not DB_USER:
    missing_vars.append("DB_USER")
if not DB_PASSWORD:
    missing_vars.append("DB_PASSWORD")

if missing_vars:
    raise ValueError(
        f"❌ ERROR: Environment variables tidak ditemukan!\n"
        f"Missing: {', '.join(missing_vars)}\n"
        f"Pastikan file .env sudah ada dan berisi:\n"
        f"  DB_HOST=localhost\n"
        f"  DB_PORT=5432\n"
        f"  DB_NAME=asmi_db\n"
        f"  DB_USER=postgres\n"
        f"  DB_PASSWORD=your_password"
    )

# Encode password untuk handle karakter khusus seperti @, !, #, dll
DATABASE_URL = (
    f"postgresql://{DB_USER}:{quote_plus(DB_PASSWORD)}"
    f"@{DB_HOST}:{DB_PORT}/{DB_NAME}"
)
