from rest_framework import viewsets
from .models import Department, Employee, Workplace, Computer, Monitor, TV, MFP, UPS
from .serializers import *
from django.db.models import Q
from rest_framework.decorators import action
from rest_framework.response import Response

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

class BatteryHistoryViewSet(viewsets.ModelViewSet):
    queryset = BatteryHistory.objects.all()
    serializer_class = BatteryHistorySerializer
    
    def get_queryset(self):
        queryset = super().get_queryset()
        ups_id = self.request.query_params.get('ups', None)
        if ups_id:
            queryset = queryset.filter(ups_id=ups_id)
        return queryset
    

class GlobalSearchViewSet(viewsets.GenericViewSet):
    """Глобальный поиск по всем сущностям"""
    
    @action(detail=False, methods=['get'])
    def search(self, request):
        query = request.query_params.get('q', '').strip()
        print(f"🔍 Поисковый запрос: '{query}'")
        
        if not query:
            return Response({
                'employees': [],
                'workplaces': [],
                'computers': [],
                'mfps': [],
                'tvs': [],
                'ups': [],
                'departments': [],
                'locations': []
            })
        
        results = {
            'employees': [],
            'workplaces': [],
            'computers': [],
            'mfps': [],
            'tvs': [],
            'ups': [],
            'departments': [],
            'locations': []
        }
        
        # Поиск сотрудников - делаем поиск без учета регистра
        employees = Employee.objects.filter(
            Q(last_name__icontains=query) |
            Q(first_name__icontains=query) |
            Q(patronymic__icontains=query)
        )
        
        print(f"📊 Найдено сотрудников: {employees.count()}")
        
        # Для отладки выведем всех сотрудников в базе
        all_employees = Employee.objects.all()
        print(f"📋 Всего сотрудников в базе: {all_employees.count()}")
        for emp in all_employees:
            print(f"   - {emp.last_name} {emp.first_name} {emp.patronymic or ''}")
        
        for emp in employees:
            print(f"✅ Обработка сотрудника: {emp.last_name} {emp.first_name}")
            
            # Находим рабочее место сотрудника
            workplace = Workplace.objects.filter(employee=emp).first()
            computer = None
            ups = None
            mfp = None
            
            if workplace:
                computer = workplace.computer
                ups = workplace.ups
                mfp = workplace.mfp
            
            # История замен аккумулятора для ИБП
            battery_history = []
            if ups:
                battery_history = BatteryHistory.objects.filter(ups=ups).order_by('-replaced_at')
            
            results['employees'].append({
                'id': emp.id,
                'full_name': emp.full_name,
                'last_name': emp.last_name,
                'first_name': emp.first_name,
                'patronymic': emp.patronymic,
                'department': {
                    'id': emp.department.id if emp.department else None,
                    'name': emp.department.name if emp.department else None
                },
                'workplace': {
                    'id': workplace.id if workplace else None,
                    'city': workplace.city.name if workplace and workplace.city else None,
                    'status': workplace.status if workplace else None,
                    'created_at': workplace.created_at if workplace else None
                } if workplace else None,
                'computer': {
                    'id': computer.id if computer else None,
                    'asset_number': computer.asset_number if computer else None,
                    'system_unit': computer.system_unit if computer else None,
                    'computer_type': computer.computer_type if computer else None,
                    'has_keyboard': computer.has_keyboard if computer else None,
                    'has_mouse': computer.has_mouse if computer else None,
                    'monitors': [{'brand': m.brand} for m in computer.monitors.all()] if computer else [],
                    'service_status': computer.service_status if computer else None
                } if computer else None,
                'ups': {
                    'id': ups.id if ups else None,
                    'asset_number': ups.asset_number if ups else None,
                    'model': ups.model if ups else None,
                    'battery_replaced_at': ups.battery_replaced_at if ups else None,
                    'battery_history': [{
                        'id': bh.id,
                        'old_battery_serial': bh.old_battery_serial,
                        'new_battery_serial': bh.new_battery_serial,
                        'replaced_at': bh.replaced_at,
                        'performed_by': bh.performed_by
                    } for bh in battery_history]
                } if ups else None,
                'mfp': {
                    'id': mfp.id if mfp else None,
                    'asset_number': mfp.asset_number if mfp else None,
                    'model': mfp.model if mfp else None,
                    'ip_address': mfp.ip_address if mfp else None
                } if mfp else None
            })
        
        # Поиск рабочих мест
        workplaces = Workplace.objects.filter(
            Q(employee__last_name__icontains=query) |
            Q(employee__first_name__icontains=query) |
            Q(location__icontains=query) |
            Q(city__name__icontains=query)
        )
        
        for wp in workplaces:
            results['workplaces'].append({
                'id': wp.id,
                'employee_name': wp.employee.full_name,
                'location': wp.location,
                'city': wp.city.name if wp.city else None,
                'status': wp.status,
                'created_at': wp.created_at,
                'computer': {
                    'asset_number': wp.computer.asset_number if wp.computer else None,
                    'system_unit': wp.computer.system_unit if wp.computer else None
                } if wp.computer else None,
                'mfp': {
                    'model': wp.mfp.model if wp.mfp else None,
                    'ip_address': wp.mfp.ip_address if wp.mfp else None
                } if wp.mfp else None,
                'ups': {
                    'model': wp.ups.model if wp.ups else None,
                    'battery_replaced_at': wp.ups.battery_replaced_at if wp.ups else None
                } if wp.ups else None
            })
        
        # Поиск компьютеров
        computers = Computer.objects.filter(
            Q(asset_number__icontains=query) |
            Q(system_unit__icontains=query)
        )
        
        for comp in computers:
            workplace = Workplace.objects.filter(computer=comp).first()
            
            results['computers'].append({
                'id': comp.id,
                'asset_number': comp.asset_number,
                'system_unit': comp.system_unit,
                'computer_type': comp.computer_type,
                'has_keyboard': comp.has_keyboard,
                'has_mouse': comp.has_mouse,
                'service_status': comp.service_status,
                'needs_upgrade': comp.needs_upgrade,
                'monitors': [{'brand': m.brand} for m in comp.monitors.all()],
                'assigned_to': {
                    'id': workplace.employee.id if workplace else None,
                    'full_name': workplace.employee.full_name if workplace else None
                } if workplace else None,
                'workplace': {
                    'id': workplace.id if workplace else None,
                    'city': workplace.city.name if workplace and workplace.city else None
                } if workplace else None
            })
        
        # Поиск МФУ
        mfps = MFP.objects.filter(
            Q(asset_number__icontains=query) |
            Q(model__icontains=query) |
            Q(ip_address__icontains=query)
        )
        
        for mfp in mfps:
            workplaces_with_mfp = Workplace.objects.filter(mfp=mfp)
            results['mfps'].append({
                'id': mfp.id,
                'asset_number': mfp.asset_number,
                'model': mfp.model,
                'ip_address': mfp.ip_address,
                'used_in_workplaces': [{
                    'id': wp.id,
                    'employee_name': wp.employee.full_name,
                    'city': wp.city.name if wp.city else None
                } for wp in workplaces_with_mfp]
            })
        
        # Поиск ИБП
        upses = UPS.objects.filter(
            Q(asset_number__icontains=query) |
            Q(model__icontains=query)
        )
        
        for ups in upses:
            workplaces_with_ups = Workplace.objects.filter(ups=ups)
            battery_history = BatteryHistory.objects.filter(ups=ups).order_by('-replaced_at')
            
            results['ups'].append({
                'id': ups.id,
                'asset_number': ups.asset_number,
                'model': ups.model,
                'status': ups.status,
                'comment': ups.comment,
                'battery_serial_number': ups.battery_serial_number,
                'battery_replaced_at': ups.battery_replaced_at,
                'battery_history': [{
                    'id': bh.id,
                    'old_battery_serial': bh.old_battery_serial,
                    'new_battery_serial': bh.new_battery_serial,
                    'replaced_at': bh.replaced_at,
                    'performed_by': bh.performed_by
                } for bh in battery_history],
                'used_in_workplaces': [{
                    'id': wp.id,
                    'employee_name': wp.employee.full_name,
                    'city': wp.city.name if wp.city else None
                } for wp in workplaces_with_ups]
            })
        
        # Поиск телевизоров
        tvs = TV.objects.filter(
            Q(asset_number__icontains=query) |
            Q(brand__icontains=query) |
            Q(location__icontains=query)
        )
        
        for tv in tvs:
            results['tvs'].append({
                'id': tv.id,
                'asset_number': tv.asset_number,
                'brand': tv.brand,
                'size': tv.size,
                'location': tv.location
            })
        
        # Поиск отделов
        departments = Department.objects.filter(name__icontains=query)
        for dep in departments:
            employees_in_dep = Employee.objects.filter(department=dep)
            results['departments'].append({
                'id': dep.id,
                'name': dep.name,
                'employees_count': employees_in_dep.count(),
                'employees': [{
                    'id': e.id,
                    'full_name': e.full_name
                } for e in employees_in_dep[:5]]
            })
        
        # Поиск локаций
        locations = Location.objects.filter(name__icontains=query)
        for loc in locations:
            workplaces_in_loc = Workplace.objects.filter(city=loc)
            results['locations'].append({
                'id': loc.id,
                'name': loc.name,
                'workplaces_count': workplaces_in_loc.count(),
                'workplaces': [{
                    'id': wp.id,
                    'employee_name': wp.employee.full_name
                } for wp in workplaces_in_loc[:5]]
            })
        
        print(f"✅ Результатов сотрудников: {len(results['employees'])}")
        return Response(results)