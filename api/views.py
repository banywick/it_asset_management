from rest_framework import viewsets
from rest_framework.viewsets import GenericViewSet
from django.contrib.auth import authenticate, login, logout
from .models import *
from .serializers import *
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework import status
import io
import xlsxwriter
from django.http import HttpResponse
from django.db.models import Q
from django.utils import timezone
from datetime import datetime, timedelta
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator


class CsrfExemptViewSet(viewsets.ModelViewSet):
    @method_decorator(csrf_exempt)
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)

class ReportViewSet(viewsets.GenericViewSet):
    
    @action(detail=False, methods=['post'])
    def generate_report(self, request):
        """Генерация Excel отчета по выбранным сущностям"""
        
        # Получаем параметры из запроса
        entities = request.data.get('entities', [])
        date_from = request.data.get('date_from')
        date_to = request.data.get('date_to')
        
        # Парсим даты
        if date_from and date_to:
            date_from = datetime.strptime(date_from, '%Y-%m-%d')
            date_to = datetime.strptime(date_to, '%Y-%m-%d')
        else:
            # За все время: устанавливаем очень раннюю дату
            date_from = datetime(2000, 1, 1)
            date_to = timezone.now()
        
        # Создаем Excel файл в памяти
        output = io.BytesIO()
        workbook = xlsxwriter.Workbook(output)
        
        # Форматы для стилей
        header_format = workbook.add_format({
            'bold': True,
            'bg_color': '#1abc9c',
            'font_color': 'white',
            'border': 1,
            'align': 'center',
            'valign': 'vcenter'
        })
        
        cell_format = workbook.add_format({
            'border': 1,
            'align': 'left',
            'valign': 'vcenter'
        })
        
        date_format = workbook.add_format({
            'border': 1,
            'align': 'center',
            'valign': 'vcenter',
            'num_format': 'dd.mm.yyyy'
        })
        
        # Шапка отчета
        report_sheet = workbook.add_worksheet('Общая информация')
        report_sheet.merge_range('A1:E1', 'IT Asset Tracker - Отчет по активам', header_format)
        report_sheet.write(2, 0, 'Дата формирования отчета:', cell_format)
        report_sheet.write(2, 1, datetime.now().strftime('%d.%m.%Y %H:%M:%S'), cell_format)
        report_sheet.write(3, 0, 'Период:', cell_format)
        report_sheet.write(3, 1, f"{date_from.strftime('%d.%m.%Y')} - {date_to.strftime('%d.%m.%Y')}", cell_format)
        report_sheet.set_column('A:A', 20)
        report_sheet.set_column('B:B', 30)
        
        # Генерируем отчеты по выбранным сущностям
        if not entities or 'employees' in entities:
            self._generate_employee_report(workbook, header_format, cell_format, date_format, date_from, date_to)
        
        if not entities or 'workplaces' in entities:
            self._generate_workplace_report(workbook, header_format, cell_format, date_format, date_from, date_to)
        
        if not entities or 'computers' in entities:
            self._generate_computer_report(workbook, header_format, cell_format, date_format, date_from, date_to)
        
        if not entities or 'mfps' in entities:
            self._generate_mfp_report(workbook, header_format, cell_format, date_format, date_from, date_to)
        
        if not entities or 'ups' in entities:
            self._generate_ups_report(workbook, header_format, cell_format, date_format, date_from, date_to)
        
        if not entities or 'cartridges' in entities:
            self._generate_cartridge_report(workbook, header_format, cell_format, date_format, date_from, date_to)
        
        if not entities or 'tvs' in entities:
            self._generate_tv_report(workbook, header_format, cell_format, date_format, date_from, date_to)
        
        workbook.close()
        output.seek(0)
        
        # Формируем имя файла
        filename = f"report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
        
        # Отправляем файл
        response = HttpResponse(
            output,
            content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        )
        response['Content-Disposition'] = f'attachment; filename="{filename}"'
        return response
    
    def _generate_employee_report(self, workbook, header_format, cell_format, date_format, date_from, date_to):
        """Отчет по сотрудникам"""
        worksheet = workbook.add_worksheet('Сотрудники')
        
        # Заголовки
        headers = ['ID', 'ФИО', 'Отдел', 'Рабочее место', 'Город', 'Статус рабочего места', 'Компьютер', 'ИБП', 'МФУ']
        for col, header in enumerate(headers):
            worksheet.write(0, col, header, header_format)
        
        # Данные
        employees = Employee.objects.all()
        row = 1
        for emp in employees:
            workplace = Workplace.objects.filter(employee=emp).first()
            
            worksheet.write(row, 0, emp.id, cell_format)
            worksheet.write(row, 1, emp.full_name, cell_format)
            worksheet.write(row, 2, emp.department.name if emp.department else '-', cell_format)
            worksheet.write(row, 3, workplace.location if workplace else '-', cell_format)
            worksheet.write(row, 4, workplace.city.name if workplace and workplace.city else '-', cell_format)
            worksheet.write(row, 5, workplace.get_status_display() if workplace else '-', cell_format)
            worksheet.write(row, 6, workplace.computer.asset_number if workplace and workplace.computer else '-', cell_format)
            worksheet.write(row, 7, workplace.ups.model if workplace and workplace.ups else '-', cell_format)
            worksheet.write(row, 8, workplace.mfp.model if workplace and workplace.mfp else '-', cell_format)
            row += 1
        
        worksheet.set_column('A:A', 8)
        worksheet.set_column('B:B', 30)
        worksheet.set_column('C:C', 20)
        worksheet.set_column('D:D', 25)
        worksheet.set_column('E:E', 15)
        worksheet.set_column('F:F', 20)
        worksheet.set_column('G:G', 15)
        worksheet.set_column('H:H', 20)
        worksheet.set_column('I:I', 20)
    
    def _generate_workplace_report(self, workbook, header_format, cell_format, date_format, date_from, date_to):
        """Отчет по рабочим местам"""
        worksheet = workbook.add_worksheet('Рабочие места')
        
        headers = ['ID', 'Сотрудник', 'Отдел', 'Расположение', 'Город', 'Статус', 'Компьютер', 'ИБП', 'МФУ', 'Дата создания']
        for col, header in enumerate(headers):
            worksheet.write(0, col, header, header_format)
        
        workplaces = Workplace.objects.all()
        row = 1
        for wp in workplaces:
            worksheet.write(row, 0, wp.id, cell_format)
            worksheet.write(row, 1, wp.employee.full_name, cell_format)
            worksheet.write(row, 2, wp.employee.department.name if wp.employee.department else '-', cell_format)
            worksheet.write(row, 3, wp.location, cell_format)
            worksheet.write(row, 4, wp.city.name if wp.city else '-', cell_format)
            worksheet.write(row, 5, wp.get_status_display(), cell_format)
            worksheet.write(row, 6, wp.computer.asset_number if wp.computer else '-', cell_format)
            worksheet.write(row, 7, wp.ups.model if wp.ups else '-', cell_format)
            worksheet.write(row, 8, wp.mfp.model if wp.mfp else '-', cell_format)
            worksheet.write(row, 9, wp.created_at.strftime('%d.%m.%Y'), date_format)
            row += 1
        
        worksheet.set_column('A:A', 8)
        worksheet.set_column('B:B', 30)
        worksheet.set_column('C:C', 20)
        worksheet.set_column('D:D', 25)
        worksheet.set_column('E:E', 15)
        worksheet.set_column('F:F', 20)
        worksheet.set_column('G:G', 15)
        worksheet.set_column('H:H', 20)
        worksheet.set_column('I:I', 20)
        worksheet.set_column('J:J', 15)
    
    def _generate_computer_report(self, workbook, header_format, cell_format, date_format, date_from, date_to):
        """Отчет по компьютерам"""
        worksheet = workbook.add_worksheet('Компьютеры')
        
        headers = ['ID', 'Номер ОС', 'Тип', 'Системный блок', 'Мониторы', 'Клавиатура', 'Мышь', 'Статус', 'Владелец', 'Отдел']
        for col, header in enumerate(headers):
            worksheet.write(0, col, header, header_format)
        
        computers = Computer.objects.all()
        row = 1
        for comp in computers:
            workplace = Workplace.objects.filter(computer=comp).first()
            owner = workplace.employee.full_name if workplace else '-'
            department = workplace.employee.department.name if workplace and workplace.employee.department else '-'
            
            worksheet.write(row, 0, comp.id, cell_format)
            worksheet.write(row, 1, comp.asset_number, cell_format)
            worksheet.write(row, 2, comp.get_computer_type_display(), cell_format)
            worksheet.write(row, 3, comp.system_unit or '-', cell_format)
            monitors = ', '.join([m.brand for m in comp.monitors.all()]) or '-'
            worksheet.write(row, 4, monitors, cell_format)
            worksheet.write(row, 5, 'Да' if comp.has_keyboard else 'Нет', cell_format)
            worksheet.write(row, 6, 'Да' if comp.has_mouse else 'Нет', cell_format)
            worksheet.write(row, 7, comp.get_service_status_display(), cell_format)
            worksheet.write(row, 8, owner, cell_format)
            worksheet.write(row, 9, department, cell_format)
            row += 1
        
        worksheet.set_column('A:A', 8)
        worksheet.set_column('B:B', 15)
        worksheet.set_column('C:C', 15)
        worksheet.set_column('D:D', 35)
        worksheet.set_column('E:E', 20)
        worksheet.set_column('F:F', 10)
        worksheet.set_column('G:G', 10)
        worksheet.set_column('H:H', 15)
        worksheet.set_column('I:I', 25)
        worksheet.set_column('J:J', 20)
    
    def _generate_mfp_report(self, workbook, header_format, cell_format, date_format, date_from, date_to):
        """Отчет по МФУ"""
        worksheet = workbook.add_worksheet('МФУ')
        
        headers = ['ID', 'Номер ОС', 'Модель', 'IP адрес', 'Кабинет', 'Серийный номер', 'MAC адрес', 'Логин', 'Статус', 'Примечания']
        for col, header in enumerate(headers):
            worksheet.write(0, col, header, header_format)
        
        mfps = MFP.objects.all()
        row = 1
        for mfp in mfps:
            worksheet.write(row, 0, mfp.id, cell_format)
            worksheet.write(row, 1, mfp.asset_number, cell_format)
            worksheet.write(row, 2, mfp.model, cell_format)
            worksheet.write(row, 3, mfp.ip_address or '-', cell_format)
            worksheet.write(row, 4, mfp.cabinet_number or '-', cell_format)
            worksheet.write(row, 5, mfp.serial_number or '-', cell_format)
            worksheet.write(row, 6, mfp.mac_address or '-', cell_format)
            worksheet.write(row, 7, mfp.login or '-', cell_format)
            worksheet.write(row, 8, mfp.get_status_display(), cell_format)
            worksheet.write(row, 9, mfp.notes or '-', cell_format)
            row += 1
        
        worksheet.set_column('A:A', 8)
        worksheet.set_column('B:B', 15)
        worksheet.set_column('C:C', 25)
        worksheet.set_column('D:D', 18)
        worksheet.set_column('E:E', 12)
        worksheet.set_column('F:F', 18)
        worksheet.set_column('G:G', 18)
        worksheet.set_column('H:H', 15)
        worksheet.set_column('I:I', 15)
        worksheet.set_column('J:J', 30)
    
    def _generate_ups_report(self, workbook, header_format, cell_format, date_format, date_from, date_to):
        """Отчет по ИБП"""
        worksheet = workbook.add_worksheet('ИБП')
        
        headers = ['ID', 'Номер ОС', 'Модель', 'Статус', 'Аккумулятор', 'Дата замены АКБ', 'Комментарий', 'Рабочее место', 'Сотрудник']
        for col, header in enumerate(headers):
            worksheet.write(0, col, header, header_format)
        
        upses = UPS.objects.all()
        row = 1
        for ups in upses:
            workplace = Workplace.objects.filter(ups=ups).first()
            employee = workplace.employee.full_name if workplace else '-'
            
            worksheet.write(row, 0, ups.id, cell_format)
            worksheet.write(row, 1, ups.asset_number, cell_format)
            worksheet.write(row, 2, ups.model, cell_format)
            worksheet.write(row, 3, ups.get_status_display(), cell_format)
            worksheet.write(row, 4, ups.battery_serial_number or '-', cell_format)
            worksheet.write(row, 5, ups.battery_replaced_at.strftime('%d.%m.%Y') if ups.battery_replaced_at else '-', date_format)
            worksheet.write(row, 6, ups.comment or '-', cell_format)
            worksheet.write(row, 7, workplace.location if workplace else '-', cell_format)
            worksheet.write(row, 8, employee, cell_format)
            row += 1
        
        worksheet.set_column('A:A', 8)
        worksheet.set_column('B:B', 15)
        worksheet.set_column('C:C', 25)
        worksheet.set_column('D:D', 15)
        worksheet.set_column('E:E', 18)
        worksheet.set_column('F:F', 15)
        worksheet.set_column('G:G', 30)
        worksheet.set_column('H:H', 20)
        worksheet.set_column('I:I', 25)
    
    def _generate_cartridge_report(self, workbook, header_format, cell_format, date_format, date_from, date_to):
        """Отчет по картриджам"""
        worksheet = workbook.add_worksheet('Картриджи')
        
        headers = ['ID', 'Модель', 'Минск (шт)', 'Мачулищи (шт)', 'Всего (шт)', 'Совместимые МФУ']
        for col, header in enumerate(headers):
            worksheet.write(0, col, header, header_format)
        
        cartridges = Cartridge.objects.all()
        row = 1
        for cart in cartridges:
            compatible_mfps = ', '.join([m.model for m in cart.compatible_mfps.all()]) or '-'
            
            worksheet.write(row, 0, cart.id, cell_format)
            worksheet.write(row, 1, cart.model, cell_format)
            worksheet.write(row, 2, cart.quantity_minsk, cell_format)
            worksheet.write(row, 3, cart.quantity_machulishchi, cell_format)
            worksheet.write(row, 4, cart.quantity_minsk + cart.quantity_machulishchi, cell_format)
            worksheet.write(row, 5, compatible_mfps, cell_format)
            row += 1
        
        worksheet.set_column('A:A', 8)
        worksheet.set_column('B:B', 20)
        worksheet.set_column('C:C', 12)
        worksheet.set_column('D:D', 15)
        worksheet.set_column('E:E', 12)
        worksheet.set_column('F:F', 30)
    
    def _generate_tv_report(self, workbook, header_format, cell_format, date_format, date_from, date_to):
        """Отчет по телевизорам"""
        worksheet = workbook.add_worksheet('Телевизоры')
        
        headers = ['ID', 'Марка', 'Диагональ', 'Номер ОС', 'Расположение']
        for col, header in enumerate(headers):
            worksheet.write(0, col, header, header_format)
        
        tvs = TV.objects.all()
        row = 1
        for tv in tvs:
            worksheet.write(row, 0, tv.id, cell_format)
            worksheet.write(row, 1, tv.brand, cell_format)
            worksheet.write(row, 2, tv.size, cell_format)
            worksheet.write(row, 3, tv.asset_number or '-', cell_format)
            worksheet.write(row, 4, tv.location or '-', cell_format)
            row += 1
        
        worksheet.set_column('A:A', 8)
        worksheet.set_column('B:B', 20)
        worksheet.set_column('C:C', 10)
        worksheet.set_column('D:D', 15)
        worksheet.set_column('E:E', 30)

class AuthViewSet(CsrfExemptGenericViewSet):
    
    @action(detail=False, methods=['post'])
    def login(self, request):
        username = request.data.get('username')
        password = request.data.get('password')
        
        if not username or not password:
            return Response(
                {'error': 'Пожалуйста, укажите логин и пароль'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        user = authenticate(request, username=username, password=password)
        
        if user is not None:
            # Проверяем, подтвержден ли пользователь
            if hasattr(user, 'profile') and not user.profile.is_approved:
                return Response(
                    {'error': 'Ваша учетная запись ожидает подтверждения администратором'},
                    status=status.HTTP_401_UNAUTHORIZED
                )
            
            login(request, user)
            return Response({
                'success': True,
                'user': UserSerializer(user).data,
                'message': f'Добро пожаловать, {user.username}!'
            })
        else:
            return Response(
                {'error': 'Неверный логин или пароль'},
                status=status.HTTP_401_UNAUTHORIZED
            )
    
    @action(detail=False, methods=['post'])
    def logout(self, request):
        logout(request)
        return Response({'success': True, 'message': 'Вы успешно вышли из системы'})
    
    @action(detail=False, methods=['get'])
    def check_auth(self, request):
        if request.user.is_authenticated:
            return Response({
                'authenticated': True,
                'user': UserSerializer(request.user).data
            })
        return Response({'authenticated': False})
    
    @action(detail=False, methods=['post'])
    def register(self, request):
        serializer = RegisterSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            return Response({
                'success': True,
                'message': 'Регистрация прошла успешно! После подтверждения администратором вы сможете войти в систему.',
                'requires_approval': True
            }, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
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
                'cartridges': [],
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
            'cartridges': [],
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


        # Поиск картриджей
        all_cartridges = Cartridge.objects.all()
        for cart in all_cartridges:
            searchable = f"{cart.model}".lower()
            match = all(word in searchable for word in query_words)
            
            if match:
                results['cartridges'].append({
                    'id': cart.id,
                    'model': cart.model,
                    'quantity_minsk': cart.quantity_minsk,
                    'quantity_machulishchi': cart.quantity_machulishchi,
                    'compatible_mfps_detail': [{
                        'id': m.id,
                        'model': m.model,
                        'asset_number': m.asset_number
                    } for m in cart.compatible_mfps.all()],
                    'total_quantity': cart.quantity_minsk + cart.quantity_machulishchi
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
            searchable = f"{mfp.asset_number} {mfp.model} {mfp.ip_address or ''} {mfp.cabinet_number or ''} {mfp.serial_number or ''} {mfp.mac_address or ''}".lower()
            match = all(word in searchable for word in query_words)
            
            if match:
                workplaces_with_mfp = Workplace.objects.filter(mfp=mfp)
                # Получаем совместимые картриджи
                compatible_cartridges = Cartridge.objects.filter(compatible_mfps=mfp)
                
                results['mfps'].append({
                    'id': mfp.id,
                    'asset_number': mfp.asset_number,
                    'model': mfp.model,
                    'ip_address': mfp.ip_address,
                    'cabinet_number': mfp.cabinet_number,
                    'login': mfp.login,
                    'password': mfp.password,
                    'status': mfp.status,
                    'notes': mfp.notes,
                    'serial_number': mfp.serial_number,
                    'mac_address': mfp.mac_address,
                    'used_in_workplaces': [{
                        'id': wp.id,
                        'employee_name': wp.employee.full_name,
                        'city': wp.city.name if wp.city else None
                    } for wp in workplaces_with_mfp],
                    'compatible_cartridges': [{
                        'id': c.id,
                        'model': c.model,
                        'quantity_minsk': c.quantity_minsk
                    } for c in compatible_cartridges]
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
        query_lower = query.lower()
        
        # Поиск сотрудников
        employees = Employee.objects.all()
        for emp in employees:
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
                if len(suggestions) >= 15:
                    break
        
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
        
        # Поиск картриджей
        cartridges = Cartridge.objects.all()
        for cart in cartridges:
            if query_lower in cart.model.lower():
                suggestions.append({
                    'id': f'cart_{cart.id}',
                    'icon': '🖨️',
                    'title': cart.model,
                    'subtitle': f"Картридж, остаток в Минске: {cart.quantity_minsk} шт.",
                    'type': 'Картридж',
                    'searchValue': cart.model
                })
                if len(suggestions) >= 15:
                    break
        
        # Поиск телевизоров
        tvs = TV.objects.all()
        for tv in tvs:
            if (query_lower in tv.brand.lower() or 
                (tv.asset_number and query_lower in tv.asset_number.lower())):
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
                    'subtitle': 'Отдел',
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
                    'subtitle': 'Локация',
                    'type': 'Локация',
                    'searchValue': loc.name
                })
                if len(suggestions) >= 15:
                    break
        
        return Response(suggestions[:15])
            



class CartridgeViewSet(viewsets.ModelViewSet):
    queryset = Cartridge.objects.all()
    serializer_class = CartridgeSerializer
    filterset_fields = ['compatible_mfps']

class CartridgeMovementViewSet(viewsets.ModelViewSet):
    queryset = CartridgeMovement.objects.all()
    serializer_class = CartridgeMovementSerializer