"""
Thermal Safety Management System for EV Battery
Implements temperature monitoring, warnings, and emergency shutoffs
Based on industry standards for lithium-ion battery safety
"""

import logging
from datetime import datetime
from typing import Optional, Tuple, Dict
from enum import Enum
from dataclasses import dataclass


# Configure logging for thermal events
logging.basicConfig(level=logging.INFO)
thermal_logger = logging.getLogger('thermal_safety')


class ThermalStatus(Enum):
    """Battery thermal status levels"""
    NORMAL = "normal"
    WARNING = "warning"
    CRITICAL = "critical"
    SHUTDOWN = "shutdown"


@dataclass
class ThermalThresholds:
    """Temperature thresholds for different safety levels"""
    warning_temp: float = 50.0      # Start logging warnings
    critical_temp: float = 55.0     # Critical warning, prepare for shutdown
    shutdown_temp: float = 60.0     # Emergency shutdown
    recovery_temp: float = 45.0     # Temperature to resume after shutdown
    

class ThermalSafetyManager:
    """
    Manages battery thermal safety with multi-level protection.
    
    Temperature thresholds:
    - Normal: < 50°C
    - Warning: 50-55°C (log warnings, notify user)
    - Critical: 55-60°C (urgent warnings, reduce power)
    - Shutdown: ≥ 60°C (emergency stop all operations)
    """
    
    def __init__(self, vehicle_id: str, thresholds: Optional[ThermalThresholds] = None):
        self.vehicle_id = vehicle_id
        self.thresholds = thresholds or ThermalThresholds()
        self.current_status = ThermalStatus.NORMAL
        self.shutdown_active = False
        self.warning_count = 0
        self.event_history = []
        
    def check_temperature(self, current_temp: float, timestamp: Optional[datetime] = None) -> Dict:
        """
        Check current temperature and determine safety status.
        
        Args:
            current_temp: Current battery temperature in °C
            timestamp: Current timestamp (defaults to now)
            
        Returns:
            Dict with status, actions, and any warnings/errors
        """
        if timestamp is None:
            timestamp = datetime.now()
            
        previous_status = self.current_status
        result = {
            'temperature': current_temp,
            'status': ThermalStatus.NORMAL,
            'action_required': False,
            'power_limit': 1.0,  # 1.0 = no limit, 0.0 = full shutdown
            'message': '',
            'timestamp': timestamp
        }
        
        # Check if in shutdown recovery mode
        if self.shutdown_active:
            if current_temp <= self.thresholds.recovery_temp:
                self.shutdown_active = False
                self.current_status = ThermalStatus.NORMAL
                message = f"Temperature recovered to {current_temp:.1f}°C - Resuming normal operation"
                thermal_logger.info(f"[{self.vehicle_id}] {message}")
                self._log_event('recovery', current_temp, timestamp, message)
                result['message'] = message
            else:
                result['status'] = ThermalStatus.SHUTDOWN
                result['power_limit'] = 0.0
                result['action_required'] = True
                result['message'] = f"Shutdown active - Waiting for temp < {self.thresholds.recovery_temp}°C"
                return result
        
        # Determine current thermal status
        if current_temp >= self.thresholds.shutdown_temp:
            # EMERGENCY SHUTDOWN
            self.current_status = ThermalStatus.SHUTDOWN
            self.shutdown_active = True
            result['status'] = ThermalStatus.SHUTDOWN
            result['power_limit'] = 0.0
            result['action_required'] = True
            message = f"EMERGENCY SHUTDOWN! Temperature {current_temp:.1f}°C exceeds {self.thresholds.shutdown_temp}°C"
            
            thermal_logger.critical(f"[{self.vehicle_id}] {message}")
            self._log_event('shutdown', current_temp, timestamp, message)
            result['message'] = message
            
        elif current_temp >= self.thresholds.critical_temp:
            # CRITICAL WARNING
            self.current_status = ThermalStatus.CRITICAL
            result['status'] = ThermalStatus.CRITICAL
            result['power_limit'] = 0.3  # Severely limit power
            result['action_required'] = True
            message = f"CRITICAL: Temperature {current_temp:.1f}°C approaching shutdown ({self.thresholds.shutdown_temp}°C)"
            
            thermal_logger.error(f"[{self.vehicle_id}] {message}")
            self._log_event('critical', current_temp, timestamp, message)
            result['message'] = message
            
        elif current_temp >= self.thresholds.warning_temp:
            # WARNING
            self.current_status = ThermalStatus.WARNING
            result['status'] = ThermalStatus.WARNING
            result['power_limit'] = 0.7  # Moderate power reduction
            self.warning_count += 1
            message = f"WARNING: Temperature {current_temp:.1f}°C exceeds warning threshold ({self.thresholds.warning_temp}°C)"
            
            # Log every 10th warning to avoid spam
            if self.warning_count % 10 == 1:
                thermal_logger.warning(f"[{self.vehicle_id}] {message} (count: {self.warning_count})")
            
            self._log_event('warning', current_temp, timestamp, message)
            result['message'] = message
            
        else:
            # NORMAL
            self.current_status = ThermalStatus.NORMAL
            result['status'] = ThermalStatus.NORMAL
            
            # Reset warning count if we've cooled down
            if previous_status != ThermalStatus.NORMAL:
                self.warning_count = 0
                message = f"Temperature normal at {current_temp:.1f}°C"
                thermal_logger.info(f"[{self.vehicle_id}] {message}")
                result['message'] = message
        
        return result
    
    def _log_event(self, event_type: str, temperature: float, timestamp: datetime, message: str):
        """Log thermal event to history"""
        self.event_history.append({
            'type': event_type,
            'temperature': temperature,
            'timestamp': timestamp,
            'message': message
        })
        
        # Keep only last 1000 events to prevent memory issues
        if len(self.event_history) > 1000:
            self.event_history = self.event_history[-1000:]
    
    def get_thermal_report(self) -> Dict:
        """Get summary of thermal status and recent events"""
        recent_events = self.event_history[-10:] if self.event_history else []
        
        return {
            'vehicle_id': self.vehicle_id,
            'current_status': self.current_status.value,
            'shutdown_active': self.shutdown_active,
            'warning_count': self.warning_count,
            'thresholds': {
                'warning': self.thresholds.warning_temp,
                'critical': self.thresholds.critical_temp,
                'shutdown': self.thresholds.shutdown_temp,
                'recovery': self.thresholds.recovery_temp
            },
            'recent_events': recent_events,
            'total_events': len(self.event_history)
        }
    
    def should_allow_charging(self, current_temp: float) -> Tuple[bool, str]:
        """
        Determine if charging should be allowed based on temperature.
        More conservative than driving limits.
        
        Returns:
            Tuple of (allowed: bool, reason: str)
        """
        if self.shutdown_active:
            return False, "Thermal shutdown active"
        
        if current_temp >= self.thresholds.critical_temp:
            return False, f"Temperature too high ({current_temp:.1f}°C)"
        
        if current_temp >= self.thresholds.warning_temp:
            # Allow slow charging only
            return True, f"Slow charging only - elevated temperature ({current_temp:.1f}°C)"
        
        return True, "Normal charging allowed"
    
    def reset(self):
        """Reset thermal safety system (for testing/simulation)"""
        self.current_status = ThermalStatus.NORMAL
        self.shutdown_active = False
        self.warning_count = 0
        self.event_history = []
        thermal_logger.info(f"[{self.vehicle_id}] Thermal safety system reset")


# Example usage and testing
if __name__ == "__main__":
    # Create thermal manager
    manager = ThermalSafetyManager("VEH001")
    
    # Simulate temperature rise
    print("Simulating temperature rise...")
    temperatures = [25, 35, 45, 52, 56, 61, 58, 50, 45, 40]
    
    for temp in temperatures:
        result = manager.check_temperature(temp)
        print(f"\nTemp: {temp}°C")
        print(f"Status: {result['status'].value}")
        print(f"Power Limit: {result['power_limit']*100:.0f}%")
        print(f"Message: {result['message']}")
    
    # Get thermal report
    print("\n" + "="*50)
    print("Thermal Report:")
    report = manager.get_thermal_report()
    print(f"Total warnings: {report['warning_count']}")
    print(f"Total events: {report['total_events']}")
    print(f"Current status: {report['current_status']}")