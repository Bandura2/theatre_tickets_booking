from abc import ABC, abstractmethod


class TicketState(ABC):
    """Абстрактний стан квитка"""

    def __init__(self, ticket):
        self.ticket = ticket

    @abstractmethod
    def book(self):
        pass

    @abstractmethod
    def sell(self):
        pass

    @abstractmethod
    def cancel(self):
        pass


class FreeState(TicketState):
    def book(self):
        print("Booking ticket...")
        self.ticket.status = 'BOOKED'
        self.ticket.save()

    def sell(self):
        print("Direct selling ticket...")
        self.ticket.status = 'SOLD'
        self.ticket.save()

    def cancel(self):
        raise Exception("Cannot cancel a free ticket.")


class BookedState(TicketState):
    def book(self):
        raise Exception("Ticket is already booked.")

    def sell(self):
        print("Confirming sale...")
        self.ticket.status = 'SOLD'
        self.ticket.save()

    def cancel(self):
        print("Cancelling booking...")
        self.ticket.status = 'FREE'
        self.ticket.booking = None
        self.ticket.save()


class SoldState(TicketState):
    def book(self):
        raise Exception("Ticket is already sold.")

    def sell(self):
        raise Exception("Ticket is already sold.")

    def cancel(self):
        # Логіка повернення коштів може бути тут
        print("Refunding ticket...")
        self.ticket.status = 'FREE'
        self.ticket.booking = None
        self.ticket.save()
