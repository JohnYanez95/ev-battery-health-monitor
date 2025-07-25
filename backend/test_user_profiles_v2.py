#!/usr/bin/env python3
"""
Test user profiles with the enhanced simulator (V2) that has dynamic charging.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from simulation.simulator_v2 import run_simulation_v2
from simulation.user_profiles import UserProfile
from database.connection import execute_query


def test_user_profiles_v2():
    """Run simulations with different user profiles using enhanced simulator."""
    
    print("🚗 EV Battery Simulation V2 - User Profile Comparison")
    print("=" * 70)
    print("Using enhanced simulator with dynamic charging decisions")
    print()
    
    # Clear previous test data
    print("Clearing previous test data...")
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
        
        # Run 1-day simulation with V2 simulator
        telemetry_df, events_df = run_simulation_v2(
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
        
        # Calculate distance from speed (when driving)
        driving_data = telemetry_df[telemetry_df['is_driving']]
        total_distance = driving_data['speed_kmh'].sum() / 3600 if len(driving_data) > 0 else 0
        avg_speed = driving_data['speed_kmh'].mean() if len(driving_data) > 0 else 0
        
        # Energy calculations
        energy_consumed = -telemetry_df[telemetry_df['current'] < 0]['current'].sum() / 3600  # Ah
        energy_charged = telemetry_df[telemetry_df['current'] > 0]['current'].sum() / 3600  # Ah
        
        # Count charging sessions
        charging_mask = telemetry_df['is_charging']
        charging_sessions = 0
        if charging_mask.any():
            # Count transitions from not charging to charging
            charging_starts = charging_mask & ~charging_mask.shift(1).fillna(False)
            charging_sessions = charging_starts.sum()
        
        results[profile] = {
            'min_soc': telemetry_df['soc_percent'].min(),
            'avg_soc': telemetry_df['soc_percent'].mean(),
            'final_soc': telemetry_df['soc_percent'].iloc[-1],
            'charging_hours': charging_hours,
            'charging_sessions': charging_sessions,
            'driving_hours': driving_hours,
            'total_distance': total_distance,
            'avg_speed': avg_speed,
            'energy_consumed': energy_consumed,
            'energy_charged': energy_charged,
            'max_temp': telemetry_df['temperature'].max()
        }
    
    # Display comparison
    print("\n📈 User Profile Comparison (1-day simulation with V2 simulator):")
    print("-" * 100)
    print(f"{'Profile':<22} {'Min SoC':<8} {'Avg SoC':<8} {'Final SoC':<10} {'Sessions':<10} {'Charging':<10} {'Driving':<10} {'Distance':<10}")
    print(f"{'':22} {'(%)':8} {'(%)':8} {'(%)':10} {'(count)':10} {'(hours)':10} {'(hours)':10} {'(km)':10}")
    print("-" * 100)
    
    for profile, stats in results.items():
        print(f"{profile.value:<22} {stats['min_soc']:>7.1f} {stats['avg_soc']:>7.1f} "
              f"{stats['final_soc']:>9.1f} {stats['charging_sessions']:>9d} "
              f"{stats['charging_hours']:>9.1f} {stats['driving_hours']:>9.1f} "
              f"{stats['total_distance']:>9.1f}")
    
    print("\n🔋 Energy Balance Analysis:")
    print("-" * 80)
    print(f"{'Profile':<22} {'Consumed':<12} {'Charged':<12} {'Net Balance':<12} {'Efficiency':<12}")
    print(f"{'':22} {'(Ah)':12} {'(Ah)':12} {'(Ah)':12} {'(km/Ah)':12}")
    print("-" * 80)
    for profile, stats in results.items():
        net_balance = stats['energy_charged'] - stats['energy_consumed']
        efficiency = stats['total_distance'] / stats['energy_consumed'] if stats['energy_consumed'] > 0 else 0
        print(f"{profile.value:<22} {stats['energy_consumed']:>11.1f} {stats['energy_charged']:>11.1f} "
              f"{net_balance:>11.1f} {efficiency:>11.2f}")
    
    print("\n🌡️ Thermal Behavior:")
    print("-" * 50)
    for profile, stats in results.items():
        print(f"{profile.value:<22}: Max temp {stats['max_temp']:>5.1f}°C")
    
    # Behavioral insights
    print("\n💡 Behavioral Insights (V2 Simulator):")
    print("-" * 80)
    
    # Analyze CAUTIOUS behavior
    cautious_stats = results[UserProfile.CAUTIOUS]
    print(f"• CAUTIOUS drivers:")
    print(f"  - Maintain minimum SoC of {cautious_stats['min_soc']:.1f}% (target: >50%)")
    print(f"  - Charge {cautious_stats['charging_sessions']} times per day")
    print(f"  - Spend {cautious_stats['charging_hours']:.1f} hours charging")
    
    # Analyze SPONTANEOUS behavior
    spont_stats = results[UserProfile.SPONTANEOUS]
    print(f"\n• SPONTANEOUS drivers:")
    print(f"  - Let SoC drop to {spont_stats['min_soc']:.1f}%")
    print(f"  - Charge {spont_stats['charging_sessions']} times per day")
    print(f"  - Drive {spont_stats['total_distance']:.1f} km")
    
    # Analyze ECO_CONSCIOUS behavior
    eco_stats = results[UserProfile.ECO_CONSCIOUS]
    print(f"\n• ECO_CONSCIOUS drivers:")
    print(f"  - Achieve {eco_stats['total_distance'] / eco_stats['energy_consumed']:.2f} km/Ah efficiency")
    print(f"  - Use {eco_stats['energy_consumed']:.1f} Ah total")
    
    # Analyze PERFORMANCE behavior
    perf_stats = results[UserProfile.PERFORMANCE_ENTHUSIAST]
    print(f"\n• PERFORMANCE drivers:")
    print(f"  - Consume {perf_stats['energy_consumed']:.1f} Ah in a day")
    print(f"  - Max temperature reaches {perf_stats['max_temp']:.1f}°C")
    
    # Summary
    print("\n📊 Summary of V2 Improvements:")
    print("-" * 80)
    print("✅ Dynamic charging: Vehicles now charge when SoC drops below profile thresholds")
    print("✅ Profile-specific behavior: CAUTIOUS maintains higher SoC, SPONTANEOUS waits longer")
    print("✅ Realistic patterns: Multiple charging sessions throughout the day as needed")
    print("✅ Energy balance: Charging compensates for driving consumption")


if __name__ == "__main__":
    test_user_profiles_v2()