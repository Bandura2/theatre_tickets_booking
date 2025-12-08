from django.db import models


class Movie(models.Model):
    title = models.CharField(max_length=255)
    description = models.TextField()
    duration_minutes = models.PositiveIntegerField()
    genre = models.CharField(max_length=100)
    poster = models.ImageField(upload_to='posters/', blank=True, null=True)

    def __str__(self):
        return self.title


class Session(models.Model):
    movie = models.ForeignKey(Movie, on_delete=models.CASCADE, related_name='sessions')
    # hall ми підключимо як String, щоб уникнути циклічного імпорту, або імпортуємо пізніше
    hall = models.ForeignKey('halls.Hall', on_delete=models.CASCADE, related_name='sessions')
    start_time = models.DateTimeField()
    price_base = models.DecimalField(max_digits=8, decimal_places=2)  # Базова ціна квитка

    def __str__(self):
        return f"{self.movie.title} at {self.start_time}"
