from django.contrib import admin
from django.urls import path
from django.shortcuts import redirect
from django.template.response import TemplateResponse
from django.contrib import messages
from django.http import HttpResponse
import pandas as pd
from io import BytesIO
from .models import Department, Employee, Workplace, Computer, Monitor, TV, MFP, UPS, Location, BatteryHistory, Cartridge, CartridgeMovement, UserProfile

# ========== ФУНКЦИИ ИМПОРТА ДЛЯ КАЖДОГО ЛИСТА ==========

def import_departments_from_df(df, request):
    """Импорт отделов из DataFrame"""
    try:
        first_col = df.columns[0]
        new_count = 0
        for _, row in df.iterrows():
            name = str(row[first_col]).strip()
            if name and name != 'nan' and name.lower() != 'название':
                obj, created = Department.objects.get_or_create(name=name)
                if created:
                    new_count += 1
        return new_count
    except Exception as e:
        raise Exception(f"Ошибка при импорте отделов: {str(e)}")

def import_employees_from_df(df, request):
    """Импорт сотрудников из DataFrame"""
    try:
        new_count = 0
        for _, row in df.iterrows():
            last_name = str(row['фамилия']).strip() if 'фамилия' in df.columns else ''
            first_name = str(row['имя']).strip() if 'имя' in df.columns else ''
            patronymic = str(row['отчество']).strip() if 'отчество' in df.columns and pd.notna(row.get('отчество')) else ''
            
            if last_name and last_name != 'nan' and first_name and first_name != 'nan':
                if last_name.lower() not in ['фамилия', 'last_name']:
                    obj, created = Employee.objects.get_or_create(
                        last_name=last_name,
                        first_name=first_name,
                        patronymic=patronymic if patronymic != 'nan' else ''
                    )
                    if created:
                        new_count += 1
        return new_count
    except Exception as e:
        raise Exception(f"Ошибка при импорте сотрудников: {str(e)}")

def import_mfp_from_df(df, request):
    """Импорт МФУ из DataFrame"""
    try:
        new_count = 0
        
        # Определяем колонки
        model_col = None
        asset_col = None
        ip_col = None
        cabinet_col = None
        serial_col = None
        mac_col = None
        login_col = None
        password_col = None
        status_col = None
        notes_col = None
        
        for col in df.columns:
            col_lower = str(col).lower()
            if 'модель' in col_lower or 'model' in col_lower:
                model_col = col
            elif 'номер' in col_lower or 'asset' in col_lower:
                asset_col = col
            elif 'ip' in col_lower:
                ip_col = col
            elif 'кабинет' in col_lower or 'cabinet' in col_lower:
                cabinet_col = col
            elif 'серийный' in col_lower or 'serial' in col_lower:
                serial_col = col
            elif 'mac' in col_lower:
                mac_col = col
            elif 'логин' in col_lower or 'login' in col_lower:
                login_col = col
            elif 'пароль' in col_lower or 'password' in col_lower:
                password_col = col
            elif 'статус' in col_lower or 'status' in col_lower:
                status_col = col
            elif 'примечание' in col_lower or 'note' in col_lower:
                notes_col = col
        
        if not model_col:
            raise Exception("Не найдена колонка 'модель'")
        
        for _, row in df.iterrows():
            model = str(row[model_col]).strip()
            if model and model != 'nan' and model.lower() not in ['модель', 'model']:
                asset_number = str(row[asset_col]).strip() if asset_col and pd.notna(row.get(asset_col)) else 'не определен'
                ip_address = str(row[ip_col]).strip() if ip_col and pd.notna(row.get(ip_col)) else None
                cabinet_number = str(row[cabinet_col]).strip() if cabinet_col and pd.notna(row.get(cabinet_col)) else None
                serial_number = str(row[serial_col]).strip() if serial_col and pd.notna(row.get(serial_col)) else None
                mac_address = str(row[mac_col]).strip() if mac_col and pd.notna(row.get(mac_col)) else None
                login = str(row[login_col]).strip() if login_col and pd.notna(row.get(login_col)) else None
                password = str(row[password_col]).strip() if password_col and pd.notna(row.get(password_col)) else None
                status = str(row[status_col]).strip() if status_col and pd.notna(row.get(status_col)) else 'operational'
                notes = str(row[notes_col]).strip() if notes_col and pd.notna(row.get(notes_col)) else None
                
                # Приводим статус к правильному формату
                if 'списание' in status.lower():
                    status = 'write_off'
                else:
                    status = 'operational'
                
                obj, created = MFP.objects.get_or_create(
                    model=model,
                    asset_number=asset_number,
                    defaults={
                        'ip_address': ip_address,
                        'cabinet_number': cabinet_number,
                        'serial_number': serial_number,
                        'mac_address': mac_address,
                        'login': login,
                        'password': password,
                        'status': status,
                        'notes': notes
                    }
                )
                if created:
                    new_count += 1
                else:
                    # Обновляем существующую запись
                    obj.ip_address = ip_address
                    obj.cabinet_number = cabinet_number
                    obj.serial_number = serial_number
                    obj.mac_address = mac_address
                    obj.login = login
                    obj.password = password
                    obj.status = status
                    obj.notes = notes
                    obj.save()
        return new_count
    except Exception as e:
        raise Exception(f"Ошибка при импорте МФУ: {str(e)}")

def import_tv_from_df(df, request):
    """Импорт телевизоров из DataFrame"""
    try:
        new_count = 0
        brand_col = None
        size_col = None
        asset_col = None
        location_col = None
        
        for col in df.columns:
            col_lower = str(col).lower()
            if 'марка' in col_lower or 'brand' in col_lower:
                brand_col = col
            elif 'диагональ' in col_lower or 'size' in col_lower:
                size_col = col
            elif 'номер' in col_lower or 'asset' in col_lower:
                asset_col = col
            elif 'место' in col_lower or 'location' in col_lower:
                location_col = col
        
        if not brand_col or not size_col:
            raise Exception("Не найдены колонки 'марка' и 'диагональ'")
        
        for _, row in df.iterrows():
            brand = str(row[brand_col]).strip()
            size = float(row[size_col]) if pd.notna(row[size_col]) else None
            asset_number = str(row[asset_col]).strip() if asset_col and pd.notna(row.get(asset_col)) else None
            location = str(row[location_col]).strip() if location_col and pd.notna(row.get(location_col)) else None
            
            if brand and brand != 'nan' and size:
                if brand.lower() not in ['марка', 'brand']:
                    obj, created = TV.objects.get_or_create(
                        brand=brand,
                        size=size,
                        asset_number=asset_number if asset_number and asset_number != 'nan' else None,
                        location=location if location and location != 'nan' else None
                    )
                    if created:
                        new_count += 1
        return new_count
    except Exception as e:
        raise Exception(f"Ошибка при импорте телевизоров: {str(e)}")

def import_monitors_from_df(df, request):
    """Импорт мониторов из DataFrame"""
    try:
        first_col = df.columns[0]
        new_count = 0
        for _, row in df.iterrows():
            brand = str(row[first_col]).strip()
            if brand and brand != 'nan' and brand.lower() != 'марка':
                obj, created = Monitor.objects.get_or_create(brand=brand)
                if created:
                    new_count += 1
        return new_count
    except Exception as e:
        raise Exception(f"Ошибка при импорте мониторов: {str(e)}")

def import_ups_from_df(df, request):
    """Импорт ИБП из DataFrame"""
    try:
        new_count = 0
        model_col = None
        asset_col = None
        status_col = None
        comment_col = None
        
        for col in df.columns:
            col_lower = str(col).lower()
            if 'модель' in col_lower or 'model' in col_lower:
                model_col = col
            elif 'номер' in col_lower or 'asset' in col_lower:
                asset_col = col
            elif 'статус' in col_lower or 'status' in col_lower:
                status_col = col
            elif 'комментарий' in col_lower or 'comment' in col_lower:
                comment_col = col
        
        if not model_col:
            raise Exception("Не найдена колонка 'модель'")
        
        for _, row in df.iterrows():
            model = str(row[model_col]).strip()
            asset_number = str(row[asset_col]).strip() if asset_col and pd.notna(row.get(asset_col)) else None
            status = str(row[status_col]).strip() if status_col and pd.notna(row.get(status_col)) else 'active'
            comment = str(row[comment_col]).strip() if comment_col and pd.notna(row.get(comment_col)) else None
            
            if model and model != 'nan' and model.lower() not in ['модель', 'model']:
                if not asset_number or asset_number == 'nan':
                    asset_number = f"UPS-{model[:20].replace(' ', '_')}"
                
                if 'ремонт' in status.lower():
                    status = 'repair'
                elif 'замен' in status.lower():
                    status = 'replaced'
                else:
                    status = 'active'
                
                obj, created = UPS.objects.get_or_create(
                    model=model,
                    asset_number=asset_number,
                    defaults={'status': status, 'comment': comment}
                )
                if created:
                    new_count += 1
                else:
                    obj.status = status
                    obj.comment = comment
                    obj.save()
        return new_count
    except Exception as e:
        raise Exception(f"Ошибка при импорте ИБП: {str(e)}")

def import_locations_from_df(df, request):
    """Импорт локаций из DataFrame"""
    try:
        first_col = df.columns[0]
        new_count = 0
        for _, row in df.iterrows():
            name = str(row[first_col]).strip()
            if name and name != 'nan' and name.lower() != 'название':
                obj, created = Location.objects.get_or_create(name=name)
                if created:
                    new_count += 1
        return new_count
    except Exception as e:
        raise Exception(f"Ошибка при импорте локаций: {str(e)}")

# ========== ФУНКЦИЯ ГЕНЕРАЦИИ ШАБЛОНА ==========

def generate_excel_template():
    """Генерация Excel шаблона с примерами данных"""
    output = BytesIO()
    
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        # Лист 1: Отделы
        df_departments = pd.DataFrame({
            'название': ['IT отдел', 'Бухгалтерия', 'Отдел продаж', 'Отдел маркетинга']
        })
        df_departments.to_excel(writer, sheet_name='Отделы', index=False)
        
        # Лист 2: Сотрудники
        df_employees = pd.DataFrame({
            'фамилия': ['Иванов', 'Петров', 'Сидорова'],
            'имя': ['Иван', 'Петр', 'Мария'],
            'отчество': ['Иванович', 'Петрович', 'Алексеевна']
        })
        df_employees.to_excel(writer, sheet_name='Сотрудники', index=False)
        
        # Лист 3: МФУ (обновленный с новыми полями)
        df_mfp = pd.DataFrame({
            'модель': ['Xerox WorkCentre 123', 'HP LaserJet MFP 234', 'Canon PIXMA MG3640S'],
            'номер ОС': ['МФУ-001', 'МФУ-002', 'МФУ-003'],
            'IP адрес': ['192.168.1.100', '192.168.1.101', '192.168.1.102'],
            'кабинет': ['305', '210', '101'],
            'серийный номер': ['SN123456', 'SN789012', 'SN345678'],
            'MAC адрес': ['00:11:22:33:44:55', 'AA:BB:CC:DD:EE:FF', '11:22:33:44:55:66'],
            'логин': ['admin', 'user', 'admin'],
            'пароль': ['123456', 'password', 'admin123'],
            'статус': ['В эксплуатации', 'В эксплуатации', 'На списание'],
            'примечания': ['Основной принтер', 'Для отдела кадров', 'Требуется замена']
        })
        df_mfp.to_excel(writer, sheet_name='МФУ', index=False)
        
        # Лист 4: Телевизоры
        df_tv = pd.DataFrame({
            'марка': ['Samsung', 'LG', 'Sony'],
            'диагональ': [55, 65, 43],
            'номер ОС': ['ТВ-001', 'ТВ-002', 'ТВ-003'],
            'место': ['Конференц-зал', 'Холл 1 этаж', 'Кабинет 305']
        })
        df_tv.to_excel(writer, sheet_name='Телевизоры', index=False)
        
        # Лист 5: Мониторы
        df_monitors = pd.DataFrame({
            'марка': ['Dell', 'LG', 'Samsung', 'AOC', 'Philips']
        })
        df_monitors.to_excel(writer, sheet_name='Мониторы', index=False)
        
        # Лист 6: ИБП
        df_ups = pd.DataFrame({
            'модель': ['APC Back-UPS 650', 'CyberPower 1500', 'Powercom Raptor 1000'],
            'номер ОС': ['ИБП-001', 'ИБП-002', 'ИБП-003'],
            'статус': ['Активен', 'В ремонте', 'Активен'],
            'комментарий': ['', 'Замена АКБ', '']
        })
        df_ups.to_excel(writer, sheet_name='ИБП', index=False)
        
        # Лист 7: Локации
        df_locations = pd.DataFrame({
            'название': ['Минск', 'Мачулищи', 'Жодино']
        })
        df_locations.to_excel(writer, sheet_name='Локации', index=False)
        
        # Лист 8: Инструкция
        df_instructions = pd.DataFrame({
            'Инструкция': [
                '1. Заполните каждый лист своими данными',
                '2. Не удаляйте и не переименовывайте листы',
                '3. Не изменяйте названия колонок в первой строке',
                '4. Для отделов, мониторов, локаций достаточно одной колонки',
                '5. Для сотрудников нужно заполнить все три колонки (фамилия, имя, отчество)',
                '6. Для МФУ доступны колонки: модель, номер ОС, IP адрес, кабинет, серийный номер,',
                '   MAC адрес, логин, пароль, статус (В эксплуатации/На списание), примечания',
                '7. Для телевизоров нужны марка, диагональ, номер ОС (опционально) и место (опционально)',
                '8. Для ИБП нужны модель, номер ОС (опционально), статус и комментарий',
                '9. При повторной загрузке добавляются только новые записи',
                '10. Пустые строки и дубликаты игнорируются'
            ]
        })
        df_instructions.to_excel(writer, sheet_name='Инструкция', index=False)
    
    output.seek(0)
    return output

# ========== ОСНОВНАЯ ФУНКЦИЯ ИМПОРТА ==========

def import_all_from_excel(file, request):
    """Импорт всех данных из Excel файла с несколькими листами"""
    try:
        excel_file = pd.ExcelFile(file)
        sheet_names = excel_file.sheet_names
        
        results = {}
        total_new = 0
        
        sheet_mapping = {
            'отделы': import_departments_from_df,
            'departments': import_departments_from_df,
            'сотрудники': import_employees_from_df,
            'employees': import_employees_from_df,
            'мфу': import_mfp_from_df,
            'mfp': import_mfp_from_df,
            'телевизоры': import_tv_from_df,
            'tvs': import_tv_from_df,
            'мониторы': import_monitors_from_df,
            'monitors': import_monitors_from_df,
            'ибп': import_ups_from_df,
            'ups': import_ups_from_df,
            'локации': import_locations_from_df,
            'locations': import_locations_from_df,
        }
        
        for sheet_name in sheet_names:
            if 'инструкция' in sheet_name.lower():
                continue
                
            sheet_lower = sheet_name.lower().strip()
            
            import_func = None
            for key, func in sheet_mapping.items():
                if key in sheet_lower:
                    import_func = func
                    break
            
            if import_func:
                try:
                    df = pd.read_excel(file, sheet_name=sheet_name)
                    if len(df) > 0:
                        count = import_func(df, request)
                        results[sheet_name] = count
                        total_new += count
                except Exception as e:
                    results[sheet_name] = f"Ошибка: {str(e)}"
            else:
                results[sheet_name] = "Пропущен (неизвестный тип данных)"
        
        success_message = f"✅ Импорт завершен! Всего добавлено: {total_new} записей.\n\n"
        for sheet, count in results.items():
            if isinstance(count, int):
                success_message += f"📄 {sheet}: добавлено {count}\n"
            else:
                success_message += f"⚠️ {sheet}: {count}\n"
        
        return True, success_message
    except Exception as e:
        return False, f"❌ Ошибка при импорте: {str(e)}"

# ========== ADMIN КЛАСС ДЛЯ ИМПОРТА ==========

class ImportExcelAdmin(admin.ModelAdmin):
    """Базовый класс для импорта Excel с несколькими листами"""
    change_list_template = "admin/api/change_list.html"
    
    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path('import-excel/', self.import_excel_view, name='import_excel'),
            path('download-template/', self.download_template, name='download_template'),
        ]
        return custom_urls + urls
    
    def download_template(self, request):
        try:
            excel_file = generate_excel_template()
            response = HttpResponse(
                excel_file,
                content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
            )
            response['Content-Disposition'] = 'attachment; filename="import_template.xlsx"'
            return response
        except Exception as e:
            messages.error(request, f'Ошибка при создании шаблона: {str(e)}')
            return redirect('../')
    
    def import_excel_view(self, request):
        if request.method == 'POST' and request.FILES.get('excel_file'):
            excel_file = request.FILES['excel_file']
            
            if not excel_file.name.endswith(('.xlsx', '.xls')):
                messages.error(request, 'Пожалуйста, загрузите файл Excel (.xlsx или .xls)')
                return redirect(request.path)
            
            success, message = import_all_from_excel(excel_file, request)
            if success:
                messages.success(request, message)
            else:
                messages.error(request, message)
            return redirect(request.path)
        
        context = {
            'title': 'Импорт данных из Excel',
            'description': 'Загрузка данных из Excel файла с несколькими листами',
            'instructions': [
                '📌 Файл должен быть в формате .xlsx или .xls',
                '📌 Каждый лист должен содержать данные определенного типа:',
                '   • "Отделы" - колонка: название',
                '   • "Сотрудники" - колонки: фамилия, имя, отчество',
                '   • "МФУ" - колонки: модель, номер ОС, IP адрес, кабинет, серийный номер,',
                '     MAC адрес, логин, пароль, статус, примечания',
                '   • "Телевизоры" - колонки: марка, диагональ, номер ОС (опционально), место (опционально)',
                '   • "Мониторы" - колонка: марка',
                '   • "ИБП" - колонки: модель, номер ОС (опционально), статус, комментарий',
                '   • "Локации" - колонка: название',
                '📌 Первая строка должна содержать заголовки колонок',
                '📌 При повторной загрузке добавляются только новые уникальные позиции',
            ]
        }
        return TemplateResponse(request, 'admin/import_excel_multi.html', context)
    
    def changelist_view(self, request, extra_context=None):
        extra_context = extra_context or {}
        extra_context['import_url'] = 'import-excel/'
        extra_context['download_url'] = 'download-template/'
        return super().changelist_view(request, extra_context=extra_context)

# ========== ADMIN КЛАССЫ ДЛЯ МОДЕЛЕЙ ==========

class DepartmentAdmin(ImportExcelAdmin):
    list_display = ('name',)
    search_fields = ('name',)
    list_per_page = 20

class EmployeeAdmin(ImportExcelAdmin):
    list_display = ('last_name', 'first_name', 'patronymic', 'department')
    list_display_links = ('last_name', 'first_name')
    search_fields = ('last_name', 'first_name', 'patronymic')
    list_filter = ('department',)
    list_per_page = 20
    
    fieldsets = (
        ('Личная информация', {
            'fields': ('last_name', 'first_name', 'patronymic')
        }),
        ('Рабочая информация', {
            'fields': ('department',)
        }),
    )

class MFPAdmin(ImportExcelAdmin):
    list_display = ('asset_number', 'model', 'ip_address', 'cabinet_number', 'status', 'serial_number')
    list_display_links = ('asset_number', 'model')
    search_fields = ('asset_number', 'model', 'ip_address', 'cabinet_number', 'serial_number', 'mac_address')
    list_filter = ('status',)
    list_per_page = 20
    
    fieldsets = (
        ('Основная информация', {
            'fields': ('asset_number', 'model', 'status')
        }),
        ('Сетевые настройки', {
            'fields': ('ip_address', 'mac_address')
        }),
        ('Расположение', {
            'fields': ('cabinet_number',)
        }),
        ('Доступ', {
            'fields': ('login', 'password')
        }),
        ('Идентификация', {
            'fields': ('serial_number',)
        }),
        ('Дополнительно', {
            'fields': ('notes',)
        }),
    )

class TVAdmin(ImportExcelAdmin):
    list_display = ('brand', 'size', 'asset_number', 'location')
    list_display_links = ('brand',)
    search_fields = ('brand', 'asset_number', 'location')
    list_per_page = 20
    
    fieldsets = (
        ('Основная информация', {
            'fields': ('brand', 'size', 'asset_number', 'location')
        }),
    )

class MonitorAdmin(ImportExcelAdmin):
    list_display = ('brand',)
    search_fields = ('brand',)
    list_per_page = 20

class UPSAdmin(ImportExcelAdmin):
    list_display = ('asset_number', 'model', 'status', 'battery_replaced_at')
    list_display_links = ('asset_number', 'model')
    search_fields = ('asset_number', 'model')
    list_filter = ('status',)
    list_per_page = 20
    
    fieldsets = (
        ('Основная информация', {
            'fields': ('asset_number', 'model', 'status')
        }),
        ('Информация об аккумуляторе', {
            'fields': ('battery_serial_number', 'battery_replaced_at')
        }),
        ('Дополнительно', {
            'fields': ('comment', 'replacement_ups')
        }),
    )

class LocationAdmin(ImportExcelAdmin):
    list_display = ('name',)
    search_fields = ('name',)
    list_per_page = 20

class ComputerAdmin(admin.ModelAdmin):
    list_display = ('asset_number', 'system_unit', 'computer_type', 'service_status', 'needs_upgrade')
    list_display_links = ('asset_number', 'system_unit')
    search_fields = ('asset_number', 'system_unit')
    list_filter = ('computer_type', 'service_status', 'needs_upgrade', 'has_keyboard', 'has_mouse')
    filter_horizontal = ('monitors',)
    list_per_page = 20
    
    fieldsets = (
        ('Основное средство', {
            'fields': ('asset_number', 'computer_type')
        }),
        ('Комплектация', {
            'fields': ('system_unit', 'monitors', 'has_keyboard', 'has_mouse')
        }),
        ('Состояние', {
            'fields': ('service_status', 'needs_upgrade')
        }),
    )

class WorkplaceAdmin(admin.ModelAdmin):
    list_display = ('employee', 'city', 'status', 'created_at')
    list_display_links = ('employee',)
    list_filter = ('status', 'city', 'created_at')
    search_fields = ('employee__last_name', 'employee__first_name', 'location', 'city__name')
    raw_id_fields = ('employee', 'mfp', 'ups', 'computer', 'city')
    list_per_page = 20
    
    fieldsets = (
        ('Информация о рабочем месте', {
            'fields': ('employee', 'city', 'status')
        }),
        ('Оборудование', {
            'fields': ('mfp', 'ups', 'computer')
        }),
    )

class CartridgeAdmin(ImportExcelAdmin):
    list_display = ('model', 'quantity_minsk', 'quantity_machulishchi')
    search_fields = ('model',)
    list_per_page = 20
    
    fieldsets = (
        ('Основная информация', {
            'fields': ('model',)
        }),
        ('Количество на складах', {
            'fields': ('quantity_minsk', 'quantity_machulishchi')
        }),
        ('Совместимость', {
            'fields': ('compatible_mfps',)
        }),
    )
    filter_horizontal = ('compatible_mfps',)

class CartridgeMovementAdmin(admin.ModelAdmin):
    list_display = ('cartridge', 'movement_type', 'quantity', 'get_from_location', 'get_to_location', 'created_at')
    list_filter = ('movement_type', 'created_at')
    search_fields = ('cartridge__model', 'comment', 'performed_by')
    list_per_page = 20
    readonly_fields = ('created_at',)
    
    fieldsets = (
        ('Информация о перемещении', {
            'fields': ('cartridge', 'movement_type', 'quantity')
        }),
        ('Локации', {
            'fields': ('from_location', 'to_location')
        }),
        ('Дополнительно', {
            'fields': ('comment', 'performed_by', 'created_at')
        }),
    )
    
    def get_from_location(self, obj):
        return obj.get_from_location_display() if obj.from_location else '-'
    get_from_location.short_description = 'Откуда'
    
    def get_to_location(self, obj):
        return obj.get_to_location_display() if obj.to_location else '-'
    get_to_location.short_description = 'Куда'

class BatteryHistoryAdmin(admin.ModelAdmin):
    list_display = ('ups', 'new_battery_serial', 'replaced_at', 'performed_by')
    list_filter = ('replaced_at',)
    search_fields = ('ups__asset_number', 'ups__model', 'new_battery_serial', 'old_battery_serial')
    list_per_page = 20
    readonly_fields = ('replaced_at',)
    
    fieldsets = (
        ('Информация о замене', {
            'fields': ('ups', 'old_battery_serial', 'new_battery_serial', 'replaced_at')
        }),
        ('Дополнительно', {
            'fields': ('performed_by', 'comment')
        }),
    )

class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'is_approved', 'phone', 'position', 'created_at')
    list_filter = ('is_approved', 'created_at')
    search_fields = ('user__username', 'user__email', 'phone', 'position')
    list_per_page = 20
    
    fieldsets = (
        ('Пользователь', {
            'fields': ('user', 'is_approved')
        }),
        ('Контактная информация', {
            'fields': ('phone',)
        }),
        ('Рабочая информация', {
            'fields': ('position',)
        }),
        ('Дополнительно', {
            'fields': ('avatar',)
        }),
    )

# ========== РЕГИСТРАЦИЯ МОДЕЛЕЙ ==========

admin.site.register(Department, DepartmentAdmin)
admin.site.register(Employee, EmployeeAdmin)
admin.site.register(Workplace, WorkplaceAdmin)
admin.site.register(Computer, ComputerAdmin)
admin.site.register(Monitor, MonitorAdmin)
admin.site.register(TV, TVAdmin)
admin.site.register(MFP, MFPAdmin)
admin.site.register(UPS, UPSAdmin)
admin.site.register(Location, LocationAdmin)
admin.site.register(Cartridge, CartridgeAdmin)
admin.site.register(CartridgeMovement, CartridgeMovementAdmin)
admin.site.register(BatteryHistory, BatteryHistoryAdmin)
admin.site.register(UserProfile, UserProfileAdmin)