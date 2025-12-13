from abc import ABC, abstractmethod


class TicketState(ABC):
    def __init__(self, ticket): self.ticket = ticket

    @abstractmethod
    def book(self): pass

    @abstractmethod
    def cancel(self): pass


class FreeState(TicketState):
    def book(self):
        self.ticket.status = 'BOOKED'
        self.ticket.save()

    def cancel(self): raise Exception("Cannot cancel free ticket")


class BookedState(TicketState):
    def book(self): raise Exception("Already booked")

    def cancel(self):
        self.ticket.status = 'FREE'
        self.ticket.booking = None
        self.ticket.save()


class SoldState(TicketState):
    def book(self): raise Exception("Already sold")

    def cancel(self):
        self.ticket.status = 'FREE'
        self.ticket.booking = None
        self.ticket.save()
