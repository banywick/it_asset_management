from django.db import models

class Department(models.Model):
    name = models.CharField(max_length=100, verbose_name="Отдел", unique=True)

    class Meta:
        verbose_name = "Отдел"
        verbose_name_plural = "Отделы"

    def __str__(self):
        return self.name

class Location(models.Model):
    """Модель для локаций (город/населенный пункт)"""
    name = models.CharField(max_length=100, verbose_name="Название локации", unique=True)
    
    class Meta:
        verbose_name = "Локация"
        verbose_name_plural = "Локации"
    
    def __str__(self):
        return self.name

class Employee(models.Model):
    last_name = models.CharField(max_length=100, verbose_name="Фамилия")
    first_name = models.CharField(max_length=100, verbose_name="Имя")
    patronymic = models.CharField(max_length=100, verbose_name="Отчество", blank=True, null=True)
    department = models.ForeignKey(Department, on_delete=models.SET_NULL, null=True, verbose_name="Отдел")
    ups_asset_number = models.ForeignKey('UPS', on_delete=models.SET_NULL, null=True, blank=True, verbose_name="Номер основного средства бесперебойника", related_name='assigned_to_employees')

    class Meta:
        verbose_name = "Сотрудник"
        verbose_name_plural = "Сотрудники"

    @property
    def full_name(self):
        if self.patronymic:
            return f"{self.last_name} {self.first_name} {self.patronymic}"
        return f"{self.last_name} {self.first_name}"

    def __str__(self):
        return self.full_name

class Workplace(models.Model):
    STATUS_CHOICES = [
        ('active', 'Активно'),
        ('inactive', 'Неактивно'),
        ('maintenance', 'На обслуживании'),
        ('repair', 'Требует ремонта'),
    ]
    
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE, verbose_name="Сотрудник")
    location = models.CharField(max_length=200, verbose_name="Место (кабинет/здание)", default="Рабочее место")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='active', verbose_name="Статус")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата создания")
    
    # Существующие поля
    mfp = models.ForeignKey('MFP', on_delete=models.SET_NULL, null=True, blank=True, verbose_name="МФУ")
    ups = models.ForeignKey('UPS', on_delete=models.SET_NULL, null=True, blank=True, verbose_name="Бесперебойник")
    city = models.ForeignKey(Location, on_delete=models.SET_NULL, null=True, blank=True, verbose_name="Город/Локация")
    
    # Новое поле - компьютер
    computer = models.ForeignKey('Computer', on_delete=models.SET_NULL, null=True, blank=True, verbose_name="Компьютер")

    class Meta:
        verbose_name = "Рабочее место"
        verbose_name_plural = "Рабочие места"

    def __str__(self):
        return f"{self.employee.full_name} - {self.location}"

class Monitor(models.Model):
    brand = models.CharField(max_length=100, verbose_name="Марка монитора", unique=True)

    class Meta:
        verbose_name = "Монитор"
        verbose_name_plural = "Мониторы"

    def __str__(self):
        return self.brand

class TV(models.Model):
    brand = models.CharField(max_length=100, verbose_name="Марка телевизора")
    size = models.DecimalField(max_digits=5, decimal_places=1, verbose_name="Диагональ (дюймы)")
    asset_number = models.CharField(max_length=100, verbose_name="Номер основного средства", blank=True, null=True)
    location = models.TextField(blank=True, null=True, verbose_name="Место расположения")

    class Meta:
        verbose_name = "Телевизор"
        verbose_name_plural = "Телевизоры"

    def __str__(self):
        return f"{self.brand} {self.size}\" - {self.asset_number or 'без номера'}"

class Computer(models.Model):
    COMPUTER_TYPES = [
        ('desktop', '🖥️ Стационарный'),
        ('laptop', '💻 Ноутбук'),
        ('all-in-one', '🖥️ Моноблок'),
    ]
    
    SERVICE_STATUS = [
        ('operational', '✅ В эксплуатации'),
        ('repair', '🔧 В ремонте'),
        ('upgrade', '⚡ На модернизации'),
    ]
    
    asset_number = models.CharField(max_length=100, verbose_name="Номер основного средства", default="не определен")
    
    # Тип компьютера
    computer_type = models.CharField(max_length=20, choices=COMPUTER_TYPES, default='desktop', verbose_name="Тип компьютера")
    
    # Статус обслуживания
    service_status = models.CharField(max_length=20, choices=SERVICE_STATUS, default='operational', verbose_name="Статус обслуживания")
    
    # Комплектация
    system_unit = models.CharField(max_length=200, verbose_name="Системный блок", blank=True, null=True)
    monitors = models.ManyToManyField(Monitor, blank=True, verbose_name="Мониторы")
    has_keyboard = models.BooleanField(default=False, verbose_name="Клавиатура")
    has_mouse = models.BooleanField(default=False, verbose_name="Мышь")
    
    needs_upgrade = models.BooleanField(default=False, verbose_name="Требует модернизации")

    class Meta:
        verbose_name = "Компьютер"
        verbose_name_plural = "Компьютеры"

    def __str__(self):
        type_icon = dict(self.COMPUTER_TYPES).get(self.computer_type, '')
        return f"{type_icon} ОС №{self.asset_number} - {self.system_unit or 'системный блок не указан'}"

class MFP(models.Model):
    asset_number = models.CharField(max_length=100, verbose_name="Номер основного средства", default="не определен")
    model = models.CharField(max_length=100, verbose_name="Модель МФУ")
    ip_address = models.GenericIPAddressField(null=True, blank=True, verbose_name="IP адрес")

    class Meta:
        verbose_name = "МФУ"
        verbose_name_plural = "МФУ"

    def __str__(self):
        return f"ОС №{self.asset_number} - {self.model}"

class UPS(models.Model):
    STATUS_CHOICES = [
        ('active', 'Активен'),
        ('repair', 'В ремонте'),
        ('replaced', 'Заменен временно'),
    ]
    
    asset_number = models.CharField(max_length=100, verbose_name="Номер основного средства", default="не определен")
    model = models.CharField(max_length=100, verbose_name="Модель ИБП")
    department = models.ForeignKey(Department, on_delete=models.SET_NULL, null=True, verbose_name="Отдел", blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='active', verbose_name="Статус")
    comment = models.TextField(blank=True, null=True, verbose_name="Комментарий")
    battery_serial_number = models.CharField(max_length=100, blank=True, null=True, verbose_name="Серийный номер аккумулятора")
    battery_replaced_at = models.DateField(null=True, blank=True, verbose_name="Дата замены аккумулятора")
    
    # Временная замена
    replacement_ups = models.OneToOneField('self', on_delete=models.SET_NULL, null=True, blank=True, verbose_name="Временная замена", related_name='replaced_by')
    
    def __str__(self):
        status_emoji = {
            'active': '✅',
            'repair': '🔧',
            'replaced': '🔄'
        }
        return f"{status_emoji.get(self.status, '')} ОС №{self.asset_number} - {self.model}"

class BatteryHistory(models.Model):
    """История замены аккумуляторов"""
    ups = models.ForeignKey(UPS, on_delete=models.CASCADE, verbose_name="ИБП", related_name='battery_history')
    old_battery_serial = models.CharField(max_length=100, verbose_name="Извлеченный аккумулятор (серийный номер)", blank=True, null=True)
    new_battery_serial = models.CharField(max_length=100, verbose_name="Установленный аккумулятор (серийный номер)")
    replaced_at = models.DateField(auto_now_add=True, verbose_name="Дата замены")
    comment = models.TextField(blank=True, null=True, verbose_name="Комментарий к замене")
    performed_by = models.CharField(max_length=150, verbose_name="Кто выполнил замену", blank=True, null=True)
    
    class Meta:
        verbose_name = "История замены АКБ"
        verbose_name_plural = "История замены АКБ"
        ordering = ['-replaced_at']
    
    def __str__(self):
        return f"{self.ups} - замена АКБ от {self.replaced_at}"