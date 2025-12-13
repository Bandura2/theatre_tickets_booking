# backend/cinema/reports.py

from django.db.models import Sum
from bookings.models import Ticket
from halls.models import Seat

# === 1. ШАБЛОНИ (HTML/CSS/JS) ===

# Початок файлу (Стилі + Скрипт PDF)
HTML_HEAD = """
<!DOCTYPE html>
<html lang="uk">
<head>
    <meta charset="UTF-8">
    <title>Звіт Grand Cinema</title>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/html2pdf.js/0.10.1/html2pdf.bundle.min.js"></script>
    <style>
        body { font-family: 'Helvetica', 'Arial', sans-serif; padding: 20px; background: #fff; color: #333; }

        .control-bar { 
            background: #343a40; color: white; padding: 15px; text-align: center; 
            position: fixed; top: 0; left: 0; width: 100%; z-index: 999;
            box-shadow: 0 2px 5px rgba(0,0,0,0.3);
        }
        .btn {
            background: #dc3545; color: white; border: none; padding: 10px 20px; 
            font-size: 16px; border-radius: 5px; cursor: pointer; font-weight: bold;
        }
        .btn:hover { background: #c82333; }

        .report-content { margin-top: 80px; padding: 20px; }

        h1 { text-align: center; color: #007bff; margin-bottom: 5px; }
        .subtitle { text-align: center; color: #666; margin-bottom: 30px; font-size: 14px; }

        table { width: 100%; border-collapse: collapse; margin-bottom: 30px; }
        th, td { border: 1px solid #dee2e6; padding: 10px; text-align: center; }
        th { background: #e9ecef; font-weight: bold; }
        td { font-size: 14px; }

        /* Кольори для статистики */
        .text-success { color: #28a745; font-weight: bold; }
        .text-warning { color: #ffc107; font-weight: bold; }
        .text-danger { color: #dc3545; font-weight: bold; }

        .total-row { background: #fff3cd; font-weight: bold; }
    </style>
</head>
<body>
    <div class="control-bar">
        <button class="btn" onclick="savePDF()">📥 Завантажити як PDF</button>
    </div>
    <div id="report-body" class="report-content">
"""

# Кінець файлу (Скрипт збереження)
HTML_FOOTER = """
    </div>
    <script>
        function savePDF() {
            const element = document.getElementById('report-body');
            const opt = {
                margin: 0.5,
                filename: 'Report_GrandCinema.pdf',
                image: { type: 'jpeg', quality: 0.98 },
                html2canvas: { scale: 2 },
                jsPDF: { unit: 'in', format: 'a4', orientation: 'landscape' }
            };
            html2pdf().set(opt).from(element).save();
        }
    </script>
</body>
</html>
"""


# === 2. ЛОГІКА ГЕНЕРАЦІЇ ЗВІТІВ ===

def generate_sold_tickets_report(sessions):
    """
    Звіт 1: Продані квитки за певний період.
    Показує список всіх проданих квитків детально.
    """
    rows = ""
    total_count = 0
    total_sum = 0

    for session in sessions:
        # Шукаємо продані квитки
        tickets = Ticket.objects.filter(session=session, status__in=['SOLD', 'BOOKED'])

        for t in tickets:
            rows += f"""
            <tr>
                <td>{session.start_time.strftime("%d.%m.%Y %H:%M")}</td>
                <td style="text-align:left">{session.movie.title}</td>
                <td>{session.hall.name}</td>
                <td>Місце {t.seat.number} ({t.seat.get_seat_type_display()})</td>
                <td>{t.price} грн</td>
            </tr>
            """
            total_count += 1
            total_sum += t.price

    table = f"""
    <h1>Звіт: Продані квитки</h1>
    <div class="subtitle">Детальний список транзакцій за обраний період</div>
    <table>
        <thead>
            <tr>
                <th>Дата та Час</th>
                <th>Фільм</th>
                <th>Зал</th>
                <th>Місце</th>
                <th>Ціна</th>
            </tr>
        </thead>
        <tbody>
            {rows}
            <tr class="total-row">
                <td colspan="3">ВСЬОГО</td>
                <td>{total_count} шт.</td>
                <td>{total_sum} грн</td>
            </tr>
        </tbody>
    </table>
    """
    return HTML_HEAD + table + HTML_FOOTER


def generate_revenue_report(sessions):
    """
    Звіт 2: Виручка по кожній виставі/сеансу.
    Згрупована таблиця (один рядок = один сеанс).
    """
    rows = ""
    grand_total = 0

    for session in sessions:
        # Агрегуємо суму по сеансу
        data = Ticket.objects.filter(session=session, status__in=['SOLD', 'BOOKED']).aggregate(
            total_money=Sum('price'),
            count=Sum('id')  # Count trick is safer done via .count() separately
        )
        count = Ticket.objects.filter(session=session, status__in=['SOLD', 'BOOKED']).count()
        revenue = data['total_money'] or 0

        grand_total += revenue

        rows += f"""
        <tr>
            <td>{session.id}</td>
            <td style="text-align:left">{session.movie.title}</td>
            <td>{session.hall.name}</td>
            <td>{session.start_time.strftime("%d.%m.%Y %H:%M")}</td>
            <td>{count}</td>
            <td class="text-success">{revenue} грн</td>
        </tr>
        """

    table = f"""
    <h1>Звіт: Фінансова виручка</h1>
    <div class="subtitle">Підсумки по кожному сеансу</div>
    <table>
        <thead>
            <tr>
                <th>ID</th>
                <th>Фільм</th>
                <th>Зал</th>
                <th>Час початку</th>
                <th>Квитків продано</th>
                <th>Виручка</th>
            </tr>
        </thead>
        <tbody>
            {rows}
            <tr class="total-row">
                <td colspan="5" style="text-align:right; padding-right:20px;">ЗАГАЛЬНА СУМА:</td>
                <td>{grand_total} грн</td>
            </tr>
        </tbody>
    </table>
    """
    return HTML_HEAD + table + HTML_FOOTER


def generate_occupancy_report(sessions):
    """
    Звіт 3: Завантаженість залів.
    Показує відсотки та графічну шкалу.
    """
    rows = ""

    for session in sessions:
        # Всього місць у залі (рахуємо всі компоненти типу Seat)
        total_seats = session.hall.all_components.filter(seat__isnull=False).count()
        sold = Ticket.objects.filter(session=session, status__in=['SOLD', 'BOOKED']).count()

        percent = 0
        if total_seats > 0:
            percent = round((sold / total_seats) * 100, 1)

        # Колір статусу
        status_color = "text-danger"  # Мало людей
        if percent > 50: status_color = "text-warning"
        if percent > 80: status_color = "text-success"

        # Прогрес-бар
        bar_html = f"""
        <div style="background:#e9ecef; width:100%; height:20px; border-radius:10px; overflow:hidden;">
            <div style="width:{percent}%; background:{'#28a745' if percent > 50 else '#dc3545'}; height:100%;"></div>
        </div>
        """

        rows += f"""
        <tr>
            <td>{session.start_time.strftime("%d.%m.%Y")}</td>
            <td>{session.start_time.strftime("%H:%M")}</td>
            <td style="text-align:left">{session.movie.title}</td>
            <td>{session.hall.name}</td>
            <td>{sold} / {total_seats}</td>
            <td class="{status_color}">{percent}%</td>
            <td width="150">{bar_html}</td>
        </tr>
        """

    table = f"""
    <h1>Звіт: Завантаженість залів</h1>
    <div class="subtitle">Ефективність роботи кінотеатру</div>
    <table>
        <thead>
            <tr>
                <th>Дата</th>
                <th>Час</th>
                <th>Фільм</th>
                <th>Зал</th>
                <th>Місця (Зайнято/Всього)</th>
                <th>%</th>
                <th>Графік</th>
            </tr>
        </thead>
        <tbody>
            {rows}
        </tbody>
    </table>
    """
    return HTML_HEAD + table + HTML_FOOTER
