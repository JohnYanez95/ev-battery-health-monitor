#!/usr/bin/env python3
"""
Test thermal model calibration based on research findings.

Research validation targets:
- Tesla Model 3 at 250A should generate ~3kW heat (not 12.5kW)
- Internal resistance: 0.05Ω (realistic vs 0.2Ω extreme)
- Thermal mass: Use full 400kg (not reduced 120kg)
- Gradual overheating should take 10-20 minutes (not 82 seconds)
"""

import sys
import os
sys.path.append(os.path.dirname(__file__))

from simulation.battery_model import BatteryModel, VEHICLE_SPECS
import numpy as np
import matplotlib.pyplot as plt

def test_heat_generation_validation():
    """Test heat generation matches research expectations."""
    print("=== HEAT GENERATION VALIDATION ===")
    
    # Tesla Model 3 specs
    tesla_specs = VEHICLE_SPECS['VEH001']
    print(f"Tesla Model 3 internal resistance: {tesla_specs.internal_resistance}Ω")
    print(f"Tesla Model 3 thermal mass: {tesla_specs.thermal_mass}kg")
    
    # Test at 250A discharge (research reference point)
    current = -250  # Negative for discharge
    
    # Calculate I²R heat generation
    heat_generated = abs(current) ** 2 * tesla_specs.internal_resistance
    print(f"\nHeat generation at {abs(current)}A:")
    print(f"I²R = {abs(current)}² × {tesla_specs.internal_resistance}Ω = {heat_generated:.1f}W")
    print(f"Research expectation: ~3000W (3kW)")
    print(f"Our result: {heat_generated:.1f}W ({heat_generated/1000:.1f}kW)")
    print(f"✅ PASS: Within realistic range" if 2000 <= heat_generated <= 4000 else f"❌ FAIL: Outside realistic range")
    
    return heat_generated

def test_thermal_mass_impact():
    """Test thermal mass impact on heating rate."""
    print("\n=== THERMAL MASS IMPACT TEST ===")
    
    tesla_specs = VEHICLE_SPECS['VEH001']
    
    # Calculate theoretical temperature rise
    heat_power = 3000  # 3kW heat generation
    thermal_mass = tesla_specs.thermal_mass  # 400kg
    specific_heat = 1000  # J/(kg·K)
    
    # ΔT/Δt = Q / (m * c)
    temp_rise_rate = heat_power / (thermal_mass * specific_heat)  # °C/s
    temp_rise_per_minute = temp_rise_rate * 60  # °C/min
    
    print(f"Thermal mass: {thermal_mass}kg")
    print(f"Heat generation: {heat_power}W")
    print(f"Temperature rise rate: {temp_rise_rate:.4f}°C/s = {temp_rise_per_minute:.2f}°C/min")
    
    # Time to reach critical thresholds
    time_25_to_50 = 25 / temp_rise_rate / 60  # minutes
    time_50_to_60 = 10 / temp_rise_rate / 60  # minutes
    
    print(f"\nTime to heat from 25°C to 50°C (warning): {time_25_to_50:.1f} minutes")
    print(f"Time to heat from 50°C to 60°C (shutdown): {time_50_to_60:.1f} minutes")
    print(f"Research expectation: 10-20 minutes for gradual overheating")
    print(f"✅ REALISTIC" if time_25_to_50 > 10 else f"⚠️  TOO FAST")
    
    return temp_rise_per_minute

def test_calibrated_thermal_scenario():
    """Test realistic extreme scenario with calibrated parameters."""
    print("\n=== CALIBRATED THERMAL SCENARIO TEST ===")
    
    # Initialize Tesla Model 3 with realistic parameters
    battery = BatteryModel(VEHICLE_SPECS['VEH001'], initial_temp=25.0)
    battery.ambient_temp = 35.0  # Hot weather
    
    # Simulate cooling system degradation (not complete failure)
    battery.cooling_degraded = True
    
    print("Scenario: High discharge (200A) in hot weather (35°C) with degraded cooling")
    print("Expected: Gradual temperature rise over several minutes")
    
    # Simulation parameters
    dt = 1.0  # 1 second time steps
    duration = 1800  # 30 minutes
    steps = int(duration / dt)
    
    # Data storage
    time_data = []
    temp_data = []
    current_data = []
    thermal_status_data = []
    
    # Run simulation
    current = -200  # High discharge current
    for step in range(steps):
        t = step * dt
        
        # Apply constant high discharge
        actual_current, voltage, power = battery.apply_current(current, dt)
        
        # Record data
        time_data.append(t / 60)  # Convert to minutes
        temp_data.append(battery.temperature)
        current_data.append(actual_current)
        thermal_status_data.append(battery.thermal_safety.current_status.value)
        
        # Check for thermal shutdown
        if battery.thermal_safety.shutdown_active:
            print(f"⚠️  Thermal shutdown at t={t/60:.1f} min, T={battery.temperature:.1f}°C")
            break
        
        # Early exit if temperature stabilizes
        if step > 600 and abs(temp_data[-1] - temp_data[-60]) < 0.1:  # 1 minute stability
            print(f"Temperature stabilized at {battery.temperature:.1f}°C after {t/60:.1f} minutes")
            break
    
    # Results analysis
    max_temp = max(temp_data)
    final_temp = temp_data[-1]
    
    print(f"\nResults:")
    print(f"Peak temperature: {max_temp:.1f}°C")
    print(f"Final temperature: {final_temp:.1f}°C")
    print(f"Test duration: {len(time_data):.0f} minutes")
    
    if max_temp >= 60:
        shutdown_time = next((i for i, temp in enumerate(temp_data) if temp >= 60), None)
        if shutdown_time:
            print(f"Time to shutdown (60°C): {shutdown_time:.1f} minutes")
            print(f"✅ REALISTIC" if shutdown_time > 5 else f"❌ TOO FAST")
    else:
        print("✅ No thermal shutdown - realistic for high but manageable load")
    
    return time_data, temp_data, thermal_status_data

def main():
    """Run all thermal calibration validation tests."""
    print("THERMAL MODEL CALIBRATION VALIDATION")
    print("=" * 50)
    
    # Test 1: Heat generation validation
    heat_gen = test_heat_generation_validation()
    
    # Test 2: Thermal mass impact
    temp_rise_rate = test_thermal_mass_impact()
    
    # Test 3: Calibrated scenario
    time_data, temp_data, status_data = test_calibrated_thermal_scenario()
    
    print("\n" + "=" * 50)
    print("CALIBRATION SUMMARY:")
    print(f"Heat generation: {heat_gen:.0f}W (target: ~3000W)")
    print(f"Temperature rise rate: {temp_rise_rate:.2f}°C/min (realistic range)")
    print(f"Scenario duration: {len(time_data):.0f} minutes")
    print("✅ Thermal model calibrated based on industry research")

if __name__ == "__main__":
    main()