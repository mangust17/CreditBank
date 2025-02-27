from django.contrib.auth.models import AbstractUser
from django.db import models
from django.core.validators import MinValueValidator
from decimal import Decimal
from django.utils import timezone

class User(AbstractUser):
    ROLE_CHOICES = [
        ('client', 'Клиент банка'),
        ('referrer', 'Референт по кредитованию'),
        ('admin', 'Системный администратор'),
    ]
    
    role = models.CharField(
        max_length=10,
        choices=ROLE_CHOICES,
        default='client',
        verbose_name='Роль'
    )
    phone = models.CharField(
        max_length=15,
        blank=True,
        verbose_name='Телефон'
    )
    
    groups = models.ManyToManyField(
        'auth.Group',
        verbose_name='groups',
        blank=True,
        help_text='The groups this user belongs to.',
        related_name='custom_user_set',
        related_query_name='custom_user'
    )
    
    user_permissions = models.ManyToManyField(
        'auth.Permission',
        verbose_name='user permissions',
        blank=True,
        help_text='Specific permissions for this user.',
        related_name='custom_user_set',
        related_query_name='custom_user'
    )
    
    def get_unread_notifications_count(self):
        return self.notifications.filter(is_read=False).count()

    class Meta:
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'

    def __str__(self):
        return f"{self.username} ({self.get_role_display()})"

class CreditApplication(models.Model):
    STATUS_CHOICES = [
        ('pending', 'На рассмотрении'),
        ('documents_required', 'Требуются документы'),
        ('under_review', 'Проверка документов'),
        ('approved', 'Одобрено'),
        ('rejected', 'Отклонено'),
    ]
    
    client = models.ForeignKey(
        User, 
        on_delete=models.CASCADE,
        related_name='applications',
        verbose_name='Клиент'
    )
    amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        verbose_name='Сумма кредита'
    )
    term_months = models.IntegerField(verbose_name='Срок (месяцев)')
    purpose = models.TextField(verbose_name='Цель кредита')
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='pending',
        verbose_name='Статус'
    )
    referrer = models.ForeignKey(
        User, 
        on_delete=models.SET_NULL, 
        null=True, 
        related_name='reviewed_applications',
        verbose_name='Референт'
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Дата создания'
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name='Дата обновления'
    )
    
    class Meta:
        verbose_name = 'Заявка на кредит'
        verbose_name_plural = 'Заявки на кредит'
        ordering = ['-created_at']

    def __str__(self):
        return f"Заявка №{self.id} от {self.client.username}"

class Document(models.Model):
    DOC_TYPE_CHOICES = [
        ('passport', 'Паспорт'),
        ('income', 'Справка о доходах'),
        ('employment', 'Справка с места работы'),
        ('other', 'Другое'),
    ]
    
    application = models.ForeignKey(
        CreditApplication,
        on_delete=models.CASCADE,
        related_name='documents',
        verbose_name='Заявка'
    )
    doc_type = models.CharField(
        max_length=20,
        choices=DOC_TYPE_CHOICES,
        verbose_name='Тип документа'
    )
    file = models.FileField(
        upload_to='documents/',
        verbose_name='Файл'
    )
    uploaded_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Дата загрузки'
    )
    
    class Meta:
        verbose_name = 'Документ'
        verbose_name_plural = 'Документы'

    def __str__(self):
        return f"{self.get_doc_type_display()} для заявки №{self.application.id}"

class CreditHistory(models.Model):
    client = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='credit_history',
        verbose_name='Клиент'
    )
    application = models.OneToOneField(
        CreditApplication,
        on_delete=models.CASCADE,
        verbose_name='Заявка'
    )
    approved_amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        verbose_name='Одобренная сумма'
    )
    monthly_payment = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        verbose_name='Ежемесячный платеж'
    )
    start_date = models.DateField(verbose_name='Дата начала')
    end_date = models.DateField(verbose_name='Дата окончания')
    
    class Meta:
        verbose_name = 'Кредитная история'
        verbose_name_plural = 'Кредитная история'

    def __str__(self):
        return f"Кредит клиента {self.client.username} от {self.start_date}"

class Notification(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='notifications',
        verbose_name='Пользователь'
    )
    title = models.CharField(
        max_length=200,
        verbose_name='Заголовок'
    )
    message = models.TextField(verbose_name='Сообщение')
    is_read = models.BooleanField(
        default=False,
        verbose_name='Прочитано'
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Дата создания'
    )
    
    class Meta:
        verbose_name = 'Уведомление'
        verbose_name_plural = 'Уведомления'
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.title} для {self.user.username}"

class Report(models.Model):
    referrer = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='reports',
        verbose_name='Референт'
    )
    title = models.CharField(
        max_length=200,
        verbose_name='Заголовок'
    )
    content = models.TextField(verbose_name='Содержание')
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Дата создания'
    )
    
    class Meta:
        verbose_name = 'Отчет'
        verbose_name_plural = 'Отчеты'
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.title} от {self.referrer.username}"