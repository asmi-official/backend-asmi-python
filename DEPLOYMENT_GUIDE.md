# 🚀 Production Deployment Guide - ASMI Backend

Tutorial lengkap deploy ASMI Backend ke production server (VPS/Cloud).

---

## 📋 Prerequisites

Sebelum mulai, pastikan kamu punya:

- ✅ VPS/Cloud Server (DigitalOcean, AWS, GCP, Vultr, dll)
- ✅ Ubuntu 20.04+ / Debian 11+ (recommended)
- ✅ Domain (opsional, bisa pakai IP)
- ✅ SSH access ke server
- ✅ Repository Git (GitHub/GitLab)

---

## 🎯 Table of Contents

1. [Setup Server](#1-setup-server)
2. [Install Dependencies](#2-install-dependencies)
3. [Setup PostgreSQL](#3-setup-postgresql)
4. [Clone & Configure Project](#4-clone--configure-project)
5. [Deploy dengan Docker](#5-deploy-dengan-docker)
6. [Setup Auto-Start](#6-setup-auto-start)
7. [Setup Nginx (Optional)](#7-setup-nginx-optional)
8. [Setup SSL/HTTPS (Optional)](#8-setup-sslhttps-optional)
9. [Monitoring & Maintenance](#9-monitoring--maintenance)

---

## 1. Setup Server

### Step 1.1: Login ke Server

```bash
# SSH ke server (ganti dengan IP/domain kamu)
ssh root@your-server-ip

# Atau jika pakai user non-root
ssh username@your-server-ip
```

### Step 1.2: Update System

```bash
# Update package list
sudo apt update

# Upgrade installed packages
sudo apt upgrade -y

# Install essential tools
sudo apt install -y curl git vim wget net-tools
```

### Step 1.3: Create Non-Root User (Optional tapi Recommended)

```bash
# Create user
sudo adduser asmi

# Add to sudo group
sudo usermod -aG sudo asmi

# Add to docker group (nanti setelah install docker)
sudo usermod -aG docker asmi

# Switch to new user
su - asmi
```

---

## 2. Install Dependencies

### Step 2.1: Install Docker

```bash
# Install Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh

# Start Docker
sudo systemctl start docker

# Enable auto-start
sudo systemctl enable docker

# Test Docker
docker --version
```

### Step 2.2: Install Docker Compose

```bash
# Install Docker Compose
sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose

# Make executable
sudo chmod +x /usr/local/bin/docker-compose

# Test Docker Compose
docker-compose --version
```

### Step 2.3: Add User to Docker Group

```bash
# Add current user to docker group
sudo usermod -aG docker $USER

# Apply changes (logout & login, atau reboot)
# Logout
exit

# Login kembali
ssh asmi@your-server-ip

# Test (tanpa sudo)
docker ps
```

---

## 3. Setup PostgreSQL

### Step 3.1: Install PostgreSQL

```bash
# Install PostgreSQL
sudo apt install -y postgresql postgresql-contrib

# Start service
sudo systemctl start postgresql

# Enable auto-start
sudo systemctl enable postgresql

# Check status
sudo systemctl status postgresql
```

### Step 3.2: Create Database & User

```bash
# Login sebagai postgres user
sudo -u postgres psql

# Di dalam psql shell:
```

```sql
-- Create database
CREATE DATABASE asmi_db;

-- Create user
CREATE USER asmi WITH PASSWORD 'YOUR_STRONG_PASSWORD_HERE';

-- Grant privileges
GRANT ALL PRIVILEGES ON DATABASE asmi_db TO asmi;

-- Exit
\q
```

### Step 3.3: Test Connection

```bash
# Test connect
psql -h localhost -U asmi -d asmi_db

# Enter password saat diminta
# Jika berhasil, keluar dengan \q
\q
```

---

## 4. Clone & Configure Project

### Step 4.1: Clone Repository

```bash
# Buat folder untuk projects
mkdir -p ~/projects
cd ~/projects

# Clone repo (ganti dengan URL repo kamu)
git clone https://github.com/your-username/backend-asmi-python.git

# Masuk ke folder project
cd backend-asmi-python
```

### Step 4.2: Configure Environment

```bash
# Copy template production
cp .env.production.example .env.production

# Edit file
nano .env.production
```

**Isi `.env.production`:**

```env
# Database Configuration
DB_HOST=localhost
DB_PORT=5432
DB_NAME=asmi_db
DB_USER=asmi
DB_PASSWORD=YOUR_STRONG_PASSWORD_HERE

# JWT Configuration (GENERATE SECRET KEY BARU!)
SECRET_KEY=GENERATE_WITH_COMMAND_BELOW
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=1440

# Application
ENVIRONMENT=production
```

**Generate Secret Key:**

```bash
# Generate secret key
openssl rand -hex 32

# Copy output dan paste ke SECRET_KEY di .env.production
```

**Save file:**
- Tekan `Ctrl + X`
- Tekan `Y`
- Tekan `Enter`

---

## 5. Deploy dengan Docker

### Step 5.1: Build & Start Services

```bash
# Build dan start (pertama kali)
docker-compose -f docker-compose.prod.yml up -d --build

# Check logs
docker-compose -f docker-compose.prod.yml logs -f
```

**Output yang BAGUS:**
```
🔄 Running database migrations...
✅ Migrations completed!
🚀 Starting production server...
INFO:     Started server process
INFO:     Uvicorn running on http://0.0.0.0:8000
```

Tekan `Ctrl + C` untuk keluar dari logs.

### Step 5.2: Verify Deployment

```bash
# Check containers
docker ps

# Test API
curl http://localhost:8000/health

# Test database connection
curl http://localhost:8000/health/db

# View API docs
curl http://localhost:8000/docs
```

**Output yang BAGUS:**
```json
{
  "status": "ok",
  "message": "API is running"
}
```

---

## 6. Setup Auto-Start

Agar aplikasi otomatis jalan setelah server restart.

### Step 6.1: Install Systemd Service

```bash
# Make script executable
chmod +x scripts/install-systemd-service.sh

# Install service
sudo ./scripts/install-systemd-service.sh
```

### Step 6.2: Test Service

```bash
# Check status
sudo systemctl status asmi-backend

# Test restart
sudo systemctl restart asmi-backend

# Check logs
journalctl -u asmi-backend -f
```

### Step 6.3: Test Auto-Start (ULTIMATE TEST!)

```bash
# Reboot server
sudo reboot

# Tunggu 1-2 menit, lalu SSH kembali
ssh asmi@your-server-ip

# Check apakah app sudah jalan
docker ps
curl http://localhost:8000/health

# ✅ App harus sudah jalan otomatis!
```

---

## 7. Setup Nginx (Optional)

Untuk expose API ke internet dengan domain.

### Step 7.1: Install Nginx

```bash
# Install Nginx
sudo apt install -y nginx

# Start service
sudo systemctl start nginx
sudo systemctl enable nginx

# Check status
sudo systemctl status nginx
```

### Step 7.2: Configure Nginx

```bash
# Create config
sudo nano /etc/nginx/sites-available/asmi-backend
```

**Paste konfigurasi ini:**

```nginx
server {
    listen 80;
    server_name your-domain.com www.your-domain.com;
    # Atau pakai IP: server_name your-server-ip;

    # Security headers
    add_header X-Frame-Options "SAMEORIGIN" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header X-XSS-Protection "1; mode=block" always;

    # Logs
    access_log /var/log/nginx/asmi-backend-access.log;
    error_log /var/log/nginx/asmi-backend-error.log;

    # Proxy to FastAPI
    location / {
        proxy_pass http://localhost:8000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_cache_bypass $http_upgrade;

        # Timeouts
        proxy_connect_timeout 60s;
        proxy_send_timeout 60s;
        proxy_read_timeout 60s;
    }

    # Health check endpoint (bypass authentication)
    location /health {
        proxy_pass http://localhost:8000/health;
    }
}
```

**Save file** (`Ctrl + X`, `Y`, `Enter`)

### Step 7.3: Enable Site

```bash
# Create symlink
sudo ln -s /etc/nginx/sites-available/asmi-backend /etc/nginx/sites-enabled/

# Test config
sudo nginx -t

# Reload Nginx
sudo systemctl reload nginx
```

### Step 7.4: Configure Firewall

```bash
# Allow HTTP
sudo ufw allow 'Nginx HTTP'

# Allow HTTPS (untuk nanti)
sudo ufw allow 'Nginx HTTPS'

# Allow SSH (IMPORTANT!)
sudo ufw allow OpenSSH

# Enable firewall
sudo ufw enable

# Check status
sudo ufw status
```

### Step 7.5: Test Nginx

```bash
# Test dari server
curl http://localhost

# Test dari komputer lokal
# Buka browser: http://your-server-ip/health
```

---

## 8. Setup SSL/HTTPS (Optional)

Untuk HTTPS dengan SSL certificate gratis dari Let's Encrypt.

### Step 8.1: Install Certbot

```bash
# Install Certbot
sudo apt install -y certbot python3-certbot-nginx
```

### Step 8.2: Get SSL Certificate

```bash
# Get certificate (ganti dengan domain kamu)
sudo certbot --nginx -d your-domain.com -d www.your-domain.com

# Follow prompts:
# - Enter email
# - Agree to terms
# - Choose redirect HTTP to HTTPS (pilih 2)
```

### Step 8.3: Test Auto-Renewal

```bash
# Test renewal
sudo certbot renew --dry-run

# ✅ Jika sukses, certificate akan auto-renew setiap 90 hari
```

### Step 8.4: Verify HTTPS

```bash
# Buka browser
https://your-domain.com/health

# ✅ Harus ada gembok hijau (secure connection)
```

---

## 9. Monitoring & Maintenance

### 9.1: View Logs

```bash
# Docker logs
docker-compose -f docker-compose.prod.yml logs -f backend

# Systemd logs
journalctl -u asmi-backend -f

# Nginx logs
sudo tail -f /var/log/nginx/asmi-backend-access.log
sudo tail -f /var/log/nginx/asmi-backend-error.log
```

### 9.2: Database Backup

```bash
# Manual backup
./scripts/backup_database.sh production_backup

# Check backups
ls -lh backups/
```

### 9.3: Setup Automated Backup (Cron)

```bash
# Edit crontab
crontab -e

# Add this line (backup setiap hari jam 2 pagi)
0 2 * * * cd ~/projects/backend-asmi-python && ./scripts/backup_database.sh daily_backup

# Save and exit
```

### 9.4: Update Application

```bash
# Pull latest code
cd ~/projects/backend-asmi-python
git pull

# Rebuild and restart
docker-compose -f docker-compose.prod.yml up -d --build

# Check logs
docker-compose -f docker-compose.prod.yml logs -f backend
```

### 9.5: Check System Resources

```bash
# Check disk space
df -h

# Check memory
free -h

# Check Docker stats
docker stats

# Check PostgreSQL size
sudo -u postgres psql -c "SELECT pg_size_pretty(pg_database_size('asmi_db'));"
```

---

## 🛠️ Common Commands

### Docker Commands

```bash
# Start services
docker-compose -f docker-compose.prod.yml up -d

# Stop services
docker-compose -f docker-compose.prod.yml down

# Restart services
docker-compose -f docker-compose.prod.yml restart

# View logs
docker-compose -f docker-compose.prod.yml logs -f

# Rebuild & restart
docker-compose -f docker-compose.prod.yml up -d --build

# Execute command in container
docker-compose -f docker-compose.prod.yml exec backend bash
```

### Systemd Commands

```bash
# Start service
sudo systemctl start asmi-backend

# Stop service
sudo systemctl stop asmi-backend

# Restart service
sudo systemctl restart asmi-backend

# Status
sudo systemctl status asmi-backend

# Enable auto-start
sudo systemctl enable asmi-backend

# Disable auto-start
sudo systemctl disable asmi-backend
```

### Database Commands

```bash
# Connect to database
psql -h localhost -U asmi -d asmi_db

# Backup
./scripts/backup_database.sh

# Restore
./scripts/restore_database.sh backups/backup_file.sql.gz

# Check database size
sudo -u postgres psql -c "SELECT pg_size_pretty(pg_database_size('asmi_db'));"
```

---

## 🔧 Troubleshooting

### App tidak bisa diakses

```bash
# Check container status
docker ps

# Check container logs
docker-compose -f docker-compose.prod.yml logs backend

# Check port
sudo netstat -tlnp | grep 8000

# Check firewall
sudo ufw status
```

### Database connection error

```bash
# Check PostgreSQL status
sudo systemctl status postgresql

# Check database
sudo -u postgres psql -l

# Test connection
psql -h localhost -U asmi -d asmi_db

# Check .env.production
cat .env.production | grep DB_
```

### Container restart terus

```bash
# Check logs untuk error
docker logs asmi_backend_prod --tail 100

# Check restart count
docker inspect asmi_backend_prod | grep -A 5 RestartCount

# Common issues:
# - Database connection failed (.env salah)
# - Migration error (check alembic)
# - Port already in use
```

### Nginx 502 Bad Gateway

```bash
# Check backend is running
curl http://localhost:8000/health

# Check Nginx config
sudo nginx -t

# Check Nginx logs
sudo tail -f /var/log/nginx/error.log

# Restart Nginx
sudo systemctl restart nginx
```

---

## 📊 Performance Tips

1. **Database Connection Pooling**
   - Sudah di-handle oleh SQLAlchemy
   - Default: 5 connections

2. **Nginx Caching** (Optional)
   - Tambah caching untuk static responses
   - Reduce load ke backend

3. **Database Indexing**
   - Pastikan index pada kolom yang sering di-query
   - Check dengan `EXPLAIN ANALYZE`

4. **Monitoring**
   - Install monitoring tools (Prometheus, Grafana)
   - Setup alerts untuk downtime

---

## 🎉 Deployment Complete!

Sekarang aplikasi kamu sudah:

- ✅ Deploy di production server
- ✅ PostgreSQL running native (optimal performance)
- ✅ Auto-start setelah server reboot
- ✅ Auto-restart jika crash
- ✅ Backup otomatis setiap hari
- ✅ HTTPS dengan SSL (jika setup)
- ✅ Nginx reverse proxy (jika setup)

**Access API:**
- HTTP: `http://your-server-ip:8000`
- Nginx: `http://your-domain.com`
- HTTPS: `https://your-domain.com` (jika SSL enabled)

**API Docs:**
- Swagger: `https://your-domain.com/docs`
- ReDoc: `https://your-domain.com/redoc`

---

## 📞 Need Help?

1. Check logs: `docker-compose logs -f`
2. Check status: `docker ps`
3. Check firewall: `sudo ufw status`
4. Test health: `curl http://localhost:8000/health`

Happy Deploying! 🚀
