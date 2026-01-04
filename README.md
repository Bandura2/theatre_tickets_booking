**Покрокова інструкція запуску додатку:**

**1. Клонування репозиторію**

    Відкрийте термінал та виконайте команди:

    git clone [link_to_repository]

    cd theatre_tickets_booking/backend

**2. Створення віртуального оточення**

    python -m venv venv

    venv\Scripts\activate

**3. Встановлення залежностей**

    pip install -r requirements.txt

**4. Налаштування бази даних**

    python manage.py migrate

**5. Створення адміністратора** 

    python manage.py createsuperuser

    (Введіть логін, email та пароль, коли система запитає)

**6. Запуск сервера**

    python manage.py runserver

**7. Запуск веб додатку**

    Відкрити файл frontend/index.html (Open with Live Server)