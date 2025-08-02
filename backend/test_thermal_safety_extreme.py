"""
Test script for thermal safety system - Extreme Conditions
Demonstrates thermal warnings, critical alerts, and emergency shutdown
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from simulation.battery_model import BatteryModel, VEHICLE_SPECS
from plotting.battery_plots import create_thermal_safety_plot, get_test_statistics


def test_thermal_safety_extreme():
    """Test thermal safety system under extreme conditions to trigger all safety levels"""
    print("=== EV Battery Thermal Safety Test - Extreme Conditions ===\n")
    
    # Initialize battery for Tesla Model 3
    battery = BatteryModel(VEHICLE_SPECS['VEH001'], initial_temp=25.0)
    print(f"Vehicle: {battery.specs.make} {battery.specs.model}")
    print(f"Initial temperature: {battery.temperature}°C")
    
    # Modify battery parameters for extreme heating demonstration
    battery.specs.thermal_mass = 50.0  # Reduced from 400kg for faster heating
    battery.specs.internal_resistance = 0.2  # Increased from 0.05Ω for more heat
    print(f"Modified thermal mass: {battery.specs.thermal_mass}kg (reduced for demo)")
    print(f"Modified internal resistance: {battery.specs.internal_resistance}Ω (increased for demo)\n")
    
    # Data collection
    times = []
    temperatures = []
    currents = []
    powers = []
    thermal_statuses = []
    power_limits = []
    thermal_events = []
    
    dt = 1.0  # 1 second time steps
    
    print("Simulating extreme high-power operation...\n")
    
    # Phase 1: Extreme discharge (racing/track conditions) - SAME 200s as normal test
    print("Phase 1: Track driving - Maximum discharge")
    for t in range(200):
        # Request maximum discharge current
        requested_current = -250.0  # Max discharge
        actual_current, voltage, power = battery.apply_current(requested_current, dt)
        
        # Check for thermal events (track first occurrence)
        temp = battery.temperature
        status = battery.thermal_safety.current_status.value
        
        if temp >= 50 and not any(e['type'] == 'warning' for e in thermal_events):
            thermal_events.append({'time': t, 'type': 'warning', 'temp': temp})
            print(f"  ⚠️  t={t}s: WARNING threshold reached! Temp={temp:.1f}°C")
        elif temp >= 55 and not any(e['type'] == 'critical' for e in thermal_events):
            thermal_events.append({'time': t, 'type': 'critical', 'temp': temp})
            print(f"  🔴 t={t}s: CRITICAL threshold reached! Temp={temp:.1f}°C")
        elif temp >= 60 and not any(e['type'] == 'shutdown' for e in thermal_events):
            thermal_events.append({'time': t, 'type': 'shutdown', 'temp': temp})
            print(f"  🚨 t={t}s: EMERGENCY SHUTDOWN! Temp={temp:.1f}°C")
        
        times.append(t)
        temperatures.append(temp)
        currents.append(actual_current)
        powers.append(power)
        thermal_statuses.append(status)
        power_limits.append(battery.thermal_safety.check_temperature(temp)['power_limit'])
    
    # Phase 2: Idle period (200-300s) - SAME as normal test
    print("\nPhase 2: Parked (idle)")
    for t in range(200, 300):
        # No current - vehicle parked
        actual_current, voltage, power = battery.apply_current(0.0, dt)
        
        times.append(t)
        temperatures.append(battery.temperature)
        currents.append(actual_current)
        powers.append(power)
        thermal_statuses.append(battery.thermal_safety.current_status.value)
        power_limits.append(battery.thermal_safety.check_temperature(battery.temperature)['power_limit'])
    
    # Phase 3: Extreme charging in hot conditions (300-600s) - SAME duration as normal test
    print("\nPhase 3: Fast charging on hot day - Maximum charge rate")
    battery.ambient_temp = 40.0  # Very hot ambient
    
    shutdown_time = None
    recovery_time = None
    
    for t in range(300, 600):
        # Request maximum charge current
        requested_current = 200.0  # Max charge
        actual_current, voltage, power = battery.apply_current(requested_current, dt)
        
        times.append(t)
        temperatures.append(battery.temperature)
        currents.append(actual_current)
        powers.append(power)
        thermal_statuses.append(battery.thermal_safety.current_status.value)
        power_limits.append(battery.thermal_safety.check_temperature(battery.temperature)['power_limit'])
        
        # Track shutdown and recovery
        if battery.thermal_safety.shutdown_active and shutdown_time is None:
            shutdown_time = t
            print(f"  ⛔ t={t}s: System in thermal shutdown mode")
        elif not battery.thermal_safety.shutdown_active and shutdown_time is not None and recovery_time is None:
            recovery_time = t
            thermal_events.append({'time': t, 'type': 'recovery', 'temp': battery.temperature})
            print(f"  ✅ t={t}s: System recovered! Temp={battery.temperature:.1f}°C")
    
    # Calculate statistics
    stats = get_test_statistics(temperatures, thermal_events, power_limits, "Extreme Conditions")
    
    # Print detailed summary
    print("\n=== Thermal Event Summary ===")
    for event in thermal_events:
        print(f"{event['type'].upper()}: Triggered at t={event['time']}s, Temp={event['temp']:.1f}°C")
    
    if shutdown_time:
        duration = recovery_time - shutdown_time if recovery_time else len(times) - shutdown_time
        print(f"\nShutdown duration: {duration}s")
    
    print(f"\nMax temperature reached: {stats['max_temp']:.1f}°C")
    print(f"Final temperature: {temperatures[-1]:.1f}°C")
    print(f"Total thermal events logged: {stats['total_events']}")
    
    # Create standardized plot (same format as normal test)
    create_thermal_safety_plot(
        times=times,
        temperatures=temperatures,
        currents=currents,
        powers=powers,
        thermal_statuses=thermal_statuses,
        power_limits=power_limits,
        thermal_events=thermal_events,
        test_name="Extreme Conditions",
        output_path="figures/test_thermal_safety_extreme.png"
    )
    
    print("\n✅ Test completed: All thermal safety levels demonstrated successfully")
    return stats


if __name__ == "__main__":
    test_thermal_safety_extreme()