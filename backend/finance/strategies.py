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
        student_id = context.get('student_id')
        if not student_id:
            raise ValueError("Для студентської знижки потрібно ввести номер студентського квитка!")

        return base_price * Decimal('0.8')


class PromoDiscountStrategy(DiscountStrategy):
    def calculate(self, base_price: Decimal, context: dict = None) -> Decimal:
        code = context.get('promo_code', '').upper()

        if code != "BANDURA2":
            raise ValueError("Невірний промокод! Спробуйте: CINEMA2025")

        return base_price * Decimal('0.9')
