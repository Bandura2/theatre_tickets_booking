from django.db.models import Sum, Count, Q
from bookings.models import Ticket
from halls.models import Seat


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

        table { width: 100%; border-collapse: collapse; margin-bottom: 30px; font-size: 13px; }
        th, td { border: 1px solid #dee2e6; padding: 8px; text-align: center; }
        th { background: #e9ecef; font-weight: bold; }

        /* Статуси */
        .badge { padding: 4px 8px; border-radius: 4px; font-weight: bold; font-size: 11px; }
        .badge-sold { background-color: #d4edda; color: #155724; border: 1px solid #c3e6cb; }
        .badge-booked { background-color: #fff3cd; color: #856404; border: 1px solid #ffeeba; }

        .text-money { font-weight: bold; color: #28a745; }
        .text-pending { font-weight: bold; color: #ffc107; }

        .total-row { background: #f8f9fa; font-weight: bold; border-top: 2px solid #dee2e6; }
    </style>
</head>
<body>
    <div class="control-bar">
        <button class="btn" onclick="savePDF()">📥 Завантажити як PDF</button>
    </div>
    <div id="report-body" class="report-content">
"""

HTML_FOOTER = """
    </div>
    <script>
        function savePDF() {
            const element = document.getElementById('report-body');
            const opt = {
                margin: 0.3,
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
    Звіт 1: Детальний список квитків.
    Розділяє SOLD (Оплачено) та BOOKED (Резерв).
    """
    rows = ""
    count_sold = 0
    sum_sold = 0
    count_booked = 0
    sum_booked = 0

    for session in sessions:
        tickets = Ticket.objects.filter(session=session, status__in=['SOLD', 'BOOKED']).select_related('seat')

        for t in tickets:
            status_badge = ""
            if t.status == 'SOLD':
                status_badge = '<span class="badge badge-sold">ОПЛАЧЕНО</span>'
                count_sold += 1
                sum_sold += t.price
            else:
                status_badge = '<span class="badge badge-booked">РЕЗЕРВ</span>'
                count_booked += 1
                sum_booked += t.price

            rows += f"""
            <tr>
                <td>{session.start_time.strftime("%d.%m.%Y %H:%M")}</td>
                <td style="text-align:left">{session.movie.title}</td>
                <td>{session.hall.name}</td>
                <td>Місце {t.seat.number} ({t.seat.get_seat_type_display()})</td>
                <td>{t.price} грн</td>
                <td>{status_badge}</td>
            </tr>
            """

    table = f"""
    <h1>Звіт: Рух квитків</h1>
    <div class="subtitle">Деталізація за статусами оплати</div>
    <table>
        <thead>
            <tr>
                <th>Дата</th>
                <th>Фільм</th>
                <th>Зал</th>
                <th>Місце</th>
                <th>Ціна</th>
                <th>Статус</th>
            </tr>
        </thead>
        <tbody>
            {rows}
            <tr class="total-row">
                <td colspan="4" style="text-align:right">ПІДСУМОК (ОПЛАЧЕНО):</td>
                <td colspan="2" class="text-money">{count_sold} шт. / {sum_sold} грн</td>
            </tr>
            <tr class="total-row">
                <td colspan="4" style="text-align:right">ПІДСУМОК (РЕЗЕРВ):</td>
                <td colspan="2" class="text-pending">{count_booked} шт. / {sum_booked} грн</td>
            </tr>
        </tbody>
    </table>
    """
    return HTML_HEAD + table + HTML_FOOTER


def generate_revenue_report(sessions):
    """
    Звіт 2: Фінансовий звіт.
    Показує Реальні гроші (SOLD) та Потенційні (BOOKED) окремо.
    """
    rows = ""
    total_real_revenue = 0
    total_potential_revenue = 0

    for session in sessions:
        # Агрегація SOLD
        sold_data = Ticket.objects.filter(session=session, status='SOLD').aggregate(
            qty=Count('id'), total=Sum('price')
        )
        sold_qty = sold_data['qty'] or 0
        sold_sum = sold_data['total'] or 0

        # Агрегація BOOKED
        booked_data = Ticket.objects.filter(session=session, status='BOOKED').aggregate(
            qty=Count('id'), total=Sum('price')
        )
        booked_qty = booked_data['qty'] or 0
        booked_sum = booked_data['total'] or 0

        total_real_revenue += sold_sum
        total_potential_revenue += booked_sum

        if sold_qty == 0 and booked_qty == 0:
            continue  # Пропускаємо пусті сеанси, щоб не забивати звіт

        rows += f"""
        <tr>
            <td style="text-align:left">{session.movie.title}</td>
            <td>{session.hall.name}</td>
            <td>{session.start_time.strftime("%d.%m %H:%M")}</td>

            <td style="background:#f0fff4">{sold_qty}</td>
            <td style="background:#f0fff4" class="text-money">{sold_sum} грн</td>

            <td style="background:#fff9db">{booked_qty}</td>
            <td style="background:#fff9db" class="text-pending">{booked_sum} грн</td>
        </tr>
        """

    table = f"""
    <h1>Звіт: Виручка та Прогнози</h1>
    <div class="subtitle">Розподіл: Фактична оплата vs Бронювання</div>
    <table>
        <thead>
            <tr>
                <th rowspan="2">Фільм</th>
                <th rowspan="2">Зал</th>
                <th rowspan="2">Дата</th>
                <th colspan="2" style="background:#d4edda">✅ Фактично (SOLD)</th>
                <th colspan="2" style="background:#fff3cd">⏳ Очікується (BOOKED)</th>
            </tr>
            <tr>
                <th style="background:#e2e6ea">К-сть</th>
                <th style="background:#e2e6ea">Сума</th>
                <th style="background:#e2e6ea">К-сть</th>
                <th style="background:#e2e6ea">Сума</th>
            </tr>
        </thead>
        <tbody>
            {rows}
            <tr class="total-row">
                <td colspan="3" style="text-align:right">ВСЬОГО:</td>
                <td colspan="2" class="text-money">{total_real_revenue} грн</td>
                <td colspan="2" class="text-pending">{total_potential_revenue} грн</td>
            </tr>
        </tbody>
    </table>
    """
    return HTML_HEAD + table + HTML_FOOTER


def generate_occupancy_report(sessions):
    """
    Звіт 3: Завантаженість.
    Показує сумарну зайнятість (SOLD + BOOKED), бо місце фізично зайняте.
    """
    rows = ""

    for session in sessions:
        total_seats = session.hall.all_components.filter(seat__isnull=False).count()

        # Рахуємо окремо для деталізації
        sold = Ticket.objects.filter(session=session, status='SOLD').count()
        booked = Ticket.objects.filter(session=session, status='BOOKED').count()

        occupied = sold + booked

        percent = 0
        if total_seats > 0:
            percent = round((occupied / total_seats) * 100, 1)

        # Прогрес-бар (складений: зелений = продано, жовтий = резерв)
        if total_seats > 0:
            pct_sold = round((sold / total_seats) * 100, 1)
            pct_booked = round((booked / total_seats) * 100, 1)
        else:
            pct_sold = 0
            pct_booked = 0

        bar_html = f"""
        <div style="background:#e9ecef; width:100%; height:20px; border-radius:4px; overflow:hidden; display:flex;">
            <div style="width:{pct_sold}%; background:#28a745; height:100%;" title="Продано"></div>
            <div style="width:{pct_booked}%; background:#ffc107; height:100%;" title="Резерв"></div>
        </div>
        """

        rows += f"""
        <tr>
            <td>{session.start_time.strftime("%d.%m.%Y")}</td>
            <td style="text-align:left">{session.movie.title}</td>
            <td>{session.hall.name}</td>
            <td>{total_seats}</td>
            <td>
                <span class="text-money">{sold}</span> + 
                <span class="text-pending">{booked}</span> = 
                <b>{occupied}</b>
            </td>
            <td>{percent}%</td>
            <td width="150">{bar_html}</td>
        </tr>
        """

    table = f"""
    <h1>Звіт: Завантаженість залів</h1>
    <div class="subtitle">Зелений = Продано, Жовтий = Резерв</div>
    <table>
        <thead>
            <tr>
                <th>Дата</th>
                <th>Фільм</th>
                <th>Зал</th>
                <th>Всього місць</th>
                <th>Зайнято (Прод + Рез)</th>
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
