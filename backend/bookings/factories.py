from abc import ABC, abstractmethod
from .models import Booking
from finance.strategies import NoDiscountStrategy
from .states import FreeState


class BookingCreator(ABC):
    @abstractmethod
    def create_booking(self, user, tickets_list): pass


class OnlineBookingCreator(BookingCreator):
    def create_booking(self, user, tickets_list):
        booking = Booking.objects.create(user=user, discount_applied="NoDiscount")
        total = 0
        strategy = NoDiscountStrategy()

        for ticket in tickets_list:
            state = FreeState(ticket)
            state.book()  # Зміна статусу через State
            ticket.booking = booking
            ticket.save()
            total += strategy.calculate(ticket.price)

        booking.total_price = total
        booking.save()
        return booking
