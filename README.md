# ASMI Dashboard API

Backend API untuk ASMI Dashboard menggunakan FastAPI dan PostgreSQL.

## 🚀 Tech Stack

- **Framework**: FastAPI
- **Database**: PostgreSQL
- **ORM**: SQLAlchemy
- **Authentication**: JWT (JSON Web Token)
- **Password Hashing**: Passlib with bcrypt
- **Python Version**: 3.13+

## 📁 Struktur Project

```
backend-asmi-python/
├── app/
│   ├── config/              # Konfigurasi aplikasi
│   │   ├── config.py        # Environment variables & database URL
│   │   ├── database.py      # Database engine & session
│   │   ├── deps.py          # Dependencies (get_db)
│   │   └── logging_config.py # Setup logging
│   │
│   ├── core/                # Core functionality
│   │   └── events.py        # Startup & shutdown events
│   │
│   ├── middleware/          # Middleware
│   │   ├── cors_middleware.py    # CORS configuration
│   │   └── logging_middleware.py # Request logging
│   │
│   ├── models/              # Database models (SQLAlchemy)
│   │   ├── user.py          # User model
│   │   └── category.py      # Category model
│   │
│   ├── schemas/             # Pydantic schemas (validation)
│   │   ├── auth_schema.py   # Auth request/response schemas
│   │   └── category_schema.py # Category schemas
│   │
│   ├── controller/          # Business logic
│   │   ├── auth_controller.py     # Auth logic (register, login)
│   │   └── category_controller.py # Category CRUD logic
│   │
│   ├── routes/              # API routes
│   │   ├── auth.py          # Auth endpoints
│   │   └── category.py      # Category endpoints
│   │
│   ├── utils/               # Utility functions
│   │   ├── jwt.py           # JWT token utilities
│   │   └── security.py      # Password hashing utilities
│   │
│   └── main.py              # Application entry point
│
├── logs/                    # Log files (auto-generated)
│   ├── app.log             # All logs
│   └── error.log           # Error logs only
│
├── .env                     # Environment variables
├── .env.example            # Environment variables template
├── .gitignore              # Git ignore rules
├── requirements.txt        # Python dependencies
└── README.md               # This file
```

## ⚙️ Setup & Installation

### 1. Clone Repository
```bash
git clone <repository-url>
cd backend-asmi-python
```

### 2. Create Virtual Environment
```bash
python -m venv .venv

# Activate virtual environment
# Windows (PowerShell)
.venv\Scripts\Activate.ps1

# Windows (Git Bash)
source .venv/Scripts/activate

# Linux/Mac
source .venv/bin/activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Setup Environment Variables
```bash
# Copy .env.example to .env
cp .env.example .env

# Edit .env dengan konfigurasi Anda
```

**.env** file:
```env
DB_HOST=localhost
DB_PORT=5432
DB_NAME=asmi_db
DB_USER=postgres
DB_PASSWORD=your_password

SECRET_KEY=your-secret-key-here
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=60000
```

### 5. Setup PostgreSQL Database
```bash
# Login ke PostgreSQL
psql -U postgres

# Buat database
CREATE DATABASE asmi_db;

# Exit
\q
```

### 6. Run Application
```bash
uvicorn app.main:app --reload
```

Server akan berjalan di: `http://127.0.0.1:8000`

## 📚 API Documentation

Setelah aplikasi berjalan, akses dokumentasi API di:

- **Swagger UI**: http://127.0.0.1:8000/docs
- **ReDoc**: http://127.0.0.1:8000/redoc

## 🔐 API Endpoints

### Health Check
- `GET /` - Root endpoint & API info
- `GET /health` - Health check
- `GET /health/db` - Database health check

### Authentication (`/api/auth`)
- `POST /api/auth/register` - Register user baru
- `POST /api/auth/login` - Login user

### Categories (`/api/categories`)
- `POST /api/categories/` - Create category
- `GET /api/categories/` - Get all categories
- `PUT /api/categories/{id}` - Update category
- `DELETE /api/categories/{id}` - Delete category

## 📝 Logging

Aplikasi menggunakan sistem logging dengan 3 handlers:

### 1. Console Handler
- Tampil di terminal saat aplikasi running
- Level: INFO

### 2. File Handler - `logs/app.log`
- Semua log (INFO, WARNING, ERROR)
- Max size: 10MB
- Auto rotate: 5 backup files

### 3. Error Handler - `logs/error.log`
- Hanya ERROR
- Max size: 10MB
- Auto rotate: 5 backup files

### Format Log
```
2025-12-20 10:30:45 - __main__ - INFO - 📥 GET /api/categories - Client: 127.0.0.1
2025-12-20 10:30:45 - __main__ - INFO - ✅ GET /api/categories - Status: 200 - Duration: 0.003s
```

## 🔒 Security Features

### Password Handling
- Passwords di-hash menggunakan bcrypt
- Tidak pernah menyimpan plain text password

### Database Connection
- Password dengan karakter khusus (@, !, #, dll) di-encode otomatis
- Connection pool dengan `pool_pre_ping=True`

### Error Handling
- Pesan error yang jelas dan informatif
- Error handling untuk berbagai kasus:
  - Password salah
  - Database tidak ditemukan
  - PostgreSQL tidak running
  - User tidak ada

## 🛠️ Development

### Code Structure
- **Separation of Concerns**: Config, middleware, routes, controllers terpisah
- **Clean Architecture**: Struktur yang rapi dan mudah di-maintain
- **Type Hints**: Menggunakan Pydantic untuk validasi data
- **Modern FastAPI**: Menggunakan lifespan events (bukan deprecated on_event)

### Best Practices
- Environment variables untuk konfigurasi
- Logging untuk tracking requests
- CORS middleware untuk security
- Database connection pooling
- Error handling yang comprehensive

## 📄 License

Internal Project – ASMI
