# FOFIS - Flight Corridor Monitoring System

A Django-based web application for monitoring and analyzing aircraft trajectories against defined flight corridors. The system features real-time visualization on an OpenStreetMap interface, file-based trajectory analysis, and playback simulation.

![FOFIS Screenshot](https://via.placeholder.com/800x400?text=FOFIS+Aircraft+Trajectory+Monitoring)

## Features

- **Interactive OSM Map**: Real-time visualization using Leaflet
- **Corridor Management**: Upload and display allowed flight corridors with 3D tubes
- **Trajectory Analysis**: Upload aircraft trajectories and compute deviations
- **Playback Controls**: Simulate aircraft movement with variable speed (1×, 2×, 4×, 8×, 16×)
- **Metrics Calculation**: 
  - Mean deviation from corridor
  - Average and maximum speeds
  - Compliance percentage
- **File Management**: Easy drag-and-drop interface for file uploads
- **3D Geometry**: Accurate calculations considering altitude and Earth curvature
- **C++ Integration**: Optional high-performance validation using compiled C++ code

## Architecture

### Backend (Django)
- **Models**: `FlightCase` stores corridor/trajectory pairs and computed metrics
- **Parsers**: Parse corridor.txt and trajectory.txt files
- **Geometry Engine**: 3D distance calculations with haversine formula
- **REST API**: DRF-based endpoints for CRUD operations
- **Processing Pipeline**: Automatic file parsing and metric computation

### Frontend (HTML/JS)
- **Leaflet Map**: OSM-based map with corridor and trajectory overlays
- **Playback Player**: Time-based animation with smooth interpolation
- **File Upload Table**: Drag-and-drop zones for each file type
- **Real-time Updates**: AJAX-based communication with backend

### C++ Module
- **trajectory_validator**: Standalone program for point-to-segment distance calculation
- **High Performance**: Fast computation for large datasets
- **Subprocess Integration**: Called from Django via subprocess

## File Formats

### Corridor File (corridor.txt)

Each line contains 5 space-separated values:

```
longitude latitude altitude allowed_deviation allowed_speed
```

- **longitude, latitude**: GPS coordinates (degrees)
- **altitude**: Height above sea level (meters)
- **allowed_deviation**: Maximum allowed distance from corridor center (meters)
- **allowed_speed**: Maximum allowed speed (km/h)

**Example:**
```
8.6821 50.1109 1000.0 500.0 300.0
9.0000 49.8000 1200.0 500.0 320.0
9.5000 49.5000 1400.0 500.0 340.0
```

### Trajectory File (trajectory.txt)

Each line contains 4 space-separated values:

```
latitude longitude altitude time
```

- **latitude, longitude**: GPS coordinates (degrees)
- **altitude**: Height above sea level (meters)
- **time**: Timestamp in format `hh:mm:ss`

**Example:**
```
50.1109 8.6821 1000.0 13:00:00
49.8000 9.0000 1200.0 13:09:00
49.5000 9.5000 1400.0 13:18:00
```

## Installation

### Prerequisites

- Python 3.8+
- pip
- g++ (for C++ module)
- make

### Step 1: Clone and Set Up Python Environment

```bash
cd /Users/ivan/PycharmProjects/FOFIS

# Create virtual environment (recommended)
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install Python dependencies
pip install -r requirements.txt
```

### Step 2: Compile C++ Module

```bash
cd cpp
make
cd ..
```

This creates the `cpp/trajectory_validator` executable.

### Step 3: Initialize Database

```bash
# Run migrations
python manage.py makemigrations
python manage.py migrate

# Create superuser (optional, for admin access)
python manage.py createsuperuser
```

### Step 4: Create Required Directories

```bash
mkdir -p media/corridors
mkdir -p media/trajectories
mkdir -p static
```

## Running the Application

### Start Development Server

```bash
python manage.py runserver
```

The application will be available at: **http://127.0.0.1:8000/**

### Access Admin Interface

Navigate to **http://127.0.0.1:8000/admin/** and log in with your superuser credentials to manage flight cases directly.

## Usage Guide

### 1. Upload Files

1. Open the application in your browser
2. At the bottom of the page, find the file upload table
3. **Drag and drop** or **click** the corridor dropzone to upload your corridor file
4. **Drag and drop** or **click** the trajectory dropzone to upload your trajectory file
5. Files are automatically processed upon upload

### 2. View Corridor on Map

- Once the corridor file is uploaded, the corridor is immediately displayed on the map as a green polyline
- Green circles around each corridor point show the allowed deviation radius
- Click on corridor points to see allowed deviation and speed limits

### 3. Start Playback

1. Click on any row in the table to load that flight case
2. The corridor and trajectory will be displayed on the map
3. Click the **▶ Play** button in the playback controls (top-right)
4. The aircraft marker (blue circle) will move along the trajectory
5. Use the **time slider** to jump to specific times
6. Select **playback speed** (1×, 2×, 4×, 8×, 16×) to speed up or slow down the animation
7. Click **⏸ Pause** to pause the animation

### 4. View Metrics

Each row in the table shows:
- **Mean Deviation**: Average distance from trajectory to corridor (meters)
- **Mean Speed**: Average aircraft speed (km/h)
- **Compliance**: Percentage of points within corridor constraints (visible in admin)

### 5. Delete Flight Cases

Click the **Delete** button on any row to remove that flight case and its associated files.

## Sample Data

Sample files are provided in the `sample_data/` directory:

### Normal Flight
- `corridor.txt` - Frankfurt to Munich corridor
- `trajectory.txt` - Aircraft following the corridor

### Violation Scenario
- `corridor_violation.txt` - Tight corridor constraints
- `trajectory_violation.txt` - Aircraft violating constraints

To test, upload these files through the web interface.

## API Endpoints

The application provides a RESTful API:

### List Flight Cases
```
GET /api/flight-cases/
```

### Create Flight Case (Upload Files)
```
POST /api/flight-cases/
Content-Type: multipart/form-data

corridor_file: <file>
trajectory_file: <file>
```

### Get Flight Case Details
```
GET /api/flight-cases/{id}/
```

### Get Trajectory Data for Playback
```
GET /api/flight-cases/{id}/trajectory_data/
```

Returns:
```json
{
  "corridor": [...],
  "trajectory": [...],
  "start_time": "13:00:00",
  "end_time": "14:00:00",
  "mean_speed": 285.5,
  "mean_deviation": 1234.56
}
```

### Delete Flight Case
```
DELETE /api/flight-cases/{id}/
```

### Trigger Processing
```
POST /api/flight-cases/{id}/process/
```

## Technical Details

### 3D Geometry Calculations

The system uses the **haversine formula** for calculating great-circle distances on Earth, combined with altitude differences for true 3D distance:

```python
horizontal_distance = haversine(lat1, lon1, lat2, lon2)
vertical_distance = |alt2 - alt1|
distance_3d = √(horizontal_distance² + vertical_distance²)
```

### Point-to-Segment Distance

For each trajectory point, the system calculates the shortest distance to each corridor segment using vector projection:

1. Calculate vectors AP (point to segment start) and AB (segment vector)
2. Compute projection parameter: `t = (AP · AB) / |AB|²`
3. Clamp t to [0, 1] to stay on segment
4. Find closest point: `C = A + t * AB`
5. Return distance from point to C

### Speed Calculation

Speed is computed from consecutive trajectory points:

```
distance = distance_3d(p1, p2)
time_diff = t2 - t1
speed = (distance / time_diff) * 3.6  # Convert m/s to km/h
```

### Playback Interpolation

For smooth animation, positions are interpolated linearly between trajectory points:

```
position = p1 + ((current_time - t1) / (t2 - t1)) * (p2 - p1)
```

## C++ Validator

The C++ program validates individual trajectory points:

### Compilation
```bash
cd cpp
g++ -std=c++11 -O2 -o trajectory_validator trajectory_validator.cpp -lm
```

### Usage
```bash
./trajectory_validator traj_lat traj_lon traj_alt traj_speed \
                       seg_start_lat seg_start_lon seg_start_alt \
                       seg_end_lat seg_end_lon seg_end_alt \
                       allowed_deviation allowed_speed
```

### Output
```
deviation speed_violation
```

Example:
```bash
./trajectory_validator 50.0 10.0 1000.0 250.0 \
                       50.1 10.1 1000.0 50.2 10.2 1000.0 \
                       500.0 300.0
```

Output: `15724.32 0.00`

## Development

### Project Structure

```
FOFIS/
├── fofis_project/          # Django project settings
│   ├── settings.py
│   ├── urls.py
│   └── wsgi.py
├── monitoring/             # Main Django app
│   ├── models.py          # FlightCase model
│   ├── views.py           # API views
│   ├── serializers.py     # DRF serializers
│   ├── parsers.py         # File parsing logic
│   ├── geometry.py        # 3D calculations
│   ├── processing.py      # File processing pipeline
│   └── admin.py           # Admin interface
├── templates/             # HTML templates
│   └── index.html        # Main frontend
├── cpp/                   # C++ module
│   ├── trajectory_validator.cpp
│   ├── Makefile
│   └── README.md
├── sample_data/           # Example files
│   ├── corridor.txt
│   └── trajectory.txt
├── media/                 # User uploads (created at runtime)
├── static/               # Static files (created at runtime)
├── manage.py             # Django management script
├── requirements.txt      # Python dependencies
└── README.md            # This file
```

### Adding New Features

1. **Models**: Modify `monitoring/models.py`
2. **API Endpoints**: Add views in `monitoring/views.py`
3. **Frontend**: Edit `templates/index.html`
4. **Calculations**: Extend `monitoring/geometry.py`

### Running Tests

```bash
# Create tests in monitoring/tests.py
python manage.py test
```

## Troubleshooting

### "Module not found" errors
```bash
pip install -r requirements.txt
```

### Database errors
```bash
rm db.sqlite3
python manage.py migrate
```

### C++ validator not found
```bash
cd cpp
make
chmod +x trajectory_validator
```

### Files not uploading
```bash
mkdir -p media/corridors media/trajectories
chmod 755 media
```

### Map not displaying
- Check browser console for JavaScript errors
- Ensure internet connection (Leaflet loads from CDN)
- Verify that files are being processed (check admin interface)

## Performance Notes

- The system handles hundreds of corridor and trajectory points efficiently
- For very large datasets (thousands of points), consider:
  - Sampling trajectory points for display
  - Using the C++ validator for all calculations
  - Implementing database indexing
  - Adding caching for processed results

## License

This is a demonstration project for educational purposes.

## Contributing

Feel free to submit issues or pull requests for improvements.

## Support

For questions or issues, please open an issue on the project repository.

---

**FOFIS** - Flight Corridor Monitoring System
Developed with Django, Leaflet, and C++

