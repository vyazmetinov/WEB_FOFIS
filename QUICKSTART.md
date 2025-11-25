# FOFIS Quick Start Guide

## 1. Installation (5 minutes)

```bash
# Navigate to project directory
cd /Users/ivan/PycharmProjects/FOFIS

# Create and activate virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Compile C++ validator
cd cpp
make
cd ..

# Setup database
python manage.py makemigrations
python manage.py migrate

# Create directories
mkdir -p media/corridors media/trajectories static
```

## 2. Run the Server

```bash
python manage.py runserver
```

## 3. Open in Browser

Navigate to: http://127.0.0.1:8000/

## 4. Upload Sample Data

1. Look for the table at the bottom of the page
2. In the last row:
   - **Corridor File**: Drag and drop `sample_data/corridor.txt` or click to browse
   - **Trajectory File**: Drag and drop `sample_data/trajectory.txt` or click to browse
3. Files will be automatically processed

## 5. Start Playback

1. Click on the newly created row in the table
2. The corridor (green line) and trajectory (blue dashed line) will appear on the map
3. In the playback controls (top-right):
   - Click **▶ Play** to start animation
   - Adjust speed with the dropdown (1×, 2×, 4×, etc.)
   - Use the time slider to jump to specific times
   - Click **⏸ Pause** to pause

## 6. View Metrics

Each row shows:
- **Mean Deviation**: Average distance from corridor (meters)
- **Mean Speed**: Average aircraft speed (km/h)

## Test Different Scenarios

### Compliant Flight
```
Corridor: sample_data/corridor.txt
Trajectory: sample_data/trajectory.txt
```

### Violation Scenario
```
Corridor: sample_data/corridor_violation.txt
Trajectory: sample_data/trajectory_violation.txt
```

## Troubleshooting

### Import Error
```bash
pip install -r requirements.txt
```

### Database Error
```bash
rm db.sqlite3
python manage.py migrate
```

### C++ Not Found
```bash
cd cpp
make
chmod +x trajectory_validator
```

## Next Steps

- Create superuser: `python manage.py createsuperuser`
- Access admin: http://127.0.0.1:8000/admin/
- Read full documentation: `README.md`
- API documentation: See README.md "API Endpoints" section

Enjoy using FOFIS!

