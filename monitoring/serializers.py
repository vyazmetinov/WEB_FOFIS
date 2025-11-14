"""
DRF Serializers for API endpoints.
"""
from rest_framework import serializers
from .models import FlightCase


class FlightCaseSerializer(serializers.ModelSerializer):
    """
    Serializer for FlightCase model.
    """
    trajectory_start_time = serializers.ReadOnlyField()
    trajectory_end_time = serializers.ReadOnlyField()
    
    class Meta:
        model = FlightCase
        fields = [
            'id',
            'corridor_file',
            'trajectory_file',
            'mean_deviation',
            'mean_speed',
            'max_speed',
            'corridor_data',
            'trajectory_data',
            'is_processed',
            'processing_error',
            'created_at',
            'updated_at',
            'trajectory_start_time',
            'trajectory_end_time',
            'compliance_percentage',
        ]
        read_only_fields = [
            'mean_deviation',
            'mean_speed',
            'max_speed',
            'compliance_percentage',
            'corridor_data',
            'trajectory_data',
            'is_processed',
            'processing_error',
            'created_at',
            'updated_at',
        ]


class FlightCaseCreateSerializer(serializers.ModelSerializer):
    """
    Serializer for creating a new FlightCase with file uploads.
    """
    class Meta:
        model = FlightCase
        fields = ['corridor_file', 'trajectory_file']


class FlightCaseListSerializer(serializers.ModelSerializer):
    """
    Minimal serializer for listing flight cases (without full data).
    """
    
    class Meta:
        model = FlightCase
        fields = [
            'id',
            'mean_deviation',
            'mean_speed',
            'max_speed',
            'is_processed',
            'processing_error',
            'created_at',
            'compliance_percentage',
        ]

