"""
File processing and analysis logic.
"""
import os
import subprocess
import json
from typing import Dict, List, Optional
from django.conf import settings
from .parsers import parse_corridor_file, parse_trajectory_file
from .geometry import (
    compute_trajectory_speeds,
    compute_deviations,
)


def process_flight_case(flight_case) -> bool:
    """
    Process a FlightCase: parse files, compute metrics, run C++ validation.
    
    Args:
        flight_case: FlightCase model instance
    
    Returns:
        True if processing succeeded, False otherwise
    """
    try:
        # Parse corridor file
        corridor_path = flight_case.corridor_file.path
        corridor_points = parse_corridor_file(corridor_path)
        
        # Parse trajectory file
        trajectory_path = flight_case.trajectory_file.path
        trajectory_points = parse_trajectory_file(trajectory_path)
        
        # Compute speeds
        trajectory_points = compute_trajectory_speeds(trajectory_points)
        
        # Compute deviations from corridor
        trajectory_points = compute_deviations(trajectory_points, corridor_points)
        
        # Run C++ validator (optional, for additional validation)
        if settings.CPP_VALIDATOR_PATH.exists():
            trajectory_points = run_cpp_validation(
                trajectory_points,
                corridor_points,
                settings.CPP_VALIDATOR_PATH
            )
        
        # Calculate aggregate metrics
        speeds = [p['speed'] for p in trajectory_points if 'speed' in p]
        deviations = [p['deviation'] for p in trajectory_points if 'deviation' in p]
        
        mean_speed = sum(speeds) / len(speeds) if speeds else 0.0
        max_speed = max(speeds) if speeds else 0.0
        mean_deviation = sum(deviations) / len(deviations) if deviations else 0.0
        
        # Calculate compliance percentage
        # Use C++ results if available, otherwise use Python calculation
        cpp_compliant_count = sum(1 for p in trajectory_points if p.get('cpp_compliant', False))
        
        if cpp_compliant_count > 0:
            # Use C++ calculated compliance
            compliance_percentage = (cpp_compliant_count / len(trajectory_points)) * 100
        else:
            # Fallback to Python calculation
            compliant_count = sum(
                1 for p in trajectory_points 
                if p.get('deviation') is not None 
                and p.get('allowed_deviation') is not None
                and p['deviation'] <= p['allowed_deviation']
                and p.get('speed', 0) <= p.get('allowed_speed', float('inf'))
            )
            compliance_percentage = (compliant_count / len(trajectory_points)) * 100 if len(trajectory_points) > 0 else 0.0
        
        # Store results
        flight_case.corridor_data = corridor_points
        flight_case.trajectory_data = trajectory_points
        flight_case.mean_speed = mean_speed
        flight_case.max_speed = max_speed
        flight_case.mean_deviation = mean_deviation
        flight_case.compliance_percentage = compliance_percentage
        flight_case.is_processed = True
        flight_case.processing_error = None
        flight_case.save()
        
        return True
        
    except Exception as e:
        flight_case.processing_error = str(e)
        flight_case.is_processed = False
        flight_case.save()
        return False


def run_cpp_validation(
    trajectory_points: List[Dict],
    corridor_points: List[Dict],
    cpp_executable_path: str
) -> List[Dict]:
    """
    Run C++ validator for each trajectory point.
    
    The C++ program is called with:
    - Corridor segment parameters
    - Trajectory point parameters
    
    And returns validation metrics that are added to trajectory points.
    
    Args:
        trajectory_points: List of trajectory points
        corridor_points: List of corridor points
        cpp_executable_path: Path to compiled C++ executable
    
    Returns:
        Updated trajectory points with C++ validation results
    """
    if not os.path.exists(cpp_executable_path):
        return trajectory_points
    
    for i, traj_point in enumerate(trajectory_points):
        try:
            # Find the nearest corridor segment
            segment_idx = traj_point.get('nearest_segment', 0)
            
            if segment_idx < 0 or segment_idx >= len(corridor_points) - 1:
                continue
            
            corridor_start = corridor_points[segment_idx]
            corridor_end = corridor_points[segment_idx + 1]
            
            # Prepare input for C++ program
            # Format: traj_lat traj_lon traj_alt traj_speed 
            #         seg_start_lat seg_start_lon seg_start_alt 
            #         seg_end_lat seg_end_lon seg_end_alt 
            #         allowed_dev allowed_speed
            
            args = [
                str(cpp_executable_path),
                str(traj_point['latitude']),
                str(traj_point['longitude']),
                str(traj_point['altitude']),
                str(traj_point.get('speed', 0)),
                str(corridor_start['latitude']),
                str(corridor_start['longitude']),
                str(corridor_start['altitude']),
                str(corridor_end['latitude']),
                str(corridor_end['longitude']),
                str(corridor_end['altitude']),
                str((corridor_start['allowed_deviation'] + corridor_end['allowed_deviation']) / 2),
                str((corridor_start['allowed_speed'] + corridor_end['allowed_speed']) / 2),
            ]
            
            # Call C++ program
            result = subprocess.run(
                args,
                capture_output=True,
                text=True,
                timeout=1.0
            )
            
            if result.returncode == 0:
                # Parse output (expected format: deviation speed_violation is_compliant)
                output = result.stdout.strip()
                if output:
                    parts = output.split()
                    if len(parts) >= 3:
                        trajectory_points[i]['cpp_deviation'] = float(parts[0])
                        trajectory_points[i]['cpp_speed_violation'] = float(parts[1])
                        trajectory_points[i]['cpp_compliant'] = int(parts[2]) == 1
            
        except (subprocess.TimeoutExpired, subprocess.SubprocessError, ValueError) as e:
            # If C++ validation fails, continue with Python calculations
            trajectory_points[i]['cpp_error'] = str(e)
            continue
    
    return trajectory_points


def interpolate_position(
    point1: Dict,
    point2: Dict,
    target_time_seconds: float
) -> Dict:
    """
    Interpolate position between two trajectory points for smooth animation.
    
    Args:
        point1: First trajectory point
        point2: Second trajectory point
        target_time_seconds: Target time in seconds since midnight
    
    Returns:
        Interpolated position dict with lat, lon, alt
    """
    t1 = point1['time_seconds']
    t2 = point2['time_seconds']
    
    if t2 - t1 == 0:
        return {
            'latitude': point1['latitude'],
            'longitude': point1['longitude'],
            'altitude': point1['altitude'],
        }
    
    # Linear interpolation factor
    factor = (target_time_seconds - t1) / (t2 - t1)
    factor = max(0.0, min(1.0, factor))
    
    return {
        'latitude': point1['latitude'] + factor * (point2['latitude'] - point1['latitude']),
        'longitude': point1['longitude'] + factor * (point2['longitude'] - point1['longitude']),
        'altitude': point1['altitude'] + factor * (point2['altitude'] - point1['altitude']),
    }

