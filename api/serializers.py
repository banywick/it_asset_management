from rest_framework import serializers
from .models import Department, Employee, Workplace, Computer, Monitor, TV, MFP, UPS, Location

class LocationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Location
        fields = '__all__'

class DepartmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Department
        fields = '__all__'

class MonitorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Monitor
        fields = '__all__'

class TVSerializer(serializers.ModelSerializer):
    class Meta:
        model = TV
        fields = '__all__'

class MFPSerializer(serializers.ModelSerializer):
    department_name = serializers.ReadOnlyField(source='department.name')
    
    class Meta:
        model = MFP
        fields = '__all__'

class UPSSerializer(serializers.ModelSerializer):
    department_name = serializers.ReadOnlyField(source='department.name')
    
    class Meta:
        model = UPS
        fields = '__all__'

class EmployeeSerializer(serializers.ModelSerializer):
    department_name = serializers.ReadOnlyField(source='department.name')
    ups_asset_number_detail = UPSSerializer(source='ups_asset_number', read_only=True)
    
    class Meta:
        model = Employee
        fields = '__all__'

class WorkplaceSerializer(serializers.ModelSerializer):
    employee_name = serializers.ReadOnlyField(source='employee.full_name')
    department_name = serializers.ReadOnlyField(source='employee.department.name')
    mfp_detail = MFPSerializer(source='mfp', read_only=True)
    ups_detail = UPSSerializer(source='ups', read_only=True)
    city_name = serializers.ReadOnlyField(source='city.name')
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    
    class Meta:
        model = Workplace
        fields = '__all__'

class ComputerSerializer(serializers.ModelSerializer):
    department_name = serializers.ReadOnlyField(source='department.name')
    assigned_to_name = serializers.ReadOnlyField(source='assigned_to.full_name')
    monitors_detail = MonitorSerializer(source='monitors', many=True, read_only=True)
    
    class Meta:
        model = Computer
        fields = '__all__'