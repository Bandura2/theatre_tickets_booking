import csv
from django.http import HttpResponse
from rest_framework import viewsets
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAdminUser
from django.db.models import Sum
from django.utils.dateparse import parse_date
from .models import Movie, Session
from .serializers import MovieSerializer, SessionSerializer
from bookings.models import Ticket


class MovieViewSet(viewsets.ModelViewSet):
    queryset = Movie.objects.all()
    serializer_class = MovieSerializer


class SessionViewSet(viewsets.ModelViewSet):
    queryset = Session.objects.all()
    serializer_class = SessionSerializer


@api_view(['GET'])
@permission_classes([IsAdminUser])
def download_sales_report(request):
    response = HttpResponse(content_type='text/csv; charset=utf-8-sig')
    response['Content-Disposition'] = 'attachment; filename="cinema_report.csv"'
    writer = csv.writer(response)
    writer.writerow(['Фільм', 'Зал', 'Час', 'Квитки', 'Виручка', 'Зайнятість'])

    start_str = request.GET.get('start_date')
    end_str = request.GET.get('end_date')
    sessions = Session.objects.all().order_by('-start_time')

    if start_str and end_str:
        s_date = parse_date(start_str)
        e_date = parse_date(end_str)
        if s_date and e_date:
            sessions = sessions.filter(start_time__date__range=[s_date, e_date])

    for s in sessions:
        sold = Ticket.objects.filter(session=s, status__in=['SOLD', 'BOOKED']).count()
        rev = Ticket.objects.filter(session=s, status__in=['SOLD', 'BOOKED']).aggregate(Sum('price'))['price__sum'] or 0
        total = s.hall.all_components.filter(seat__isnull=False).count()
        occ = int((sold / total) * 100) if total > 0 else 0
        writer.writerow([s.movie.title, s.hall.name, s.start_time, sold, rev, f"{occ}%"])

    return response
