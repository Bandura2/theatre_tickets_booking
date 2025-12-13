from django.contrib import admin
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from drf_yasg.views import get_schema_view
from drf_yasg import openapi
from rest_framework import permissions

from django.conf import settings
from django.conf.urls.static import static

from users.views import UserViewSet
from cinema.views import MovieViewSet, SessionViewSet, download_sales_report
from halls.views import HallViewSet
from bookings.views import BookingViewSet, TicketViewSet

router = DefaultRouter()
router.register(r'users', UserViewSet)
router.register(r'movies', MovieViewSet)
router.register(r'sessions', SessionViewSet)
router.register(r'halls', HallViewSet)
router.register(r'bookings', BookingViewSet, basename='bookings')
router.register(r'tickets', TicketViewSet, basename='tickets')

schema_view = get_schema_view(
    openapi.Info(title="Cinema API", default_version='v1'),
    public=True,
    permission_classes=(permissions.AllowAny,),
)

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include(router.urls)),

    path('api/reports/download/', download_sales_report, name='download_report'),

    path('swagger/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
]

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include(router.urls)),
    path('api/reports/download/', download_sales_report, name='download_report'),
    path('swagger/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
