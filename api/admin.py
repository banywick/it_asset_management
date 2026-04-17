from django.contrib import admin
from django.urls import path
from django.shortcuts import redirect
from django.template.response import TemplateResponse
from django.contrib import messages
from django.http import HttpResponse
import pandas as pd
from io import BytesIO
from .models import Department, Employee, Workplace, Computer, Monitor, TV, MFP, UPS, Location

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
        first_col = df.columns[0]
        new_count = 0
        for _, row in df.iterrows():
            model = str(row[first_col]).strip()
            if model and model != 'nan' and model.lower() != 'модель':
                asset_number = f"MFP-{model[:20].replace(' ', '_')}"
                obj, created = MFP.objects.get_or_create(
                    model=model,
                    defaults={'asset_number': asset_number}
                )
                if created:
                    new_count += 1
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
        
        for col in df.columns:
            col_lower = str(col).lower()
            if 'марка' in col_lower or 'brand' in col_lower:
                brand_col = col
            elif 'диагональ' in col_lower or 'size' in col_lower:
                size_col = col
            elif 'номер' in col_lower or 'asset' in col_lower:
                asset_col = col
        
        if not brand_col or not size_col:
            raise Exception("Не найдены колонки 'марка' и 'диагональ'")
        
        for _, row in df.iterrows():
            brand = str(row[brand_col]).strip()
            size = float(row[size_col]) if pd.notna(row[size_col]) else None
            asset_number = str(row[asset_col]).strip() if asset_col and pd.notna(row.get(asset_col)) else None
            
            if brand and brand != 'nan' and size:
                if brand.lower() not in ['марка', 'brand']:
                    obj, created = TV.objects.get_or_create(
                        brand=brand,
                        size=size,
                        asset_number=asset_number if asset_number and asset_number != 'nan' else None
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
        
        for col in df.columns:
            col_lower = str(col).lower()
            if 'модель' in col_lower or 'model' in col_lower:
                model_col = col
            elif 'номер' in col_lower or 'asset' in col_lower:
                asset_col = col
        
        if not model_col:
            raise Exception("Не найдена колонка 'модель'")
        
        for _, row in df.iterrows():
            model = str(row[model_col]).strip()
            asset_number = str(row[asset_col]).strip() if asset_col and pd.notna(row.get(asset_col)) else None
            
            if model and model != 'nan' and model.lower() not in ['модель', 'model']:
                if not asset_number or asset_number == 'nan':
                    asset_number = f"UPS-{model[:20].replace(' ', '_')}"
                
                obj, created = UPS.objects.get_or_create(
                    model=model,
                    asset_number=asset_number
                )
                if created:
                    new_count += 1
        return new_count
    except Exception as e:
        raise Exception(f"Ошибка при импорте ИБП: {str(e)}")

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
        
        # Лист 3: МФУ
        df_mfp = pd.DataFrame({
            'модель': ['Xerox WorkCentre 123', 'HP LaserJet MFP 234', 'Canon PIXMA MG3640S']
        })
        df_mfp.to_excel(writer, sheet_name='МФУ', index=False)
        
        # Лист 4: Телевизоры
        df_tv = pd.DataFrame({
            'марка': ['Samsung', 'LG', 'Sony'],
            'диагональ': [55, 65, 43],
            'номер ОС': ['ТВ-001', 'ТВ-002', 'ТВ-003']
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
            'номер ОС': ['ИБП-001', 'ИБП-002', 'ИБП-003']
        })
        df_ups.to_excel(writer, sheet_name='ИБП', index=False)
        
        # Лист 7: Локации
        df_locations = pd.DataFrame({
            'название': ['Минск', 'Мачулищи', 'Жодино']
        })
        df_locations.to_excel(writer, sheet_name='Локации', index=False)
        
        # Добавляем лист с инструкцией
        df_instructions = pd.DataFrame({
            'Инструкция': [
                '1. Заполните каждый лист своими данными',
                '2. Не удаляйте и не переименовывайте листы',
                '3. Не изменяйте названия колонок в первой строке',
                '4. Для отделов, МФУ, мониторов, локаций достаточно одной колонки',
                '5. Для сотрудников нужно заполнить все три колонки (фамилия, имя, отчество)',
                '6. Для телевизоров нужны марка, диагональ и опционально номер ОС',
                '7. Для ИБП нужны модель и опционально номер ОС',
                '8. При повторной загрузке добавляются только новые записи',
                '9. Пустые строки и дубликаты игнорируются'
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
                '   • "МФУ" - колонка: модель',
                '   • "Телевизоры" - колонки: марка, диагональ, номер ОС (необязательно)',
                '   • "Мониторы" - колонка: марка',
                '   • "ИБП" - колонки: модель, номер ОС (необязательно)',
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

class EmployeeAdmin(ImportExcelAdmin):
    list_display = ('last_name', 'first_name', 'patronymic', 'department')
    search_fields = ('last_name', 'first_name')
    list_filter = ('department',)

class MFPAdmin(ImportExcelAdmin):
    list_display = ('asset_number', 'model', 'department', 'ip_address')
    search_fields = ('asset_number', 'model')
    list_filter = ('department',)

class TVAdmin(ImportExcelAdmin):
    list_display = ('brand', 'size', 'asset_number', 'location')
    search_fields = ('brand', 'asset_number', 'location')

class MonitorAdmin(ImportExcelAdmin):
    list_display = ('brand',)
    search_fields = ('brand',)

class UPSAdmin(ImportExcelAdmin):
    list_display = ('asset_number', 'model', 'department', 'battery_serial_number', 'battery_replaced_at')
    search_fields = ('asset_number', 'model')
    list_filter = ('department',)

class LocationAdmin(ImportExcelAdmin):
    list_display = ('name',)
    search_fields = ('name',)

class ComputerAdmin(admin.ModelAdmin):
    list_display = ('asset_number', 'system_unit', 'department', 'assigned_to', 'needs_upgrade')
    search_fields = ('asset_number', 'system_unit')
    list_filter = ('department', 'needs_upgrade', 'has_keyboard', 'has_mouse')
    filter_horizontal = ('monitors',)

class WorkplaceAdmin(admin.ModelAdmin):
    list_display = ('employee', 'location', 'city', 'get_status_display', 'created_at')
    list_filter = ('status', 'city')
    search_fields = ('employee__last_name', 'employee__first_name', 'location', 'city__name')
    raw_id_fields = ('employee', 'mfp', 'ups', 'city')
    
    def get_status_display(self, obj):
        return obj.get_status_display()
    get_status_display.short_description = 'Статус'
    get_status_display.admin_order_field = 'status'

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