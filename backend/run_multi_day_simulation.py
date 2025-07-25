#!/usr/bin/env python3
"""
Run a multi-day, multi-vehicle simulation to see realistic patterns.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from simulation.simulator import run_simulation
from database.connection import execute_query
import pandas as pd


def analyze_simulation_results():
    """Analyze the simulation results to verify realistic behavior."""
    
    # Query SoC statistics
    soc_stats = execute_query("""
        SELECT 
            vehicle_id,
            DATE(time) as day,
            MIN(soc_percent) as min_soc,
            MAX(soc_percent) as max_soc,
            AVG(soc_percent) as avg_soc,
            COUNT(*) as data_points
        FROM battery_telemetry
        WHERE time >= NOW() - INTERVAL '7 days'
        GROUP BY vehicle_id, DATE(time)
        ORDER BY vehicle_id, day
    """)
    
    print("\n📊 Daily SoC Statistics by Vehicle:")
    print("-" * 70)
    for stat in soc_stats:
        print(f"{stat['vehicle_id']} | {stat['day']} | "
              f"Min: {stat['min_soc']:.1f}% | Max: {stat['max_soc']:.1f}% | "
              f"Avg: {stat['avg_soc']:.1f}%")
    
    # Query charging sessions
    charging_sessions = execute_query("""
        SELECT 
            vehicle_id,
            DATE(time) as day,
            COUNT(DISTINCT CASE WHEN is_charging THEN DATE_TRUNC('hour', time) END) as charging_hours,
            SUM(CASE WHEN is_charging AND current > 0 THEN current * 1.0 / 3600 ELSE 0 END) as total_charge_ah
        FROM battery_telemetry
        WHERE time >= NOW() - INTERVAL '7 days'
        GROUP BY vehicle_id, DATE(time)
        ORDER BY vehicle_id, day
    """)
    
    print("\n🔌 Charging Activity by Vehicle:")
    print("-" * 70)
    for session in charging_sessions:
        print(f"{session['vehicle_id']} | {session['day']} | "
              f"Charging hours: {session['charging_hours'] or 0} | "
              f"Total charge: {session['total_charge_ah'] or 0:.1f} Ah")
    
    # Query anomalies
    anomalies = execute_query("""
        SELECT 
            vehicle_id,
            event_type,
            severity,
            COUNT(*) as count
        FROM anomaly_events
        WHERE start_time >= NOW() - INTERVAL '7 days'
        GROUP BY vehicle_id, event_type, severity
        ORDER BY vehicle_id, count DESC
    """)
    
    if anomalies:
        print("\n⚠️ Anomalies Generated:")
        print("-" * 50)
        for anomaly in anomalies:
            print(f"{anomaly['vehicle_id']} | {anomaly['event_type']} | "
                  f"{anomaly['severity']} | Count: {anomaly['count']}")


def main():
    print("🚗 Running 7-day simulation for both vehicles...")
    print("=" * 70)
    
    # Clear previous data
    print("\nClearing previous simulation data...")
    execute_query("DELETE FROM anomaly_events WHERE vehicle_id IN ('VEH001', 'VEH002')")
    execute_query("DELETE FROM battery_telemetry WHERE vehicle_id IN ('VEH001', 'VEH002')")
    
    # Run simulation for both vehicles
    for vehicle_id in ['VEH001', 'VEH002']:
        print(f"\n🔋 Simulating {vehicle_id}...")
        telemetry_df, events_df = run_simulation(
            vehicle_id=vehicle_id,
            days=7,
            include_anomalies=True,
            save_to_db=True,
            seed=None  # Random seed for variety
        )
    
    # Analyze results
    analyze_simulation_results()
    
    # Additional analysis
    print("\n📈 Additional Insights:")
    
    # Check if any vehicle hit 0% SoC
    zero_soc = execute_query("""
        SELECT vehicle_id, COUNT(*) as occurrences
        FROM battery_telemetry
        WHERE soc_percent <= 1.0
        AND time >= NOW() - INTERVAL '7 days'
        GROUP BY vehicle_id
    """)
    
    if zero_soc:
        print("\n❗ Vehicles that hit critically low SoC (<1%):")
        for v in zero_soc:
            print(f"  - {v['vehicle_id']}: {v['occurrences']} times")
    else:
        print("\n✅ No vehicles hit critically low SoC")
    
    # Check charging patterns
    print("\n🔋 Battery Usage Patterns:")
    usage = execute_query("""
        SELECT 
            vehicle_id,
            SUM(CASE WHEN current < 0 THEN ABS(current) * 1.0/3600 ELSE 0 END) as total_discharge_ah,
            SUM(CASE WHEN current > 0 THEN current * 1.0/3600 ELSE 0 END) as total_charge_ah,
            AVG(temperature) as avg_temp,
            MAX(temperature) as max_temp
        FROM battery_telemetry
        WHERE time >= NOW() - INTERVAL '7 days'
        GROUP BY vehicle_id
    """)
    
    for u in usage:
        efficiency = (u['total_charge_ah'] / u['total_discharge_ah'] * 100) if u['total_discharge_ah'] > 0 else 0
        print(f"\n{u['vehicle_id']}:")
        print(f"  - Total discharged: {u['total_discharge_ah']:.1f} Ah")
        print(f"  - Total charged: {u['total_charge_ah']:.1f} Ah")
        print(f"  - Charging efficiency: {efficiency:.1f}%")
        print(f"  - Avg temperature: {u['avg_temp']:.1f}°C (Max: {u['max_temp']:.1f}°C)")


if __name__ == "__main__":
    main()