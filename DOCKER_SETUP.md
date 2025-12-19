# 🐳 Docker Setup Guide - ASMI Backend

Panduan lengkap untuk menggunakan Docker di project ASMI Backend.

---

## 📋 Table of Contents

1. [Quick Start](#quick-start)
2. [Development Setup](#development-setup)
3. [Production Setup](#production-setup)
4. [Database Backup & Restore](#database-backup--restore)
5. [Troubleshooting](#troubleshooting)
6. [Advanced Usage](#advanced-usage)

---

## 🚀 Quick Start

### Development (Database di Docker)

```bash
# 1. Copy environment file
cp .env.example .env

# 2. Start services
docker-compose up -d

# 3. Check logs
docker-compose logs -f backend

# 4. Access API
# http://localhost:8000
# http://localhost:8000/docs
```

### Production (Database Eksternal)

```bash
# 1. Setup environment
cp .env.production.example .env.production

# 2. Install PostgreSQL di server
sudo apt install postgresql postgresql-contrib

# 3. Deploy backend
docker-compose -f docker-compose.prod.yml up -d
```

---

## 🛠️ Development Setup

### Konsep Development
- ✅ Backend di Docker (hot reload enabled)
- ✅ PostgreSQL di Docker (data persistent)
- ✅ Auto migration dengan Alembic
- ✅ Database accessible di `localhost:5432`

### File: `docker-compose.yml`

```yaml
services:
  backend:
    # FastAPI backend dengan hot reload
  db:
    # PostgreSQL 16 dengan persistent volume
```

### Commands

```bash
# Start semua services
docker-compose up -d

# Stop services (data TIDAK hilang)
docker-compose down

# Stop dan HAPUS data (⚠️ DANGER!)
docker-compose down -v

# Rebuild container
docker-compose up -d --build

# View logs
docker-compose logs -f

# View logs backend only
docker-compose logs -f backend

# Execute command di container
docker-compose exec backend bash

# Check status
docker-compose ps
```

### Data Persistence

Data PostgreSQL disimpan di **Docker named volume**: `postgres_data`

Lokasi di sistem:
- **Windows**: `\\wsl$\docker-desktop-data\data\docker\volumes\backend-asmi-python_postgres_data\_data`
- **Linux/Mac**: `/var/lib/docker/volumes/backend-asmi-python_postgres_data/_data`

Data **TETAP ADA** meskipun:
- Container di-stop
- Container di-restart
- Container di-rebuild
- Docker di-restart

Data **HILANG** hanya jika:
- `docker-compose down -v` (hapus volume)
- `docker volume rm postgres_data`

---

## 🏭 Production Setup

### Konsep Production
- ✅ Backend di Docker (optimized, no reload)
- ✅ PostgreSQL EKSTERNAL (install di server)
- ✅ 4 worker processes (production-grade)
- ✅ Healthcheck enabled
- ✅ Auto restart on failure

### File: `docker-compose.prod.yml`

### Step-by-Step

#### 1. Install PostgreSQL di Server

**Ubuntu/Debian:**
```bash
# Install PostgreSQL
sudo apt update
sudo apt install postgresql postgresql-contrib

# Start service
sudo systemctl start postgresql
sudo systemctl enable postgresql

# Create database
sudo -u postgres psql
postgres=# CREATE DATABASE asmi_db;
postgres=# CREATE USER asmi_user WITH PASSWORD 'strong_password';
postgres=# GRANT ALL PRIVILEGES ON DATABASE asmi_db TO asmi_user;
postgres=# \q
```

#### 2. Configure Environment

```bash
# Copy template
cp .env.production.example .env.production

# Edit file
nano .env.production
```

Isi `.env.production`:
```env
DB_HOST=localhost
DB_PORT=5432
DB_NAME=asmi_db
DB_USER=asmi_user
DB_PASSWORD=strong_password

SECRET_KEY=generated_secret_key_here
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=1440
ENVIRONMENT=production
```

Generate secret key:
```bash
openssl rand -hex 32
```

#### 3. Deploy Backend

```bash
# Build dan start
docker-compose -f docker-compose.prod.yml up -d --build

# Check logs
docker-compose -f docker-compose.prod.yml logs -f

# Check healthcheck
docker ps
```

#### 4. Verify Deployment

```bash
# Test API
curl http://localhost:8000/health

# Check database connection
curl http://localhost:8000/health/db
```

---

## 💾 Database Backup & Restore

### Automatic Backup Script

Script sudah disediakan di `scripts/backup_database.sh`

```bash
# Backup dengan timestamp
./scripts/backup_database.sh

# Backup dengan custom name
./scripts/backup_database.sh production_before_migration

# Output: backups/asmi_db_20250120_143022.sql.gz
```

**Features:**
- ✅ Auto-detect Docker atau PostgreSQL lokal
- ✅ Auto-compress dengan gzip
- ✅ Auto-delete backup lama (keep last 10)
- ✅ Timestamp otomatis

### Restore Database

```bash
# Restore dari backup
./scripts/restore_database.sh backups/asmi_db_20250120_143022.sql.gz

# ⚠️ WARNING: Ini akan REPLACE semua data!
```

### Manual Backup (Docker)

```bash
# Backup
docker exec asmi_postgres_dev pg_dump -U postgres asmi_db > backup.sql

# Compress
gzip backup.sql

# Restore
gunzip -c backup.sql.gz | docker exec -i asmi_postgres_dev psql -U postgres asmi_db
```

### Manual Backup (PostgreSQL Lokal)

```bash
# Backup
pg_dump -U postgres -h localhost asmi_db > backup.sql

# Restore
psql -U postgres -h localhost asmi_db < backup.sql
```

### Scheduled Backup (Cron)

```bash
# Edit crontab
crontab -e

# Backup setiap hari jam 2 pagi
0 2 * * * cd /path/to/project && ./scripts/backup_database.sh daily_backup
```

---

## 🔧 Troubleshooting

### Container tidak bisa connect ke database

**Problem:** `connection refused` atau `could not connect to server`

**Solution:**
```bash
# Check database container status
docker-compose ps

# Check database logs
docker-compose logs db

# Restart database
docker-compose restart db

# Wait for healthcheck (5-10 seconds)
```

### Port 5432 already in use

**Problem:** PostgreSQL sudah jalan di host

**Solution 1 (Recommended):** Gunakan PostgreSQL lokal
```yaml
# Edit docker-compose.yml - remove db service
# Update .env:
DB_HOST=host.docker.internal  # Windows/Mac
# DB_HOST=172.17.0.1  # Linux
```

**Solution 2:** Ganti port
```yaml
db:
  ports:
    - "5433:5432"  # External:Internal
```

### Data hilang setelah restart

**Check volume:**
```bash
# List volumes
docker volume ls

# Inspect volume
docker volume inspect backend-asmi-python_postgres_data
```

**Restore dari backup:**
```bash
./scripts/restore_database.sh backups/latest_backup.sql.gz
```

### Migration error

```bash
# Check migration status
docker-compose exec backend alembic current

# Run migration manually
docker-compose exec backend alembic upgrade head

# Rollback migration
docker-compose exec backend alembic downgrade -1
```

### Backend tidak bisa akses database eksternal (Production)

**Linux only:** Tambahkan extra_hosts

```yaml
# docker-compose.prod.yml
services:
  backend:
    extra_hosts:
      - "host.docker.internal:host-gateway"
```

Update `.env.production`:
```env
DB_HOST=host.docker.internal
```

---

## 🔬 Advanced Usage

### View Database dari Terminal

```bash
# Docker database
docker exec -it asmi_postgres_dev psql -U postgres asmi_db

# Lokal database
psql -U postgres -h localhost asmi_db
```

### Useful SQL Commands

```sql
-- List tables
\dt

-- Describe table
\d categories

-- Count records
SELECT COUNT(*) FROM categories;

-- Exit
\q
```

### Logs Management

```bash
# Follow logs dengan filter
docker-compose logs -f backend | grep ERROR

# View logs tertentu
docker-compose logs --tail=100 backend

# Save logs ke file
docker-compose logs backend > backend_logs.txt
```

### Performance Monitoring

```bash
# Container stats
docker stats asmi_backend_dev

# Database connections
docker exec asmi_postgres_dev psql -U postgres -c "SELECT count(*) FROM pg_stat_activity;"
```

### Clean Up

```bash
# Remove stopped containers
docker-compose down

# Remove images
docker-compose down --rmi all

# Remove volumes (⚠️ DATA LOSS!)
docker-compose down -v

# Prune all unused Docker data
docker system prune -a
```

---

## 📦 Migration Checklist

### Pindah dari Development ke Production

- [ ] Backup database development
  ```bash
  ./scripts/backup_database.sh before_prod_migration
  ```

- [ ] Setup PostgreSQL di server production

- [ ] Copy `.env.production` dan generate secret key baru

- [ ] Deploy dengan docker-compose.prod.yml

- [ ] Restore backup jika perlu
  ```bash
  ./scripts/restore_database.sh backups/before_prod_migration.sql.gz
  ```

- [ ] Test API endpoints

- [ ] Setup scheduled backup (cron)

### Pindah antar Server

- [ ] Backup database di server lama
  ```bash
  ./scripts/backup_database.sh
  ```

- [ ] Copy backup file ke server baru
  ```bash
  scp backups/*.sql.gz user@new-server:/tmp/
  ```

- [ ] Setup PostgreSQL di server baru

- [ ] Clone repository di server baru

- [ ] Configure `.env.production`

- [ ] Deploy docker container

- [ ] Restore database
  ```bash
  ./scripts/restore_database.sh /tmp/backup.sql.gz
  ```

- [ ] Verify deployment
  ```bash
  curl http://localhost:8000/health/db
  ```

---

## 📞 Support

Jika ada masalah dengan Docker setup:

1. Check logs: `docker-compose logs -f`
2. Check container status: `docker-compose ps`
3. Verify `.env` configuration
4. Restart services: `docker-compose restart`
5. Rebuild if needed: `docker-compose up -d --build`

---

## 📝 Notes

- **Development**: Database di Docker untuk kemudahan development
- **Production**: Database eksternal untuk stability & performance
- **Data Safety**: Always backup sebelum migration atau update besar
- **Security**: Jangan commit file `.env` atau `.env.production` ke Git!

Happy Dockering! 🐳🚀
