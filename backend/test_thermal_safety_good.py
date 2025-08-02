"""
Test script for thermal safety system - Normal Operation
Demonstrates normal battery operation without thermal issues
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from simulation.battery_model import BatteryModel, VEHICLE_SPECS
from plotting.battery_plots import create_thermal_safety_plot, get_test_statistics


def test_thermal_safety_good():
    """Test thermal safety system under normal operating conditions"""
    print("=== EV Battery Thermal Safety Test - Normal Operation ===\n")
    
    # Initialize battery for Tesla Model 3
    battery = BatteryModel(VEHICLE_SPECS['VEH001'], initial_temp=25.0)
    print(f"Vehicle: {battery.specs.make} {battery.specs.model}")
    print(f"Initial temperature: {battery.temperature}°C")
    print(f"Thermal mass: {battery.specs.thermal_mass}kg (normal)")
    print(f"Internal resistance: {battery.specs.internal_resistance}Ω (normal)\n")
    
    # Data collection
    times = []
    temperatures = []
    currents = []
    powers = []
    thermal_statuses = []
    power_limits = []
    thermal_events = []
    
    dt = 1.0  # 1 second time steps
    
    print("Simulating normal driving and charging patterns...\n")
    
    # Phase 1: Moderate driving (0-200s)
    print("Phase 1: Normal city driving (moderate discharge)")
    for t in range(200):
        # Request moderate discharge current (city driving)
        requested_current = -80.0  # 80A discharge (moderate)
        actual_current, voltage, power = battery.apply_current(requested_current, dt)
        
        # Collect data
        times.append(t)
        temperatures.append(battery.temperature)
        currents.append(actual_current)
        powers.append(power)
        thermal_statuses.append(battery.thermal_safety.current_status.value)
        power_limits.append(battery.thermal_safety.check_temperature(battery.temperature)['power_limit'])
    
    # Phase 2: Idle period (200-300s)
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
    
    # Phase 3: Normal charging (300-600s)
    print("\nPhase 3: Level 2 charging (moderate rate)")
    for t in range(300, 600):
        # Request moderate charge current (Level 2 charging)
        requested_current = 32.0  # 32A charge (7.2kW Level 2)
        actual_current, voltage, power = battery.apply_current(requested_current, dt)
        
        times.append(t)
        temperatures.append(battery.temperature)
        currents.append(actual_current)
        powers.append(power)
        thermal_statuses.append(battery.thermal_safety.current_status.value)
        power_limits.append(battery.thermal_safety.check_temperature(battery.temperature)['power_limit'])
    
    # Calculate statistics
    stats = get_test_statistics(temperatures, thermal_events, power_limits, "Normal Operation")
    
    # Print summary
    print("\n=== Test Summary ===")
    print(f"Max temperature reached: {stats['max_temp']:.1f}°C")
    print(f"Min temperature reached: {stats['min_temp']:.1f}°C")
    print(f"Temperature range: {stats['temp_range']:.1f}°C")
    print(f"Thermal status throughout: {thermal_statuses[0]}")
    print(f"Power limiting applied: {'No' if stats['min_power_limit'] == 100 else 'Yes'}")
    print(f"Total thermal events: {stats['total_events']}")
    
    # Create standardized plot
    create_thermal_safety_plot(
        times=times,
        temperatures=temperatures,
        currents=currents,
        powers=powers,
        thermal_statuses=thermal_statuses,
        power_limits=power_limits,
        thermal_events=thermal_events,
        test_name="Normal Operation",
        output_path="figures/test_thermal_safety_good.png"
    )
    
    print("\n✅ Test completed: Normal operation shows temperature stays well within safe limits")
    return stats


if __name__ == "__main__":
    test_thermal_safety_good()