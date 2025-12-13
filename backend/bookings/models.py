from django.db import models
from django.conf import settings
from cinema.models import Session
from halls.models import Seat


class Booking(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='bookings')
    created_at = models.DateTimeField(auto_now_add=True)
    total_price = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    discount_applied = models.CharField(max_length=50, default="NoDiscount")


class Ticket(models.Model):
    STATUS_CHOICES = [('FREE', 'Free'), ('BOOKED', 'Booked'), ('SOLD', 'Sold')]
    session = models.ForeignKey(Session, on_delete=models.CASCADE, related_name='tickets')
    seat = models.ForeignKey(Seat, on_delete=models.CASCADE)
    booking = models.ForeignKey(Booking, on_delete=models.SET_NULL, null=True, blank=True, related_name='tickets')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='FREE')
    price = models.DecimalField(max_digits=8, decimal_places=2)

    class Meta: unique_together = ('session', 'seat')
