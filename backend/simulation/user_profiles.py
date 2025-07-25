"""
User behavior profiles for EV simulation.
Different personality types affect driving patterns, charging habits, and vehicle usage.
"""

from dataclasses import dataclass
from typing import Dict, List, Tuple, Optional
from datetime import time, timedelta
from enum import Enum
import random
import numpy as np


class UserProfile(Enum):
    """Different user personality types."""
    NIGHT_OWL = "night_owl"
    EARLY_BIRD = "early_bird"
    SPONTANEOUS = "spontaneous"
    CAUTIOUS = "cautious"
    COMMUTER = "commuter"
    WEEKEND_WARRIOR = "weekend_warrior"
    ECO_CONSCIOUS = "eco_conscious"
    PERFORMANCE_ENTHUSIAST = "performance_enthusiast"


@dataclass
class UserBehavior:
    """Defines behavior patterns for a user profile."""
    profile_type: UserProfile
    
    # Activity timing preferences
    wake_time_range: Tuple[time, time]  # Typical wake up time range
    sleep_time_range: Tuple[time, time]  # Typical sleep time range
    peak_activity_hours: List[int]  # Hours of day with most activity
    
    # Driving behavior
    preferred_driving_mode: str  # eco, normal, aggressive
    avg_daily_distance_km: Tuple[float, float]  # Min, max range
    weekend_distance_multiplier: float  # How much more/less they drive on weekends
    
    # Charging behavior
    preferred_soc_min: float  # They charge when SoC drops below this
    preferred_soc_target: float  # They charge up to this level
    charging_anxiety_factor: float  # How early they charge (1.0 = normal, >1 = anxious)
    night_charging_probability: float  # Likelihood of charging at night
    opportunity_charging_probability: float  # Likelihood of charging during the day
    
    # General characteristics
    spontaneity_factor: float  # 0-1, affects random trips
    planning_factor: float  # 0-1, affects charging preparation
    eco_consciousness: float  # 0-1, affects driving efficiency
    performance_preference: float  # 0-1, affects aggressive driving


# Pre-defined user profiles
USER_PROFILES = {
    UserProfile.NIGHT_OWL: UserBehavior(
        profile_type=UserProfile.NIGHT_OWL,
        wake_time_range=(time(10, 0), time(12, 0)),
        sleep_time_range=(time(2, 0), time(4, 0)),
        peak_activity_hours=[14, 15, 16, 20, 21, 22, 23, 0, 1],
        preferred_driving_mode="normal",
        avg_daily_distance_km=(30, 80),
        weekend_distance_multiplier=1.5,
        preferred_soc_min=20.0,  # Less anxious about charging
        preferred_soc_target=80.0,
        charging_anxiety_factor=0.7,
        night_charging_probability=0.3,  # Often forgets
        opportunity_charging_probability=0.4,
        spontaneity_factor=0.8,
        planning_factor=0.3,
        eco_consciousness=0.4,
        performance_preference=0.6
    ),
    
    UserProfile.EARLY_BIRD: UserBehavior(
        profile_type=UserProfile.EARLY_BIRD,
        wake_time_range=(time(5, 0), time(6, 30)),
        sleep_time_range=(time(21, 0), time(22, 30)),
        peak_activity_hours=[6, 7, 8, 9, 10, 11],
        preferred_driving_mode="eco",
        avg_daily_distance_km=(40, 100),
        weekend_distance_multiplier=0.8,
        preferred_soc_min=40.0,  # More cautious
        preferred_soc_target=90.0,
        charging_anxiety_factor=1.3,
        night_charging_probability=0.9,  # Always charges at night
        opportunity_charging_probability=0.2,
        spontaneity_factor=0.2,
        planning_factor=0.9,
        eco_consciousness=0.7,
        performance_preference=0.3
    ),
    
    UserProfile.SPONTANEOUS: UserBehavior(
        profile_type=UserProfile.SPONTANEOUS,
        wake_time_range=(time(7, 0), time(11, 0)),  # Varies a lot
        sleep_time_range=(time(22, 0), time(2, 0)),  # Varies a lot
        peak_activity_hours=list(range(10, 22)),  # Active throughout day
        preferred_driving_mode="mixed",
        avg_daily_distance_km=(20, 150),  # High variance
        weekend_distance_multiplier=1.2,
        preferred_soc_min=15.0,  # Lets it get low
        preferred_soc_target=70.0,  # Doesn't always charge full
        charging_anxiety_factor=0.5,
        night_charging_probability=0.5,  # Random
        opportunity_charging_probability=0.6,  # Charges when convenient
        spontaneity_factor=0.95,
        planning_factor=0.1,
        eco_consciousness=0.5,
        performance_preference=0.7
    ),
    
    UserProfile.CAUTIOUS: UserBehavior(
        profile_type=UserProfile.CAUTIOUS,
        wake_time_range=(time(6, 30), time(7, 30)),
        sleep_time_range=(time(22, 0), time(23, 0)),
        peak_activity_hours=[8, 9, 10, 14, 15, 16, 17],
        preferred_driving_mode="eco",
        avg_daily_distance_km=(30, 60),
        weekend_distance_multiplier=0.9,
        preferred_soc_min=50.0,  # Never lets it get low
        preferred_soc_target=95.0,  # Always charges to near full
        charging_anxiety_factor=1.5,
        night_charging_probability=0.95,
        opportunity_charging_probability=0.7,  # Tops up frequently
        spontaneity_factor=0.1,
        planning_factor=0.95,
        eco_consciousness=0.8,
        performance_preference=0.1
    ),
    
    UserProfile.COMMUTER: UserBehavior(
        profile_type=UserProfile.COMMUTER,
        wake_time_range=(time(6, 0), time(7, 0)),
        sleep_time_range=(time(22, 30), time(23, 30)),
        peak_activity_hours=[7, 8, 17, 18],  # Rush hours
        preferred_driving_mode="normal",
        avg_daily_distance_km=(60, 120),  # Consistent commute
        weekend_distance_multiplier=0.4,  # Much less on weekends
        preferred_soc_min=30.0,
        preferred_soc_target=85.0,
        charging_anxiety_factor=1.1,
        night_charging_probability=0.8,
        opportunity_charging_probability=0.3,  # Sometimes at work
        spontaneity_factor=0.3,
        planning_factor=0.7,
        eco_consciousness=0.6,
        performance_preference=0.4
    ),
    
    UserProfile.WEEKEND_WARRIOR: UserBehavior(
        profile_type=UserProfile.WEEKEND_WARRIOR,
        wake_time_range=(time(7, 0), time(8, 0)),
        sleep_time_range=(time(23, 0), time(0, 0)),
        peak_activity_hours=[9, 10, 11, 14, 15, 16],
        preferred_driving_mode="mixed",
        avg_daily_distance_km=(20, 40),  # Low weekday
        weekend_distance_multiplier=4.0,  # High weekend usage
        preferred_soc_min=25.0,
        preferred_soc_target=90.0,
        charging_anxiety_factor=1.0,
        night_charging_probability=0.6,
        opportunity_charging_probability=0.5,  # DC fast on trips
        spontaneity_factor=0.6,
        planning_factor=0.6,
        eco_consciousness=0.4,
        performance_preference=0.8
    ),
    
    UserProfile.ECO_CONSCIOUS: UserBehavior(
        profile_type=UserProfile.ECO_CONSCIOUS,
        wake_time_range=(time(6, 30), time(7, 30)),
        sleep_time_range=(time(22, 0), time(23, 0)),
        peak_activity_hours=[8, 9, 10, 11, 14, 15, 16, 17],
        preferred_driving_mode="eco",
        avg_daily_distance_km=(40, 80),
        weekend_distance_multiplier=1.1,
        preferred_soc_min=20.0,  # Comfortable using full range
        preferred_soc_target=80.0,  # Optimal for battery health
        charging_anxiety_factor=0.9,
        night_charging_probability=0.9,  # Charges during off-peak
        opportunity_charging_probability=0.4,
        spontaneity_factor=0.4,
        planning_factor=0.8,
        eco_consciousness=0.95,
        performance_preference=0.1
    ),
    
    UserProfile.PERFORMANCE_ENTHUSIAST: UserBehavior(
        profile_type=UserProfile.PERFORMANCE_ENTHUSIAST,
        wake_time_range=(time(7, 0), time(8, 30)),
        sleep_time_range=(time(23, 0), time(1, 0)),
        peak_activity_hours=[9, 10, 17, 18, 19, 20],
        preferred_driving_mode="aggressive",
        avg_daily_distance_km=(50, 120),
        weekend_distance_multiplier=1.5,  # Track days
        preferred_soc_min=30.0,
        preferred_soc_target=90.0,
        charging_anxiety_factor=1.0,
        night_charging_probability=0.7,
        opportunity_charging_probability=0.6,  # Supercharger stops
        spontaneity_factor=0.7,
        planning_factor=0.5,
        eco_consciousness=0.2,
        performance_preference=0.95
    )
}


class UserBehaviorSimulator:
    """Simulates user behavior based on profile."""
    
    def __init__(self, profile: UserProfile, seed: Optional[int] = None):
        self.profile = profile
        self.behavior = USER_PROFILES[profile]
        if seed:
            random.seed(seed)
            np.random.seed(seed)
    
    def get_wake_time(self, is_weekend: bool = False) -> time:
        """Get wake up time for a given day."""
        start, end = self.behavior.wake_time_range
        
        # Convert to minutes for easier calculation
        start_minutes = start.hour * 60 + start.minute
        end_minutes = end.hour * 60 + end.minute
        
        # Add some randomness
        if is_weekend:
            # Sleep in on weekends (except early birds)
            if self.profile != UserProfile.EARLY_BIRD:
                start_minutes += 60
                end_minutes += 90
        
        # Add spontaneity
        variance = int((end_minutes - start_minutes) * self.behavior.spontaneity_factor)
        wake_minutes = random.randint(start_minutes, start_minutes + variance)
        
        return time(wake_minutes // 60 % 24, wake_minutes % 60)
    
    def should_drive_now(self, hour: int, is_weekend: bool = False) -> bool:
        """Determine if user is likely to drive at this hour."""
        if hour in self.behavior.peak_activity_hours:
            base_probability = 0.6
        else:
            base_probability = 0.2
        
        # Adjust for profile
        if self.profile == UserProfile.COMMUTER and not is_weekend:
            if hour in [7, 8, 17, 18]:
                base_probability = 0.9
        elif self.profile == UserProfile.WEEKEND_WARRIOR and is_weekend:
            base_probability *= 2
        
        # Add spontaneity
        probability = base_probability + (self.behavior.spontaneity_factor - 0.5) * 0.2
        
        return random.random() < probability
    
    def get_trip_distance(self, is_weekend: bool = False) -> float:
        """Get trip distance based on profile."""
        min_dist, max_dist = self.behavior.avg_daily_distance_km
        
        if is_weekend:
            min_dist *= self.behavior.weekend_distance_multiplier
            max_dist *= self.behavior.weekend_distance_multiplier
        
        # Add randomness based on spontaneity
        if self.behavior.spontaneity_factor > 0.7:
            # High variance for spontaneous users
            return random.uniform(min_dist * 0.5, max_dist * 1.5)
        else:
            # More consistent for planned users
            return random.uniform(min_dist * 0.8, max_dist * 1.1)
    
    def should_charge(self, current_soc: float, hour: int) -> Tuple[bool, float]:
        """
        Determine if user wants to charge and to what level.
        
        Returns:
            Tuple of (should_charge, target_soc)
        """
        # Check if below comfort threshold
        threshold = self.behavior.preferred_soc_min * self.behavior.charging_anxiety_factor
        
        if current_soc < threshold:
            # Definitely charge
            return True, self.behavior.preferred_soc_target
        
        # Check opportunity charging
        if current_soc < self.behavior.preferred_soc_target * 0.8:
            # Night time charging
            if 22 <= hour or hour <= 6:
                if random.random() < self.behavior.night_charging_probability:
                    return True, self.behavior.preferred_soc_target
            # Day time opportunity
            elif random.random() < self.behavior.opportunity_charging_probability:
                # Might do a partial charge
                target = random.uniform(
                    current_soc + 20,
                    self.behavior.preferred_soc_target
                )
                return True, min(target, 100)
        
        return False, 0
    
    def get_driving_style(self, trip_purpose: str = "normal") -> str:
        """Get driving style for a trip."""
        if trip_purpose == "commute":
            # Commute is usually more conservative
            if random.random() < 0.7:
                return "eco" if self.behavior.eco_consciousness > 0.5 else "normal"
        
        # Use profile preference with some randomness
        styles = ["eco", "normal", "aggressive"]
        weights = [
            self.behavior.eco_consciousness,
            1 - abs(self.behavior.performance_preference - 0.5),
            self.behavior.performance_preference
        ]
        
        return random.choices(styles, weights=weights)[0]
    
    def get_charging_type_preference(self, urgency: float = 0.5) -> str:
        """Get preferred charging type based on profile and urgency."""
        if urgency > 0.8 or self.behavior.spontaneity_factor > 0.7:
            # Need fast charging
            return "DC_FAST" if random.random() > 0.3 else "SUPERCHARGER"
        elif self.behavior.eco_consciousness > 0.7:
            # Prefer slower charging for battery health
            return "AC_L2" if random.random() > 0.2 else "AC_L1"
        else:
            # Normal preference
            return "AC_L2"