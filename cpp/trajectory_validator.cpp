/**
 * Aircraft Trajectory Validator
 * 
 * This C++ program validates a single trajectory point against a corridor segment.
 * 
 * Input (command-line arguments):
 *   1. traj_lat - Trajectory point latitude
 *   2. traj_lon - Trajectory point longitude
 *   3. traj_alt - Trajectory point altitude (meters)
 *   4. traj_speed - Trajectory point speed (km/h)
 *   5. seg_start_lat - Corridor segment start latitude
 *   6. seg_start_lon - Corridor segment start longitude
 *   7. seg_start_alt - Corridor segment start altitude (meters)
 *   8. seg_end_lat - Corridor segment end latitude
 *   9. seg_end_lon - Corridor segment end longitude
 *   10. seg_end_alt - Corridor segment end altitude (meters)
 *   11. allowed_deviation - Maximum allowed deviation (meters)
 *   12. allowed_speed - Maximum allowed speed (km/h)
 * 
 * Output:
 *   Three values separated by space:
 *   - deviation: 3D distance from trajectory point to corridor segment (meters)
 *   - speed_violation: 0 if speed is within limits, otherwise the excess speed
 *   - is_compliant: 1 if point is compliant (deviation and speed within limits), 0 otherwise
 * 
 * Example usage:
 *   ./trajectory_validator 50.0 10.0 1000.0 250.0 50.1 10.1 1000.0 50.2 10.2 1000.0 500.0 300.0
 */

#include <iostream>
#include <cmath>
#include <iomanip>
#include <string>
#include <stdexcept>

using namespace std;

// Earth radius in meters (approximate)
const double EARTH_RADIUS = 6371000.0;

// Convert degrees to radians
double toRadians(double degrees) {
    return degrees * M_PI / 180.0;
}

// Calculate haversine distance between two points on Earth
double haversineDistance(double lat1, double lon1, double lat2, double lon2) {
    double lat1_rad = toRadians(lat1);
    double lat2_rad = toRadians(lat2);
    double delta_lat = toRadians(lat2 - lat1);
    double delta_lon = toRadians(lon2 - lon1);
    
    double a = sin(delta_lat / 2) * sin(delta_lat / 2) +
               cos(lat1_rad) * cos(lat2_rad) *
               sin(delta_lon / 2) * sin(delta_lon / 2);
    
    double c = 2 * asin(sqrt(a));
    
    return EARTH_RADIUS * c;
}

// Calculate 3D distance between two points
double distance3D(double lat1, double lon1, double alt1,
                  double lat2, double lon2, double alt2) {
    double horizontal_dist = haversineDistance(lat1, lon1, lat2, lon2);
    double vertical_dist = fabs(alt2 - alt1);
    
    return sqrt(horizontal_dist * horizontal_dist + vertical_dist * vertical_dist);
}

// Calculate the shortest distance from a point to a line segment in 3D
double pointToSegmentDistance3D(
    double lat_p, double lon_p, double alt_p,
    double lat_a, double lon_a, double alt_a,
    double lat_b, double lon_b, double alt_b) {
    
    double dist_ap = distance3D(lat_a, lon_a, alt_a, lat_p, lon_p, alt_p);
    double dist_bp = distance3D(lat_b, lon_b, alt_b, lat_p, lon_p, alt_p);
    double dist_ab = distance3D(lat_a, lon_a, alt_a, lat_b, lon_b, alt_b);
    
    // If segment has zero length, return distance to point A
    if (dist_ab < 1e-6) {
        return dist_ap;
    }
    
    // Calculate projection parameter t
    // Vector AP
    double ap_lat = lat_p - lat_a;
    double ap_lon = lon_p - lon_a;
    double ap_alt = alt_p - alt_a;
    
    // Vector AB
    double ab_lat = lat_b - lat_a;
    double ab_lon = lon_b - lon_a;
    double ab_alt = alt_b - alt_a;
    
    // Scale longitude by cos(latitude) for better accuracy
    double lat_avg = toRadians((lat_a + lat_b) / 2.0);
    double cos_lat = cos(lat_avg);
    
    // Dot product
    double dot_product = ap_lat * ab_lat +
                        ap_lon * ab_lon * cos_lat * cos_lat +
                        ap_alt * ab_alt / EARTH_RADIUS / EARTH_RADIUS;
    
    double ab_length_sq = ab_lat * ab_lat +
                         ab_lon * ab_lon * cos_lat * cos_lat +
                         ab_alt * ab_alt / EARTH_RADIUS / EARTH_RADIUS;
    
    if (ab_length_sq < 1e-10) {
        return dist_ap;
    }
    
    double t = dot_product / ab_length_sq;
    
    // Clamp t to [0, 1] to stay on the segment
    t = max(0.0, min(1.0, t));
    
    // Find the closest point on the segment
    double closest_lat = lat_a + t * ab_lat;
    double closest_lon = lon_a + t * ab_lon;
    double closest_alt = alt_a + t * ab_alt;
    
    // Return distance to closest point
    return distance3D(lat_p, lon_p, alt_p, closest_lat, closest_lon, closest_alt);
}

int main(int argc, char* argv[]) {
    // Check number of arguments
    if (argc != 13) {
        cerr << "Error: Expected 12 arguments, got " << (argc - 1) << endl;
        cerr << "Usage: " << argv[0] << " traj_lat traj_lon traj_alt traj_speed "
             << "seg_start_lat seg_start_lon seg_start_alt "
             << "seg_end_lat seg_end_lon seg_end_alt "
             << "allowed_deviation allowed_speed" << endl;
        return 1;
    }
    
    try {
        // Parse arguments
        double traj_lat = stod(argv[1]);
        double traj_lon = stod(argv[2]);
        double traj_alt = stod(argv[3]);
        double traj_speed = stod(argv[4]);
        
        double seg_start_lat = stod(argv[5]);
        double seg_start_lon = stod(argv[6]);
        double seg_start_alt = stod(argv[7]);
        
        double seg_end_lat = stod(argv[8]);
        double seg_end_lon = stod(argv[9]);
        double seg_end_alt = stod(argv[10]);
        
        double allowed_deviation = stod(argv[11]);
        double allowed_speed = stod(argv[12]);
        
        // Calculate deviation
        double deviation = pointToSegmentDistance3D(
            traj_lat, traj_lon, traj_alt,
            seg_start_lat, seg_start_lon, seg_start_alt,
            seg_end_lat, seg_end_lon, seg_end_alt
        );
        
        // Calculate speed violation
        double speed_violation = 0.0;
        if (traj_speed > allowed_speed) {
            speed_violation = traj_speed - allowed_speed;
        }
        
        // Check compliance (1 = compliant, 0 = not compliant)
        int is_compliant = 0;
        if (deviation <= allowed_deviation && traj_speed <= allowed_speed) {
            is_compliant = 1;
        }
        
        // Output results: deviation speed_violation is_compliant
        cout << fixed << setprecision(2);
        cout << deviation << " " << speed_violation << " " << is_compliant << endl;
        
        return 0;
        
    } catch (const exception& e) {
        cerr << "Error: " << e.what() << endl;
        return 1;
    }
}

