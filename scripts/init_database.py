#!/usr/bin/env python3
"""
Database initialization script for PostgreSQL.
Creates tables, enums, and indexes for the sensor metrics application.
"""

import asyncio
import os
import sys
from pathlib import Path

# Add the app directory to the Python path
sys.path.insert(0, str(Path(__file__).parent.parent))

from sqlalchemy import text
from sqlalchemy.ext.asyncio import create_async_engine

from app.storage.database_config import get_db_config


async def create_enum_types(engine):
    """Create PostgreSQL enum types."""
    async with engine.begin() as conn:
        # Create metric_type_enum if it doesn't exist
        await conn.execute(text("""
            DO $$ BEGIN
                CREATE TYPE metric_type_enum AS ENUM ('temperature', 'humidity');
            EXCEPTION
                WHEN duplicate_object THEN null;
            END $$;
        """))


async def create_tables(engine):
    """Create database tables."""
    async with engine.begin() as conn:
        # Create sensors table
        await conn.execute(text("""
            CREATE TABLE IF NOT EXISTS sensors (
                sensor_id VARCHAR PRIMARY KEY,
                sensor_type VARCHAR NOT NULL,
                created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
            );
        """))

        # Create metrics table with composite primary key
        await conn.execute(text("""
            CREATE TABLE IF NOT EXISTS metrics (
                sensor_id VARCHAR NOT NULL REFERENCES sensors(sensor_id),
                metric_type metric_type_enum NOT NULL,
                timestamp TIMESTAMPTZ NOT NULL,
                value DOUBLE PRECISION NOT NULL,
                PRIMARY KEY (sensor_id, metric_type, timestamp)
            );
        """))


async def create_indexes(engine):
    """Create database indexes for performance."""
    async with engine.begin() as conn:
        # Create composite index for fast range scans
        await conn.execute(text("""
            CREATE INDEX IF NOT EXISTS idx_metrics_sensor_type_time 
            ON metrics(sensor_id, metric_type, timestamp);
        """))

        # Create index on timestamp for time-based queries
        await conn.execute(text("""
            CREATE INDEX IF NOT EXISTS idx_metrics_timestamp 
            ON metrics(timestamp);
        """))


async def main():
    """Initialize the database."""
    print("Initializing PostgreSQL database...")
    
    db_config = get_db_config()
    
    try:
        # Create enum types
        print("Creating enum types...")
        await create_enum_types(db_config.engine)
        
        # Create tables
        print("Creating tables...")
        await create_tables(db_config.engine)
        
        # Create indexes
        print("Creating indexes...")
        await create_indexes(db_config.engine)
        
        print("Database initialization completed successfully!")
        
    except Exception as e:
        print(f"Error initializing database: {e}")
        sys.exit(1)
    
    finally:
        await db_config.close()


if __name__ == "__main__":
    asyncio.run(main())
