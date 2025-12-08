from django.contrib import admin
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from drf_yasg.views import get_schema_view
from drf_yasg import openapi
from rest_framework import permissions

# Імпорти наших Views
from users.views import UserViewSet
from cinema.views import MovieViewSet, SessionViewSet
from halls.views import HallViewSet
from bookings.views import BookingViewSet, TicketViewSet

# Налаштування роутера (автоматично створює посилання /api/movies/, /api/users/ тощо)
router = DefaultRouter()
router.register(r'users', UserViewSet)
router.register(r'movies', MovieViewSet)
router.register(r'sessions', SessionViewSet)
router.register(r'halls', HallViewSet)
router.register(r'bookings', BookingViewSet)
router.register(r'tickets', TicketViewSet)

# Налаштування Swagger (документація)
schema_view = get_schema_view(
    openapi.Info(
        title="Cinema Booking API",
        default_version='v1',
        description="API for Coursework Project 11",
    ),
    public=True,
    permission_classes=(permissions.AllowAny,),
)

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include(router.urls)),

    # Swagger Documentation URLs
    path('swagger/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
]
