"""
Admin interface for monitoring app.
"""
from django.contrib import admin
from .models import FlightCase


@admin.register(FlightCase)
class FlightCaseAdmin(admin.ModelAdmin):
    list_display = [
        'id',
        'created_at',
        'is_processed',
        'mean_deviation',
        'mean_speed',
        'compliance_percentage',
    ]
    list_filter = ['is_processed', 'created_at']
    readonly_fields = [
        'created_at',
        'updated_at',
        'mean_deviation',
        'mean_speed',
        'max_speed',
        'corridor_data',
        'trajectory_data',
        'is_processed',
        'processing_error',
    ]
    
    fieldsets = (
        ('Files', {
            'fields': ('corridor_file', 'trajectory_file')
        }),
        ('Computed Metrics', {
            'fields': ('mean_deviation', 'mean_speed', 'max_speed')
        }),
        ('Processing Status', {
            'fields': ('is_processed', 'processing_error')
        }),
        ('Parsed Data', {
            'fields': ('corridor_data', 'trajectory_data'),
            'classes': ('collapse',)
        }),
        ('Metadata', {
            'fields': ('created_at', 'updated_at')
        }),
    )

