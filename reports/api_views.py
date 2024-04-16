from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from .serializers import TrafficViolationSerializer, MediaFileSerializer
from .forms import ReportForm
from .models import TrafficViolation, MediaFile
from utils.utils import (
    process_input, 
    ReportManager,
)
from utils.mysql_utils import (
    get_user_records,
)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_report_api(request):
    # Create a report using the logged-in user
    user = request.user
    serializer = TrafficViolationSerializer(data=request.data)
    
    if serializer.is_valid():
        serializer.save(user=user)  # Associate the report with the logged-in user
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def traffic_violation_list_api(request):
    # Filter violation records by the logged-in user id and get a list of titles
    user_id = request.user.id
    violations = TrafficViolation.objects.filter(user_id=user_id).values('id', 'title')
    return Response(violations)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def traffic_violation_detail_api(request, violation_id):
    try:
        # Get detailed data for a specific traffic violation
        violation = TrafficViolation.objects.get(id=violation_id)
        
        # Verify if the user has permission to access this report
        if violation.user != request.user:
            return Response({'detail': 'You do not have permission to access this report.'}, status=status.HTTP_403_FORBIDDEN)
        
        serializer = TrafficViolationSerializer(violation)
        return Response(serializer.data)
    except TrafficViolation.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)

@api_view(['PUT'])
@permission_classes([IsAuthenticated])
def update_report_api(request, violation_id):
    try:
        # Get the existing TrafficViolation object
        violation = TrafficViolation.objects.get(id=violation_id)

        # Check if the user has permission to update this report
        if violation.user != request.user:
            return Response({'detail': 'You do not have permission to update this report.'}, status=status.HTTP_403_FORBIDDEN)

        # Deserialize the request data using the TrafficViolationSerializer
        serializer = TrafficViolationSerializer(instance=violation, data=request.data, partial=True)

        if serializer.is_valid():
            serializer.save()  # Save the updated report
            return Response(serializer.data, status=status.HTTP_200_OK)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    except TrafficViolation.DoesNotExist:
        return Response({'detail': 'Report not found.'}, status=status.HTTP_404_NOT_FOUND)
