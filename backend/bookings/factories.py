from abc import ABC, abstractmethod
from .models import Booking, Ticket
from finance.strategies import NoDiscountStrategy, StudentDiscountStrategy


class BookingCreator(ABC):
    """
    Factory Method (Creator).
    Абстрактний клас, який оголошує фабричний метод.
    """

    @abstractmethod
    def create_booking(self, user, tickets_list):
        pass


class OnlineBookingCreator(BookingCreator):
    def create_booking(self, user, tickets_list):
        # Онлайн бронювання може мати свою специфіку (наприклад, таймер оплати)
        booking = Booking.objects.create(user=user, discount_applied="NoDiscount")

        total = 0
        strategy = NoDiscountStrategy()  # За замовчуванням без знижки

        for ticket in tickets_list:
            # Використовуємо State pattern для зміни статусу
            from .states import FreeState
            state = FreeState(ticket)
            state.book()  # Змінюємо статус на BOOKED

            ticket.booking = booking
            ticket.save()
            total += strategy.calculate(ticket.price)

        booking.total_price = total
        booking.save()
        return booking


class BoxOfficeBookingCreator(BookingCreator):
    """Бронювання через касу (наприклад, для студентів)"""

    def create_booking(self, user, tickets_list):
        booking = Booking.objects.create(user=user, discount_applied="StudentDiscount")

        total = 0
        strategy = StudentDiscountStrategy()  # Застосовуємо студентську знижку

        for ticket in tickets_list:
            # Одразу продаємо
            from .states import FreeState
            state = FreeState(ticket)
            state.sell()  # Змінюємо статус на SOLD

            ticket.booking = booking
            ticket.save()
            total += strategy.calculate(ticket.price)

        booking.total_price = total
        booking.save()
        return booking
