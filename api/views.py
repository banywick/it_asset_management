from rest_framework import viewsets
from .models import Department, Employee, Workplace, Computer, Monitor, TV, MFP, UPS
from .serializers import *

class DepartmentViewSet(viewsets.ModelViewSet):
    queryset = Department.objects.all()
    serializer_class = DepartmentSerializer

class EmployeeViewSet(viewsets.ModelViewSet):
    queryset = Employee.objects.all()
    serializer_class = EmployeeSerializer

class WorkplaceViewSet(viewsets.ModelViewSet):
    queryset = Workplace.objects.all()
    serializer_class = WorkplaceSerializer

class ComputerViewSet(viewsets.ModelViewSet):
    queryset = Computer.objects.all()
    serializer_class = ComputerSerializer

class MonitorViewSet(viewsets.ModelViewSet):
    queryset = Monitor.objects.all()
    serializer_class = MonitorSerializer

class TVViewSet(viewsets.ModelViewSet):
    queryset = TV.objects.all()
    serializer_class = TVSerializer

class MFPViewSet(viewsets.ModelViewSet):
    queryset = MFP.objects.all()
    serializer_class = MFPSerializer

class UPSViewSet(viewsets.ModelViewSet):
    queryset = UPS.objects.all()
    serializer_class = UPSSerializer

class LocationViewSet(viewsets.ModelViewSet):
    queryset = Location.objects.all()
    serializer_class = LocationSerializer