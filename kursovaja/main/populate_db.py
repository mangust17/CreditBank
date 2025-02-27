import os
import sys
import django
from datetime import datetime, timedelta
from decimal import Decimal
import random

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'kursovaja.settings')
django.setup()

from django.utils import timezone
from main.models import User, CreditApplication, Notification, CreditHistory, Report

def create_users():
    clients = []
    for i in range(1, 11):
        client = User.objects.create_user(
            username=f'client{i}',
            email=f'client{i}@example.com',
            password='test123',
            role='client',
            phone=f'+7900{i:07}'
        )
        clients.append(client)
    
    referrers = []
    for i in range(1, 6):
        referrer = User.objects.create_user(
            username=f'referrer{i}',
            email=f'referrer{i}@example.com',
            password='test123',
            role='referrer',
            phone=f'+7911{i:07}'
        )
        referrers.append(referrer)
    
    for i in range(1, 3):
        User.objects.create_user(
            username=f'admin{i}',
            email=f'admin{i}@example.com',
            password='test123',
            role='admin',
            phone=f'+7922{i:07}'
        )
    
    return clients, referrers

def create_credit_applications(clients):
    status_choices = ['pending', 'documents_required', 'under_review', 'approved', 'rejected']
    applications = []
    
    for client in clients:
        for _ in range(random.randint(2, 3)):
            application = CreditApplication.objects.create(
                client=client,
                amount=Decimal(random.randint(50000, 1000000)),
                term_months=random.randint(6, 60),
                status=random.choice(status_choices),
                purpose=random.choice([
                    'Ремонт квартиры',
                    'Покупка автомобиля',
                    'Образование',
                    'Путешествие',
                    'Бытовая техника'
                ]),
                created_at=timezone.now() - timedelta(days=random.randint(1, 90))
            )
            applications.append(application)
    return applications

def create_notifications(users):
    messages = [
        "Ваша заявка одобрена",
        "Требуются дополнительные документы",
        "Заявка находится на рассмотрении",
        "Изменение статуса заявки",
        "Напоминание о платеже",
        "Специальное предложение по кредиту",
        "Важное уведомление о вашем счете",
        "Новый функционал в личном кабинете",
        "Изменение условий обслуживания",
        "Подтверждение операции"
    ]
    
    for user in users:
        for _ in range(3):  
            Notification.objects.create(
                user=user,
                title=random.choice(messages),
                message=f"Подробная информация о {random.choice(messages).lower()}",
                created_at=timezone.now() - timedelta(days=random.randint(1, 30))
            )

def create_credit_history(applications):
    for application in applications:
        if application.status == 'approved':
            start_date = application.created_at.date()
            CreditHistory.objects.create(
                client=application.client,
                application=application,
                approved_amount=application.amount,
                monthly_payment=application.amount / application.term_months,
                start_date=start_date,
                end_date=start_date + timedelta(days=30 * application.term_months)
            )

def create_reports(referrers):
    report_titles = [
        "Ежемесячный отчет по кредитам",
        "Анализ одобренных заявок",
        "Отчет по отклоненным заявкам",
        "Статистика по клиентам",
        "Анализ рисков",
        "Эффективность обработки заявок",
        "Качество кредитного портфеля",
        "Мониторинг просрочек",
        "Анализ целевого использования",
        "Сводный отчет по документации"
    ]
    
    report_contents = [
        "Проведен анализ кредитоспособности клиентов",
        "Выполнена проверка документации заемщиков",
        "Составлен отчет о кредитных рисках",
        "Проведена оценка качества кредитного портфеля",
        "Выполнен анализ эффективности работы отдела",
        "Подготовлено заключение по проблемным кредитам",
        "Проведен мониторинг текущих заявок",
        "Выполнен анализ целевого использования средств",
        "Составлен отчет по работе с клиентами",
        "Подготовлен анализ кредитной документации"
    ]
    
    for referrer in referrers:
        for _ in range(3):  
            Report.objects.create(
                referrer=referrer,
                title=random.choice(report_titles),
                content=random.choice(report_contents),
                created_at=timezone.now() - timedelta(days=random.randint(1, 30))
            )

def populate_database():
    try:
        print("Создание пользователей...")
        clients, referrers = create_users()
        
        print("Создание заявок на кредит...")
        applications = create_credit_applications(clients)
        
        print("Создание уведомлений...")
        create_notifications(clients + referrers)
        
        print("Создание кредитной истории...")
        create_credit_history(applications)
        
        print("Создание отчетов референтов...")
        create_reports(referrers)
        
        print("База данных успешно заполнена!")
        
    except Exception as e:
        print(f"Ошибка при заполнении базы данных: {e}")

if __name__ == "__main__":
    populate_database()