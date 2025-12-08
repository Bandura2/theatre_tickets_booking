from django.db import models
from django.conf import settings
from cinema.models import Session
from halls.models import Seat


class Booking(models.Model):
    """
    Замовлення. Створюється через Factory Method.
    """
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='bookings')
    created_at = models.DateTimeField(auto_now_add=True)
    total_price = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)

    # Зберігаємо назву застосованої стратегії знижки для історії
    discount_applied = models.CharField(max_length=50, default="NoDiscount")

    def __str__(self):
        return f"Booking #{self.id} by {self.user}"


class Ticket(models.Model):
    """
    Квиток. Працює за патерном State.
    """
    STATUS_CHOICES = [
        ('FREE', 'Free'),
        ('BOOKED', 'Booked'),
        ('SOLD', 'Sold'),
    ]

    session = models.ForeignKey(Session, on_delete=models.CASCADE, related_name='tickets')
    seat = models.ForeignKey(Seat, on_delete=models.CASCADE)
    booking = models.ForeignKey(Booking, on_delete=models.SET_NULL, null=True, blank=True, related_name='tickets')

    # Поле стану в БД
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='FREE')
    price = models.DecimalField(max_digits=8, decimal_places=2)

    class Meta:
        unique_together = ('session', 'seat')  # Не можна продати одне місце двічі на той самий сеанс

    def __str__(self):
        return f"Ticket {self.id} ({self.status})"
