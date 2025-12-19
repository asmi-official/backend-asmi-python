#!/bin/bash

# ========================================
# Database Restore Script
# ========================================
# Usage:
#   ./scripts/restore_database.sh backups/asmi_db_20250120_143022.sql.gz
# ========================================

set -e  # Exit on error

# Warna untuk output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Validasi input
if [ -z "$1" ]; then
    echo -e "${RED}❌ Error: Backup file not specified${NC}"
    echo -e "${YELLOW}Usage: ./scripts/restore_database.sh <backup-file>${NC}"
    echo -e "${YELLOW}Example: ./scripts/restore_database.sh backups/asmi_db_20250120_143022.sql.gz${NC}"
    exit 1
fi

BACKUP_FILE=$1

# Cek apakah file ada
if [ ! -f "$BACKUP_FILE" ]; then
    echo -e "${RED}❌ Error: Backup file not found: $BACKUP_FILE${NC}"
    exit 1
fi

echo -e "${YELLOW}⚠️  WARNING: This will REPLACE all data in the database!${NC}"
echo -e "${YELLOW}Backup file: $BACKUP_FILE${NC}"
read -p "Are you sure? (yes/no): " CONFIRM

if [ "$CONFIRM" != "yes" ]; then
    echo -e "${RED}❌ Restore cancelled${NC}"
    exit 0
fi

echo -e "${YELLOW}🔄 Starting database restore...${NC}"

# Extract jika file .gz
if [[ $BACKUP_FILE == *.gz ]]; then
    echo -e "${YELLOW}📦 Extracting backup file...${NC}"
    TEMP_SQL="/tmp/restore_temp.sql"
    gunzip -c "$BACKUP_FILE" > "$TEMP_SQL"
    SQL_FILE="$TEMP_SQL"
else
    SQL_FILE="$BACKUP_FILE"
fi

# Cek apakah database ada di Docker atau external
if docker ps | grep -q asmi_postgres_dev; then
    echo -e "${GREEN}📦 Restoring to Docker container...${NC}"

    # Drop dan create database baru
    docker exec asmi_postgres_dev psql -U postgres -c "DROP DATABASE IF EXISTS asmi_db;"
    docker exec asmi_postgres_dev psql -U postgres -c "CREATE DATABASE asmi_db;"

    # Restore
    docker exec -i asmi_postgres_dev psql -U postgres asmi_db < "$SQL_FILE"

    echo -e "${GREEN}✅ Restore completed!${NC}"

else
    echo -e "${GREEN}💻 Restoring to local PostgreSQL...${NC}"

    # Baca dari .env
    if [ -f .env ]; then
        export $(cat .env | grep -v '^#' | xargs)
    fi

    # Drop dan create database baru
    PGPASSWORD=$DB_PASSWORD psql -h ${DB_HOST:-localhost} -p ${DB_PORT:-5432} -U $DB_USER postgres -c "DROP DATABASE IF EXISTS $DB_NAME;"
    PGPASSWORD=$DB_PASSWORD psql -h ${DB_HOST:-localhost} -p ${DB_PORT:-5432} -U $DB_USER postgres -c "CREATE DATABASE $DB_NAME;"

    # Restore
    PGPASSWORD=$DB_PASSWORD psql -h ${DB_HOST:-localhost} -p ${DB_PORT:-5432} -U $DB_USER $DB_NAME < "$SQL_FILE"

    echo -e "${GREEN}✅ Restore completed!${NC}"
fi

# Cleanup temp file
if [ -f "$TEMP_SQL" ]; then
    rm "$TEMP_SQL"
fi

echo ""
echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}✅ Database restored successfully!${NC}"
echo -e "${GREEN}========================================${NC}"
