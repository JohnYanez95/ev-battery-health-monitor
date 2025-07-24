#!/usr/bin/env python3
"""
Initialize the EV Battery Health Monitor database schema.
Creates all tables, indexes, and TimescaleDB configurations.
"""

import os
import sys
import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Database configuration from environment
DB_CONFIG = {
    'host': os.getenv('DB_HOST', 'localhost'),
    'port': os.getenv('DB_PORT', '5432'),
    'database': os.getenv('POSTGRES_DB', 'battery_health'),
    'user': os.getenv('POSTGRES_USER', 'ev_monitor_user'),
    'password': os.getenv('POSTGRES_PASSWORD', 'secure_battery_monitor_2024!')
}

def get_schema_sql():
    """Read the schema SQL file."""
    schema_path = Path(__file__).parent / 'schema.sql'
    with open(schema_path, 'r') as f:
        return f.read()

def init_database():
    """Initialize the database with TimescaleDB schema."""
    conn = None
    cur = None
    
    try:
        # Connect to database
        print(f"Connecting to PostgreSQL at {DB_CONFIG['host']}:{DB_CONFIG['port']}")
        conn = psycopg2.connect(**DB_CONFIG)
        conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
        cur = conn.cursor()
        
        # Check if TimescaleDB is available
        cur.execute("SELECT extname FROM pg_extension WHERE extname = 'timescaledb';")
        if not cur.fetchone():
            print("Creating TimescaleDB extension...")
            cur.execute("CREATE EXTENSION IF NOT EXISTS timescaledb;")
        else:
            print("TimescaleDB extension already exists")
        
        # Execute schema
        print("Creating database schema...")
        schema_sql = get_schema_sql()
        cur.execute(schema_sql)
        
        # Verify hypertable creation
        cur.execute("""
            SELECT hypertable_name 
            FROM timescaledb_information.hypertables 
            WHERE hypertable_name = 'battery_telemetry';
        """)
        if cur.fetchone():
            print("✓ Hypertable 'battery_telemetry' created successfully")
        
        # Check continuous aggregate
        cur.execute("""
            SELECT view_name 
            FROM timescaledb_information.continuous_aggregates 
            WHERE view_name = 'telemetry_hourly';
        """)
        if cur.fetchone():
            print("✓ Continuous aggregate 'telemetry_hourly' created successfully")
        
        # List all created tables
        cur.execute("""
            SELECT tablename 
            FROM pg_tables 
            WHERE schemaname = 'public' 
            AND tablename IN ('battery_telemetry', 'anomaly_events', 'vehicles', 'charging_sessions')
            ORDER BY tablename;
        """)
        tables = cur.fetchall()
        print("\n✓ Created tables:")
        for table in tables:
            print(f"  - {table[0]}")
        
        # Insert sample vehicle for testing
        print("\nInserting sample vehicle data...")
        cur.execute("""
            INSERT INTO vehicles (
                vehicle_id, make, model, year, battery_capacity_kwh,
                nominal_voltage, cell_configuration, chemistry_type
            ) VALUES 
            ('VEH001', 'Tesla', 'Model 3', 2023, 82.0, 350.0, '96s46p', 'NCA'),
            ('VEH002', 'Nissan', 'Leaf', 2023, 62.0, 350.0, '96s2p', 'NMC')
            ON CONFLICT (vehicle_id) DO NOTHING;
        """)
        
        print("\n✅ Database initialization completed successfully!")
        
    except psycopg2.Error as e:
        print(f"\n❌ Database error: {e}")
        if cur:
            cur.execute("ROLLBACK")
        return False
    except Exception as e:
        print(f"\n❌ Error: {e}")
        return False
    finally:
        if cur:
            cur.close()
        if conn:
            conn.close()
    
    return True

def verify_connection():
    """Verify database connection before initialization."""
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        conn.close()
        return True
    except psycopg2.Error as e:
        print(f"❌ Cannot connect to database: {e}")
        print("\nPlease ensure:")
        print("1. Docker Compose is running: docker-compose up -d postgres")
        print("2. Database is ready: docker exec ev-battery-postgres pg_isready")
        print("3. Environment variables are set correctly")
        return False

if __name__ == "__main__":
    print("EV Battery Health Monitor - Database Initialization")
    print("=" * 50)
    
    # Verify connection first
    if not verify_connection():
        sys.exit(1)
    
    # Initialize database
    if init_database():
        print("\nNext steps:")
        print("1. Run the data simulation engine to generate test data")
        print("2. Start the FastAPI backend server")
        print("3. Access the web interface to visualize data")
    else:
        sys.exit(1)