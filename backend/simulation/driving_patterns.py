"""
Driving patterns simulator - generates realistic EV usage patterns.
Based on research showing typical discharge patterns, regenerative braking,
and various driving scenarios (city, highway, aggressive, eco).
"""

import numpy as np
from typing import List, Tuple, Optional
from enum import Enum
import random


class DrivingMode(Enum):
    """Different driving patterns."""
    CITY = "city"
    HIGHWAY = "highway"
    AGGRESSIVE = "aggressive"
    ECO = "eco"
    MIXED = "mixed"


class DrivingPatternGenerator:
    """Generates realistic driving current profiles."""
    
    def __init__(self, seed: Optional[int] = None):
        if seed:
            np.random.seed(seed)
            random.seed(seed)
    
    def generate_city_driving(self, duration_seconds: int, dt: float = 1.0) -> List[float]:
        """
        Generate city driving pattern with frequent stops and starts.
        Characteristics:
        - Frequent acceleration/deceleration
        - Lower speeds (0-60 km/h)
        - More regenerative braking opportunities
        - Average power: 15-25 kW
        """
        samples = int(duration_seconds / dt)
        current_profile = []
        
        # City driving state machine
        state = "stopped"
        state_timer = 0
        speed_mph = 0
        
        for _ in range(samples):
            if state == "stopped":
                current = 0
                state_timer += dt
                # Traffic light changes every 30-90 seconds
                if state_timer > np.random.uniform(30, 90):
                    state = "accelerating"
                    state_timer = 0
                    
            elif state == "accelerating":
                # Moderate acceleration in city
                acceleration_power = np.random.uniform(30, 60)  # kW
                # Add some variability
                acceleration_power *= (1 + np.random.normal(0, 0.1))
                current = -acceleration_power * 1000 / 350  # Assuming 350V nominal
                
                speed_mph += 3 * dt  # Accelerate at 3 mph/s
                if speed_mph >= np.random.uniform(25, 37):
                    state = "cruising"
                    state_timer = 0
                    
            elif state == "cruising":
                # Steady state with small variations
                cruise_power = 10 + speed_mph * 0.5  # Simple model
                current = -cruise_power * 1000 / 350
                # Add road/traffic variations
                current *= (1 + np.random.normal(0, 0.05))
                
                state_timer += dt
                if state_timer > np.random.uniform(10, 30):
                    # Randomly brake or stop
                    state = "braking" if random.random() > 0.3 else "coasting"
                    state_timer = 0
                    
            elif state == "braking":
                # Regenerative braking
                regen_power = np.random.uniform(10, 30)  # kW recovered
                current = regen_power * 1000 / 350  # Positive current
                
                speed_mph -= 6 * dt  # Decelerate
                if speed_mph <= 0:
                    speed_mph = 0
                    state = "stopped"
                    state_timer = 0
                    
            elif state == "coasting":
                # Gentle deceleration
                current = -2 * 1000 / 350  # Small power draw
                speed_mph -= 1.2 * dt
                
                state_timer += dt
                if state_timer > np.random.uniform(5, 15) or speed_mph <= 12:
                    state = "braking"
                    state_timer = 0
            
            current_profile.append(current)
            
        return current_profile
    
    def generate_highway_driving(self, duration_seconds: int, dt: float = 1.0) -> List[float]:
        """
        Generate highway driving pattern.
        Characteristics:
        - Higher sustained speeds (50-75 mph)
        - Less frequent stops
        - More consistent power draw
        - Average power: 20-40 kW
        """
        samples = int(duration_seconds / dt)
        current_profile = []
        
        # Highway entry acceleration
        for i in range(min(30, samples)):  # 30 seconds to reach highway speed
            acceleration_power = 80 - i * 2  # Decreasing power as we reach speed
            current = -acceleration_power * 1000 / 350
            current_profile.append(current)
        
        # Cruise with variations
        cruise_speed = np.random.uniform(56, 68)  # mph
        base_power = 15 + cruise_speed * 0.4  # Simple aerodynamic model
        
        for i in range(30, samples):
            # Add variations for hills, wind, passing
            if random.random() < 0.05:  # 5% chance of passing maneuver
                # Passing acceleration
                current = -80 * 1000 / 350
            elif random.random() < 0.02:  # 2% chance of hill
                # Uphill requires more power
                hill_factor = np.random.uniform(1.3, 1.8)
                current = -base_power * hill_factor * 1000 / 350
            else:
                # Normal cruise with small variations
                variation = 1 + np.random.normal(0, 0.03)
                current = -base_power * variation * 1000 / 350
            
            current_profile.append(current)
            
        return current_profile
    
    def generate_aggressive_driving(self, duration_seconds: int, dt: float = 1.0) -> List[float]:
        """
        Generate aggressive driving pattern.
        Characteristics:
        - Hard acceleration and braking
        - Higher power draws
        - Less efficient driving
        """
        samples = int(duration_seconds / dt)
        current_profile = []
        
        for i in range(samples):
            phase = (i * dt) % 60  # 60-second cycles
            
            if phase < 10:  # Hard acceleration
                power = np.random.uniform(100, 150)  # kW
                current = -power * 1000 / 350
            elif phase < 20:  # High-speed cruise
                power = np.random.uniform(40, 60)
                current = -power * 1000 / 350
            elif phase < 25:  # Hard braking
                regen_power = np.random.uniform(40, 60)
                current = regen_power * 1000 / 350
            else:  # Moderate cruise
                power = np.random.uniform(20, 40)
                current = -power * 1000 / 350
            
            # Add noise
            current *= (1 + np.random.normal(0, 0.1))
            current_profile.append(current)
            
        return current_profile
    
    def generate_eco_driving(self, duration_seconds: int, dt: float = 1.0) -> List[float]:
        """
        Generate eco-friendly driving pattern.
        Characteristics:
        - Gentle acceleration
        - Optimal speeds for efficiency
        - Maximum regenerative braking
        - Predictive driving
        """
        samples = int(duration_seconds / dt)
        current_profile = []
        
        # Eco driving tends to be very smooth
        speed_mph = 0
        target_speed = 0
        
        for i in range(samples):
            # Change target speed occasionally
            if i % 300 == 0:  # Every 5 minutes
                target_speed = np.random.choice([0, 50, 70, 90])
            
            # Smooth acceleration/deceleration
            speed_diff = target_speed - speed_mph
            if abs(speed_diff) > 1:
                if speed_diff > 0:  # Need to accelerate
                    acceleration_power = min(30, speed_diff * 2)  # Gentle
                    current = -acceleration_power * 1000 / 350
                    speed_mph += 2 * dt  # Slow acceleration
                else:  # Need to decelerate
                    # Maximum regen
                    regen_power = min(25, abs(speed_diff) * 1.5)
                    current = regen_power * 1000 / 350
                    speed_mph -= 5 * dt
            else:
                # Efficient cruise
                if speed_mph > 0:
                    # Optimal efficiency power curve
                    power = 5 + speed_mph * 0.25  # Very efficient
                    current = -power * 1000 / 350
                else:
                    current = 0
            
            current_profile.append(current)
            
        return current_profile
    
    def generate_mixed_driving(self, duration_seconds: int, dt: float = 1.0) -> List[float]:
        """
        Generate mixed driving pattern combining different modes.
        More realistic for actual daily driving.
        """
        samples = int(duration_seconds / dt)
        current_profile = []
        
        # Define segments
        segments = [
            ("city", int(samples * 0.3)),
            ("highway", int(samples * 0.4)),
            ("city", int(samples * 0.2)),
            ("eco", int(samples * 0.1))
        ]
        
        for mode_name, segment_samples in segments:
            if mode_name == "city":
                segment = self.generate_city_driving(int(segment_samples * dt), dt)
            elif mode_name == "highway":
                segment = self.generate_highway_driving(int(segment_samples * dt), dt)
            elif mode_name == "eco":
                segment = self.generate_eco_driving(int(segment_samples * dt), dt)
            
            current_profile.extend(segment[:segment_samples])
            
        # Ensure we have exactly the right number of samples
        return current_profile[:samples]
    
    def add_noise(self, current_profile: List[float], noise_level: float = 0.02) -> List[float]:
        """Add realistic measurement noise to current profile."""
        noise = np.random.normal(0, noise_level * np.abs(current_profile).mean(), len(current_profile))
        return [c + n for c, n in zip(current_profile, noise)]