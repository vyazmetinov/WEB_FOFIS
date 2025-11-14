"""
File parsers for corridor and trajectory files.
"""
import re
from typing import List, Dict, Tuple
from datetime import datetime, time


def parse_corridor_file(file_path: str) -> List[Dict]:
    """
    Parse corridor file.
    
    Format: longitude latitude altitude allowed_deviation allowed_speed
    
    Args:
        file_path: Path to corridor file
    
    Returns:
        List of dictionaries with corridor point data
    """
    corridor_points = []
    
    with open(file_path, 'r') as f:
        for line_num, line in enumerate(f, 1):
            line = line.strip()
            if not line or line.startswith('#'):
                continue
            
            parts = line.split()
            if len(parts) != 5:
                raise ValueError(f"Line {line_num}: Expected 5 values, got {len(parts)}")
            
            try:
                point = {
                    'longitude': float(parts[0]),
                    'latitude': float(parts[1]),
                    'altitude': float(parts[2]),
                    'allowed_deviation': float(parts[3]),
                    'allowed_speed': float(parts[4]),
                    'index': len(corridor_points)
                }
                corridor_points.append(point)
            except ValueError as e:
                raise ValueError(f"Line {line_num}: Invalid number format - {e}")
    
    if not corridor_points:
        raise ValueError("Corridor file is empty or contains no valid data")
    
    return corridor_points


def parse_time(time_str: str) -> time:
    """
    Parse time string in format hh:mm:ss.
    
    Args:
        time_str: Time string
    
    Returns:
        datetime.time object
    """
    # Try different time formats
    for fmt in ['%H:%M:%S', '%H:%M:%S.%f']:
        try:
            dt = datetime.strptime(time_str, fmt)
            return dt.time()
        except ValueError:
            continue
    
    raise ValueError(f"Invalid time format: {time_str}. Expected hh:mm:ss")


def time_to_seconds(t: time) -> float:
    """
    Convert time to total seconds since midnight.
    
    Args:
        t: time object
    
    Returns:
        Total seconds
    """
    return t.hour * 3600 + t.minute * 60 + t.second + t.microsecond / 1000000


def parse_trajectory_file(file_path: str) -> List[Dict]:
    """
    Parse trajectory file.
    
    Format: latitude longitude altitude time
    Time format: hh:mm:ss
    
    Args:
        file_path: Path to trajectory file
    
    Returns:
        List of dictionaries with trajectory point data
    """
    trajectory_points = []
    
    with open(file_path, 'r') as f:
        for line_num, line in enumerate(f, 1):
            line = line.strip()
            if not line or line.startswith('#'):
                continue
            
            parts = line.split()
            if len(parts) != 4:
                raise ValueError(f"Line {line_num}: Expected 4 values, got {len(parts)}")
            
            try:
                time_obj = parse_time(parts[3])
                
                point = {
                    'latitude': float(parts[0]),
                    'longitude': float(parts[1]),
                    'altitude': float(parts[2]),
                    'time': parts[3],  # Keep original string format
                    'time_seconds': time_to_seconds(time_obj),
                    'index': len(trajectory_points)
                }
                trajectory_points.append(point)
            except ValueError as e:
                raise ValueError(f"Line {line_num}: Invalid data - {e}")
    
    if not trajectory_points:
        raise ValueError("Trajectory file is empty or contains no valid data")
    
    # Verify points are sorted by time
    for i in range(1, len(trajectory_points)):
        if trajectory_points[i]['time_seconds'] < trajectory_points[i-1]['time_seconds']:
            raise ValueError(f"Trajectory points are not sorted by time (line {i+1})")
    
    return trajectory_points


def format_time_for_display(seconds: float) -> str:
    """
    Format seconds since midnight as hh:mm:ss.
    
    Args:
        seconds: Seconds since midnight
    
    Returns:
        Formatted time string
    """
    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    secs = int(seconds % 60)
    return f"{hours:02d}:{minutes:02d}:{secs:02d}"

