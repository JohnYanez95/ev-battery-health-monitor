"""
Anomaly generator - creates realistic battery anomalies based on industry research.
Includes thermal events, capacity fade, sensor glitches, and charging anomalies.
"""

import numpy as np
from typing import List, Dict, Tuple, Optional
from dataclasses import dataclass
from datetime import datetime, timedelta
import random


@dataclass
class AnomalyEvent:
    """Represents an anomaly event with metadata."""
    event_type: str
    start_time: datetime
    end_time: datetime
    severity: str  # low, medium, high, critical
    description: str
    affected_metrics: List[str]
    parameters: Dict[str, float]


class AnomalyGenerator:
    """Generates various types of battery anomalies."""
    
    def __init__(self, seed: Optional[int] = None):
        if seed:
            np.random.seed(seed)
            random.seed(seed)
            
    def generate_thermal_event(
        self,
        normal_temp: float,
        duration_seconds: int,
        severity: str = "medium"
    ) -> Tuple[List[float], AnomalyEvent]:
        """
        Generate thermal event (cooling system failure).
        Based on research: temperature rising > Y°C/min indicates failure.
        
        Args:
            normal_temp: Normal operating temperature
            duration_seconds: Duration of the event
            severity: Event severity level
            
        Returns:
            Tuple of (temperature_profile, anomaly_event)
        """
        severity_params = {
            "low": {"rate": 0.5, "peak": normal_temp + 10},
            "medium": {"rate": 1.0, "peak": normal_temp + 20},
            "high": {"rate": 2.0, "peak": normal_temp + 30},
            "critical": {"rate": 3.0, "peak": normal_temp + 40}
        }
        
        params = severity_params[severity]
        temp_profile = []
        
        # Temperature rise phase (first half)
        rise_duration = duration_seconds // 2
        for t in range(rise_duration):
            # Exponential rise with some noise
            temp_rise = params["rate"] * t / 60  # °C/min to °C/s
            temp = normal_temp + temp_rise * (1 + np.random.normal(0, 0.05))
            temp = min(temp, params["peak"])
            temp_profile.append(temp)
            
        # Temperature fall phase (second half)
        fall_duration = duration_seconds - rise_duration
        peak_temp = temp_profile[-1]
        for t in range(fall_duration):
            # Exponential decay
            temp_fall = (peak_temp - normal_temp) * np.exp(-t / (fall_duration / 3))
            temp = normal_temp + temp_fall + np.random.normal(0, 1)
            temp_profile.append(temp)
            
        # Create anomaly event
        event = AnomalyEvent(
            event_type="thermal_event",
            start_time=datetime.now(),
            end_time=datetime.now() + timedelta(seconds=duration_seconds),
            severity=severity,
            description=f"Cooling system failure - temperature rose at {params['rate']}°C/min",
            affected_metrics=["temperature", "max_cell_temp", "min_cell_temp"],
            parameters={
                "peak_temperature": params["peak"],
                "rise_rate": params["rate"],
                "normal_temp": normal_temp
            }
        )
        
        return temp_profile, event
    
    def generate_capacity_fade(
        self,
        initial_soh: float,
        days: int,
        degradation_rate: float = 0.02  # 2% per year nominal
    ) -> Tuple[List[float], AnomalyEvent]:
        """
        Generate gradual capacity fade over time.
        Based on research: average 2.3% annual degradation.
        
        Args:
            initial_soh: Starting State of Health (%)
            days: Number of days to simulate
            degradation_rate: Annual degradation rate (fraction)
            
        Returns:
            Tuple of (soh_profile, anomaly_event)
        """
        # Daily degradation rate
        daily_rate = degradation_rate / 365
        
        soh_profile = []
        current_soh = initial_soh
        
        for day in range(days):
            # Add daily variation and degradation
            daily_degradation = daily_rate * (1 + np.random.normal(0, 0.1))
            
            # Accelerate degradation if battery is stressed (simplified model)
            if random.random() < 0.1:  # 10% chance of stressful day
                daily_degradation *= 2
                
            current_soh -= daily_degradation
            soh_profile.append(max(current_soh, 70))  # Floor at 70%
            
        total_degradation = initial_soh - soh_profile[-1]
        
        event = AnomalyEvent(
            event_type="capacity_fade",
            start_time=datetime.now(),
            end_time=datetime.now() + timedelta(days=days),
            severity="low" if total_degradation < 5 else "medium",
            description=f"Battery degraded {total_degradation:.1f}% over {days} days",
            affected_metrics=["soh_percent", "energy_kwh", "estimated_range_km"],
            parameters={
                "initial_soh": initial_soh,
                "final_soh": soh_profile[-1],
                "degradation_rate": degradation_rate
            }
        )
        
        return soh_profile, event
    
    def generate_sensor_glitch(
        self,
        normal_value: float,
        glitch_type: str = "spike",
        duration_samples: int = 1
    ) -> Tuple[List[float], AnomalyEvent]:
        """
        Generate sensor glitches (unrealistic jumps in data).
        
        Args:
            normal_value: Normal sensor reading
            glitch_type: Type of glitch (spike, dropout, noise)
            duration_samples: How long the glitch lasts
            
        Returns:
            Tuple of (glitched_values, anomaly_event)
        """
        glitched_values = []
        
        if glitch_type == "spike":
            # Sudden spike to unrealistic value
            spike_magnitude = normal_value * np.random.uniform(5, 10)
            for i in range(duration_samples):
                if i == 0:
                    glitched_values.append(spike_magnitude)
                else:
                    # Decay back to normal
                    decay = np.exp(-i / (duration_samples / 3))
                    glitched_values.append(normal_value + (spike_magnitude - normal_value) * decay)
                    
        elif glitch_type == "dropout":
            # Sensor reads zero or very low
            for i in range(duration_samples):
                glitched_values.append(np.random.uniform(0, normal_value * 0.1))
                
        elif glitch_type == "noise":
            # High frequency noise
            for i in range(duration_samples):
                noise = np.random.normal(0, normal_value * 0.5)
                glitched_values.append(normal_value + noise)
                
        event = AnomalyEvent(
            event_type="sensor_glitch",
            start_time=datetime.now(),
            end_time=datetime.now() + timedelta(seconds=duration_samples),
            severity="low",
            description=f"Sensor {glitch_type} - unrealistic data readings",
            affected_metrics=["voltage", "current"],  # Typically affects electrical measurements
            parameters={
                "glitch_type": glitch_type,
                "normal_value": normal_value,
                "max_deviation": max(abs(v - normal_value) for v in glitched_values)
            }
        )
        
        return glitched_values, event
    
    def generate_rapid_degradation(
        self,
        normal_soc_rate: float,
        duration_seconds: int,
        degradation_factor: float = 3.0
    ) -> Tuple[List[float], AnomalyEvent]:
        """
        Generate rapid degradation event (cell failure).
        SoC drops faster than normal, indicating internal damage.
        
        Args:
            normal_soc_rate: Normal SoC discharge rate (%/second)
            duration_seconds: Duration of rapid degradation
            degradation_factor: How much faster than normal
            
        Returns:
            Tuple of (soc_drop_rates, anomaly_event)
        """
        rapid_rate = normal_soc_rate * degradation_factor
        soc_rates = []
        
        for t in range(duration_seconds):
            # Add some variation
            rate = rapid_rate * (1 + np.random.normal(0, 0.1))
            soc_rates.append(rate)
            
        total_soc_loss = sum(soc_rates)
        
        event = AnomalyEvent(
            event_type="rapid_degradation",
            start_time=datetime.now(),
            end_time=datetime.now() + timedelta(seconds=duration_seconds),
            severity="high" if degradation_factor > 3 else "medium",
            description=f"Abnormal discharge rate - possible cell failure",
            affected_metrics=["soc_percent", "voltage", "estimated_range_km"],
            parameters={
                "normal_rate": normal_soc_rate,
                "rapid_rate": rapid_rate,
                "total_soc_loss": total_soc_loss
            }
        )
        
        return soc_rates, event
    
    def generate_charging_anomaly(
        self,
        expected_current: float,
        anomaly_type: str = "slow_charge",
        duration_seconds: int = 300
    ) -> Tuple[List[float], AnomalyEvent]:
        """
        Generate charging anomalies (slow charging, interruptions).
        
        Args:
            expected_current: Expected charging current
            anomaly_type: Type of charging issue
            duration_seconds: Duration of anomaly
            
        Returns:
            Tuple of (current_profile, anomaly_event)
        """
        current_profile = []
        
        if anomaly_type == "slow_charge":
            # Charging at reduced rate
            reduction_factor = np.random.uniform(0.3, 0.6)
            for t in range(duration_seconds):
                current = expected_current * reduction_factor
                # Add some variation
                current *= (1 + np.random.normal(0, 0.05))
                current_profile.append(current)
                
        elif anomaly_type == "intermittent":
            # Charging keeps cutting out
            for t in range(duration_seconds):
                if (t // 30) % 2 == 0:  # On for 30s, off for 30s
                    current = expected_current * (1 + np.random.normal(0, 0.02))
                else:
                    current = 0
                current_profile.append(current)
                
        elif anomaly_type == "no_charge":
            # Plugged in but not charging
            for t in range(duration_seconds):
                current_profile.append(0)
                
        event = AnomalyEvent(
            event_type="charging_anomaly",
            start_time=datetime.now(),
            end_time=datetime.now() + timedelta(seconds=duration_seconds),
            severity="medium" if anomaly_type == "no_charge" else "low",
            description=f"Charging issue - {anomaly_type.replace('_', ' ')}",
            affected_metrics=["current", "is_charging", "soc_percent"],
            parameters={
                "expected_current": expected_current,
                "anomaly_type": anomaly_type,
                "average_current": np.mean(current_profile)
            }
        )
        
        return current_profile, event
    
    def inject_anomalies(
        self,
        base_data: Dict[str, List[float]],
        anomaly_events: List[Tuple[str, int, Dict]],
        dt: float = 1.0
    ) -> Tuple[Dict[str, List[float]], List[AnomalyEvent]]:
        """
        Inject multiple anomalies into base telemetry data.
        
        Args:
            base_data: Dictionary of metric timeseries
            anomaly_events: List of (anomaly_type, start_time_idx, params)
            dt: Time step in seconds
            
        Returns:
            Tuple of (modified_data, anomaly_events_list)
        """
        modified_data = {k: v.copy() for k, v in base_data.items()}
        events = []
        
        for anomaly_type, start_idx, params in anomaly_events:
            if anomaly_type == "thermal":
                temp_profile, event = self.generate_thermal_event(
                    normal_temp=base_data["temperature"][start_idx],
                    duration_seconds=params.get("duration", 300),
                    severity=params.get("severity", "medium")
                )
                # Inject into data
                for i, temp in enumerate(temp_profile):
                    if start_idx + i < len(modified_data["temperature"]):
                        modified_data["temperature"][start_idx + i] = temp
                        
            elif anomaly_type == "sensor_glitch":
                glitch_values, event = self.generate_sensor_glitch(
                    normal_value=base_data["voltage"][start_idx],
                    glitch_type=params.get("glitch_type", "spike"),
                    duration_samples=params.get("duration", 1)
                )
                # Inject into voltage data
                for i, val in enumerate(glitch_values):
                    if start_idx + i < len(modified_data["voltage"]):
                        modified_data["voltage"][start_idx + i] = val
                        
            events.append(event)
            
        return modified_data, events