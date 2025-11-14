"""
Tests for the monitoring application.
"""
from django.test import TestCase, Client
from django.core.files.uploadedfile import SimpleUploadedFile
from .models import FlightCase
from .parsers import parse_corridor_file, parse_trajectory_file, parse_time
from .geometry import (
    haversine_distance,
    distance_3d,
    point_to_segment_distance_3d,
    calculate_speed,
)
import os
import tempfile


class ParserTests(TestCase):
    """Test file parsing functionality."""
    
    def test_parse_time(self):
        """Test time parsing."""
        t = parse_time("13:45:30")
        self.assertEqual(t.hour, 13)
        self.assertEqual(t.minute, 45)
        self.assertEqual(t.second, 30)
    
    def test_parse_corridor_file(self):
        """Test corridor file parsing."""
        # Create temporary file
        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
            f.write("10.0 50.0 1000.0 500.0 300.0\n")
            f.write("11.0 51.0 1200.0 500.0 320.0\n")
            temp_path = f.name
        
        try:
            points = parse_corridor_file(temp_path)
            self.assertEqual(len(points), 2)
            self.assertEqual(points[0]['longitude'], 10.0)
            self.assertEqual(points[0]['latitude'], 50.0)
            self.assertEqual(points[0]['altitude'], 1000.0)
            self.assertEqual(points[0]['allowed_deviation'], 500.0)
            self.assertEqual(points[0]['allowed_speed'], 300.0)
        finally:
            os.unlink(temp_path)
    
    def test_parse_trajectory_file(self):
        """Test trajectory file parsing."""
        # Create temporary file
        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
            f.write("50.0 10.0 1000.0 13:00:00\n")
            f.write("51.0 11.0 1200.0 13:10:00\n")
            temp_path = f.name
        
        try:
            points = parse_trajectory_file(temp_path)
            self.assertEqual(len(points), 2)
            self.assertEqual(points[0]['latitude'], 50.0)
            self.assertEqual(points[0]['longitude'], 10.0)
            self.assertEqual(points[0]['altitude'], 1000.0)
            self.assertEqual(points[0]['time'], '13:00:00')
        finally:
            os.unlink(temp_path)


class GeometryTests(TestCase):
    """Test geometry calculations."""
    
    def test_haversine_distance(self):
        """Test haversine distance calculation."""
        # Distance from (0, 0) to (0, 1) should be approximately 111 km
        dist = haversine_distance(0, 0, 0, 1)
        self.assertAlmostEqual(dist / 1000, 111.19, delta=1.0)
    
    def test_distance_3d(self):
        """Test 3D distance calculation."""
        # Same point should have zero distance
        dist = distance_3d(50.0, 10.0, 1000.0, 50.0, 10.0, 1000.0)
        self.assertAlmostEqual(dist, 0.0, delta=0.1)
        
        # Different altitude only
        dist = distance_3d(50.0, 10.0, 1000.0, 50.0, 10.0, 2000.0)
        self.assertAlmostEqual(dist, 1000.0, delta=0.1)
    
    def test_point_to_segment_distance_3d(self):
        """Test point to segment distance."""
        # Point on the segment should have distance 0
        point = (50.0, 10.0, 1000.0)
        segment_start = (50.0, 10.0, 1000.0)
        segment_end = (51.0, 11.0, 1000.0)
        
        dist = point_to_segment_distance_3d(point, segment_start, segment_end)
        self.assertAlmostEqual(dist, 0.0, delta=1.0)
    
    def test_calculate_speed(self):
        """Test speed calculation."""
        point1 = {
            'latitude': 50.0,
            'longitude': 10.0,
            'altitude': 1000.0,
            'time_seconds': 0
        }
        point2 = {
            'latitude': 50.0,
            'longitude': 10.01,
            'altitude': 1000.0,
            'time_seconds': 3600  # 1 hour later
        }
        
        speed = calculate_speed(point1, point2)
        # Should be approximately 1.11 km/h (0.01 degrees ≈ 1.11 km at equator)
        self.assertGreater(speed, 0)


class FlightCaseModelTests(TestCase):
    """Test FlightCase model."""
    
    def test_create_flight_case(self):
        """Test creating a flight case."""
        corridor_file = SimpleUploadedFile(
            "corridor.txt",
            b"10.0 50.0 1000.0 500.0 300.0\n11.0 51.0 1200.0 500.0 320.0"
        )
        trajectory_file = SimpleUploadedFile(
            "trajectory.txt",
            b"50.0 10.0 1000.0 13:00:00\n51.0 11.0 1200.0 13:10:00"
        )
        
        fc = FlightCase.objects.create(
            corridor_file=corridor_file,
            trajectory_file=trajectory_file
        )
        
        self.assertIsNotNone(fc.id)
        self.assertFalse(fc.is_processed)
        self.assertIsNone(fc.mean_deviation)
        self.assertIsNone(fc.mean_speed)


class APITests(TestCase):
    """Test API endpoints."""
    
    def setUp(self):
        self.client = Client()
    
    def test_list_flight_cases(self):
        """Test listing flight cases."""
        response = self.client.get('/api/flight-cases/')
        self.assertEqual(response.status_code, 200)
    
    def test_create_flight_case_missing_files(self):
        """Test creating flight case without files."""
        response = self.client.post('/api/flight-cases/', {})
        self.assertEqual(response.status_code, 400)
    
    def test_index_view(self):
        """Test main index view."""
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)

