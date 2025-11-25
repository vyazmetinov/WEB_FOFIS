# FOFIS Project Overview

## Project Structure

```
FOFIS/
├── fofis_project/              # Django project configuration
│   ├── __init__.py
│   ├── settings.py            # Project settings (database, apps, static files)
│   ├── urls.py                # Main URL routing
│   ├── wsgi.py                # WSGI configuration
│   └── asgi.py                # ASGI configuration
│
├── monitoring/                 # Main application
│   ├── __init__.py
│   ├── apps.py                # App configuration
│   ├── models.py              # FlightCase model
│   ├── views.py               # API views (ViewSets)
│   ├── serializers.py         # DRF serializers
│   ├── urls.py                # API URL routing
│   ├── urls_views.py          # Frontend URL routing
│   ├── admin.py               # Django admin configuration
│   ├── tests.py               # Unit tests
│   ├── parsers.py             # File parsing utilities
│   ├── geometry.py            # 3D geometry calculations
│   ├── processing.py          # File processing pipeline
│   └── migrations/            # Database migrations
│
├── templates/                  # HTML templates
│   └── index.html             # Main frontend (Leaflet map + controls)
│
├── static/                     # Static files (CSS, JS, images)
│   └── .gitkeep
│
├── media/                      # User uploads (created at runtime)
│   ├── corridors/             # Uploaded corridor files
│   └── trajectories/          # Uploaded trajectory files
│
├── cpp/                        # C++ validation module
│   ├── trajectory_validator.cpp  # C++ source code
│   ├── Makefile               # Build configuration
│   └── README.md              # C++ module documentation
│
├── sample_data/                # Example files for testing
│   ├── corridor.txt           # Normal corridor
│   ├── trajectory.txt         # Normal trajectory
│   ├── corridor_violation.txt # Tight constraints
│   └── trajectory_violation.txt # Violating trajectory
│
├── manage.py                   # Django management script
├── requirements.txt            # Python dependencies
├── setup.sh                    # Automated setup script
├── .gitignore                  # Git ignore rules
├── README.md                   # Full documentation
├── QUICKSTART.md              # Quick start guide
└── PROJECT_OVERVIEW.md        # This file
```

## Core Components

### 1. Backend (Django)

#### Models (`monitoring/models.py`)
- **FlightCase**: Represents one pair of corridor + trajectory files
  - File fields for corridor and trajectory
  - Computed metrics (mean_deviation, mean_speed, max_speed)
  - JSON fields for parsed data
  - Processing status tracking

#### Parsers (`monitoring/parsers.py`)
- `parse_corridor_file()`: Parse corridor.txt files
- `parse_trajectory_file()`: Parse trajectory.txt files
- `parse_time()`: Convert time strings to datetime objects
- Time conversion utilities

#### Geometry Engine (`monitoring/geometry.py`)
- `haversine_distance()`: Great-circle distance on Earth
- `distance_3d()`: 3D distance with altitude
- `point_to_segment_distance_3d()`: Shortest distance from point to segment
- `find_nearest_corridor_segment()`: Find closest corridor segment
- `calculate_speed()`: Compute speed between two points
- `compute_trajectory_speeds()`: Add speed to all trajectory points
- `compute_deviations()`: Calculate deviations for all points

#### Processing Pipeline (`monitoring/processing.py`)
- `process_flight_case()`: Main processing function
  - Parse both files
  - Compute speeds
  - Compute deviations
  - Call C++ validator (optional)
  - Store results in database
- `run_cpp_validation()`: Interface to C++ program
- `interpolate_position()`: Smooth animation interpolation

#### API Views (`monitoring/views.py`)
- `FlightCaseViewSet`: RESTful API
  - `list()`: Get all flight cases
  - `create()`: Upload files and process
  - `retrieve()`: Get single flight case
  - `destroy()`: Delete flight case
  - `process()`: Manually trigger processing
  - `trajectory_data()`: Get data for playback
- `index_view()`: Serve frontend HTML

#### Serializers (`monitoring/serializers.py`)
- `FlightCaseSerializer`: Full serialization
- `FlightCaseCreateSerializer`: For file uploads
- `FlightCaseListSerializer`: Minimal list view

### 2. Frontend (HTML/JavaScript)

#### Main Interface (`templates/index.html`)
All-in-one HTML file with embedded CSS and JavaScript:

**HTML Structure:**
- Map container with Leaflet map
- Playback controls (overlay on map)
- Table container at bottom

**CSS:**
- Minimalistic design
- Responsive layout
- Drag-and-drop styling
- Button and control styling

**JavaScript Modules:**

1. **Map Management**
   - `initMap()`: Initialize Leaflet map
   - `displayCorridor()`: Render corridor polyline and circles
   - `displayTrajectory()`: Render trajectory path
   - `updateAircraftPosition()`: Move aircraft marker

2. **Playback System**
   - `startPlayback()`: Begin animation
   - `pausePlayback()`: Pause animation
   - `stopPlayback()`: Reset to start
   - `updatePlayback()`: Animation loop (requestAnimationFrame)
   - `interpolatePosition()`: Smooth movement between points
   - `setPlaybackTime()`: Jump to specific time

3. **API Communication**
   - `loadFlightCases()`: Fetch all flight cases
   - `uploadFiles()`: Upload corridor and trajectory
   - `deleteFlightCase()`: Remove flight case
   - `loadFlightCaseData()`: Get data for playback

4. **Table Management**
   - `renderTable()`: Render all rows
   - `createTableRow()`: Create row from flight case
   - `createEmptyRow()`: Add upload row
   - `createDropzone()`: Drag-and-drop file zone
   - `checkAndUpload()`: Auto-upload when both files ready

### 3. C++ Module

#### Validator (`cpp/trajectory_validator.cpp`)
Standalone C++ program that:
- Accepts 12 command-line arguments
- Calculates 3D distance from point to segment
- Checks speed violations
- Outputs: `deviation speed_violation`

**Key Functions:**
- `toRadians()`: Convert degrees to radians
- `haversineDistance()`: Great-circle distance
- `distance3D()`: 3D distance
- `pointToSegmentDistance3D()`: Point-to-segment calculation

**Integration:**
- Called via `subprocess` from Django
- Results added to trajectory data
- Optional (system works without it)

## Data Flow

### Upload Flow
1. User drops files in dropzones
2. JavaScript detects both files uploaded
3. `uploadFiles()` sends FormData to `/api/flight-cases/`
4. Django creates `FlightCase` model instance
5. `process_flight_case()` automatically triggered
6. Files parsed, metrics computed, results stored
7. Corridor displayed on map immediately
8. Table updated with new row showing metrics

### Playback Flow
1. User clicks table row
2. JavaScript calls `loadFlightCaseData(id)`
3. Backend returns corridor, trajectory, and metrics
4. Corridor and trajectory rendered on map
5. Playback times set (start, end, current)
6. User clicks Play
7. `updatePlayback()` called in animation loop
8. Current time increments based on speed multiplier
9. Position interpolated between trajectory points
10. Aircraft marker updated on map
11. Loop continues until end time reached

### Processing Pipeline
```
Upload Files
    ↓
Create FlightCase
    ↓
Parse corridor.txt → List[CorridorPoint]
    ↓
Parse trajectory.txt → List[TrajectoryPoint]
    ↓
Compute Speeds → trajectory[i].speed
    ↓
For each trajectory point:
    ├─ Find nearest corridor segment
    ├─ Compute 3D deviation
    ├─ Get allowed_deviation, allowed_speed
    ├─ Check compliance
    └─ (Optional) Call C++ validator
    ↓
Compute Aggregate Metrics:
    ├─ mean_deviation
    ├─ mean_speed
    └─ max_speed
    ↓
Store in Database
    ↓
Return to Frontend
```

## Key Algorithms

### 1. 3D Distance Calculation
```
horizontal_distance = haversine(lat1, lon1, lat2, lon2)
vertical_distance = |alt2 - alt1|
distance_3d = √(horizontal² + vertical²)
```

### 2. Point-to-Segment Distance
```
Vector AP = point - segment_start
Vector AB = segment_end - segment_start

t = dot(AP, AB) / dot(AB, AB)
t = clamp(t, 0, 1)

closest_point = segment_start + t * AB
distance = distance_3d(point, closest_point)
```

### 3. Speed Calculation
```
distance = distance_3d(point1, point2)
time_diff = point2.time - point1.time

speed = distance / time_diff  (m/s)
speed_kmh = speed * 3.6
```

### 4. Playback Interpolation
```
factor = (current_time - t1) / (t2 - t1)
factor = clamp(factor, 0, 1)

interpolated_position = point1 + factor * (point2 - point1)
```

## Database Schema

### FlightCase Table
| Column | Type | Description |
|--------|------|-------------|
| id | INTEGER | Primary key |
| corridor_file | FILE | Path to corridor file |
| trajectory_file | FILE | Path to trajectory file |
| mean_deviation | FLOAT | Average deviation (m) |
| mean_speed | FLOAT | Average speed (km/h) |
| max_speed | FLOAT | Maximum speed (km/h) |
| corridor_data | JSON | Parsed corridor points |
| trajectory_data | JSON | Parsed trajectory points |
| is_processed | BOOLEAN | Processing complete? |
| processing_error | TEXT | Error message if failed |
| created_at | DATETIME | Creation timestamp |
| updated_at | DATETIME | Last update timestamp |

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/` | Main frontend page |
| GET | `/api/flight-cases/` | List all flight cases |
| POST | `/api/flight-cases/` | Upload files and create flight case |
| GET | `/api/flight-cases/{id}/` | Get flight case details |
| DELETE | `/api/flight-cases/{id}/` | Delete flight case |
| POST | `/api/flight-cases/{id}/process/` | Trigger processing |
| GET | `/api/flight-cases/{id}/trajectory_data/` | Get playback data |

## File Formats

### corridor.txt
```
longitude latitude altitude allowed_deviation allowed_speed
longitude latitude altitude allowed_deviation allowed_speed
...
```
- Space-separated values
- Lines starting with # are comments
- longitude, latitude: GPS coordinates (degrees)
- altitude: meters above sea level
- allowed_deviation: tube radius (meters)
- allowed_speed: speed limit (km/h)

### trajectory.txt
```
latitude longitude altitude time
latitude longitude altitude time
...
```
- Space-separated values
- Lines starting with # are comments
- latitude, longitude: GPS coordinates (degrees)
- altitude: meters above sea level
- time: hh:mm:ss format
- Must be sorted by time

## Configuration

### Django Settings (`fofis_project/settings.py`)
- `DEBUG = True`: Development mode
- `DATABASES`: SQLite by default
- `MEDIA_ROOT`: User upload directory
- `STATIC_ROOT`: Static files directory
- `CPP_VALIDATOR_PATH`: Path to C++ executable
- `INSTALLED_APPS`: Includes monitoring, rest_framework, corsheaders

### Frontend Configuration
- Leaflet map center: [50.0, 10.0]
- Default zoom: 6
- OpenStreetMap tiles
- Playback speeds: 1×, 2×, 4×, 8×, 16×

## Testing

Run tests:
```bash
python manage.py test
```

Test coverage:
- File parsing (corridor, trajectory, time)
- Geometry calculations (haversine, 3D distance, point-to-segment)
- Model creation
- API endpoints (list, create, view)

## Deployment Considerations

### Development
- Use `python manage.py runserver`
- SQLite database
- Debug mode enabled
- CORS allows all origins

### Production
1. Set `DEBUG = False`
2. Configure proper `SECRET_KEY`
3. Use PostgreSQL or MySQL
4. Set `ALLOWED_HOSTS`
5. Configure CORS properly
6. Use gunicorn/uwsgi
7. Serve static files with nginx
8. Enable HTTPS
9. Set up proper logging
10. Configure backups

## Performance

### Current Capabilities
- Handles hundreds of points efficiently
- Real-time processing on upload
- Smooth playback animation
- Responsive UI

### Optimization Opportunities
- Cache processed results
- Use database indexes
- Implement pagination for large datasets
- Optimize C++ validator usage
- Add WebSocket for real-time updates
- Implement background task queue (Celery)

## Extension Ideas

1. **Multi-aircraft support**: Track multiple aircraft simultaneously
2. **Real-time data**: WebSocket integration for live tracking
3. **Historical analysis**: Charts and graphs of past flights
4. **Alerts system**: Notifications when violations occur
5. **Export functionality**: Generate PDF reports
6. **3D visualization**: Three.js for 3D corridor rendering
7. **Weather data**: Integrate weather conditions
8. **Flight planning**: Create corridors interactively
9. **Batch processing**: Upload multiple files at once
10. **Machine learning**: Predict trajectory violations

## Troubleshooting

### Common Issues

1. **Import errors**: Run `pip install -r requirements.txt`
2. **Database errors**: Delete `db.sqlite3` and run migrations
3. **C++ not compiling**: Check g++ installation, run `make` in cpp/
4. **Files not uploading**: Check media directory permissions
5. **Map not loading**: Check internet connection (CDN dependencies)
6. **Playback not working**: Check browser console for JavaScript errors

## Resources

- Django Documentation: https://docs.djangoproject.com/
- Django REST Framework: https://www.django-rest-framework.org/
- Leaflet Documentation: https://leafletjs.com/
- Haversine Formula: https://en.wikipedia.org/wiki/Haversine_formula

## Support

For issues or questions:
1. Check README.md for detailed instructions
2. Review QUICKSTART.md for setup steps
3. Examine browser console for frontend errors
4. Check Django logs for backend errors
5. Run tests to verify functionality

---

**FOFIS** - A comprehensive solution for aircraft trajectory monitoring and analysis.

