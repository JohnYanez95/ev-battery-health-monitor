"""
Battery plotting utilities for thermal safety tests and analysis.
Provides standardized plots for apples-to-apples comparison between different test scenarios.
"""

import matplotlib.pyplot as plt
import numpy as np
from typing import List, Dict, Optional
from matplotlib.patches import Patch


def create_thermal_safety_plot(
    times: List[float],
    temperatures: List[float], 
    currents: List[float],
    powers: List[float],
    thermal_statuses: List[str],
    power_limits: List[float],
    thermal_events: Optional[List[Dict]] = None,
    test_name: str = "Thermal Safety Test",
    output_path: str = "thermal_test.png"
) -> None:
    """
    Create standardized 4-subplot thermal safety plot for comparison between tests.
    
    Args:
        times: Time points (seconds)
        temperatures: Battery temperatures (°C)
        currents: Battery currents (A) 
        powers: Battery powers (W)
        thermal_statuses: Thermal status at each time point
        power_limits: Power limit percentage (0.0-1.0) at each time point
        thermal_events: List of thermal events with time, type, temp
        test_name: Name for plot title
        output_path: Path to save figure
    """
    # Create 4-subplot figure for standardized comparison
    fig, axes = plt.subplots(4, 1, figsize=(14, 12))
    fig.suptitle(f'{test_name} - Thermal Safety Analysis', fontsize=16, fontweight='bold')
    
    # 1. Temperature with safety thresholds
    ax1 = axes[0]
    ax1.plot(times, temperatures, 'b-', linewidth=2.5, label='Battery Temperature')
    
    # Safety threshold lines
    ax1.axhline(y=50, color='orange', linestyle='--', linewidth=2, alpha=0.8, label='Warning (50°C)')
    ax1.axhline(y=55, color='red', linestyle='--', linewidth=2, alpha=0.8, label='Critical (55°C)')
    ax1.axhline(y=60, color='darkred', linestyle='--', linewidth=2, alpha=0.8, label='Shutdown (60°C)')
    ax1.axhline(y=45, color='green', linestyle='--', linewidth=2, alpha=0.8, label='Recovery (45°C)')
    
    # Mark thermal events if provided
    if thermal_events:
        event_colors = {'warning': 'orange', 'critical': 'red', 'shutdown': 'darkred', 'recovery': 'green'}
        for event in thermal_events:
            color = event_colors.get(event['type'], 'black')
            ax1.plot(event['time'], event['temp'], 'o', markersize=10, color=color, 
                    markeredgecolor='black', markeredgewidth=1)
    
    ax1.set_ylabel('Temperature (°C)', fontsize=12)
    ax1.set_title('Battery Temperature vs Safety Thresholds', fontsize=13)
    ax1.legend(loc='best', fontsize=10)
    ax1.grid(True, alpha=0.3)
    ax1.set_ylim(20, 65)
    
    # 2. Current 
    ax2 = axes[1]
    ax2.plot(times, currents, 'g-', linewidth=2, label='Battery Current')
    ax2.axhline(y=0, color='black', linestyle='-', alpha=0.5)
    ax2.set_ylabel('Current (A)', fontsize=12)
    ax2.set_title('Battery Current (Negative = Discharge, Positive = Charge)', fontsize=13)
    ax2.grid(True, alpha=0.3)
    ax2.legend(loc='best', fontsize=10)
    
    # 3. Power and Power Limiting
    ax3 = axes[2]
    # Power in kW
    power_kw = [p/1000 for p in powers]
    ax3.plot(times, power_kw, 'purple', linewidth=2, label='Power (kW)')
    ax3.axhline(y=0, color='black', linestyle='-', alpha=0.5)
    
    # Power limit on secondary y-axis
    ax3_twin = ax3.twinx()
    power_limit_pct = [pl * 100 for pl in power_limits]
    ax3_twin.plot(times, power_limit_pct, 'r--', linewidth=2, label='Power Limit (%)')
    ax3_twin.fill_between(times, 0, power_limit_pct, alpha=0.2, color='red')
    
    ax3.set_ylabel('Power (kW)', color='purple', fontsize=12)
    ax3_twin.set_ylabel('Power Limit (%)', color='red', fontsize=12)
    ax3.set_title('Battery Power and Thermal Power Limiting', fontsize=13)
    ax3.grid(True, alpha=0.3)
    ax3_twin.set_ylim(-5, 105)
    
    # Combined legend
    lines1, labels1 = ax3.get_legend_handles_labels()
    lines2, labels2 = ax3_twin.get_legend_handles_labels()
    ax3.legend(lines1 + lines2, labels1 + labels2, loc='best', fontsize=10)
    
    # 4. Thermal Status Timeline
    ax4 = axes[3]
    status_colors = {
        'normal': 'green',
        'warning': 'orange', 
        'critical': 'red',
        'shutdown': 'darkred'
    }
    
    # Create colored background regions
    for i in range(len(times)-1):
        color = status_colors.get(thermal_statuses[i], 'gray')
        ax4.axvspan(times[i], times[i+1], alpha=0.7, color=color)
    
    ax4.set_ylim(0, 1)
    ax4.set_xlabel('Time (s)', fontsize=12)
    ax4.set_title('Thermal Safety Status Timeline', fontsize=13)
    ax4.set_yticks([])
    
    # Status legend
    legend_elements = [
        Patch(facecolor='green', alpha=0.7, label='Normal'),
        Patch(facecolor='orange', alpha=0.7, label='Warning'),
        Patch(facecolor='red', alpha=0.7, label='Critical'),
        Patch(facecolor='darkred', alpha=0.7, label='Shutdown')
    ]
    ax4.legend(handles=legend_elements, loc='center left', bbox_to_anchor=(1, 0.5), fontsize=10)
    
    plt.tight_layout()
    plt.subplots_adjust(top=0.93)  # Make room for suptitle
    
    # Save figure
    plt.savefig(output_path, dpi=150, bbox_inches='tight')
    print(f"Plot saved as '{output_path}'")
    plt.close()


def create_summary_comparison_plot(
    test_results: List[Dict],
    output_path: str = "thermal_comparison.png"
) -> None:
    """
    Create side-by-side comparison of multiple thermal safety tests.
    
    Args:
        test_results: List of dictionaries with test data and metadata
        output_path: Path to save comparison figure
    """
    n_tests = len(test_results)
    fig, axes = plt.subplots(2, n_tests, figsize=(6*n_tests, 10))
    
    if n_tests == 1:
        axes = axes.reshape(-1, 1)
    
    fig.suptitle('Thermal Safety Test Comparison', fontsize=16, fontweight='bold')
    
    for i, test_data in enumerate(test_results):
        times = test_data['times']
        temperatures = test_data['temperatures']
        power_limits = test_data['power_limits']
        test_name = test_data['name']
        
        # Temperature comparison
        ax_temp = axes[0, i]
        ax_temp.plot(times, temperatures, 'b-', linewidth=2)
        ax_temp.axhline(y=50, color='orange', linestyle='--', alpha=0.6)
        ax_temp.axhline(y=55, color='red', linestyle='--', alpha=0.6)
        ax_temp.axhline(y=60, color='darkred', linestyle='--', alpha=0.6)
        ax_temp.set_title(f'{test_name}\nTemperature', fontsize=12)
        ax_temp.set_ylabel('Temperature (°C)')
        ax_temp.grid(True, alpha=0.3)
        ax_temp.set_ylim(20, 65)
        
        # Power limiting comparison
        ax_power = axes[1, i]
        power_limit_pct = [pl * 100 for pl in power_limits]
        ax_power.plot(times, power_limit_pct, 'r-', linewidth=2)
        ax_power.fill_between(times, 0, power_limit_pct, alpha=0.3, color='red')
        ax_power.set_title(f'Power Limiting', fontsize=12)
        ax_power.set_ylabel('Power Limit (%)')
        ax_power.set_xlabel('Time (s)')
        ax_power.grid(True, alpha=0.3)
        ax_power.set_ylim(-5, 105)
    
    plt.tight_layout()
    plt.subplots_adjust(top=0.90)
    
    plt.savefig(output_path, dpi=150, bbox_inches='tight')
    print(f"Comparison plot saved as '{output_path}'")
    plt.close()


def get_test_statistics(
    temperatures: List[float],
    thermal_events: List[Dict],
    power_limits: List[float],
    test_name: str
) -> Dict:
    """
    Calculate standardized statistics for thermal safety test comparison.
    
    Returns:
        Dictionary with test statistics
    """
    stats = {
        'test_name': test_name,
        'max_temp': max(temperatures),
        'min_temp': min(temperatures),
        'temp_range': max(temperatures) - min(temperatures),
        'total_events': len(thermal_events),
        'warning_events': len([e for e in thermal_events if e['type'] == 'warning']),
        'critical_events': len([e for e in thermal_events if e['type'] == 'critical']),
        'shutdown_events': len([e for e in thermal_events if e['type'] == 'shutdown']),
        'min_power_limit': min(power_limits) * 100,  # Convert to percentage
        'power_limited_time': sum(1 for pl in power_limits if pl < 1.0),  # Seconds under limit
    }
    
    return stats


def print_test_comparison(stats_list: List[Dict]) -> None:
    """Print formatted comparison table of test statistics."""
    print("\n" + "="*80)
    print("THERMAL SAFETY TEST COMPARISON")
    print("="*80)
    
    # Header
    print(f"{'Test Name':<20} {'Max Temp':<10} {'Temp Range':<12} {'Events':<8} {'Min Power%':<12} {'Limited Time':<12}")
    print("-" * 80)
    
    # Data rows
    for stats in stats_list:
        print(f"{stats['test_name']:<20} "
              f"{stats['max_temp']:<10.1f} "
              f"{stats['temp_range']:<12.1f} "
              f"{stats['total_events']:<8} "
              f"{stats['min_power_limit']:<12.0f} "
              f"{stats['power_limited_time']:<12} s")
    
    print("="*80)