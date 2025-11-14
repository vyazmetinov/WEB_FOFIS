"""
API views for the monitoring application.
"""
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser
from django.shortcuts import render
from .models import FlightCase
from .serializers import (
    FlightCaseSerializer,
    FlightCaseCreateSerializer,
    FlightCaseListSerializer,
)
from .processing import process_flight_case


class FlightCaseViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing FlightCase objects.
    
    Endpoints:
    - GET /api/flight-cases/ - List all flight cases
    - POST /api/flight-cases/ - Create new flight case (upload files)
    - GET /api/flight-cases/{id}/ - Get details of a flight case
    - DELETE /api/flight-cases/{id}/ - Delete a flight case
    - POST /api/flight-cases/{id}/process/ - Trigger processing
    """
    queryset = FlightCase.objects.all()
    parser_classes = [MultiPartParser, FormParser, JSONParser]
    
    def get_serializer_class(self):
        if self.action == 'create':
            return FlightCaseCreateSerializer
        elif self.action == 'list':
            return FlightCaseListSerializer
        return FlightCaseSerializer
    
    def create(self, request, *args, **kwargs):
        """
        Create a new FlightCase by uploading corridor and trajectory files.
        Automatically triggers processing after creation.
        """
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        # Save the flight case
        flight_case = serializer.save()
        
        # Automatically process the files
        success = process_flight_case(flight_case)
        
        # Return full details
        response_serializer = FlightCaseSerializer(flight_case)
        
        return Response(
            response_serializer.data,
            status=status.HTTP_201_CREATED
        )
    
    @action(detail=True, methods=['post'])
    def process(self, request, pk=None):
        """
        Manually trigger processing for a flight case.
        """
        flight_case = self.get_object()
        success = process_flight_case(flight_case)
        
        if success:
            serializer = FlightCaseSerializer(flight_case)
            return Response(serializer.data)
        else:
            return Response(
                {'error': flight_case.processing_error},
                status=status.HTTP_400_BAD_REQUEST
            )
    
    @action(detail=True, methods=['get'])
    def trajectory_data(self, request, pk=None):
        """
        Get detailed trajectory data for playback.
        """
        flight_case = self.get_object()
        
        if not flight_case.is_processed:
            return Response(
                {'error': 'Flight case has not been processed yet'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        return Response({
            'corridor': flight_case.corridor_data,
            'trajectory': flight_case.trajectory_data,
            'start_time': flight_case.trajectory_start_time,
            'end_time': flight_case.trajectory_end_time,
            'mean_speed': flight_case.mean_speed,
            'mean_deviation': flight_case.mean_deviation,
        })


def index_view(request):
    """
    Main page view - serves the frontend HTML.
    """
    return render(request, 'index.html')

