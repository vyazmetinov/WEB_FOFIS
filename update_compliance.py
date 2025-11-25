#!/usr/bin/env python
"""
Script to update compliance_percentage for existing FlightCase records.
"""
import os
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'fofis_project.settings')
django.setup()

from monitoring.models import FlightCase
from monitoring.processing import process_flight_case

def update_existing_records():
    """Update compliance_percentage for all existing FlightCase records."""
    flight_cases = FlightCase.objects.filter(is_processed=True, compliance_percentage__isnull=True)
    
    count = flight_cases.count()
    print(f"Found {count} FlightCase(s) without compliance_percentage")
    
    for i, fc in enumerate(flight_cases, 1):
        print(f"Processing {i}/{count}: FlightCase #{fc.id}")
        
        try:
            # Reprocess to calculate compliance
            success = process_flight_case(fc)
            
            if success:
                print(f"  ✓ Updated: compliance = {fc.compliance_percentage:.1f}%")
            else:
                print(f"  ✗ Failed: {fc.processing_error}")
        
        except Exception as e:
            print(f"  ✗ Error: {e}")
    
    print(f"\n✓ Done! Updated {count} record(s)")

if __name__ == '__main__':
    update_existing_records()




