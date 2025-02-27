from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from django.contrib.staticfiles.testing import StaticLiveServerTestCase
from datetime import datetime
import time

class CreditCalculatorTest(StaticLiveServerTestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.start_time = datetime.now()
        cls.selenium = webdriver.Chrome()
        cls.selenium.implicitly_wait(10)

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()

    def test_credit_calculator(self):
        """Тест кредитного калькулятора"""
        self.selenium.get(self.live_server_url)
        print('Главная страница открыта')
        try:
            amount_input = self.selenium.find_element(By.ID, 'amount')
            term_input = self.selenium.find_element(By.ID, 'term')
            calculate_button = self.selenium.find_element(By.CSS_SELECTOR, '#creditCalculator button[type="submit"]')
            amount_input.clear()
            amount_input.send_keys('100000')
            print('Сумма кредита введена: 100000')
            
            term_input.clear()
            term_input.send_keys('12')
            print('Срок кредита введен: 12 месяцев')

            calculate_button.click()
            print('Кнопка расчета нажата')

            time.sleep(2)
            

            result_div = self.selenium.find_element(By.ID, 'result')
            self.assertTrue(result_div.is_displayed())
            self.assertTrue('Ежемесячный платеж' in result_div.text)
            print('Результаты расчета отображены')
            

            print('\nТест успешно завершен!')
            time.sleep(3600)  
    
        except Exception as e:
            print(f'\nОшибка при тестировании: {str(e)}')
            raise

if __name__ == '__main__':
    import unittest
    unittest.main(verbosity=2) 