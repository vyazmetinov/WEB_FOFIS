# C++ Trajectory Validator

This directory contains a standalone C++ program that validates aircraft trajectory points against corridor segments.

## Building

To compile the C++ program:

```bash
cd cpp
make
```

This will create the `trajectory_validator` executable.

## Usage

```bash
./trajectory_validator traj_lat traj_lon traj_alt traj_speed \
                       seg_start_lat seg_start_lon seg_start_alt \
                       seg_end_lat seg_end_lon seg_end_alt \
                       allowed_deviation allowed_speed
```

### Parameters

1. `traj_lat`, `traj_lon`, `traj_alt` - Trajectory point coordinates (degrees, degrees, meters)
2. `traj_speed` - Aircraft speed at this point (km/h)
3. `seg_start_lat`, `seg_start_lon`, `seg_start_alt` - Corridor segment start (degrees, degrees, meters)
4. `seg_end_lat`, `seg_end_lon`, `seg_end_alt` - Corridor segment end (degrees, degrees, meters)
5. `allowed_deviation` - Maximum allowed deviation from corridor (meters)
6. `allowed_speed` - Maximum allowed speed (km/h)

### Output

The program outputs two values separated by a space:
- **Deviation**: 3D distance from trajectory point to corridor segment (meters)
- **Speed violation**: 0 if within limits, otherwise the excess speed (km/h)

### Example

```bash
./trajectory_validator 50.0 10.0 1000.0 250.0 50.1 10.1 1000.0 50.2 10.2 1000.0 500.0 300.0
```

Output:
```
15724.32 0.00
```

This means:
- The trajectory point is 15,724.32 meters from the corridor segment
- The speed is within the allowed limit (no violation)

## Integration with Django

The Django backend calls this program via `subprocess` for each trajectory point to perform additional validation. The results are stored alongside Python-computed metrics.

