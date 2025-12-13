from django.contrib import admin
from django.db.models import Sum
from django.http import HttpResponse
from .models import Movie, Session
from bookings.models import Ticket

# Імпортуємо наш новий файл зі звітами
from .reports import (
    generate_sold_tickets_report,
    generate_revenue_report,
    generate_occupancy_report
)


@admin.register(Movie)
class MovieAdmin(admin.ModelAdmin):
    list_display = ('title', 'genre', 'duration_minutes')


@admin.register(Session)
class SessionAdmin(admin.ModelAdmin):
    list_display = ('movie', 'hall', 'start_time', 'get_sold_tickets', 'get_revenue', 'get_occupancy')
    # Додаємо фільтри, щоб адмін міг обрати "певний період" перед генерацією звіту
    list_filter = ('start_time', 'hall', 'movie')

    # Реєструємо 3 дії
    actions = ['action_report_tickets', 'action_report_revenue', 'action_report_occupancy']

    # --- ДІЯ 1 ---
    @admin.action(description="📄 Звіт: Продані квитки (Детально)")
    def action_report_tickets(self, request, queryset):
        html_content = generate_sold_tickets_report(queryset)
        return HttpResponse(html_content)

    # --- ДІЯ 2 ---
    @admin.action(description="💰 Звіт: Виручка (По сеансах)")
    def action_report_revenue(self, request, queryset):
        html_content = generate_revenue_report(queryset)
        return HttpResponse(html_content)

    # --- ДІЯ 3 ---
    @admin.action(description="📊 Звіт: Завантаженість залів")
    def action_report_occupancy(self, request, queryset):
        html_content = generate_occupancy_report(queryset)
        return HttpResponse(html_content)

    # --- Допоміжні методи для списку ---
    def get_sold_tickets(self, obj):
        return Ticket.objects.filter(session=obj, status__in=['SOLD', 'BOOKED']).count()

    get_sold_tickets.short_description = "Продано"

    def get_revenue(self, obj):
        rev = Ticket.objects.filter(session=obj, status__in=['SOLD', 'BOOKED']).aggregate(Sum('price'))['price__sum']
        return f"{rev or 0} грн"

    get_revenue.short_description = "Виручка"

    def get_occupancy(self, obj):
        total = obj.hall.all_components.filter(seat__isnull=False).count()
        if total == 0: return "0%"
        sold = Ticket.objects.filter(session=obj, status__in=['SOLD', 'BOOKED']).count()
        return f"{int((sold / total) * 100)}%"

    get_occupancy.short_description = "%"
