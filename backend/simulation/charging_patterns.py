"""
Charging patterns simulator - generates realistic EV charging profiles.
Implements CC-CV (Constant Current - Constant Voltage) charging curves
and different charging scenarios (L1, L2, DC Fast, Supercharger).
"""

import numpy as np
from typing import List, Tuple, Optional
from enum import Enum


class ChargingType(Enum):
    """Different charging methods with typical power levels."""
    AC_L1 = "AC_L1"  # Standard outlet, ~1.4 kW
    AC_L2 = "AC_L2"  # Home/public charger, ~7-11 kW  
    DC_FAST = "DC_FAST"  # CHAdeMO/CCS, ~50 kW
    SUPERCHARGER = "SUPERCHARGER"  # Tesla Supercharger, ~150-250 kW


class ChargingPatternGenerator:
    """Generates realistic charging current profiles following CC-CV curves."""
    
    # Charging specifications
    CHARGING_SPECS = {
        ChargingType.AC_L1: {
            'max_power_kw': 1.4,
            'efficiency': 0.85,
            'voltage': 240,
            'phases': 1
        },
        ChargingType.AC_L2: {
            'max_power_kw': 11.0,
            'efficiency': 0.90,
            'voltage': 240,
            'phases': 2
        },
        ChargingType.DC_FAST: {
            'max_power_kw': 50.0,
            'efficiency': 0.95,
            'voltage': 400,
            'phases': None  # DC
        },
        ChargingType.SUPERCHARGER: {
            'max_power_kw': 150.0,
            'efficiency': 0.97,
            'voltage': 400,
            'phases': None  # DC
        }
    }
    
    def __init__(self, battery_voltage_nominal: float = 350.0):
        self.battery_voltage = battery_voltage_nominal
    
    def generate_cc_cv_profile(
        self,
        charging_type: ChargingType,
        initial_soc: float,
        target_soc: float,
        battery_capacity_kwh: float,
        duration_seconds: int,
        dt: float = 1.0
    ) -> Tuple[List[float], List[float], bool]:
        """
        Generate CC-CV charging profile.
        
        Args:
            charging_type: Type of charger
            initial_soc: Starting State of Charge (%)
            target_soc: Target State of Charge (%)
            battery_capacity_kwh: Battery capacity in kWh
            duration_seconds: Maximum charging duration
            dt: Time step in seconds
            
        Returns:
            Tuple of (current_profile, soc_profile, completed)
        """
        specs = self.CHARGING_SPECS[charging_type]
        samples = int(duration_seconds / dt)
        
        current_profile = []
        soc_profile = []
        
        # Calculate charging parameters
        max_power = specs['max_power_kw'] * 1000  # Convert to W
        max_current = max_power / self.battery_voltage
        
        # Current SoC
        current_soc = initial_soc
        
        # CC-CV transition point (typically 80% for fast charging)
        cv_transition_soc = 80.0 if charging_type in [ChargingType.DC_FAST, ChargingType.SUPERCHARGER] else 85.0
        
        completed = False
        
        for i in range(samples):
            if current_soc >= target_soc:
                # Charging complete
                current = 0
                completed = True
            elif current_soc < cv_transition_soc:
                # Constant Current (CC) phase
                # Apply thermal derating for fast charging
                if charging_type == ChargingType.SUPERCHARGER:
                    # Supercharger tapers based on SoC even in CC phase
                    if current_soc < 20:
                        power_factor = 1.0  # Full power
                    elif current_soc < 50:
                        power_factor = 0.9  # Slight taper
                    else:
                        power_factor = 0.8 - (current_soc - 50) * 0.005
                    current = max_current * power_factor
                else:
                    # Other chargers maintain constant current
                    current = max_current
                    
                # Add charging startup ramp (first 10 seconds)
                if i < 10 / dt:
                    ramp_factor = (i * dt) / 10
                    current *= ramp_factor
                    
            else:
                # Constant Voltage (CV) phase - current tapers
                # Exponential decay of current
                soc_above_cv = current_soc - cv_transition_soc
                taper_factor = np.exp(-soc_above_cv / 10)  # Decay constant of 10%
                current = max_current * taper_factor * 0.5  # Additional factor for realistic taper
            
            # Apply efficiency losses
            effective_current = current * specs['efficiency']
            
            # Calculate energy delivered
            power = effective_current * self.battery_voltage  # W
            energy_delivered = power * dt / 3600  # Wh
            
            # Update SoC
            soc_increment = (energy_delivered / (battery_capacity_kwh * 1000)) * 100
            current_soc = min(current_soc + soc_increment, 100.0)
            
            # Add realistic variations
            if current > 0:
                # Small fluctuations in charging current
                current *= (1 + np.random.normal(0, 0.01))
                
                # Occasional dips (thermal management, grid variations)
                if np.random.random() < 0.02:  # 2% chance
                    current *= np.random.uniform(0.7, 0.9)
            
            current_profile.append(current)
            soc_profile.append(current_soc)
            
        return current_profile, soc_profile, completed
    
    def generate_interrupted_charging(
        self,
        charging_type: ChargingType,
        initial_soc: float,
        interruption_times: List[Tuple[int, int]],
        battery_capacity_kwh: float,
        duration_seconds: int,
        dt: float = 1.0
    ) -> Tuple[List[float], List[float]]:
        """
        Generate charging profile with interruptions.
        Simulates unplugging, power outages, or charging limits.
        
        Args:
            interruption_times: List of (start_time, duration) tuples for interruptions
            
        Returns:
            Tuple of (current_profile, soc_profile)
        """
        # Generate normal charging profile
        current_profile, soc_profile, _ = self.generate_cc_cv_profile(
            charging_type, initial_soc, 100.0, battery_capacity_kwh, duration_seconds, dt
        )
        
        # Apply interruptions
        for start_time, interrupt_duration in interruption_times:
            start_idx = int(start_time / dt)
            end_idx = int((start_time + interrupt_duration) / dt)
            
            # Zero current during interruption
            for idx in range(start_idx, min(end_idx, len(current_profile))):
                if idx < len(current_profile):
                    current_profile[idx] = 0
                    
            # Adjust SoC profile to be flat during interruption
            if start_idx < len(soc_profile):
                interrupted_soc = soc_profile[start_idx]
                for idx in range(start_idx + 1, min(end_idx, len(soc_profile))):
                    if idx < len(soc_profile):
                        soc_profile[idx] = interrupted_soc
                        
        return current_profile, soc_profile
    
    def generate_smart_charging(
        self,
        initial_soc: float,
        target_soc: float,
        battery_capacity_kwh: float,
        duration_seconds: int,
        electricity_prices: Optional[List[float]] = None,
        dt: float = 1.0
    ) -> Tuple[List[float], List[float]]:
        """
        Generate smart charging profile that optimizes for electricity prices.
        Charges more during low-price periods.
        
        Args:
            electricity_prices: List of electricity prices per time step (optional)
            
        Returns:
            Tuple of (current_profile, soc_profile)
        """
        samples = int(duration_seconds / dt)
        
        # Generate default price curve if not provided (time-of-use)
        if electricity_prices is None:
            electricity_prices = []
            for i in range(samples):
                hour = (i * dt / 3600) % 24
                if 23 <= hour or hour < 6:  # Night time - cheap
                    price = 0.10
                elif 17 <= hour < 21:  # Peak hours - expensive
                    price = 0.30
                else:  # Day time - moderate
                    price = 0.15
                electricity_prices.append(price)
        
        # Use L2 charging as base
        specs = self.CHARGING_SPECS[ChargingType.AC_L2]
        max_current = specs['max_power_kw'] * 1000 / self.battery_voltage
        
        current_profile = []
        soc_profile = []
        current_soc = initial_soc
        
        # Calculate required energy
        energy_needed = battery_capacity_kwh * (target_soc - initial_soc) / 100
        
        for i in range(samples):
            if current_soc >= target_soc:
                current = 0
            else:
                # Determine charging rate based on price
                price = electricity_prices[i]
                if price < 0.12:  # Cheap - charge at full rate
                    current = max_current
                elif price < 0.20:  # Moderate - charge at 50%
                    current = max_current * 0.5
                else:  # Expensive - minimal or no charging
                    current = max_current * 0.1 if current_soc < 20 else 0
                    
            # Update SoC
            if current > 0:
                power = current * self.battery_voltage * specs['efficiency']
                energy_delivered = power * dt / 3600
                soc_increment = (energy_delivered / (battery_capacity_kwh * 1000)) * 100
                current_soc = min(current_soc + soc_increment, target_soc)
                
            current_profile.append(current)
            soc_profile.append(current_soc)
            
        return current_profile, soc_profile
    
    def generate_degraded_charging(
        self,
        charging_type: ChargingType,
        initial_soc: float,
        battery_capacity_kwh: float,
        degradation_factor: float,
        duration_seconds: int,
        dt: float = 1.0
    ) -> Tuple[List[float], List[float]]:
        """
        Generate charging profile for a degraded battery.
        Degraded batteries charge slower and may not reach 100%.
        
        Args:
            degradation_factor: Battery degradation (0.0 = new, 1.0 = dead)
            
        Returns:
            Tuple of (current_profile, soc_profile)
        """
        # Adjust charging parameters based on degradation
        health_factor = 1.0 - degradation_factor
        
        # Degraded batteries have higher internal resistance
        current_derate = health_factor
        
        # Maximum achievable SoC decreases with degradation
        max_soc = 95.0 * health_factor + 5.0  # Even dead battery shows some charge
        
        # Generate normal profile
        current_profile, soc_profile, _ = self.generate_cc_cv_profile(
            charging_type, initial_soc, max_soc, battery_capacity_kwh, duration_seconds, dt
        )
        
        # Apply degradation effects
        degraded_current = [c * current_derate for c in current_profile]
        
        # Add more noise for degraded batteries
        noise_level = 0.02 + degradation_factor * 0.05
        for i in range(len(degraded_current)):
            if degraded_current[i] > 0:
                degraded_current[i] *= (1 + np.random.normal(0, noise_level))
                
        return degraded_current, soc_profile