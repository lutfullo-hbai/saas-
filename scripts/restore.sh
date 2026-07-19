#!/bin/bash
# PostgreSQL restore script for Disipl

set -e

# Configuration
DB_HOST="${DB_HOST:-db}"
DB_PORT="${DB_PORT:-5432}"
DB_NAME="${POSTGRES_DB:-disipl}"
DB_USER="${POSTGRES_USER:-disipl}"
BACKUP_DIR="/backups"
AUTO_CONFIRM="${AUTO_CONFIRM:-false}"

# Check if backup file is provided
if [ -z "$BACKUP_FILE" ]; then
    echo "Usage: BACKUP_FILE=<path> $0"
    echo "Available backups:"
    ls -lh "$BACKUP_DIR"/${DB_NAME}_*.sql.gz 2>/dev/null || echo "No backups found"
    exit 1
fi

# Check if backup file exists
if [ ! -f "$BACKUP_FILE" ]; then
    echo "Backup file not found: $BACKUP_FILE"
    exit 1
fi

# Confirm restore (skip if AUTO_CONFIRM=true)
if [ "$AUTO_CONFIRM" != "true" ]; then
    echo "WARNING: This will overwrite the current database!"
    echo "Backup file: $BACKUP_FILE"
    read -p "Are you sure? (yes/no): " CONFIRM

    if [ "$CONFIRM" != "yes" ]; then
        echo "Restore cancelled."
        exit 0
    fi
fi

# Perform restore
echo "Starting restore from: $BACKUP_FILE at $(date)"
gunzip -c "$BACKUP_FILE" | psql -h "$DB_HOST" -p "$DB_PORT" -U "$DB_USER" -d "$DB_NAME"

echo "Restore completed at $(date)"
