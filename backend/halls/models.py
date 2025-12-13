from django.db import models


class Hall(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)

    def __str__(self): return self.name


class HallComponent(models.Model):
    hall = models.ForeignKey(Hall, on_delete=models.CASCADE, related_name='all_components')
    parent = models.ForeignKey('self', null=True, blank=True, on_delete=models.CASCADE, related_name='children')
    name = models.CharField(max_length=100, blank=True)

    def get_details(self): return f"Component: {self.name}"

    def get_price_modifier(self): return 1.0

    def __str__(self): return f"{self.name} ({self.hall.name})"


class SeatGroup(HallComponent):
    description = models.CharField(max_length=255, blank=True)

    class Meta: verbose_name = "Seat Group"


class Seat(HallComponent):
    SEAT_TYPES = [
        ('STD', 'Standard'),
        ('VIP', 'VIP'),
        ('BLC', 'Balcony'),
    ]

    number = models.IntegerField()
    seat_type = models.CharField(max_length=3, choices=SEAT_TYPES, default='STD')

    def get_price_modifier(self):
        if self.seat_type == 'VIP':
            return 1.5
        elif self.seat_type == 'BLC':
            return 0.9
        return 1.0

    class Meta:
        verbose_name = "Seat"
