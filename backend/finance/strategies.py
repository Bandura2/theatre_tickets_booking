from abc import ABC, abstractmethod
from decimal import Decimal


class DiscountStrategy(ABC):
    """
    Патерн Strategy (Стратегія).
    Визначає алгоритм розрахунку ціни.
    """

    @abstractmethod
    def calculate(self, base_price: Decimal) -> Decimal:
        pass


class NoDiscountStrategy(DiscountStrategy):
    def calculate(self, base_price: Decimal) -> Decimal:
        return base_price


class StudentDiscountStrategy(DiscountStrategy):
    def calculate(self, base_price: Decimal) -> Decimal:
        # Знижка 20%
        return base_price * Decimal('0.8')


class PromoDiscountStrategy(DiscountStrategy):
    def calculate(self, base_price: Decimal) -> Decimal:
        # Знижка 10%
        return base_price * Decimal('0.9')
