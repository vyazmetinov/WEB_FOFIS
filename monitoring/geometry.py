"""
3D geometry calculations for trajectory analysis.
"""
import math
from typing import List, Dict, Tuple, Optional


# Earth radius in meters (approximate)
EARTH_RADIUS = 6371000.0


def haversine_distance(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """
    Calculate the great circle distance between two points on Earth in meters.
    
    Args:
        lat1, lon1: First point (degrees)
        lat2, lon2: Second point (degrees)
    
    Returns:
        Distance in meters
    """
    # Convert to radians
    lat1_rad = math.radians(lat1)
    lat2_rad = math.radians(lat2)
    delta_lat = math.radians(lat2 - lat1)
    delta_lon = math.radians(lon2 - lon1)
    
    # Haversine formula
    a = (math.sin(delta_lat / 2) ** 2 +
         math.cos(lat1_rad) * math.cos(lat2_rad) * math.sin(delta_lon / 2) ** 2)
    c = 2 * math.asin(math.sqrt(a))
    
    return EARTH_RADIUS * c


def distance_3d(lat1: float, lon1: float, alt1: float,
                lat2: float, lon2: float, alt2: float) -> float:
    """
    Calculate 3D distance between two points (considering altitude).
    
    Args:
        lat1, lon1, alt1: First point (degrees, degrees, meters)
        lat2, lon2, alt2: Second point (degrees, degrees, meters)
    
    Returns:
        3D distance in meters
    """
    horizontal_dist = haversine_distance(lat1, lon1, lat2, lon2)
    vertical_dist = abs(alt2 - alt1)
    
    return math.sqrt(horizontal_dist ** 2 + vertical_dist ** 2)


def point_to_segment_distance_3d(
    point: Tuple[float, float, float],
    segment_start: Tuple[float, float, float],
    segment_end: Tuple[float, float, float]
) -> float:
    """
    Calculate the shortest 3D distance from a point to a line segment.
    
    Points are in format (latitude, longitude, altitude).
    
    Args:
        point: Point to measure from (lat, lon, alt)
        segment_start: Start of segment (lat, lon, alt)
        segment_end: End of segment (lat, lon, alt)
    
    Returns:
        Shortest distance in meters
    """
    lat_p, lon_p, alt_p = point
    lat_a, lon_a, alt_a = segment_start
    lat_b, lon_b, alt_b = segment_end
    
    # Calculate distances
    dist_ap = distance_3d(lat_a, lon_a, alt_a, lat_p, lon_p, alt_p)
    dist_bp = distance_3d(lat_b, lon_b, alt_b, lat_p, lon_p, alt_p)
    dist_ab = distance_3d(lat_a, lon_a, alt_a, lat_b, lon_b, alt_b)
    
    # If segment has zero length, return distance to point
    if dist_ab < 1e-6:
        return dist_ap
    
    # Calculate projection parameter t
    # This represents where the perpendicular from point P hits segment AB
    # t = 0 means at A, t = 1 means at B
    
    # Use dot product: t = AP · AB / |AB|²
    # For geographic coordinates, we approximate with small distances
    
    # Vector AP
    ap_lat = lat_p - lat_a
    ap_lon = lon_p - lon_a
    ap_alt = alt_p - alt_a
    
    # Vector AB
    ab_lat = lat_b - lat_a
    ab_lon = lon_b - lon_a
    ab_alt = alt_b - alt_a
    
    # Approximate dot product (works for small distances)
    # Scale longitude by cos(latitude) for better accuracy
    lat_avg = math.radians((lat_a + lat_b) / 2)
    cos_lat = math.cos(lat_avg)
    
    dot_product = (ap_lat * ab_lat +
                   ap_lon * ab_lon * cos_lat * cos_lat +
                   ap_alt * ab_alt / EARTH_RADIUS / EARTH_RADIUS)
    
    ab_length_sq = (ab_lat ** 2 +
                    ab_lon ** 2 * cos_lat * cos_lat +
                    ab_alt ** 2 / EARTH_RADIUS / EARTH_RADIUS)
    
    if ab_length_sq < 1e-10:
        return dist_ap
    
    t = dot_product / ab_length_sq
    
    # Clamp t to [0, 1] to stay on the segment
    t = max(0.0, min(1.0, t))
    
    # Find the closest point on the segment
    closest_lat = lat_a + t * ab_lat
    closest_lon = lon_a + t * ab_lon
    closest_alt = alt_a + t * ab_alt
    
    # Return distance to closest point
    return distance_3d(lat_p, lon_p, alt_p, closest_lat, closest_lon, closest_alt)


def find_nearest_corridor_segment(
    trajectory_point: Dict,
    corridor_points: List[Dict]
) -> Tuple[float, int, Optional[Dict]]:
    """
    Find the nearest corridor segment to a trajectory point.
    
    Args:
        trajectory_point: Trajectory point dict with lat, lon, alt
        corridor_points: List of corridor point dicts
    
    Returns:
        Tuple of (minimum_distance, segment_index, closest_corridor_point)
    """
    if not corridor_points:
        return float('inf'), -1, None
    
    if len(corridor_points) == 1:
        # Only one corridor point
        dist = distance_3d(
            trajectory_point['latitude'],
            trajectory_point['longitude'],
            trajectory_point['altitude'],
            corridor_points[0]['latitude'],
            corridor_points[0]['longitude'],
            corridor_points[0]['altitude']
        )
        return dist, 0, corridor_points[0]
    
    min_distance = float('inf')
    nearest_segment_idx = -1
    nearest_corridor_point = None
    
    # Check distance to each segment
    for i in range(len(corridor_points) - 1):
        start_point = (
            corridor_points[i]['latitude'],
            corridor_points[i]['longitude'],
            corridor_points[i]['altitude']
        )
        end_point = (
            corridor_points[i + 1]['latitude'],
            corridor_points[i + 1]['longitude'],
            corridor_points[i + 1]['altitude']
        )
        traj_point = (
            trajectory_point['latitude'],
            trajectory_point['longitude'],
            trajectory_point['altitude']
        )
        
        dist = point_to_segment_distance_3d(traj_point, start_point, end_point)
        
        if dist < min_distance:
            min_distance = dist
            nearest_segment_idx = i
            # Use average of segment properties
            nearest_corridor_point = {
                'allowed_deviation': (corridor_points[i]['allowed_deviation'] +
                                     corridor_points[i + 1]['allowed_deviation']) / 2,
                'allowed_speed': (corridor_points[i]['allowed_speed'] +
                                corridor_points[i + 1]['allowed_speed']) / 2,
            }
    
    return min_distance, nearest_segment_idx, nearest_corridor_point


def calculate_speed(point1: Dict, point2: Dict) -> float:
    """
    Calculate speed between two trajectory points.
    
    Args:
        point1, point2: Trajectory points with lat, lon, alt, time_seconds
    
    Returns:
        Speed in km/h
    """
    distance = distance_3d(
        point1['latitude'], point1['longitude'], point1['altitude'],
        point2['latitude'], point2['longitude'], point2['altitude']
    )
    
    time_diff = point2['time_seconds'] - point1['time_seconds']
    
    if time_diff <= 0:
        return 0.0
    
    # Speed in m/s
    speed_ms = distance / time_diff
    
    # Convert to km/h
    speed_kmh = speed_ms * 3.6
    
    return speed_kmh


def compute_trajectory_speeds(trajectory_points: List[Dict]) -> List[Dict]:
    """
    Compute speed for each trajectory point based on movement to next point.
    
    Args:
        trajectory_points: List of trajectory points
    
    Returns:
        Updated list with speed information
    """
    if len(trajectory_points) < 2:
        if len(trajectory_points) == 1:
            trajectory_points[0]['speed'] = 0.0
        return trajectory_points
    
    for i in range(len(trajectory_points) - 1):
        speed = calculate_speed(trajectory_points[i], trajectory_points[i + 1])
        trajectory_points[i]['speed'] = speed
    
    # Last point gets same speed as previous
    trajectory_points[-1]['speed'] = trajectory_points[-2]['speed']
    
    return trajectory_points


def compute_deviations(
    trajectory_points: List[Dict],
    corridor_points: List[Dict]
) -> List[Dict]:
    """
    Compute deviation from corridor for each trajectory point.
    
    Args:
        trajectory_points: List of trajectory points
        corridor_points: List of corridor points
    
    Returns:
        Updated trajectory points with deviation information
    """
    for point in trajectory_points:
        deviation, segment_idx, corridor_info = find_nearest_corridor_segment(
            point, corridor_points
        )
        
        point['deviation'] = deviation
        point['nearest_segment'] = segment_idx
        
        if corridor_info:
            point['allowed_deviation'] = corridor_info['allowed_deviation']
            point['allowed_speed'] = corridor_info['allowed_speed']
            point['compliant'] = (
                deviation <= corridor_info['allowed_deviation'] and
                point.get('speed', 0) <= corridor_info['allowed_speed']
            )
        else:
            point['allowed_deviation'] = None
            point['allowed_speed'] = None
            point['compliant'] = False
    
    return trajectory_points

