# backend/finance/strategies.py
from abc import ABC, abstractmethod
from decimal import Decimal


class DiscountStrategy(ABC):
    @abstractmethod
    def calculate(self, base_price: Decimal, context: dict = None) -> Decimal:
        pass


class NoDiscountStrategy(DiscountStrategy):
    def calculate(self, base_price: Decimal, context: dict = None) -> Decimal:
        return base_price


class StudentDiscountStrategy(DiscountStrategy):
    def calculate(self, base_price: Decimal, context: dict = None) -> Decimal:
        # Перевірка наявності студентського
        student_id = context.get('student_id')
        if not student_id:
            raise ValueError("Для студентської знижки потрібно ввести номер студентського квитка!")

        # (Тут могла б бути перевірка в базі студентів, але для курсової перевіряємо просто наявність)
        return base_price * Decimal('0.8')


class PromoDiscountStrategy(DiscountStrategy):
    def calculate(self, base_price: Decimal, context: dict = None) -> Decimal:
        # Перевірка промокоду
        code = context.get('promo_code', '').upper()

        # Хардкод промокод для тесту
        if code != "BANDURA2":
            raise ValueError("Невірний промокод! Спробуйте: CINEMA2025")

        return base_price * Decimal('0.9')
