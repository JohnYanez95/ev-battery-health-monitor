"""
Main EV battery simulation orchestrator.
Combines battery model, driving patterns, charging patterns, and anomalies
to generate realistic telemetry data for the EV Battery Health Monitor.
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


class EVBatterySimulator:
    """Orchestrates complete EV battery simulation scenarios."""
    
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
        Simulate a full day of vehicle operation.
        
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
        schedule = self._generate_daily_schedule(is_weekend)
        
        telemetry_records = []
        events = []
        
        current_time = date
        
        for activity in schedule:
            activity_type = activity['type']
            duration = activity['duration']
            samples = int(duration.total_seconds() / dt)
            
            # Get ambient temperature for this period
            hour = current_time.hour
            self.battery.ambient_temp = ambient_temp_profile[hour]
            
            if activity_type == 'idle':
                # Vehicle parked - minimal battery drain
                for _ in range(samples):
                    self.battery.apply_current(0, dt)
                    telemetry_records.append(self._create_telemetry_record(current_time))
                    current_time += timedelta(seconds=dt)
                    
            elif activity_type == 'driving':
                # Generate driving pattern
                mode = activity.get('mode', DrivingMode.MIXED)
                current_profile = self.driving_gen.generate_mixed_driving(
                    int(duration.total_seconds()), dt
                )
                
                # Apply driving current profile
                for current in current_profile:
                    self.battery.apply_current(current, dt)
                    record = self._create_telemetry_record(current_time)
                    record['is_driving'] = True
                    record['speed_kmh'] = abs(current) * 0.5  # Simplified speed estimate
                    telemetry_records.append(record)
                    current_time += timedelta(seconds=dt)
                    
            elif activity_type == 'charging':
                # Generate charging pattern
                charging_type = activity.get('charging_type', ChargingType.AC_L2)
                target_soc = activity.get('target_soc', 80.0)
                
                current_profile, soc_profile, completed = self.charging_gen.generate_cc_cv_profile(
                    charging_type=charging_type,
                    initial_soc=self.battery.soc,
                    target_soc=target_soc,
                    battery_capacity_kwh=self.battery.effective_capacity_kwh,
                    duration_seconds=int(duration.total_seconds()),
                    dt=dt
                )
                
                # Apply charging current profile
                for current in current_profile:
                    self.battery.apply_current(current, dt)
                    record = self._create_telemetry_record(current_time)
                    record['is_charging'] = current > 0
                    telemetry_records.append(record)
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
    
    def _generate_daily_schedule(self, is_weekend: bool = False) -> List[Dict]:
        """Generate a realistic daily activity schedule based on user profile."""
        schedule = []
        behavior = self.user_behavior.behavior
        
        # Get wake time based on profile
        wake_time = self.user_behavior.get_wake_time(is_weekend)
        current_hour = 0
        
        # Sleep period
        wake_hour = wake_time.hour
        schedule.append({'type': 'idle', 'duration': timedelta(hours=wake_hour)})
        current_hour = wake_hour
        
        # Build day based on user profile
        if self.user_profile == UserProfile.COMMUTER and not is_weekend:
            # Regular commute pattern
            schedule.extend(self._generate_commuter_day(current_hour))
        elif self.user_profile == UserProfile.WEEKEND_WARRIOR and is_weekend:
            # Long weekend trips
            schedule.extend(self._generate_weekend_warrior_day(current_hour))
        else:
            # Generate based on profile characteristics
            schedule.extend(self._generate_profile_based_day(current_hour, is_weekend))
        
        # Check if charging is needed
        should_charge, target_soc = self.user_behavior.should_charge(
            self.battery.soc, 
            datetime.now().hour
        )
        
        if should_charge:
            # Determine charging type based on urgency
            urgency = max(0, (behavior.preferred_soc_min - self.battery.soc) / behavior.preferred_soc_min)
            charging_type_str = self.user_behavior.get_charging_type_preference(urgency)
            charging_type = getattr(ChargingType, charging_type_str)
            
            # Calculate charging duration needed
            energy_needed = self.battery.effective_capacity_kwh * (target_soc - self.battery.soc) / 100
            charging_power = self.charging_gen.CHARGING_SPECS[charging_type]['max_power_kw']
            hours_needed = energy_needed / (charging_power * 0.9)  # 90% efficiency
            
            schedule.append({
                'type': 'charging',
                'duration': timedelta(hours=min(hours_needed + 0.5, 8)),  # Add buffer, cap at 8h
                'charging_type': charging_type,
                'target_soc': target_soc
            })
        
        # Fill remaining time with idle
        total_duration = timedelta()
        for s in schedule:
            total_duration += s['duration']
        if total_duration < timedelta(hours=24):
            remaining = timedelta(hours=24) - total_duration
            schedule.append({'type': 'idle', 'duration': remaining})
            
        return schedule
    
    def _generate_commuter_day(self, start_hour: int) -> List[Dict]:
        """Generate schedule for a commuter."""
        activities = []
        
        # Morning commute
        commute_distance = self.user_behavior.get_trip_distance(False) / 2  # One way
        commute_time = commute_distance / 50  # Assume 50 km/h average
        
        activities.append({
            'type': 'driving',
            'duration': timedelta(hours=commute_time),
            'mode': DrivingMode.MIXED,
            'purpose': 'commute'
        })
        
        # Work parking
        activities.append({'type': 'idle', 'duration': timedelta(hours=9)})
        
        # Evening commute
        activities.append({
            'type': 'driving',
            'duration': timedelta(hours=commute_time),
            'mode': DrivingMode.MIXED,
            'purpose': 'commute'
        })
        
        return activities
    
    def _generate_weekend_warrior_day(self, start_hour: int) -> List[Dict]:
        """Generate schedule for a weekend warrior."""
        activities = []
        
        # Morning prep
        activities.append({'type': 'idle', 'duration': timedelta(hours=2)})
        
        # Long trip
        trip_distance = self.user_behavior.get_trip_distance(True)
        trip_time = trip_distance / 80  # Highway speeds
        
        activities.append({
            'type': 'driving',
            'duration': timedelta(hours=trip_time / 2),
            'mode': DrivingMode.HIGHWAY,
            'purpose': 'recreation'
        })
        
        # Activity break
        activities.append({'type': 'idle', 'duration': timedelta(hours=3)})
        
        # Return trip
        activities.append({
            'type': 'driving',
            'duration': timedelta(hours=trip_time / 2),
            'mode': DrivingMode.HIGHWAY,
            'purpose': 'recreation'
        })
        
        return activities
    
    def _generate_profile_based_day(self, start_hour: int, is_weekend: bool) -> List[Dict]:
        """Generate activities based on general profile behavior."""
        activities = []
        remaining_hours = 24 - start_hour
        hours_used = 0
        
        # Generate trips throughout the day
        for hour in range(start_hour, 24):
            if hours_used >= remaining_hours - 2:  # Leave time for final idle
                break
                
            if self.user_behavior.should_drive_now(hour, is_weekend):
                # Generate a trip
                trip_distance = self.user_behavior.get_trip_distance(is_weekend) / 4  # Partial day trip
                trip_time = max(0.25, trip_distance / 40)  # City speeds
                
                # Driving style based on profile
                style_map = {
                    'eco': DrivingMode.ECO,
                    'normal': DrivingMode.CITY,
                    'aggressive': DrivingMode.AGGRESSIVE
                }
                driving_style = self.user_behavior.get_driving_style()
                
                activities.append({
                    'type': 'driving',
                    'duration': timedelta(hours=trip_time),
                    'mode': style_map.get(driving_style, DrivingMode.MIXED)
                })
                hours_used += trip_time
                
                # Idle after trip
                idle_time = random.uniform(0.5, 2)
                activities.append({'type': 'idle', 'duration': timedelta(hours=idle_time)})
                hours_used += idle_time
        
        return activities
    
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
            'soc_percent': state['soc_percent'],
            'voltage': state['voltage'],
            'current': state['current'],
            'temperature': state['temperature'],
            'energy_kwh': state['energy_kwh'],
            'soh_percent': state['soh_percent'],
            'estimated_range_km': state['estimated_range_km'],
            'is_charging': False,
            'is_driving': False,
            'speed_kmh': 0.0,
            'ambient_temp': self.battery.ambient_temp,
            'data_quality': 100,
            'location_lat': None,  # Add missing fields
            'location_lon': None
        }
        
        # Cell temperature simulation (simplified)
        temp_variation = np.random.normal(0, 2)
        record['max_cell_temp'] = record['temperature'] + abs(temp_variation)
        record['min_cell_temp'] = record['temperature'] - abs(temp_variation)
        
        return record
    
    def _inject_daily_anomalies(
        self,
        telemetry_records: List[Dict],
        date: datetime
    ) -> Tuple[List[Dict], List[AnomalyEvent]]:
        """Inject realistic anomalies into daily data."""
        anomalies = []
        
        # Probability of each anomaly type per day
        anomaly_probabilities = {
            'thermal_event': 0.05,      # 5% chance
            'sensor_glitch': 0.10,      # 10% chance
            'charging_anomaly': 0.08,   # 8% chance
            'rapid_degradation': 0.02   # 2% chance
        }
        
        # Check for each anomaly type
        if random.random() < anomaly_probabilities['thermal_event']:
            # Find a driving period for thermal event
            driving_periods = self._find_activity_periods(telemetry_records, 'is_driving', True)
            if driving_periods:
                period = random.choice(driving_periods)
                start_idx = period[0] + random.randint(0, max(0, period[1] - period[0] - 300))
                
                # Generate thermal anomaly
                duration = random.randint(180, 600)  # 3-10 minutes
                temp_profile, event = self.anomaly_gen.generate_thermal_event(
                    normal_temp=telemetry_records[start_idx]['temperature'],
                    duration_seconds=duration,
                    severity=random.choice(['low', 'medium', 'high'])
                )
                
                # Apply to records
                for i, temp in enumerate(temp_profile):
                    if start_idx + i < len(telemetry_records):
                        telemetry_records[start_idx + i]['temperature'] = temp
                        telemetry_records[start_idx + i]['max_cell_temp'] = temp + 2
                        telemetry_records[start_idx + i]['min_cell_temp'] = temp - 2
                        
                anomalies.append(event)
        
        if random.random() < anomaly_probabilities['sensor_glitch']:
            # Random sensor glitch
            glitch_idx = random.randint(0, len(telemetry_records) - 1)
            glitch_values, event = self.anomaly_gen.generate_sensor_glitch(
                normal_value=telemetry_records[glitch_idx]['voltage'],
                glitch_type=random.choice(['spike', 'dropout', 'noise']),
                duration_samples=random.randint(1, 5)
            )
            
            # Apply glitch
            for i, val in enumerate(glitch_values):
                if glitch_idx + i < len(telemetry_records):
                    telemetry_records[glitch_idx + i]['voltage'] = val
                    
            anomalies.append(event)
        
        return telemetry_records, anomalies
    
    def _find_activity_periods(
        self,
        records: List[Dict],
        field: str,
        value: any
    ) -> List[Tuple[int, int]]:
        """Find continuous periods where field equals value."""
        periods = []
        start = None
        
        for i, record in enumerate(records):
            if record.get(field) == value:
                if start is None:
                    start = i
            else:
                if start is not None:
                    periods.append((start, i))
                    start = None
                    
        if start is not None:
            periods.append((start, len(records)))
            
        return periods
    
    def _anomaly_to_dict(self, event: AnomalyEvent) -> Dict:
        """Convert AnomalyEvent to dictionary for DataFrame."""
        return {
            'vehicle_id': self.vehicle_id,
            'event_type': event.event_type,
            'start_time': event.start_time,
            'end_time': event.end_time,
            'severity': event.severity,
            'description': event.description,
            'affected_metrics': ','.join(event.affected_metrics)
        }
    
    def save_to_database(self, telemetry_df: pd.DataFrame, events_df: pd.DataFrame) -> bool:
        """
        Save simulation data to TimescaleDB.
        
        Args:
            telemetry_df: DataFrame with telemetry records
            events_df: DataFrame with anomaly events
            
        Returns:
            Success status
        """
        try:
            # Convert DataFrame to list of dicts for batch insert
            telemetry_records = telemetry_df.to_dict('records')
            
            # Insert telemetry data in batches
            batch_size = 1000
            total_inserted = 0
            
            for i in range(0, len(telemetry_records), batch_size):
                batch = telemetry_records[i:i + batch_size]
                rows_inserted = insert_telemetry_batch(batch)
                total_inserted += rows_inserted
                
            print(f"Inserted {total_inserted} telemetry records")
            
            # Insert anomaly events
            if not events_df.empty:
                for _, event in events_df.iterrows():
                    query = """
                        INSERT INTO anomaly_events (
                            vehicle_id, start_time, end_time, event_type,
                            severity, description
                        ) VALUES (%s, %s, %s, %s, %s, %s)
                    """
                    execute_query(query, (
                        event['vehicle_id'],
                        event['start_time'],
                        event['end_time'],
                        event['event_type'],
                        event['severity'],
                        event['description']
                    ))
                    
                print(f"Inserted {len(events_df)} anomaly events")
                
            return True
            
        except Exception as e:
            print(f"Error saving to database: {e}")
            return False


def run_simulation(
    vehicle_id: str,
    days: int = 7,
    user_profile: Optional[UserProfile] = None,
    include_anomalies: bool = True,
    save_to_db: bool = True,
    seed: Optional[int] = None
):
    """
    Run a multi-day simulation for a vehicle.
    
    Args:
        vehicle_id: Vehicle to simulate
        days: Number of days to simulate
        include_anomalies: Whether to include anomalies
        save_to_db: Whether to save to database
        seed: Random seed for reproducibility
    """
    profile_name = user_profile.value if user_profile else "random"
    print(f"Starting simulation for {vehicle_id} ({profile_name} profile) over {days} days...")
    
    simulator = EVBatterySimulator(vehicle_id, user_profile, seed)
    
    all_telemetry = []
    all_events = []
    
    start_date = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
    
    for day in range(days):
        current_date = start_date + timedelta(days=day)
        print(f"Simulating day {day + 1}/{days}: {current_date.date()}")
        
        # Simulate one day
        results = simulator.simulate_day(
            date=current_date,
            include_anomalies=include_anomalies,
            dt=1.0  # 1 Hz data
        )
        
        all_telemetry.append(results['telemetry'])
        if not results['events'].empty:
            all_events.append(results['events'])
    
    # Combine all days
    combined_telemetry = pd.concat(all_telemetry, ignore_index=True)
    combined_events = pd.concat(all_events, ignore_index=True) if all_events else pd.DataFrame()
    
    print(f"\nSimulation complete!")
    print(f"Generated {len(combined_telemetry)} telemetry records")
    print(f"Generated {len(combined_events)} anomaly events")
    
    if save_to_db:
        print("\nSaving to database...")
        success = simulator.save_to_database(combined_telemetry, combined_events)
        if success:
            print("Data saved successfully!")
        else:
            print("Failed to save data to database")
            
    return combined_telemetry, combined_events


if __name__ == "__main__":
    # Example: Run simulations with different user profiles
    test_configs = [
        ('VEH001', UserProfile.CAUTIOUS),      # Tesla with cautious driver
        ('VEH001', UserProfile.NIGHT_OWL),     # Tesla with night owl
        ('VEH002', UserProfile.ECO_CONSCIOUS), # Leaf with eco driver
        ('VEH002', UserProfile.SPONTANEOUS),   # Leaf with spontaneous driver
    ]
    
    for vehicle_id, profile in test_configs:
        telemetry_df, events_df = run_simulation(
            vehicle_id=vehicle_id,
            days=3,  # Shorter for demo
            user_profile=profile,
            include_anomalies=True,
            save_to_db=True,
            seed=None  # Random for variety
        )
        
        print(f"\nSummary for {vehicle_id} with {profile.value} driver:")
        print(f"Average SoC: {telemetry_df['soc_percent'].mean():.1f}%")
        print(f"Min SoC reached: {telemetry_df['soc_percent'].min():.1f}%")
        print(f"Charging sessions: {telemetry_df['is_charging'].sum() // 3600} hours")
        print(f"Total distance: ~{telemetry_df['speed_kmh'].sum() * 1/3600:.1f} km")
        print(f"Anomalies: {len(events_df)}")
        print("-" * 60)