#!/bin/bash
# backup.sh - SQLite database backup script

BACKUP_DIR="./backups"
mkdir -p "$BACKUP_DIR"
TIMESTAMP=$(date +"%Y%m%d_%H%M%S")
BACKUP_FILE="$BACKUP_DIR/mental_health_$TIMESTAMP.db"

if [ -f "./backend/mental_health.db" ]; then
    cp ./backend/mental_health.db "$BACKUP_FILE"
    echo "💾 Database backup saved to $BACKUP_FILE"
else
    echo "⚠️ Database file not found, skipping backup."
fi
