#!/usr/bin/env python3
"""Quick test to verify V2 simulator fixes."""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from simulation.simulator_v2 import run_simulation_v2
from simulation.user_profiles import UserProfile

# Quick test
print("Testing V2 simulator fix...")
try:
    telemetry_df, events_df = run_simulation_v2(
        vehicle_id='VEH001',
        days=1,
        user_profile=UserProfile.CAUTIOUS,
        include_anomalies=False,
        save_to_db=False,
        seed=42
    )
    print("✅ V2 simulator working!")
    print(f"Generated {len(telemetry_df)} records")
    print(f"SoC range: {telemetry_df['soc_percent'].min():.1f}% - {telemetry_df['soc_percent'].max():.1f}%")
    print(f"Charging hours: {telemetry_df['is_charging'].sum() / 3600:.1f}")
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()