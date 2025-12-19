# ⚡ Quick Deploy Cheat Sheet

Quick reference untuk deploy production. Untuk tutorial lengkap, baca [DEPLOYMENT_GUIDE.md](DEPLOYMENT_GUIDE.md)

---

## 🚀 Quick Deploy (Copy-Paste Ready!)

### 1. Setup Server

```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install essentials
sudo apt install -y curl git vim wget

# Install Docker
curl -fsSL https://get.docker.com -o get-docker.sh && sudo sh get-docker.sh

# Install Docker Compose
sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose

# Add user to docker group
sudo usermod -aG docker $USER

# Logout & login kembali
exit
```

### 2. Setup PostgreSQL

```bash
# Install
sudo apt install -y postgresql postgresql-contrib

# Start & enable
sudo systemctl start postgresql
sudo systemctl enable postgresql

# Create database
sudo -u postgres psql << EOF
CREATE DATABASE asmi_db;
CREATE USER asmi WITH PASSWORD 'YOUR_PASSWORD';
GRANT ALL PRIVILEGES ON DATABASE asmi_db TO asmi;
\q
EOF
```

### 3. Deploy App

```bash
# Clone repo
cd ~
git clone YOUR_REPO_URL backend-asmi-python
cd backend-asmi-python

# Setup environment
cp .env.production.example .env.production

# Generate secret key
openssl rand -hex 32

# Edit .env.production (paste secret key + database password)
nano .env.production

# Deploy
docker-compose -f docker-compose.prod.yml up -d --build

# Check logs
docker-compose -f docker-compose.prod.yml logs -f
```

### 4. Setup Auto-Start

```bash
# Install systemd service
chmod +x scripts/install-systemd-service.sh
sudo ./scripts/install-systemd-service.sh

# Test
sudo systemctl status asmi-backend
```

### 5. Test Deployment

```bash
# Test API
curl http://localhost:8000/health

# Test database
curl http://localhost:8000/health/db

# View logs
docker-compose -f docker-compose.prod.yml logs -f backend
```

---

## 📝 Environment Variables Template

```env
# .env.production

DB_HOST=localhost
DB_PORT=5432
DB_NAME=asmi_db
DB_USER=asmi
DB_PASSWORD=YOUR_STRONG_PASSWORD

SECRET_KEY=GENERATE_WITH_openssl_rand_hex_32
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=1440

ENVIRONMENT=production
```

---

## 🔧 Common Commands

```bash
# Start
docker-compose -f docker-compose.prod.yml up -d

# Stop
docker-compose -f docker-compose.prod.yml down

# Restart
docker-compose -f docker-compose.prod.yml restart

# Logs
docker-compose -f docker-compose.prod.yml logs -f

# Rebuild
docker-compose -f docker-compose.prod.yml up -d --build

# Backup database
./scripts/backup_database.sh

# Check status
sudo systemctl status asmi-backend
docker ps
```

---

## 🆘 Quick Troubleshooting

```bash
# Check logs
docker-compose -f docker-compose.prod.yml logs backend

# Check container
docker ps -a

# Check database
psql -h localhost -U asmi -d asmi_db

# Restart everything
sudo systemctl restart asmi-backend
```

---

## 🎯 Access Points

- **API**: `http://your-server-ip:8000`
- **Health**: `http://your-server-ip:8000/health`
- **Docs**: `http://your-server-ip:8000/docs`

---

For detailed guide, see [DEPLOYMENT_GUIDE.md](DEPLOYMENT_GUIDE.md)
