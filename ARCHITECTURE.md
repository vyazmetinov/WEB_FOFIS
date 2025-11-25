# FOFIS Architecture Diagram

## System Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                         FRONTEND (Browser)                       │
├─────────────────────────────────────────────────────────────────┤
│  ┌──────────────┐  ┌──────────────┐  ┌─────────────────────┐  │
│  │  OSM Map     │  │  Playback    │  │  File Upload Table  │  │
│  │  (Leaflet)   │  │  Controls    │  │  (Drag & Drop)      │  │
│  └──────────────┘  └──────────────┘  └─────────────────────┘  │
│                                                                  │
│  JavaScript:                                                     │
│  - Map rendering (corridor + trajectory)                        │
│  - Aircraft animation (interpolation)                           │
│  - Playback controls (play/pause/speed)                         │
│  - AJAX API calls                                               │
└──────────────────────────┬──────────────────────────────────────┘
                           │ HTTP/REST API
                           ↓
┌─────────────────────────────────────────────────────────────────┐
│                      BACKEND (Django)                            │
├─────────────────────────────────────────────────────────────────┤
│  ┌──────────────────────────────────────────────────────────┐  │
│  │              REST API (Django REST Framework)             │  │
│  │  - /api/flight-cases/      (CRUD operations)             │  │
│  │  - /api/flight-cases/{id}/trajectory_data/               │  │
│  └───────────────────────┬──────────────────────────────────┘  │
│                          ↓                                       │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │                   Views & Serializers                     │  │
│  │  - FlightCaseViewSet                                      │  │
│  │  - FlightCaseSerializer                                   │  │
│  └───────────────────────┬──────────────────────────────────┘  │
│                          ↓                                       │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │                  Processing Pipeline                      │  │
│  │  1. Parse files (parsers.py)                              │  │
│  │  2. Compute speeds (geometry.py)                          │  │
│  │  3. Compute deviations (geometry.py)                      │  │
│  │  4. Call C++ validator (optional)                         │  │
│  │  5. Store results in database                             │  │
│  └───────────────────────┬──────────────────────────────────┘  │
│                          ↓                                       │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │                    Models (ORM)                           │  │
│  │  - FlightCase                                             │  │
│  │    * corridor_file, trajectory_file                       │  │
│  │    * mean_deviation, mean_speed                           │  │
│  │    * corridor_data (JSON), trajectory_data (JSON)         │  │
│  └───────────────────────┬──────────────────────────────────┘  │
│                          ↓                                       │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │                  Database (SQLite)                        │  │
│  │  - flight_case table                                      │  │
│  └──────────────────────────────────────────────────────────┘  │
│                                                                  │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │               File Storage (media/)                       │  │
│  │  - corridors/                                             │  │
│  │  - trajectories/                                          │  │
│  └──────────────────────────────────────────────────────────┘  │
└────────────────────────┬─────────────────────────────────────────┘
                         │ subprocess
                         ↓
┌─────────────────────────────────────────────────────────────────┐
│               C++ VALIDATOR (trajectory_validator)               │
├─────────────────────────────────────────────────────────────────┤
│  Input: traj_point, corridor_segment, constraints                │
│  Process: 3D geometry calculations                               │
│  Output: deviation, speed_violation                              │
└─────────────────────────────────────────────────────────────────┘
```

## Request Flow Diagram

### File Upload Flow

```
User uploads files
      │
      ↓
[Frontend] FormData created
      │
      ↓ POST /api/flight-cases/
[Backend] FlightCaseViewSet.create()
      │
      ├→ Save files to media/
      │
      ↓
[Backend] process_flight_case()
      │
      ├→ parse_corridor_file()
      │   └→ Return List[CorridorPoint]
      │
      ├→ parse_trajectory_file()
      │   └→ Return List[TrajectoryPoint]
      │
      ├→ compute_trajectory_speeds()
      │   └→ Add speed to each point
      │
      ├→ compute_deviations()
      │   ├→ For each trajectory point:
      │   │   ├→ find_nearest_corridor_segment()
      │   │   ├→ point_to_segment_distance_3d()
      │   │   └→ Check compliance
      │   └→ Return updated trajectory
      │
      ├→ run_cpp_validation() [optional]
      │   └→ Call C++ for each point
      │
      ├→ Compute aggregate metrics
      │   ├→ mean_deviation
      │   ├→ mean_speed
      │   └→ max_speed
      │
      └→ Save to database
      │
      ↓
[Backend] Return FlightCase JSON
      │
      ↓
[Frontend] Display corridor on map
      │
      └→ Update table with metrics
```

### Playback Flow

```
User clicks table row
      │
      ↓ GET /api/flight-cases/{id}/trajectory_data/
[Backend] Retrieve FlightCase
      │
      └→ Return corridor, trajectory, metrics
      │
      ↓
[Frontend] Render on map
      │
      ├→ displayCorridor()
      │   ├→ Draw polyline
      │   └→ Draw circles (allowed_deviation)
      │
      └→ displayTrajectory()
          └→ Draw dashed line
      │
      ↓
User clicks Play
      │
      ↓
[Frontend] startPlayback()
      │
      ↓
[Animation Loop] updatePlayback()
      │
      ├→ Increment currentTime (based on speed)
      │
      ├→ Find trajectory segment
      │
      ├→ interpolatePosition()
      │   └→ Linear interpolation between points
      │
      ├→ updateAircraftPosition()
      │   └→ Move marker on map
      │
      └→ requestAnimationFrame() → loop
```

## Component Interaction Matrix

| Component | Interacts With | Purpose |
|-----------|----------------|---------|
| Frontend JS | Backend API | Upload files, fetch data |
| Frontend JS | Leaflet Map | Render corridors, trajectories |
| Backend Views | Serializers | Validate and format data |
| Backend Views | Processing | Trigger file processing |
| Processing | Parsers | Parse uploaded files |
| Processing | Geometry | Calculate distances, speeds |
| Processing | C++ Validator | Optional validation |
| Processing | Models | Store results |
| Models | Database | Persist data |
| Geometry | Math libraries | 3D calculations |

## Module Dependencies

```
Frontend (index.html)
  └─ Leaflet.js (CDN)

Django Backend
  ├─ djangorestframework
  ├─ django-cors-headers
  └─ Pillow

monitoring app
  ├─ parsers.py
  │   └─ Python stdlib (datetime, re)
  │
  ├─ geometry.py
  │   └─ Python stdlib (math)
  │
  ├─ processing.py
  │   ├─ parsers
  │   ├─ geometry
  │   └─ subprocess (for C++)
  │
  ├─ views.py
  │   ├─ rest_framework
  │   ├─ models
  │   ├─ serializers
  │   └─ processing
  │
  └─ models.py
      └─ Django ORM

C++ Validator
  └─ Standard C++ libraries (cmath, iostream)
```

## Data Models

### FlightCase Model

```
FlightCase
├─ id: int (PK)
├─ corridor_file: File
├─ trajectory_file: File
├─ mean_deviation: float
├─ mean_speed: float
├─ max_speed: float
├─ corridor_data: JSON [
│   {
│     longitude: float,
│     latitude: float,
│     altitude: float,
│     allowed_deviation: float,
│     allowed_speed: float,
│     index: int
│   },
│   ...
│ ]
├─ trajectory_data: JSON [
│   {
│     latitude: float,
│     longitude: float,
│     altitude: float,
│     time: string,
│     time_seconds: float,
│     speed: float,
│     deviation: float,
│     allowed_deviation: float,
│     allowed_speed: float,
│     compliant: boolean,
│     nearest_segment: int,
│     index: int
│   },
│   ...
│ ]
├─ is_processed: boolean
├─ processing_error: string
├─ created_at: datetime
└─ updated_at: datetime
```

## Algorithm Complexity

| Algorithm | Complexity | Notes |
|-----------|-----------|-------|
| parse_corridor_file | O(n) | n = lines in file |
| parse_trajectory_file | O(m) | m = lines in file |
| compute_trajectory_speeds | O(m) | Linear pass through trajectory |
| compute_deviations | O(m × n) | For each trajectory point, check all segments |
| point_to_segment_distance_3d | O(1) | Constant time calculation |
| haversine_distance | O(1) | Trigonometric operations |
| interpolatePosition | O(1) | Linear interpolation |
| displayCorridor | O(n) | Render each corridor point |
| displayTrajectory | O(m) | Render each trajectory point |
| updatePlayback | O(m) | Find position in sorted array |

## Security Considerations

1. **File Upload**
   - Validate file extensions (.txt only)
   - Limit file size
   - Sanitize file contents
   - Store outside web root

2. **API Endpoints**
   - CSRF protection enabled
   - CORS configured
   - Input validation via serializers
   - Authentication (optional, not implemented)

3. **C++ Validator**
   - Subprocess timeout (1 second)
   - Error handling for crashes
   - Input sanitization

4. **Database**
   - ORM prevents SQL injection
   - No raw queries used

## Scalability

### Current Limitations
- Single server deployment
- Synchronous file processing
- SQLite (not suitable for production)
- No caching

### Scaling Strategies

1. **Horizontal Scaling**
   - Deploy multiple application servers
   - Use load balancer (nginx)
   - Shared database (PostgreSQL)
   - Shared file storage (S3)

2. **Async Processing**
   - Use Celery for background tasks
   - Redis for message queue
   - Process files asynchronously

3. **Caching**
   - Redis for processed results
   - Browser caching for static files
   - Database query caching

4. **Database Optimization**
   - PostgreSQL with indexes
   - Partition large tables
   - Connection pooling

5. **Frontend Optimization**
   - Bundle and minify JS/CSS
   - CDN for static assets
   - Lazy loading for large trajectories

## Technology Stack Summary

| Layer | Technology | Purpose |
|-------|-----------|---------|
| Frontend | HTML5 + JavaScript | User interface |
| Mapping | Leaflet.js | Interactive map |
| Backend Framework | Django 4.2 | Web framework |
| API | Django REST Framework | RESTful API |
| Database | SQLite → PostgreSQL | Data persistence |
| ORM | Django ORM | Database abstraction |
| File Storage | Local filesystem → S3 | User uploads |
| Validation | C++ | High-performance calculations |
| Web Server | Django dev → Gunicorn | WSGI server |
| Reverse Proxy | - → Nginx | Static files, load balancing |

## Deployment Architecture (Production)

```
Internet
   │
   ↓
[Nginx]
   │
   ├─→ Static Files (/static/)
   │
   ├─→ Media Files (/media/)
   │
   └─→ [Gunicorn] → [Django App]
                        │
                        ├─→ [PostgreSQL]
                        │
                        ├─→ [Redis Cache]
                        │
                        ├─→ [Celery Workers]
                        │     └─→ [Redis Queue]
                        │
                        └─→ [File Storage (S3)]
```

---

**FOFIS Architecture** - Designed for scalability, maintainability, and performance.

