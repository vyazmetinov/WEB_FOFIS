"""
Models for the Flight Corridor Monitoring System.
"""
from django.db import models
from django.core.validators import FileExtensionValidator
import json


class FlightCase(models.Model):
    """
    Represents one pair of files: corridor + trajectory.
    Each row in the frontend table corresponds to one FlightCase.
    """
    # File uploads
    corridor_file = models.FileField(
        upload_to='corridors/',
        validators=[FileExtensionValidator(allowed_extensions=['txt'])],
        help_text='Corridor definition file (longitude, latitude, altitude, allowed_deviation, allowed_speed)'
    )
    trajectory_file = models.FileField(
        upload_to='trajectories/',
        validators=[FileExtensionValidator(allowed_extensions=['txt'])],
        help_text='Aircraft trajectory file (latitude, longitude, altitude, time)'
    )
    
    # Computed metrics
    mean_deviation = models.FloatField(
        null=True,
        blank=True,
        help_text='Average deviation of trajectory from corridor (in meters)'
    )
    mean_speed = models.FloatField(
        null=True,
        blank=True,
        help_text='Average aircraft speed (km/h)'
    )
    max_speed = models.FloatField(
        null=True,
        blank=True,
        help_text='Maximum aircraft speed (km/h)'
    )
    compliance_percentage = models.FloatField(
        null=True,
        blank=True,
        help_text='Percentage of trajectory points within corridor constraints (calculated by C++)'
    )
    
    # Parsed data stored as JSON for quick retrieval
    corridor_data = models.JSONField(
        null=True,
        blank=True,
        help_text='Parsed corridor points'
    )
    trajectory_data = models.JSONField(
        null=True,
        blank=True,
        help_text='Parsed trajectory points with computed speeds'
    )
    
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    # Analysis status
    is_processed = models.BooleanField(
        default=False,
        help_text='Whether files have been parsed and analyzed'
    )
    processing_error = models.TextField(
        null=True,
        blank=True,
        help_text='Error message if processing failed'
    )
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"FlightCase #{self.id} - {self.created_at.strftime('%Y-%m-%d %H:%M')}"
    
    @property
    def trajectory_start_time(self):
        """Get the first timestamp from trajectory data."""
        if self.trajectory_data and len(self.trajectory_data) > 0:
            return self.trajectory_data[0].get('time')
        return None
    
    @property
    def trajectory_end_time(self):
        """Get the last timestamp from trajectory data."""
        if self.trajectory_data and len(self.trajectory_data) > 0:
            return self.trajectory_data[-1].get('time')
        return None
    
    def calculate_compliance_python(self):
        """
        Calculate percentage of trajectory points that comply with corridor constraints (Python fallback).
        Returns percentage of points where deviation <= allowed_deviation.
        This is a fallback if C++ calculation is not available.
        """
        if not self.trajectory_data or not self.corridor_data:
            return None
        
        compliant_count = 0
        total_count = len(self.trajectory_data)
        
        for point in self.trajectory_data:
            if point.get('deviation') is not None and point.get('allowed_deviation') is not None:
                if point['deviation'] <= point['allowed_deviation'] and point.get('speed', 0) <= point.get('allowed_speed', float('inf')):
                    compliant_count += 1
        
        if total_count > 0:
            return (compliant_count / total_count) * 100
        return None

