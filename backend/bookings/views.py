from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from decimal import Decimal
from .models import Booking, Ticket
from cinema.models import Session
from halls.models import Seat
from .serializers import BookingSerializer, TicketSerializer
from .factories import OnlineBookingCreator


class BookingViewSet(viewsets.ModelViewSet):
    queryset = Booking.objects.all()
    serializer_class = BookingSerializer

    @action(detail=False, methods=['post'])
    def create_online(self, request):
        """
        Створює бронювання. Якщо квитків на ці місця ще немає в базі - створює їх автоматично.
        """
        user_id = request.data.get('user_id')
        session_id = request.data.get('session_id')  # <-- Отримуємо ID сеансу
        seat_ids = request.data.get('seat_ids', [])  # <-- Отримуємо ID місць

        from django.contrib.auth import get_user_model
        User = get_user_model()

        try:
            user = User.objects.get(id=user_id)
            session = Session.objects.get(id=session_id)

            # === МАГІЯ: Знаходимо або створюємо квитки на льоту ===
            tickets = []
            for seat_id in seat_ids:
                seat = Seat.objects.get(id=seat_id)

                # get_or_create: якщо квитка немає, він створиться
                ticket, created = Ticket.objects.get_or_create(
                    session=session,
                    seat=seat,
                    defaults={
                        # Розрахунок ціни: Базова ціна сеансу * Модифікатор місця (VIP)
                        'price': session.price_base * Decimal(seat.get_price_modifier()),
                        'status': 'FREE'
                    }
                )
                tickets.append(ticket)

        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

        # Передаємо знайдені квитки у Фабрику
        try:
            creator = OnlineBookingCreator()
            booking = creator.create_booking(user, tickets)
            return Response(BookingSerializer(booking).data, status=status.HTTP_201_CREATED)
        except Exception as e:
            return Response({"error": f"Booking failed: {str(e)}"}, status=status.HTTP_400_BAD_REQUEST)


class TicketViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Ticket.objects.all()
    serializer_class = TicketSerializer
