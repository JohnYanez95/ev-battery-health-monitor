#!/usr/bin/env python3
"""
Debug script to analyze charging behavior in user profile simulations.
Helps identify why profiles aren't triggering charging sessions properly.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from simulation.simulator import run_simulation
from simulation.user_profiles import UserProfile
import pandas as pd


def debug_charging_behavior():
    """Debug why charging isn't being triggered in simulations."""
    
    print("🔍 EV Battery Simulation - Charging Behavior Debug")
    print("=" * 70)
    
    # Test with CAUTIOUS profile (should charge most frequently)
    profile = UserProfile.CAUTIOUS
    
    print(f"\nRunning debug simulation for {profile.value} driver...")
    print("(This profile should maintain >50% SoC and charge frequently)")
    
    telemetry_df, events_df = run_simulation(
        vehicle_id='VEH001',
        days=1,
        user_profile=profile,
        include_anomalies=False,
        save_to_db=False,
        seed=42
    )
    
    print("\n📊 Simulation Summary:")
    print(f"Total records: {len(telemetry_df):,}")
    print(f"Time span: {telemetry_df.index[0]} to {telemetry_df.index[-1]}")
    
    print("\n🔋 State of Charge Analysis:")
    print(f"Initial SoC: {telemetry_df['soc_percent'].iloc[0]:.1f}%")
    print(f"Final SoC: {telemetry_df['soc_percent'].iloc[-1]:.1f}%")
    print(f"Minimum SoC: {telemetry_df['soc_percent'].min():.1f}%")
    print(f"Maximum SoC: {telemetry_df['soc_percent'].max():.1f}%")
    print(f"Average SoC: {telemetry_df['soc_percent'].mean():.1f}%")
    
    print("\n⚡ Activity Summary:")
    charging_hours = telemetry_df['is_charging'].sum() / 3600
    driving_hours = telemetry_df['is_driving'].sum() / 3600
    idle_hours = (~telemetry_df['is_charging'] & ~telemetry_df['is_driving']).sum() / 3600
    
    print(f"Charging: {charging_hours:.1f} hours ({charging_hours/24*100:.1f}% of day)")
    print(f"Driving: {driving_hours:.1f} hours ({driving_hours/24*100:.1f}% of day)")
    print(f"Idle: {idle_hours:.1f} hours ({idle_hours/24*100:.1f}% of day)")
    
    # Analyze charging sessions
    print("\n🔌 Charging Session Analysis:")
    charging_mask = telemetry_df['is_charging']
    
    if charging_mask.any():
        # Find charging session starts
        charging_starts = telemetry_df[charging_mask & ~charging_mask.shift(1).fillna(False)]
        charging_ends = telemetry_df[~charging_mask & charging_mask.shift(1).fillna(False)]
        
        print(f"Number of charging sessions: {len(charging_starts)}")
        print("\nCharging session details:")
        
        for i, (start_idx, start_row) in enumerate(charging_starts.iterrows()):
            # Find corresponding end
            end_candidates = charging_ends[charging_ends.index > start_idx]
            if not end_candidates.empty:
                end_idx = end_candidates.index[0]
                duration = (end_idx - start_idx).total_seconds() / 3600
                soc_gained = telemetry_df.loc[end_idx, 'soc_percent'] - start_row['soc_percent']
                
                print(f"\nSession {i+1}:")
                print(f"  Start: {start_idx.strftime('%H:%M')} (SoC: {start_row['soc_percent']:.1f}%)")
                print(f"  End: {end_idx.strftime('%H:%M')} (SoC: {telemetry_df.loc[end_idx, 'soc_percent']:.1f}%)")
                print(f"  Duration: {duration:.1f} hours")
                print(f"  SoC gained: {soc_gained:.1f}%")
                print(f"  Charger type: {start_row.get('charger_type', 'Unknown')}")
    else:
        print("❌ No charging sessions found!")
        
        # Check why charging might not be triggered
        print("\n🔍 Investigating why charging isn't triggered:")
        
        # Check if SoC ever drops below charging threshold
        cautious_threshold = 50  # Cautious drivers should charge below 50%
        below_threshold = telemetry_df['soc_percent'] < cautious_threshold
        print(f"Time spent below {cautious_threshold}% SoC: {below_threshold.sum() / 3600:.1f} hours")
        
        # Find when SoC first drops below threshold
        if below_threshold.any():
            first_below_idx = telemetry_df[below_threshold].index[0]
            time_str = f"{first_below_idx // 3600:02d}:{(first_below_idx % 3600) // 60:02d}"
            print(f"First dropped below {cautious_threshold}% at: {time_str}")
    
    # SoC timeline
    print("\n📈 SoC Timeline (hourly snapshots):")
    print("Hour | SoC % | Activity")
    print("-" * 40)
    
    for hour in range(0, 24, 2):
        idx = hour * 3600
        if idx < len(telemetry_df):
            row = telemetry_df.iloc[idx]
            activity = "Charging" if row['is_charging'] else ("Driving" if row['is_driving'] else "Idle")
            print(f"{hour:4d} | {row['soc_percent']:5.1f} | {activity}")
    
    # Check vehicle state transitions
    print("\n🚗 State Transitions:")
    state_changes = []
    prev_state = None
    
    for idx, row in telemetry_df.iterrows():
        current_state = "charging" if row['is_charging'] else ("driving" if row['is_driving'] else "idle")
        if current_state != prev_state:
            state_changes.append((idx, current_state, row['soc_percent']))
            prev_state = current_state
    
    print(f"Total state changes: {len(state_changes)}")
    print("\nFirst 10 state changes:")
    for i, (time, state, soc) in enumerate(state_changes[:10]):
        print(f"{time.strftime('%H:%M:%S')} -> {state:8s} (SoC: {soc:5.1f}%)")
    
    # Energy analysis
    print("\n⚡ Energy Flow Analysis:")
    total_energy_out = -telemetry_df[telemetry_df['current'] < 0]['current'].sum() / 3600  # Ah
    total_energy_in = telemetry_df[telemetry_df['current'] > 0]['current'].sum() / 3600  # Ah
    
    print(f"Energy consumed (driving): {total_energy_out:.1f} Ah")
    print(f"Energy charged: {total_energy_in:.1f} Ah")
    print(f"Net energy balance: {total_energy_in - total_energy_out:.1f} Ah")
    
    # Save debug data
    debug_file = "debug_charging_data.csv"
    sample_df = telemetry_df[['soc_percent', 'voltage', 'current', 'temperature', 
                              'is_charging', 'is_driving', 'speed_kmh']].head(1000)
    sample_df.to_csv(debug_file)
    print(f"\n💾 Saved first 1000 records to {debug_file} for inspection")


if __name__ == "__main__":
    debug_charging_behavior()