#!/bin/bash
# Initialize PostgreSQL database for Magic Bus Compass 360

set -e

POSTGRES_HOST=${POSTGRES_HOST:-localhost}
POSTGRES_PORT=${POSTGRES_PORT:-5432}
POSTGRES_USER=${POSTGRES_USER:-mb_user}
POSTGRES_DB=${POSTGRES_DB:-mb_compass}

echo "Waiting for PostgreSQL to be ready..."
sleep 10

echo "Initializing database schema..."
psql -h "$POSTGRES_HOST" -p "$POSTGRES_PORT" -U "$POSTGRES_USER" -d "$POSTGRES_DB" -f scripts/db_schema.sql

echo "Database initialization completed!"
