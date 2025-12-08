from django.contrib import admin
from django.db.models import Sum, Count
from .models import Movie, Session
from bookings.models import Ticket


@admin.register(Movie)
class MovieAdmin(admin.ModelAdmin):
    list_display = ('title', 'genre', 'duration_minutes')


@admin.register(Session)
class SessionAdmin(admin.ModelAdmin):
    list_display = ('movie', 'hall', 'start_time', 'get_sold_tickets', 'get_revenue', 'get_occupancy')
    list_filter = ('start_time', 'hall')

    def get_sold_tickets(self, obj):
        # Рахуємо квитки зі статусом SOLD або BOOKED (залежно від логіки, зазвичай рахують продані)
        return Ticket.objects.filter(session=obj, status__in=['SOLD', 'BOOKED']).count()

    get_sold_tickets.short_description = "Продано квитків"

    def get_revenue(self, obj):
        # Сума цін проданих квитків
        revenue = Ticket.objects.filter(session=obj, status='SOLD').aggregate(Sum('price'))['price__sum']
        return f"{revenue or 0} грн"

    get_revenue.short_description = "Виручка"

    def get_occupancy(self, obj):
        # Відсоток завантаженості
        total_seats = obj.hall.all_components.filter(seat__isnull=False).count()
        if total_seats == 0: return "0%"
        sold = Ticket.objects.filter(session=obj, status__in=['SOLD', 'BOOKED']).count()
        percent = (sold / total_seats) * 100
        return f"{int(percent)}%"

    get_occupancy.short_description = "Завантаженість"
