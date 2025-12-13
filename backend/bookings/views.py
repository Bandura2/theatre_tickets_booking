from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from decimal import Decimal
from django.contrib.auth import get_user_model
from .models import Booking, Ticket
from cinema.models import Session
from halls.models import Seat
from .serializers import BookingSerializer, TicketSerializer
from .factories import OnlineBookingCreator
from .states import BookedState, SoldState


class BookingViewSet(viewsets.ModelViewSet):
    serializer_class = BookingSerializer

    def get_queryset(self):
        if self.action in ['cancel', 'retrieve', 'destroy']:
            return Booking.objects.all()

        user_id = self.request.query_params.get('user_id')
        queryset = Booking.objects.all().order_by('-created_at')

        if user_id:
            return queryset.filter(user_id=user_id)

        user = self.request.user
        if user.is_staff or user.is_superuser:
            return queryset

        return Booking.objects.none()

    @action(detail=False, methods=['post'])
    def create_online(self, request):
        user_id = request.data.get('user_id')
        session_id = request.data.get('session_id')
        seat_ids = request.data.get('seat_ids', [])
        discount_code = request.data.get('discount_type', 'NO')

        # === НОВЕ: Отримуємо додаткові дані ===
        extra_data = {
            'student_id': request.data.get('student_id'),
            'promo_code': request.data.get('promo_code')
        }

        User = get_user_model()
        try:
            user = User.objects.get(id=user_id)
            session = Session.objects.get(id=session_id)

            from finance.strategies import NoDiscountStrategy, StudentDiscountStrategy, PromoDiscountStrategy

            strategies = {
                'NO': NoDiscountStrategy(),
                'STUDENT': StudentDiscountStrategy(),
                'PROMO': PromoDiscountStrategy()
            }
            strategy = strategies.get(discount_code, NoDiscountStrategy())

            tickets = []

            for seat_id in seat_ids:
                seat = Seat.objects.get(id=seat_id)
                base_price = session.price_base * Decimal(seat.get_price_modifier())

                # === ВАЖЛИВО: Передаємо extra_data у calculate ===
                # Якщо код невірний, тут вилетить помилка ValueError
                final_price = strategy.calculate(base_price, extra_data)

                ticket, _ = Ticket.objects.get_or_create(
                    session=session, seat=seat,
                    defaults={'price': final_price, 'status': 'FREE'}
                )

                if ticket.status != 'FREE':
                    return Response({"error": f"Місце {seat.number} вже зайняте!"}, status=400)

                if ticket.price != final_price:
                    ticket.price = final_price
                    ticket.save()

                tickets.append(ticket)

            if not tickets: return Response({"error": "Місця не обрано"}, status=400)

            creator = OnlineBookingCreator()
            booking = creator.create_booking(user, tickets)
            booking.discount_applied = discount_code
            booking.save()

            return Response(BookingSerializer(booking).data, status=status.HTTP_201_CREATED)

        except ValueError as ve:
            # Обробка помилок валідації стратегії (невірний код/квиток)
            return Response({"error": str(ve)}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['post'])
    def cancel(self, request, pk=None):
        booking = self.get_object()

        user_id = request.data.get('user_id')
        is_owner = str(booking.user.id) == str(user_id)
        is_admin = request.user.is_staff or request.user.is_superuser

        if not is_owner and not is_admin:
            return Response({"error": "Заборонено"}, status=403)

        for ticket in booking.tickets.all():
            if ticket.status == 'BOOKED':
                BookedState(ticket).cancel()
            elif ticket.status == 'SOLD':
                SoldState(ticket).cancel()

        booking.delete()
        return Response({"status": "cancelled"}, status=200)


class TicketViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = TicketSerializer

    def get_queryset(self):
        sid = self.request.query_params.get('session_id')
        if sid: return Ticket.objects.filter(session_id=sid)
        return Ticket.objects.all()
