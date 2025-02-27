from django.test import TestCase
from unittest.mock import Mock, patch
from decimal import Decimal
from datetime import datetime
from .models import User, CreditApplication
from .services import CreditService

class CreditServiceMockTest(TestCase):
    """Тест с использованием мок-объекта"""
    
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        print('\n' + '='*70)
        print('Запуск теста с мок-объектом')
        print('='*70)
        cls.start_time = datetime.now()

    def test_credit_scoring_with_mock(self):
        """Тест скоринга заявки с использованием мока"""
        print('\nТестирование скоринга с мок-объектом...')

        mock_scoring = Mock()
        mock_scoring.calculate_score.return_value = 85

        test_data = {
            'income': Decimal('60000.00'),
            'employment_years': 3,
            'credit_history': 'good'
        }

        with patch('main.services.ScoringSystem', return_value=mock_scoring):
            credit_service = CreditService()
            score = credit_service.evaluate_application(test_data)
            
            mock_scoring.calculate_score.assert_called_once_with(test_data)
            
            self.assertEqual(score, 85)
            print('Мок-объект успешно использован')
            print('Скоринг корректно рассчитан')
        
        print('Тест с мок-объектом успешно завершен')


class CreditApplicationDatabaseTest(TestCase):
    """Тест с использованием базы данных"""
    
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        print('\n' + '='*70)
        print('Запуск теста с базой данных')
        print('='*70)
        cls.start_time = datetime.now()

    def setUp(self):
        print('\nПодготовка тестовой базы данных...')
        self.user = User.objects.create(
            username='testuser',
            email='test@test.com',
            role='client'
        )
        print('Тестовый пользователь создан')

    def test_credit_application_workflow(self):
        """Тест процесса обработки заявки с использованием БД"""
        print('\nТестирование процесса обработки заявки...')
        
        application = CreditApplication.objects.create(
            client=self.user,
            amount=Decimal('100000.00'),
            term_months=12,
            purpose='Test purpose'
        )
        print('Заявка создана')

        self.assertEqual(application.status, 'pending')
        print('Начальный статус корректен')

        application.status = 'approved'
        application.save()
        print('Статус заявки обновлен')

        updated_application = CreditApplication.objects.get(id=application.id)
        self.assertEqual(updated_application.status, 'approved')
        print('Обновление в базе данных подтверждено')
        
        self.assertEqual(updated_application.client, self.user)
        print('Связь с пользователем корректна')
        
        print('Тест с базой данных успешно завершен')

    def tearDown(self):
        User.objects.all().delete()
        CreditApplication.objects.all().delete()
        print('Тестовая база данных очищена')

if __name__ == '__main__':
    import unittest
    unittest.main(verbosity=2)