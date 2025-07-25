"""
Enhanced EV battery simulation orchestrator with dynamic charging decisions.
This version checks for charging needs throughout the day, not just at the beginning.
"""

import numpy as np
import pandas as pd
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
import random
import sys
import os

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from simulation.battery_model import BatteryModel, VEHICLE_SPECS
from simulation.driving_patterns import DrivingPatternGenerator, DrivingMode
from simulation.charging_patterns import ChargingPatternGenerator, ChargingType
from simulation.anomaly_generator import AnomalyGenerator, AnomalyEvent
from simulation.user_profiles import UserProfile, UserBehaviorSimulator, USER_PROFILES
from database.connection import insert_telemetry_batch, execute_query


class EVBatterySimulatorV2:
    """Enhanced orchestrator with dynamic charging decisions throughout the day."""
    
    def __init__(self, vehicle_id: str, user_profile: Optional[UserProfile] = None, 
                 seed: Optional[int] = None):
        """
        Initialize simulator for a specific vehicle.
        
        Args:
            vehicle_id: Vehicle identifier (must exist in VEHICLE_SPECS)
            user_profile: User behavior profile (random if not specified)
            seed: Random seed for reproducibility
        """
        if vehicle_id not in VEHICLE_SPECS:
            raise ValueError(f"Unknown vehicle_id: {vehicle_id}")
            
        self.vehicle_id = vehicle_id
        self.specs = VEHICLE_SPECS[vehicle_id]
        self.battery = BatteryModel(self.specs)
        
        # Set user profile
        if user_profile is None:
            # Randomly assign a profile
            user_profile = random.choice(list(UserProfile))
        self.user_profile = user_profile
        self.user_behavior = UserBehaviorSimulator(user_profile, seed)
        
        # Initialize pattern generators
        self.driving_gen = DrivingPatternGenerator(seed)
        self.charging_gen = ChargingPatternGenerator(self.specs.nominal_voltage)
        self.anomaly_gen = AnomalyGenerator(seed)
        
        # Simulation state
        self.current_time = datetime.now()
        self.telemetry_data = []
        self.anomaly_events = []
        
        # Set random seeds
        if seed:
            np.random.seed(seed)
            random.seed(seed)
    
    def simulate_day(
        self,
        date: Optional[datetime] = None,
        ambient_temp_profile: Optional[List[float]] = None,
        include_anomalies: bool = True,
        dt: float = 1.0
    ) -> Dict[str, pd.DataFrame]:
        """
        Simulate a full day of vehicle operation with dynamic charging decisions.
        
        Args:
            date: Start date for simulation (default: now)
            ambient_temp_profile: 24-hour ambient temperature profile
            include_anomalies: Whether to inject anomalies
            dt: Time step in seconds (1.0 = 1Hz data)
            
        Returns:
            Dictionary with 'telemetry' DataFrame and 'events' DataFrame
        """
        if date is None:
            date = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
            
        # Generate ambient temperature if not provided
        if ambient_temp_profile is None:
            # Simple sinusoidal temperature profile
            hours = np.arange(24)
            base_temp = 20  # Base temperature
            amplitude = 10  # Daily variation
            ambient_temp_profile = base_temp + amplitude * np.sin((hours - 6) * np.pi / 12)
            
        # Daily schedule (check if weekend)
        is_weekend = date.weekday() >= 5  # Saturday = 5, Sunday = 6
        
        telemetry_records = []
        events = []
        
        current_time = date
        end_time = date + timedelta(days=1)
        
        # Track if we're currently in an activity
        current_activity = None
        activity_end_time = current_time
        
        # Main simulation loop - process hour by hour
        while current_time < end_time:
            # Update ambient temperature
            hour = current_time.hour
            self.battery.ambient_temp = ambient_temp_profile[hour]
            
            # Check if we need a new activity
            if current_time >= activity_end_time:
                # First check if we need to charge
                should_charge, target_soc = self.user_behavior.should_charge(
                    self.battery.soc, 
                    current_time.hour
                )
                
                if should_charge and self.battery.soc < target_soc - 5:  # 5% buffer
                    # Plan charging activity
                    current_activity = self._plan_charging_activity(target_soc)
                else:
                    # Plan next regular activity
                    current_activity = self._plan_next_activity(current_time, is_weekend)
                
                # Calculate activity end time
                activity_end_time = current_time + current_activity['duration']
                # Don't go past end of day
                if activity_end_time > end_time:
                    activity_end_time = end_time
                    current_activity['duration'] = end_time - current_time
            
            # Execute current activity for one time step
            if current_activity['type'] == 'idle':
                # Vehicle parked - minimal battery drain
                self.battery.apply_current(0, dt)
                telemetry_records.append(self._create_telemetry_record(current_time))
                    
            elif current_activity['type'] == 'driving':
                # Generate driving current for this timestep
                mode = current_activity.get('mode', DrivingMode.MIXED)
                # Get instantaneous current based on driving mode
                current = self._get_driving_current(mode)
                
                self.battery.apply_current(current, dt)
                record = self._create_telemetry_record(current_time)
                record['is_driving'] = True
                record['speed_kmh'] = abs(current) * 0.5  # Simplified speed estimate
                telemetry_records.append(record)
                    
            elif current_activity['type'] == 'charging':
                # Calculate charging current for current SoC
                charging_type = current_activity.get('charging_type', ChargingType.AC_L2)
                target_soc = current_activity.get('target_soc', 80.0)
                
                # Get appropriate charging current
                current = self._get_charging_current(charging_type, self.battery.soc, target_soc)
                
                if current > 0 and self.battery.soc < target_soc:
                    self.battery.apply_current(current, dt)
                    record = self._create_telemetry_record(current_time)
                    record['is_charging'] = True
                    record['charger_type'] = charging_type.name
                    telemetry_records.append(record)
                else:
                    # Charging complete or not needed
                    self.battery.apply_current(0, dt)
                    record = self._create_telemetry_record(current_time)
                    telemetry_records.append(record)
                    # End charging activity early
                    activity_end_time = current_time
            
            # Advance time
            current_time += timedelta(seconds=dt)
        
        # Inject anomalies if requested
        if include_anomalies and len(telemetry_records) > 0:
            telemetry_records, anomaly_events = self._inject_daily_anomalies(
                telemetry_records, date
            )
            events.extend(anomaly_events)
        
        # Convert to DataFrames
        telemetry_df = pd.DataFrame(telemetry_records)
        events_df = pd.DataFrame([self._anomaly_to_dict(e) for e in events])
        
        return {
            'telemetry': telemetry_df,
            'events': events_df
        }
    
    def _plan_charging_activity(self, target_soc: float) -> Dict:
        """Plan a charging session based on current battery state and user profile."""
        # Determine charging type based on urgency
        behavior = self.user_behavior.behavior
        urgency = max(0, (behavior.preferred_soc_min - self.battery.soc) / behavior.preferred_soc_min)
        charging_type_str = self.user_behavior.get_charging_type_preference(urgency)
        charging_type = getattr(ChargingType, charging_type_str)
        
        # Estimate charging duration needed
        energy_needed = self.battery.effective_capacity_kwh * (target_soc - self.battery.soc) / 100
        charging_power = self.charging_gen.CHARGING_SPECS[charging_type]['max_power_kw']
        hours_needed = energy_needed / (charging_power * 0.9)  # 90% efficiency
        
        # User profile affects charging duration
        if self.user_profile == UserProfile.CAUTIOUS:
            # Cautious users charge fully
            duration = timedelta(hours=min(hours_needed + 0.5, 8))
        elif self.user_profile == UserProfile.SPONTANEOUS:
            # Spontaneous users might charge just enough
            duration = timedelta(hours=min(hours_needed * 0.5, 2))
        else:
            duration = timedelta(hours=min(hours_needed, 4))
        
        return {
            'type': 'charging',
            'duration': duration,
            'charging_type': charging_type,
            'target_soc': target_soc
        }
    
    def _plan_next_activity(self, current_time: datetime, is_weekend: bool) -> Dict:
        """Plan the next activity based on time of day and user profile."""
        hour = current_time.hour
        
        # Default idle activity
        activity = {'type': 'idle', 'duration': timedelta(hours=1)}
        
        # Check if user should drive now
        if self.user_behavior.should_drive_now(hour, is_weekend):
            # Plan a driving activity
            trip_distance = self.user_behavior.get_trip_distance(is_weekend) / 4  # Partial trip
            trip_time = max(0.25, trip_distance / 50)  # Average speed
            
            # Driving style based on profile
            style_map = {
                'eco': DrivingMode.ECO,
                'normal': DrivingMode.CITY,
                'aggressive': DrivingMode.AGGRESSIVE
            }
            driving_style = self.user_behavior.get_driving_style()
            
            activity = {
                'type': 'driving',
                'duration': timedelta(hours=trip_time),
                'mode': style_map.get(driving_style, DrivingMode.MIXED)
            }
        
        return activity
    
    def _get_driving_current(self, mode: DrivingMode) -> float:
        """Get instantaneous driving current based on mode."""
        # Base current draw by mode
        base_currents = {
            DrivingMode.CITY: -80,      # Stop and go
            DrivingMode.HIGHWAY: -120,   # Steady high speed
            DrivingMode.AGGRESSIVE: -180,  # Hard acceleration
            DrivingMode.ECO: -60,        # Efficient driving
            DrivingMode.MIXED: -100      # Mixed driving
        }
        
        base = base_currents.get(mode, -100)
        # Add realistic variation
        variation = np.random.normal(0, abs(base) * 0.2)
        
        return base + variation
    
    def _get_charging_current(self, charging_type: ChargingType, current_soc: float, target_soc: float) -> float:
        """Calculate appropriate charging current based on SoC and charger type."""
        if current_soc >= target_soc:
            return 0
        
        specs = self.charging_gen.CHARGING_SPECS[charging_type]
        # Calculate max current from power and voltage
        max_power_w = specs['max_power_kw'] * 1000
        max_current = max_power_w / self.specs.nominal_voltage
        
        # CC-CV logic: reduce current as we approach target
        if current_soc < target_soc - 10:
            # Constant current phase
            return max_current
        else:
            # Taper current as we approach target (CV phase)
            remaining = target_soc - current_soc
            taper_factor = remaining / 10
            return max_current * taper_factor
    
    def _create_telemetry_record(self, timestamp: datetime) -> Dict:
        """Create a telemetry record from current battery state."""
        state = self.battery.get_state()
        
        # Add some realistic sensor noise
        for metric in ['voltage', 'current', 'temperature']:
            if metric in state:
                noise = np.random.normal(0, 0.01 * abs(state[metric]))
                state[metric] += noise
        
        record = {
            'time': timestamp,
            'vehicle_id': self.vehicle_id,
            'soc_percent': round(state['soc_percent'], 2),
            'soh_percent': round(state['soh_percent'], 2),
            'voltage': round(state['voltage'], 2),
            'current': round(state['current'], 2),
            'temperature': round(state['temperature'], 2),
            'power': round(state['voltage'] * state['current'] / 1000, 2),  # kW
            'is_charging': False,
            'is_driving': False,
            'speed_kmh': 0.0
        }
        
        return record
    
    def _inject_daily_anomalies(
        self, 
        telemetry_records: List[Dict], 
        date: datetime
    ) -> Tuple[List[Dict], List[AnomalyEvent]]:
        """Inject anomalies into telemetry data."""
        records_df = pd.DataFrame(telemetry_records)
        events = []
        
        # Random chance of anomalies
        if random.random() < 0.3:  # 30% chance of anomaly day
            num_anomalies = random.randint(1, 3)
            
            for _ in range(num_anomalies):
                anomaly_type = random.choice(['thermal', 'sensor', 'charging'])
                
                if anomaly_type == 'thermal':
                    # Find a driving period
                    driving_mask = records_df['is_driving']
                    if driving_mask.any():
                        driving_indices = records_df[driving_mask].index.tolist()
                        if len(driving_indices) > 100:
                            start_idx = random.choice(driving_indices[:-100])
                            event = self.anomaly_gen.generate_thermal_event(start_idx, 300)
                            events.append(event)
                            
                            # Apply temperature spike
                            for i in range(start_idx, min(start_idx + 300, len(telemetry_records))):
                                telemetry_records[i]['temperature'] += event.severity * 10
                
                elif anomaly_type == 'sensor':
                    # Random sensor glitch
                    idx = random.randint(0, len(telemetry_records) - 1)
                    event = self.anomaly_gen.generate_sensor_glitch(idx)
                    events.append(event)
                    
                    # Apply glitch
                    telemetry_records[idx]['voltage'] *= random.uniform(0.5, 1.5)
                
                elif anomaly_type == 'charging':
                    # Find a charging period
                    charging_mask = records_df['is_charging']
                    if charging_mask.any():
                        charging_indices = records_df[charging_mask].index.tolist()
                        if charging_indices:
                            idx = random.choice(charging_indices)
                            event = self.anomaly_gen.generate_charging_anomaly(idx, 'slow_charge')
                            events.append(event)
                            
                            # Reduce charging current
                            for i in range(idx, min(idx + 600, len(telemetry_records))):
                                if telemetry_records[i]['is_charging']:
                                    telemetry_records[i]['current'] *= 0.5
        
        return telemetry_records, events
    
    def _anomaly_to_dict(self, event: AnomalyEvent) -> Dict:
        """Convert AnomalyEvent to dictionary for DataFrame."""
        return {
            'vehicle_id': self.vehicle_id,
            'start_time': event.start_time,
            'end_time': event.end_time,
            'anomaly_type': event.anomaly_type,
            'severity': event.severity,
            'description': event.description,
            'detected': True,
            'labeled_by': 'simulator'
        }


def run_simulation_v2(
    vehicle_id: str,
    days: int = 7,
    user_profile: Optional[UserProfile] = None,
    include_anomalies: bool = True,
    save_to_db: bool = True,
    seed: Optional[int] = None
) -> Tuple[pd.DataFrame, pd.DataFrame]:
    """
    Run multi-day simulation with enhanced charging logic.
    
    Args:
        vehicle_id: Vehicle ID from VEHICLE_SPECS
        days: Number of days to simulate
        user_profile: User behavior profile (random if None)
        include_anomalies: Whether to include anomalies
        save_to_db: Whether to save results to database
        seed: Random seed for reproducibility
        
    Returns:
        Tuple of (telemetry_df, events_df)
    """
    profile_name = user_profile.value if user_profile else "random"
    print(f"Starting simulation for {vehicle_id} ({profile_name} profile) over {days} days...")
    
    simulator = EVBatterySimulatorV2(vehicle_id, user_profile, seed)
    
    all_telemetry = []
    all_events = []
    
    start_date = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
    
    for day in range(days):
        print(f"Simulating day {day + 1}/{days}: {(start_date + timedelta(days=day)).strftime('%Y-%m-%d')}")
        
        # Simulate one day
        result = simulator.simulate_day(
            date=start_date + timedelta(days=day),
            include_anomalies=include_anomalies
        )
        
        all_telemetry.append(result['telemetry'])
        if not result['events'].empty:
            all_events.append(result['events'])
    
    # Combine all days
    telemetry_df = pd.concat(all_telemetry, ignore_index=True)
    events_df = pd.concat(all_events, ignore_index=True) if all_events else pd.DataFrame()
    
    print(f"\nSimulation complete!")
    print(f"Generated {len(telemetry_df):,} telemetry records")
    print(f"Generated {len(events_df)} anomaly events")
    
    # Save to database if requested
    if save_to_db and len(telemetry_df) > 0:
        print("\nSaving to database...")
        # Convert time column to index for batch insert
        telemetry_df.set_index('time', inplace=True)
        success = insert_telemetry_batch(telemetry_df)
        if success:
            print("Data successfully saved to TimescaleDB!")
        else:
            print("Failed to save data to database.")
    
    return telemetry_df, events_df


# Test the enhanced simulator
if __name__ == "__main__":
    # Quick test with cautious driver
    print("Testing enhanced simulator with dynamic charging...")
    telemetry_df, events_df = run_simulation_v2(
        vehicle_id='VEH001',
        days=1,
        user_profile=UserProfile.CAUTIOUS,
        include_anomalies=False,
        save_to_db=False,
        seed=42
    )
    
    # Analyze results
    print(f"\nResults:")
    print(f"Min SoC: {telemetry_df['soc_percent'].min():.1f}%")
    print(f"Max SoC: {telemetry_df['soc_percent'].max():.1f}%")
    print(f"Charging time: {telemetry_df['is_charging'].sum() / 3600:.1f} hours")
    print(f"Driving time: {telemetry_df['is_driving'].sum() / 3600:.1f} hours")