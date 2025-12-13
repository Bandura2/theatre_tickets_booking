class CinemaSystem:
    """
    Реалізація патерну Singleton для головної системи кінотеатру.
    Відповідає за глобальні налаштування та доступ до ресурсів.
    """
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(CinemaSystem, cls).__new__(cls)
            cls._instance.name = "My Grand Cinema"
            cls._instance.is_open = True
        return cls._instance

    @staticmethod
    def get_instance():
        """Статичний метод для отримання єдиного екземпляра."""
        if CinemaSystem._instance is None:
            CinemaSystem()
        return CinemaSystem._instance

    def get_info(self):
        return f"System: {self.name}, Status: {'Open' if self.is_open else 'Closed'}"
