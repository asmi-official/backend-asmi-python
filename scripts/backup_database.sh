#!/bin/bash

# ========================================
# Database Backup Script
# ========================================
# Usage:
#   ./scripts/backup_database.sh
#   ./scripts/backup_database.sh custom_backup_name
# ========================================

set -e  # Exit on error

# Warna untuk output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Konfigurasi
BACKUP_DIR="./backups"
TIMESTAMP=$(date +"%Y%m%d_%H%M%S")
CUSTOM_NAME=${1:-""}

# Buat folder backup jika belum ada
mkdir -p "$BACKUP_DIR"

echo -e "${YELLOW}🔄 Starting database backup...${NC}"

# Cek apakah database ada di Docker atau external
if docker ps | grep -q asmi_postgres_dev; then
    echo -e "${GREEN}📦 Backing up from Docker container...${NC}"

    # Backup dari Docker container
    if [ -n "$CUSTOM_NAME" ]; then
        BACKUP_FILE="${BACKUP_DIR}/${CUSTOM_NAME}_${TIMESTAMP}.sql"
    else
        BACKUP_FILE="${BACKUP_DIR}/asmi_db_${TIMESTAMP}.sql"
    fi

    docker exec asmi_postgres_dev pg_dump -U postgres asmi_db > "$BACKUP_FILE"

    echo -e "${GREEN}✅ Backup completed!${NC}"
    echo -e "${GREEN}📁 File: $BACKUP_FILE${NC}"

    # Compress backup
    echo -e "${YELLOW}🗜️  Compressing backup...${NC}"
    gzip "$BACKUP_FILE"
    echo -e "${GREEN}✅ Compressed to: ${BACKUP_FILE}.gz${NC}"

    # Tampilkan ukuran file
    SIZE=$(du -h "${BACKUP_FILE}.gz" | cut -f1)
    echo -e "${GREEN}📊 Size: $SIZE${NC}"

else
    echo -e "${GREEN}💻 Backing up from local PostgreSQL...${NC}"

    # Backup dari PostgreSQL lokal (baca dari .env)
    if [ -f .env ]; then
        export $(cat .env | grep -v '^#' | xargs)
    fi

    if [ -n "$CUSTOM_NAME" ]; then
        BACKUP_FILE="${BACKUP_DIR}/${CUSTOM_NAME}_${TIMESTAMP}.sql"
    else
        BACKUP_FILE="${BACKUP_DIR}/asmi_db_${TIMESTAMP}.sql"
    fi

    PGPASSWORD=$DB_PASSWORD pg_dump -h ${DB_HOST:-localhost} -p ${DB_PORT:-5432} -U $DB_USER $DB_NAME > "$BACKUP_FILE"

    echo -e "${GREEN}✅ Backup completed!${NC}"
    echo -e "${GREEN}📁 File: $BACKUP_FILE${NC}"

    # Compress backup
    echo -e "${YELLOW}🗜️  Compressing backup...${NC}"
    gzip "$BACKUP_FILE"
    echo -e "${GREEN}✅ Compressed to: ${BACKUP_FILE}.gz${NC}"

    # Tampilkan ukuran file
    SIZE=$(du -h "${BACKUP_FILE}.gz" | cut -f1)
    echo -e "${GREEN}📊 Size: $SIZE${NC}"
fi

# Hapus backup lama (keep last 10)
echo -e "${YELLOW}🧹 Cleaning old backups (keeping last 10)...${NC}"
ls -t ${BACKUP_DIR}/*.sql.gz | tail -n +11 | xargs -r rm
echo -e "${GREEN}✅ Cleanup completed!${NC}"

echo ""
echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}✅ Backup process finished successfully!${NC}"
echo -e "${GREEN}========================================${NC}"
