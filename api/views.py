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
        
        query_lower = query.lower()
        query_words = query_lower.split()
        
        # Поиск сотрудников (остается без изменений)
        all_employees = Employee.objects.all()
        employees_found = []
        
        for emp in all_employees:
            searchable = f"{emp.last_name} {emp.first_name} {emp.patronymic or ''}".lower()
            match = all(word in searchable for word in query_words)
            if match:
                employees_found.append(emp)
        
        for emp in employees_found:
            workplace = Workplace.objects.filter(employee=emp).first()
            computer = None
            ups = None
            mfp = None
            
            if workplace:
                computer = workplace.computer
                ups = workplace.ups
                mfp = workplace.mfp
            
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
                    'monitors': [{'brand': m.brand, 'id': m.id} for m in computer.monitors.all()] if computer else [],
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
        
        # Поиск компьютеров
        all_computers = Computer.objects.all()
        for comp in all_computers:
            searchable = f"{comp.asset_number} {comp.system_unit or ''}".lower()
            match = all(word in searchable for word in query_words)
            
            if match:
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
                    'monitors': [{'brand': m.brand, 'id': m.id} for m in comp.monitors.all()],
                    'monitors_detail': [{'brand': m.brand, 'id': m.id} for m in comp.monitors.all()],
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
        all_mfps = MFP.objects.all()
        for mfp in all_mfps:
            searchable = f"{mfp.asset_number} {mfp.model} {mfp.ip_address or ''}".lower()
            match = all(word in searchable for word in query_words)
            
            if match:
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
        all_ups = UPS.objects.all()
        for ups in all_ups:
            searchable = f"{ups.asset_number} {ups.model} {ups.comment or ''}".lower()
            match = all(word in searchable for word in query_words)
            
            if match:
                workplaces_with_ups = Workplace.objects.filter(ups=ups)
                battery_history = BatteryHistory.objects.filter(ups=ups).order_by('-replaced_at')
                
                results['ups'].append({
                    'id': ups.id,
                    'asset_number': ups.asset_number,
                    'model': ups.model,
                    'status': ups.status,
                    'comment': ups.comment,
                    'battery_serial_number': ups.battery_serial_number,
                    'battery_replaced_at': ups.battery_replaced_at,  # Это поле должно быть
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
        all_tvs = TV.objects.all()
        for tv in all_tvs:
            searchable = f"{tv.asset_number or ''} {tv.brand} {tv.location or ''}".lower()
            match = all(word in searchable for word in query_words)
            
            if match:
                results['tvs'].append({
                    'id': tv.id,
                    'asset_number': tv.asset_number,
                    'brand': tv.brand,
                    'size': tv.size,
                    'location': tv.location
                })
        
        return Response(results)

    @action(detail=False, methods=['get'])
    def suggestions(self, request):
        """Возвращает подсказки для поиска"""
        query = request.query_params.get('q', '').strip()
        print(f"🔍 Подсказки для: '{query}'")
        
        if not query:
            return Response([])
        
        suggestions = []
        
        # Приводим поисковый запрос к нижнему регистру для сравнения
        query_lower = query.lower()
        
        # Поиск сотрудников - ищем по нижнему регистру
        employees = Employee.objects.all()
        
        for emp in employees:
            # Проверяем совпадение вручную (без учета регистра)
            if (query_lower in emp.last_name.lower() or 
                query_lower in emp.first_name.lower() or 
                (emp.patronymic and query_lower in emp.patronymic.lower())):
                suggestions.append({
                    'id': f'emp_{emp.id}',
                    'icon': '👤',
                    'title': emp.full_name,
                    'subtitle': emp.department.name if emp.department else 'Отдел не указан',
                    'type': 'Сотрудник',
                    'searchValue': f"{emp.last_name} {emp.first_name}"
                })
        
        # Ограничиваем количество
        suggestions = suggestions[:5]
        print(f"Найдено сотрудников для подсказок: {len(suggestions)}")
        
        # Поиск компьютеров
        computers = Computer.objects.all()
        for comp in computers:
            if (query_lower in comp.asset_number.lower() or 
                (comp.system_unit and query_lower in comp.system_unit.lower())):
                suggestions.append({
                    'id': f'comp_{comp.id}',
                    'icon': '🖥️',
                    'title': f"ОС №{comp.asset_number}",
                    'subtitle': comp.system_unit or 'Системный блок не указан',
                    'type': 'Компьютер',
                    'searchValue': comp.asset_number
                })
                if len(suggestions) >= 15:
                    break
        
        # Поиск МФУ
        mfps = MFP.objects.all()
        for mfp in mfps:
            if (query_lower in mfp.asset_number.lower() or 
                query_lower in mfp.model.lower()):
                suggestions.append({
                    'id': f'mfp_{mfp.id}',
                    'icon': '🖨️',
                    'title': f"ОС №{mfp.asset_number}",
                    'subtitle': mfp.model,
                    'type': 'МФУ',
                    'searchValue': mfp.asset_number
                })
                if len(suggestions) >= 15:
                    break
        
        # Поиск ИБП
        upses = UPS.objects.all()
        for ups in upses:
            if (query_lower in ups.asset_number.lower() or 
                query_lower in ups.model.lower()):
                suggestions.append({
                    'id': f'ups_{ups.id}',
                    'icon': '🔋',
                    'title': f"ОС №{ups.asset_number}",
                    'subtitle': ups.model,
                    'type': 'ИБП',
                    'searchValue': ups.asset_number
                })
                if len(suggestions) >= 15:
                    break
        
        # Поиск телевизоров
        tvs = TV.objects.all()
        for tv in tvs:
            if ((tv.asset_number and query_lower in tv.asset_number.lower()) or 
                query_lower in tv.brand.lower()):
                suggestions.append({
                    'id': f'tv_{tv.id}',
                    'icon': '📺',
                    'title': tv.brand,
                    'subtitle': f"{tv.size}\" - {tv.asset_number or 'без номера'}",
                    'type': 'Телевизор',
                    'searchValue': tv.brand
                })
                if len(suggestions) >= 15:
                    break
        
        # Поиск отделов
        departments = Department.objects.all()
        for dep in departments:
            if query_lower in dep.name.lower():
                suggestions.append({
                    'id': f'dep_{dep.id}',
                    'icon': '📁',
                    'title': dep.name,
                    'subtitle': f'Отдел',
                    'type': 'Отдел',
                    'searchValue': dep.name
                })
                if len(suggestions) >= 15:
                    break
        
        # Поиск локаций
        locations = Location.objects.all()
        for loc in locations:
            if query_lower in loc.name.lower():
                suggestions.append({
                    'id': f'loc_{loc.id}',
                    'icon': '🏙️',
                    'title': loc.name,
                    'subtitle': f'Локация',
                    'type': 'Локация',
                    'searchValue': loc.name
                })
                if len(suggestions) >= 15:
                    break
        
        return Response(suggestions[:15])
        

