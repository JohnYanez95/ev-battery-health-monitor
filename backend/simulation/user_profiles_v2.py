"""
User behavior profiles V2 for EV simulation - Calibrated with real-world data.

Based on research from "Charging Behavior of American EV Drivers" and industry studies.
Key realistic patterns:
- SoC management: 80-90% daily target, 20-30% minimum comfort zone
- Charging frequency: 3-7 times per week (not daily for all)
- Daily distances: 19-50 miles average for most drivers
"""

from dataclasses import dataclass
from typing import Dict, List, Tuple, Optional
from datetime import time, timedelta
from enum import Enum
import random
import numpy as np


class UserProfile(Enum):
    """Different user personality types - calibrated for realism."""
    COMMON_DRIVER = "common_driver"  # Baseline representing typical EV driver behavior
    # TODO: Add other profiles iteratively


@dataclass
class UserBehavior:
    """Defines behavior patterns for a user profile."""
    profile_type: UserProfile
    
    # Activity timing preferences
    wake_time_range: Tuple[time, time]
    sleep_time_range: Tuple[time, time]
    peak_activity_hours: List[int]
    
    # Driving behavior - CALIBRATED
    preferred_driving_mode: str
    avg_daily_distance_miles: Tuple[float, float]  # Realistic 19-50 mile range
    weekend_distance_multiplier: float
    
    # Charging behavior - CALIBRATED with research data
    preferred_soc_min: float  # 20-30% comfort zone
    preferred_soc_target: float  # 80-90% daily target
    charging_anxiety_factor: float
    
    # REALISTIC charging frequency control
    base_charges_per_week: float  # 3.0-7.0 realistic range
    night_charging_probability: float
    opportunity_charging_probability: float
    
    # General characteristics
    spontaneity_factor: float
    planning_factor: float
    eco_consciousness: float
    performance_preference: float


# Start with COMMON_DRIVER as our realistic baseline
USER_PROFILES_V2 = {
    UserProfile.COMMON_DRIVER: UserBehavior(
        profile_type=UserProfile.COMMON_DRIVER,
        wake_time_range=(time(6, 30), time(7, 30)),
        sleep_time_range=(time(22, 0), time(23, 0)),
        peak_activity_hours=[8, 9, 10, 11, 14, 15, 16, 17],
        
        # CALIBRATED: Realistic daily distances for typical driver
        preferred_driving_mode="normal",  # Most drivers use normal mode
        avg_daily_distance_miles=(28, 40),  # Center of 19-50 mile research range
        weekend_distance_multiplier=1.2,  # Slightly more weekend driving
        
        # CALIBRATED: Common case SoC management (research-based)
        preferred_soc_min=25.0,  # 25% minimum - realistic comfort zone
        preferred_soc_target=85.0,  # 85% daily target - battery best practice
        charging_anxiety_factor=1.0,  # Average anxiety level
        
        # CALIBRATED: Realistic charging frequency (~4-5 times per week)
        base_charges_per_week=4.5,  # Average 4-5 charging sessions per week
        night_charging_probability=0.80,  # Most home charging is overnight
        opportunity_charging_probability=0.35,  # Some daytime top-ups
        
        spontaneity_factor=0.5,  # Average spontaneity
        planning_factor=0.7,     # Moderate planning
        eco_consciousness=0.6,   # Some environmental awareness
        performance_preference=0.4  # Balanced approach
    )
}


class UserBehaviorSimulator:
    """Simulates user behavior based on profile - V2 with realistic calibration."""
    
    def __init__(self, profile: UserProfile, seed: Optional[int] = None):
        self.profile = profile
        self.behavior = USER_PROFILES_V2[profile]
        if seed:
            random.seed(seed)
            np.random.seed(seed)
        
        # Track charging behavior over time for realistic frequency
        self._charges_this_week = 0
        self._days_since_last_charge = 0
    
    def should_charge(self, current_soc: float, hour: int, day_of_week: int = 0) -> Tuple[bool, float]:
        """
        Determine if user wants to charge - CALIBRATED for realistic frequency.
        
        Key improvements:
        - Respects base_charges_per_week limit
        - Implements realistic 20-30% minimum thresholds
        - 80-90% daily targets
        
        Returns:
            Tuple of (should_charge, target_soc)
        """
        # Reset weekly counter on Sundays
        if day_of_week == 6:  # Sunday
            self._charges_this_week = 0
        
        # CRITICAL: Don't let battery go dangerously low (safety override)
        if current_soc < 15.0:
            print(f"[SAFETY] Emergency charge at {current_soc:.1f}% SoC")
            return True, self.behavior.preferred_soc_target
        
        # Check if below preferred minimum (common case trigger)
        if current_soc <= self.behavior.preferred_soc_min:
            # But respect weekly frequency limits
            if self._charges_this_week < self.behavior.base_charges_per_week:
                self._charges_this_week += 1
                self._days_since_last_charge = 0
                return True, self.behavior.preferred_soc_target
            else:
                # Hit weekly limit - only charge if really necessary
                if current_soc < 20.0:
                    return True, self.behavior.preferred_soc_target
        
        # Opportunity charging (but only if haven't hit weekly limit)
        if self._charges_this_week < self.behavior.base_charges_per_week:
            # Night time charging opportunity
            if 22 <= hour or hour <= 6:
                if current_soc < self.behavior.preferred_soc_target * 0.9:
                    if random.random() < self.behavior.night_charging_probability:
                        self._charges_this_week += 1
                        self._days_since_last_charge = 0
                        return True, self.behavior.preferred_soc_target
            
            # Day time opportunity (less likely)
            elif current_soc < self.behavior.preferred_soc_target * 0.7:
                if random.random() < self.behavior.opportunity_charging_probability:
                    # Partial charge during day
                    target = random.uniform(
                        current_soc + 15,  # At least 15% gain
                        self.behavior.preferred_soc_target
                    )
                    self._charges_this_week += 1
                    self._days_since_last_charge = 0
                    return True, min(target, 95.0)  # Cap at 95% for day charging
        
        # Track days since charge for forcing eventual charge
        self._days_since_last_charge += 1
        
        # Force charge if too many days without charging (prevent stranding)
        if self._days_since_last_charge >= 4 and current_soc < 40.0:
            print(f"[FORCE] Forced charge after {self._days_since_last_charge} days")
            self._charges_this_week += 1
            self._days_since_last_charge = 0
            return True, self.behavior.preferred_soc_target
        
        return False, 0
    
    def get_daily_distance(self, is_weekend: bool = False) -> float:
        """Get realistic daily distance - CALIBRATED to 19-50 mile research range."""
        min_dist, max_dist = self.behavior.avg_daily_distance_miles
        
        if is_weekend:
            min_dist *= self.behavior.weekend_distance_multiplier
            max_dist *= self.behavior.weekend_distance_multiplier
        
        # Add realistic variance but keep within reasonable bounds
        if self.behavior.spontaneity_factor > 0.7:
            # Higher variance for spontaneous users
            distance = random.uniform(min_dist * 0.7, max_dist * 1.3)
        else:
            # More consistent for planned users
            distance = random.uniform(min_dist * 0.9, max_dist * 1.1)
        
        # Safety cap - prevent unrealistic daily distances
        max_realistic = 150 if is_weekend else 120
        return min(distance, max_realistic)
    
    def get_charging_session_target(self, current_soc: float, is_emergency: bool = False) -> float:
        """Get target SoC for charging session."""
        if is_emergency or current_soc < 20.0:
            return self.behavior.preferred_soc_target
        
        # Normal session - might not always go to full target
        if random.random() < 0.8:
            return self.behavior.preferred_soc_target
        else:
            # Sometimes partial charge
            return random.uniform(current_soc + 20, self.behavior.preferred_soc_target)