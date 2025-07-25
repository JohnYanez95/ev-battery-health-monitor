#!/usr/bin/env python3
"""
Test user profiles to demonstrate how different behaviors affect battery usage.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from simulation.simulator import run_simulation
from simulation.user_profiles import UserProfile
from database.connection import execute_query


def test_user_profiles():
    """Run simulations with different user profiles to show behavioral differences."""
    
    print("🚗 EV Battery Simulation - User Profile Comparison")
    print("=" * 70)
    
    # Clear previous test data
    print("\nClearing previous test data...")
    execute_query("DELETE FROM anomaly_events WHERE vehicle_id = 'VEH001'")
    execute_query("DELETE FROM battery_telemetry WHERE vehicle_id = 'VEH001'")
    
    # Test profiles with same vehicle for comparison
    profiles_to_test = [
        UserProfile.CAUTIOUS,
        UserProfile.SPONTANEOUS,
        UserProfile.ECO_CONSCIOUS,
        UserProfile.PERFORMANCE_ENTHUSIAST
    ]
    
    results = {}
    
    for profile in profiles_to_test:
        print(f"\n📊 Simulating {profile.value} driver...")
        
        # Run 1-day simulation
        telemetry_df, events_df = run_simulation(
            vehicle_id='VEH001',  # Tesla Model 3
            days=1,
            user_profile=profile,
            include_anomalies=False,  # No anomalies for cleaner comparison
            save_to_db=False,  # Don't save for this test
            seed=42  # Same seed for fair comparison
        )
        
        # Calculate statistics
        charging_hours = telemetry_df['is_charging'].sum() / 3600
        driving_hours = telemetry_df['is_driving'].sum() / 3600
        total_distance = telemetry_df[telemetry_df['is_driving']]['speed_kmh'].sum() / 3600
        avg_speed = telemetry_df[telemetry_df['is_driving']]['speed_kmh'].mean() if driving_hours > 0 else 0
        energy_consumed = -telemetry_df[telemetry_df['current'] < 0]['current'].sum() / 3600  # Ah
        
        results[profile] = {
            'min_soc': telemetry_df['soc_percent'].min(),
            'avg_soc': telemetry_df['soc_percent'].mean(),
            'final_soc': telemetry_df['soc_percent'].iloc[-1],
            'charging_hours': charging_hours,
            'driving_hours': driving_hours,
            'total_distance': total_distance,
            'avg_speed': avg_speed,
            'energy_consumed': energy_consumed,
            'max_temp': telemetry_df['temperature'].max()
        }
    
    # Display comparison
    print("\n📈 User Profile Comparison (1-day simulation):")
    print("-" * 90)
    print(f"{'Profile':<20} {'Min SoC':<10} {'Avg SoC':<10} {'Final SoC':<10} {'Charging':<10} {'Driving':<10} {'Distance':<10}")
    print(f"{'':20} {'(%)':10} {'(%)':10} {'(%)':10} {'(hours)':10} {'(hours)':10} {'(km)':10}")
    print("-" * 90)
    
    for profile, stats in results.items():
        print(f"{profile.value:<20} {stats['min_soc']:>9.1f} {stats['avg_soc']:>9.1f} "
              f"{stats['final_soc']:>9.1f} {stats['charging_hours']:>9.1f} "
              f"{stats['driving_hours']:>9.1f} {stats['total_distance']:>9.1f}")
    
    print("\n🔋 Energy Usage Analysis:")
    print("-" * 70)
    for profile, stats in results.items():
        efficiency = stats['total_distance'] / stats['energy_consumed'] if stats['energy_consumed'] > 0 else 0
        print(f"{profile.value:<20}: {stats['energy_consumed']:>6.1f} Ah consumed, "
              f"{efficiency:>4.2f} km/Ah efficiency")
    
    print("\n🌡️ Thermal Behavior:")
    print("-" * 50)
    for profile, stats in results.items():
        print(f"{profile.value:<20}: Max temp {stats['max_temp']:>5.1f}°C")
    
    # Behavioral insights
    print("\n💡 Behavioral Insights:")
    print("-" * 70)
    
    # Find extremes
    most_cautious = min(results.items(), key=lambda x: x[1]['min_soc'])
    most_risky = min(results.items(), key=lambda x: x[1]['min_soc'])
    most_efficient = max(results.items(), key=lambda x: x[1]['total_distance'] / x[1]['energy_consumed'] if x[1]['energy_consumed'] > 0 else 0)
    
    print(f"• CAUTIOUS drivers maintain {results[UserProfile.CAUTIOUS]['min_soc']:.1f}% minimum SoC")
    print(f"• SPONTANEOUS drivers let SoC drop to {results[UserProfile.SPONTANEOUS]['min_soc']:.1f}%")
    print(f"• ECO_CONSCIOUS drivers achieve {results[UserProfile.ECO_CONSCIOUS]['total_distance'] / results[UserProfile.ECO_CONSCIOUS]['energy_consumed']:.2f} km/Ah efficiency")
    print(f"• PERFORMANCE drivers use {results[UserProfile.PERFORMANCE_ENTHUSIAST]['energy_consumed']:.1f} Ah in a day")
    
    # Charging behavior
    print("\n🔌 Charging Patterns:")
    for profile in [UserProfile.CAUTIOUS, UserProfile.SPONTANEOUS]:
        print(f"• {profile.value}: {results[profile]['charging_hours']:.1f} hours charging, "
              f"final SoC {results[profile]['final_soc']:.1f}%")


if __name__ == "__main__":
    test_user_profiles()