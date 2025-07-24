"""
Database connection management for EV Battery Health Monitor.
Uses connection pooling for efficient database access.
"""

import os
from contextlib import contextmanager
from typing import Optional
import psycopg2
from psycopg2 import pool
from psycopg2.extras import RealDictCursor
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class DatabasePool:
    """Manages PostgreSQL connection pool for the application."""
    
    def __init__(self):
        self.pool: Optional[psycopg2.pool.ThreadedConnectionPool] = None
        self._init_pool()
    
    def _init_pool(self):
        """Initialize the connection pool."""
        try:
            self.pool = psycopg2.pool.ThreadedConnectionPool(
                minconn=2,
                maxconn=20,
                host=os.getenv('DB_HOST', 'localhost'),
                port=os.getenv('DB_PORT', '5432'),
                database=os.getenv('POSTGRES_DB', 'battery_health'),
                user=os.getenv('POSTGRES_USER', 'ev_monitor_user'),
                password=os.getenv('POSTGRES_PASSWORD', 'secure_battery_monitor_2024!')
            )
            print("Database connection pool initialized successfully")
        except psycopg2.Error as e:
            print(f"Error initializing database pool: {e}")
            raise
    
    @contextmanager
    def get_connection(self):
        """Get a connection from the pool."""
        connection = None
        try:
            connection = self.pool.getconn()
            yield connection
        finally:
            if connection:
                self.pool.putconn(connection)
    
    @contextmanager
    def get_cursor(self, cursor_factory=RealDictCursor):
        """Get a cursor with automatic connection management."""
        with self.get_connection() as connection:
            cursor = connection.cursor(cursor_factory=cursor_factory)
            try:
                yield cursor
                connection.commit()
            except Exception:
                connection.rollback()
                raise
            finally:
                cursor.close()
    
    def close(self):
        """Close all connections in the pool."""
        if self.pool:
            self.pool.closeall()

# Global database pool instance
db_pool = DatabasePool()

def get_db_cursor():
    """Get a database cursor for use in FastAPI dependency injection."""
    return db_pool.get_cursor()

def execute_query(query: str, params: tuple = None):
    """Execute a query and return results."""
    with db_pool.get_cursor() as cursor:
        cursor.execute(query, params)
        if cursor.description:
            return cursor.fetchall()
        return None

def execute_many(query: str, data: list):
    """Execute a query with multiple parameter sets (bulk insert)."""
    with db_pool.get_cursor() as cursor:
        cursor.executemany(query, data)
        return cursor.rowcount

def insert_telemetry_batch(telemetry_data: list):
    """
    Efficiently insert a batch of telemetry data.
    
    Args:
        telemetry_data: List of dicts with telemetry fields
    """
    insert_query = """
        INSERT INTO battery_telemetry (
            time, vehicle_id, soc_percent, voltage, current, temperature,
            energy_kwh, soh_percent, max_cell_temp, min_cell_temp, ambient_temp,
            is_charging, is_driving, speed_kmh, location_lat, location_lon,
            estimated_range_km, data_quality
        ) VALUES (
            %(time)s, %(vehicle_id)s, %(soc_percent)s, %(voltage)s, %(current)s, 
            %(temperature)s, %(energy_kwh)s, %(soh_percent)s, %(max_cell_temp)s, 
            %(min_cell_temp)s, %(ambient_temp)s, %(is_charging)s, %(is_driving)s, 
            %(speed_kmh)s, %(location_lat)s, %(location_lon)s, %(estimated_range_km)s, 
            %(data_quality)s
        )
        ON CONFLICT (vehicle_id, time) DO NOTHING;
    """
    
    with db_pool.get_cursor() as cursor:
        cursor.executemany(insert_query, telemetry_data)
        return cursor.rowcount