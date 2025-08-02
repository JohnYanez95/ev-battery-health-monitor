"""
EV Battery Model - Realistic battery physics simulation
Based on industry standards research:
- Voltage range: 300-420V typical for EVs
- Current: -200A to +200A (negative = discharge, positive = charge)
- Temperature effects on performance
- CC-CV charging profiles
"""

import numpy as np
from dataclasses import dataclass
from typing import Optional, Tuple
import math
from simulation.thermal_safety import ThermalSafetyManager, ThermalStatus


@dataclass
class BatterySpecs:
    """Battery specifications for different EV models."""
    vehicle_id: str
    make: str
    model: str
    nominal_capacity_kwh: float
    nominal_voltage: float
    max_voltage: float
    min_voltage: float
    max_charge_current: float
    max_discharge_current: float
    cell_configuration: str
    thermal_mass: float  # Affects temperature change rate
    internal_resistance: float  # Ohms


# Pre-defined vehicle battery specifications
VEHICLE_SPECS = {
    'VEH001': BatterySpecs(
        vehicle_id='VEH001',
        make='Tesla',
        model='Model 3',
        nominal_capacity_kwh=82.0,
        nominal_voltage=350.0,
        max_voltage=420.0,
        min_voltage=300.0,
        max_charge_current=200.0,  # Supercharger can do more, but this is typical
        max_discharge_current=-250.0,  # Peak acceleration
        cell_configuration='96s46p',
        thermal_mass=400.0,  # kg, affects temp change rate
        internal_resistance=0.05  # 50 milliohms pack resistance
    ),
    'VEH002': BatterySpecs(
        vehicle_id='VEH002',
        make='Nissan',
        model='Leaf',
        nominal_capacity_kwh=62.0,
        nominal_voltage=350.0,
        max_voltage=403.0,
        min_voltage=300.0,
        max_charge_current=100.0,  # CHAdeMO limited
        max_discharge_current=-150.0,
        cell_configuration='96s2p',
        thermal_mass=300.0,
        internal_resistance=0.08  # Higher resistance than Tesla
    )
}


class BatteryModel:
    """Simulates realistic EV battery behavior based on physics."""
    
    def __init__(self, specs: BatterySpecs, initial_soc: float = 80.0, 
                 initial_temp: float = 25.0, soh: float = 100.0):
        self.specs = specs
        self.soc = initial_soc  # State of Charge (%)
        self.soh = soh  # State of Health (%)
        self.temperature = initial_temp  # Battery temperature (°C)
        self.voltage = self._calculate_voltage(self.soc)
        self.current = 0.0
        self.ambient_temp = 20.0  # Default ambient temperature
        
        # Adjust capacity based on SoH
        self.effective_capacity_kwh = specs.nominal_capacity_kwh * (soh / 100.0)
        
        # Initialize thermal safety manager
        self.thermal_safety = ThermalSafetyManager(specs.vehicle_id)
        
    def _calculate_voltage(self, soc: float) -> float:
        """
        Calculate battery voltage based on SoC.
        Uses a realistic lithium-ion voltage curve.
        """
        # Normalize SoC to 0-1
        soc_norm = soc / 100.0
        
        # Lithium-ion voltage curve (simplified but realistic)
        # Steep at extremes, flatter in middle
        if soc_norm < 0.1:
            # Steep drop at low SoC
            voltage_norm = 0.0 + (soc_norm / 0.1) * 0.2
        elif soc_norm < 0.9:
            # Relatively flat in middle range
            voltage_norm = 0.2 + ((soc_norm - 0.1) / 0.8) * 0.6
        else:
            # Steep rise at high SoC
            voltage_norm = 0.8 + ((soc_norm - 0.9) / 0.1) * 0.2
            
        # Scale to actual voltage range
        voltage_range = self.specs.max_voltage - self.specs.min_voltage
        voltage = self.specs.min_voltage + (voltage_norm * voltage_range)
        
        return voltage
    
    def _calculate_voltage_under_load(self, current: float) -> float:
        """
        Calculate voltage considering load (current) and internal resistance.
        V_terminal = V_ocv - I * R_internal
        """
        ocv = self._calculate_voltage(self.soc)  # Open circuit voltage
        voltage_drop = current * self.specs.internal_resistance
        terminal_voltage = ocv - voltage_drop
        
        # Clamp to valid range
        return np.clip(terminal_voltage, self.specs.min_voltage, self.specs.max_voltage)
    
    def update_thermal(self, dt: float, power: float) -> float:
        """
        Update battery temperature based on power dissipation and cooling.
        
        Args:
            dt: Time step in seconds
            power: Power in watts (positive = charging, negative = discharging)
        
        Returns:
            New temperature
        """
        # Heat generation from I²R losses
        heat_generated = abs(self.current) ** 2 * self.specs.internal_resistance
        
        # Additional heat from charging inefficiency
        if power > 0:  # Charging
            charging_inefficiency = 0.05  # 5% energy loss as heat
            heat_generated += abs(power) * charging_inefficiency
            
        # Cooling (Newton's law of cooling)
        cooling_coefficient = 0.001  # Simplified cooling rate
        heat_removed = cooling_coefficient * (self.temperature - self.ambient_temp)
        
        # Temperature change (simplified thermal equation)
        # ΔT = (Q_in - Q_out) / (m * c) where c is specific heat capacity
        specific_heat = 1000  # J/(kg·K) approximate for battery
        temp_change = (heat_generated - heat_removed) * dt / (self.specs.thermal_mass * specific_heat)
        
        self.temperature += temp_change
        
        # Check thermal safety
        thermal_check = self.thermal_safety.check_temperature(self.temperature)
        
        # Temperature affects performance
        if self.temperature < 0:
            # Cold battery has reduced capacity
            self.effective_capacity_kwh = self.specs.nominal_capacity_kwh * (self.soh / 100.0) * 0.8
        elif self.temperature > 40:
            # Hot battery may derate power
            pass  # Handled in current limiting
            
        return self.temperature
    
    def update_soc(self, current: float, dt: float) -> float:
        """
        Update State of Charge based on current flow.
        
        Args:
            current: Current in Amperes (positive = charging)
            dt: Time step in seconds
            
        Returns:
            New SoC percentage
        """
        # Calculate energy change
        voltage = self._calculate_voltage_under_load(current)
        power = voltage * current  # Watts
        energy_change = power * dt / 3600.0  # Wh
        
        # Convert to SoC change
        soc_change = (energy_change / (self.effective_capacity_kwh * 1000)) * 100
        
        # Update SoC with limits
        self.soc = np.clip(self.soc + soc_change, 0.0, 100.0)
        
        return self.soc
    
    def apply_current(self, requested_current: float, dt: float) -> Tuple[float, float, float]:
        """
        Apply current to battery with realistic constraints.
        
        Args:
            requested_current: Requested current in Amperes
            dt: Time step in seconds
            
        Returns:
            Tuple of (actual_current, voltage, power)
        """
        # Get thermal safety status
        thermal_check = self.thermal_safety.check_temperature(self.temperature)
        
        # Apply thermal safety power limit (overrides temperature derating)
        thermal_power_limit = thermal_check['power_limit']
        
        # Temperature derating (combined with thermal safety)
        temp_derate = 1.0
        if self.temperature > 45:
            # Reduce power at high temps
            temp_derate = max(0.5, 1.0 - (self.temperature - 45) / 20)
        elif self.temperature < 0:
            # Reduce power at low temps
            temp_derate = max(0.3, 1.0 + self.temperature / 20)
        
        # Use the more conservative limit
        power_limit = min(temp_derate, thermal_power_limit)
            
        # Apply current limits with power limiting
        if requested_current > 0:  # Charging
            max_current = self.specs.max_charge_current * power_limit
            # CC-CV charging: reduce current as battery fills
            if self.soc > 80:
                # Taper current from 80% to 100% SoC
                taper_factor = 1.0 - (self.soc - 80) / 20
                max_current *= max(0.1, taper_factor)
        else:  # Discharging
            max_current = self.specs.max_discharge_current * power_limit
            
        # Apply limits
        if requested_current > 0:
            self.current = min(requested_current, max_current)
        else:
            self.current = max(requested_current, max_current)
            
        # Update voltage under load
        self.voltage = self._calculate_voltage_under_load(self.current)
        
        # Calculate power
        power = self.voltage * self.current
        
        # Update SoC
        self.update_soc(self.current, dt)
        
        # Update temperature
        self.update_thermal(dt, power)
        
        return self.current, self.voltage, power
    
    def get_state(self) -> dict:
        """Get current battery state as a dictionary."""
        thermal_status = self.thermal_safety.current_status.value
        return {
            'soc_percent': round(self.soc, 1),
            'voltage': round(self.voltage, 1),
            'current': round(self.current, 1),
            'temperature': round(self.temperature, 1),
            'power': round(self.voltage * self.current, 1),
            'energy_kwh': round(self.effective_capacity_kwh * self.soc / 100, 2),
            'soh_percent': round(self.soh, 1),
            'estimated_range_km': round(self._estimate_range(), 1),
            'thermal_status': thermal_status,
            'thermal_shutdown': self.thermal_safety.shutdown_active
        }
    
    def _estimate_range(self) -> float:
        """Estimate remaining range based on SoC and typical consumption."""
        # Typical consumption: 150-200 Wh/km
        consumption_wh_per_km = 180 if self.specs.make == 'Tesla' else 150
        remaining_energy_wh = self.effective_capacity_kwh * 1000 * (self.soc / 100)
        return remaining_energy_wh / consumption_wh_per_km