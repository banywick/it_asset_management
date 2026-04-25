from rest_framework import serializers
from .models import *

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


class BatteryHistorySerializer(serializers.ModelSerializer):
    class Meta:
        model = BatteryHistory
        fields = '__all__'

class UPSSerializer(serializers.ModelSerializer):
    department_name = serializers.ReadOnlyField(source='department.name')
    battery_history = BatteryHistorySerializer(many=True, read_only=True)
    replacement_ups_detail = serializers.SerializerMethodField()
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    
    class Meta:
        model = UPS
        fields = '__all__'
    
    def get_replacement_ups_detail(self, obj):
        if obj.replacement_ups:
            return {
                'id': obj.replacement_ups.id,
                'asset_number': obj.replacement_ups.asset_number,
                'model': obj.replacement_ups.model
            }
        return None
class EmployeeSerializer(serializers.ModelSerializer):
    department_name = serializers.ReadOnlyField(source='department.name')
    ups_asset_number_detail = UPSSerializer(source='ups_asset_number', read_only=True)
    
    class Meta:
        model = Employee
        fields = '__all__'

class ComputerSerializer(serializers.ModelSerializer):
    monitors_detail = MonitorSerializer(source='monitors', many=True, read_only=True)
    computer_type_display = serializers.CharField(source='get_computer_type_display', read_only=True)
    service_status_display = serializers.CharField(source='get_service_status_display', read_only=True)
    
    class Meta:
        model = Computer
        fields = '__all__'


class MFPSerializer(serializers.ModelSerializer):
    department_name = serializers.ReadOnlyField(source='department.name')
    compatible_cartridges = serializers.SerializerMethodField()
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    
    class Meta:
        model = MFP
        fields = '__all__'
    
    def get_compatible_cartridges(self, obj):
        cartridges = Cartridge.objects.filter(compatible_mfps=obj)
        return [{
            'id': c.id,
            'model': c.model,
            'quantity_minsk': c.quantity_minsk,
            'quantity_machulishchi': c.quantity_machulishchi
        } for c in cartridges]
        
class WorkplaceSerializer(serializers.ModelSerializer):
    employee_name = serializers.ReadOnlyField(source='employee.full_name')
    department_name = serializers.ReadOnlyField(source='employee.department.name')
    mfp_detail = MFPSerializer(source='mfp', read_only=True)
    ups_detail = UPSSerializer(source='ups', read_only=True)
    computer_detail = ComputerSerializer(source='computer', read_only=True)
    city_name = serializers.ReadOnlyField(source='city.name')
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    
    class Meta:
        model = Workplace
        fields = '__all__'

class CartridgeSerializer(serializers.ModelSerializer):
    compatible_mfps_detail = serializers.SerializerMethodField()
    total_quantity = serializers.SerializerMethodField()
    
    class Meta:
        model = Cartridge
        fields = '__all__'
    
    def get_compatible_mfps_detail(self, obj):
        return [{'id': m.id, 'model': m.model, 'asset_number': m.asset_number} for m in obj.compatible_mfps.all()]
    
    def get_total_quantity(self, obj):
        return obj.quantity_minsk + obj.quantity_machulishchi

class CartridgeMovementSerializer(serializers.ModelSerializer):
    cartridge_name = serializers.ReadOnlyField(source='cartridge.name')
    cartridge_model = serializers.ReadOnlyField(source='cartridge.model')
    
    class Meta:
        model = CartridgeMovement
        fields = '__all__'

