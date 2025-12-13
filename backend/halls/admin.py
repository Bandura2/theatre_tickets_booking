from django.contrib import admin
from .models import Hall, SeatGroup, Seat


class SeatInline(admin.TabularInline):
    model = Seat
    fk_name = 'parent'
    extra = 0
    fields = ('number', 'seat_type')
    can_delete = True


@admin.register(Hall)
class HallAdmin(admin.ModelAdmin):
    list_display = ('name', 'description')


@admin.register(SeatGroup)
class SeatGroupAdmin(admin.ModelAdmin):
    list_display = ('name', 'hall', 'parent', 'count_seats')
    list_filter = ('hall',)
    inlines = [SeatInline]
    actions = ['generate_10_standard', 'generate_10_vip', 'generate_10_balcony', 'clear_seats']

    @admin.action(description="⚡ [AUTO] Додати 10 звичайних місць")
    def generate_10_standard(self, request, queryset):
        # Передаємо request далі
        self._generate_seats(request, queryset, 'STD', "Standard")

    @admin.action(description="⚡ [AUTO] Додати 10 VIP місць")
    def generate_10_vip(self, request, queryset):
        self._generate_seats(request, queryset, 'VIP', "VIP")

    @admin.action(description="⚡ [AUTO] Додати 10 місць (Балкон -10%%)")
    def generate_10_balcony(self, request, queryset):
        self._generate_seats(request, queryset, 'BLC', "Balcony")

    def _generate_seats(self, request, queryset, type_code, type_name):
        count = 0
        for group in queryset:
            last_seat = Seat.objects.filter(parent=group).order_by('-number').first()
            start_num = last_seat.number + 1 if last_seat else 1

            for i in range(10):
                Seat.objects.create(
                    hall=group.hall,
                    parent=group,
                    name=f"{type_name} {start_num + i}",
                    number=start_num + i,
                    seat_type=type_code
                )
                count += 1

        self.message_user(request, f"Успішно створено {count} місць типу {type_name}.")

    @admin.action(description="❌ Видалити всі місця в обраних рядах")
    def clear_seats(self, request, queryset):
        deleted = 0
        for group in queryset:
            deleted += Seat.objects.filter(parent=group).delete()[0]
        self.message_user(request, f"Видалено {deleted} місць.")

    def count_seats(self, obj):
        return Seat.objects.filter(parent=obj).count()


@admin.register(Seat)
class SeatAdmin(admin.ModelAdmin):
    list_display = ('number', 'parent', 'seat_type', 'hall')
    list_filter = ('seat_type', 'hall')
