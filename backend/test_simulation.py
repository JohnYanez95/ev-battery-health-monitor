#!/usr/bin/env python3
"""
Test script for EV battery simulation.
Runs a short simulation and verifies data is correctly inserted into TimescaleDB.
"""

import sys
import os
from datetime import datetime, timedelta

# Add backend to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from simulation.simulator import EVBatterySimulator, run_simulation
from database.connection import execute_query


def test_simulation():
    """Run a test simulation and verify results."""
    print("EV Battery Health Monitor - Simulation Test")
    print("=" * 50)
    
    # Test parameters
    vehicle_id = 'VEH001'  # Tesla Model 3
    days = 1  # Just one day for testing
    
    print(f"\nRunning {days}-day simulation for {vehicle_id}...")
    
    try:
        # Run simulation
        telemetry_df, events_df = run_simulation(
            vehicle_id=vehicle_id,
            days=days,
            include_anomalies=True,
            save_to_db=True,
            seed=42  # For reproducibility
        )
        
        # Verify data in database
        print("\nVerifying database insertion...")
        
        # Check telemetry data
        telemetry_count = execute_query(
            "SELECT COUNT(*) as count FROM battery_telemetry WHERE vehicle_id = %s",
            (vehicle_id,)
        )
        db_count = telemetry_count[0]['count'] if telemetry_count else 0
        print(f"✓ Telemetry records in database: {db_count}")
        
        # Check latest data
        latest_data = execute_query(
            """
            SELECT time, soc_percent, voltage, current, temperature
            FROM battery_telemetry
            WHERE vehicle_id = %s
            ORDER BY time DESC
            LIMIT 5
            """,
            (vehicle_id,)
        )
        
        if latest_data:
            print("\n✓ Latest telemetry samples:")
            for record in latest_data:
                print(f"  {record['time']}: SoC={record['soc_percent']:.1f}%, "
                      f"V={record['voltage']:.1f}V, I={record['current']:.1f}A, "
                      f"T={record['temperature']:.1f}°C")
        
        # Check anomaly events
        anomaly_count = execute_query(
            "SELECT COUNT(*) as count FROM anomaly_events WHERE vehicle_id = %s",
            (vehicle_id,)
        )
        anomaly_db_count = anomaly_count[0]['count'] if anomaly_count else 0
        print(f"\n✓ Anomaly events in database: {anomaly_db_count}")
        
        if anomaly_db_count > 0:
            anomalies = execute_query(
                """
                SELECT event_type, severity, start_time, end_time
                FROM anomaly_events
                WHERE vehicle_id = %s
                ORDER BY start_time DESC
                LIMIT 5
                """,
                (vehicle_id,)
            )
            print("\n✓ Recent anomaly events:")
            for anomaly in anomalies:
                duration = (anomaly['end_time'] - anomaly['start_time']).total_seconds()
                print(f"  {anomaly['event_type']} ({anomaly['severity']}): "
                      f"{anomaly['start_time']} - Duration: {duration}s")
        
        # Check continuous aggregate
        hourly_data = execute_query(
            """
            SELECT hour, avg_soc, avg_temp, charging_count, driving_count
            FROM telemetry_hourly
            WHERE vehicle_id = %s
            ORDER BY hour DESC
            LIMIT 5
            """,
            (vehicle_id,)
        )
        
        if hourly_data:
            print("\n✓ Hourly aggregates working:")
            for hour in hourly_data:
                print(f"  {hour['hour']}: Avg SoC={hour['avg_soc']:.1f}%, "
                      f"Avg Temp={hour['avg_temp']:.1f}°C")
        
        # Test current vehicle status view
        status = execute_query(
            "SELECT * FROM vehicle_current_status WHERE vehicle_id = %s",
            (vehicle_id,)
        )
        
        if status:
            vehicle = status[0]
            print(f"\n✓ Current vehicle status:")
            print(f"  Vehicle: {vehicle['make']} {vehicle['model']}")
            print(f"  Status: {vehicle['status']}")
            print(f"  SoC: {vehicle['soc_percent']:.1f}%")
            print(f"  Temperature: {vehicle['temperature']:.1f}°C")
            print(f"  Range: {vehicle['estimated_range_km']:.1f} km")
        
        print("\n✅ Simulation test completed successfully!")
        
        # Print some statistics
        print("\nSimulation Statistics:")
        print(f"- Total telemetry points: {len(telemetry_df)}")
        print(f"- Data frequency: {len(telemetry_df) / (days * 24 * 3600):.1f} Hz")
        print(f"- SoC range: {telemetry_df['soc_percent'].min():.1f}% - {telemetry_df['soc_percent'].max():.1f}%")
        print(f"- Temperature range: {telemetry_df['temperature'].min():.1f}°C - {telemetry_df['temperature'].max():.1f}°C")
        print(f"- Total energy used: {telemetry_df[telemetry_df['current'] < 0]['current'].sum() * -1 / 3600:.1f} Ah")
        
        return True
        
    except Exception as e:
        print(f"\n❌ Error during simulation test: {e}")
        import traceback
        traceback.print_exc()
        return False


def cleanup_test_data(vehicle_id: str):
    """Clean up test data from database."""
    print(f"\nCleaning up test data for {vehicle_id}...")
    
    # Delete in reverse order of foreign keys
    execute_query("DELETE FROM anomaly_events WHERE vehicle_id = %s", (vehicle_id,))
    execute_query("DELETE FROM battery_telemetry WHERE vehicle_id = %s", (vehicle_id,))
    
    print("✓ Test data cleaned up")


if __name__ == "__main__":
    # Check if database is running
    try:
        result = execute_query("SELECT 1")
        print("✓ Database connection successful")
    except Exception as e:
        print(f"❌ Cannot connect to database: {e}")
        print("\nPlease ensure:")
        print("1. Docker is running: docker-compose up -d postgres")
        print("2. Database is initialized: python backend/database/init_db.py")
        sys.exit(1)
    
    # Run test
    success = test_simulation()
    
    # Optional: cleanup test data
    # cleanup_test_data('VEH001')
    
    sys.exit(0 if success else 1)