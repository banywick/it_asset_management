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
    location = models.CharField(max_length=200, verbose_name="Место (кабинет/здание)")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='active', verbose_name="Статус")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата создания")
    
    # Новые поля
    mfp = models.ForeignKey('MFP', on_delete=models.SET_NULL, null=True, blank=True, verbose_name="МФУ")
    ups = models.ForeignKey('UPS', on_delete=models.SET_NULL, null=True, blank=True, verbose_name="Бесперебойник")
    city = models.ForeignKey(Location, on_delete=models.SET_NULL, null=True, blank=True, verbose_name="Город/Локация")

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
    asset_number = models.CharField(max_length=100, verbose_name="Номер основного средства", default="не определен")
    
    system_unit = models.CharField(max_length=200, verbose_name="Системный блок", blank=True, null=True)
    monitors = models.ManyToManyField(Monitor, blank=True, verbose_name="Мониторы")
    has_keyboard = models.BooleanField(default=False, verbose_name="Клавиатура")
    has_mouse = models.BooleanField(default=False, verbose_name="Мышь")
    
    department = models.ForeignKey(Department, on_delete=models.SET_NULL, null=True, verbose_name="Отдел")
    needs_upgrade = models.BooleanField(default=False, verbose_name="Требует модернизации")
    
    assigned_to = models.ForeignKey(Employee, on_delete=models.SET_NULL, null=True, blank=True, verbose_name="Закреплен за сотрудником")

    class Meta:
        verbose_name = "Компьютер"
        verbose_name_plural = "Компьютеры"

    def __str__(self):
        return f"ОС №{self.asset_number} - {self.system_unit or 'системный блок не указан'}"

class MFP(models.Model):
    asset_number = models.CharField(max_length=100, verbose_name="Номер основного средства", default="не определен")
    model = models.CharField(max_length=100, verbose_name="Модель МФУ")
    department = models.ForeignKey(Department, on_delete=models.SET_NULL, null=True, verbose_name="Отдел")
    ip_address = models.GenericIPAddressField(null=True, blank=True, verbose_name="IP адрес")

    class Meta:
        verbose_name = "МФУ"
        verbose_name_plural = "МФУ"

    def __str__(self):
        return f"ОС №{self.asset_number} - {self.model}"

class UPS(models.Model):
    asset_number = models.CharField(max_length=100, verbose_name="Номер основного средства", default="не определен")
    model = models.CharField(max_length=100, verbose_name="Модель ИБП")
    department = models.ForeignKey(Department, on_delete=models.SET_NULL, null=True, verbose_name="Отдел", blank=True)
    battery_serial_number = models.CharField(max_length=100, blank=True, null=True, verbose_name="Серийный номер аккумулятора")
    battery_replaced_at = models.DateField(null=True, blank=True, verbose_name="Дата замены аккумулятора")
    comment = models.TextField(blank=True, null=True, verbose_name="Комментарий")

    class Meta:
        verbose_name = "ИБП (бесперебойник)"
        verbose_name_plural = "ИБП (бесперебойники)"

    def __str__(self):
        return f"ОС №{self.asset_number} - {self.model}"