from abc import ABC, abstractmethod


class IHallComponent(ABC):
    """Інтерфейс компонента"""

    @abstractmethod
    def show_details(self) -> str:
        pass

    @abstractmethod
    def get_price(self) -> float:
        pass


class SeatLeaf(IHallComponent):
    """Лист (Місце)"""

    def __init__(self, number, is_vip):
        self.number = number
        self.is_vip = is_vip

    def show_details(self) -> str:
        return f"Seat {self.number}"

    def get_price(self) -> float:
        return 150.0 if self.is_vip else 100.0


class SeatGroupComposite(IHallComponent):
    """Контейнер (Ряд/Сектор)"""

    def __init__(self, name):
        self.name = name
        self.children = []

    def add(self, component: IHallComponent):
        self.children.append(component)

    def remove(self, component: IHallComponent):
        self.children.remove(component)

    def show_details(self) -> str:
        results = [f"Group: {self.name}"]
        for child in self.children:
            results.append(child.show_details())
        return "\n".join(results)

    def get_price(self) -> float:
        return sum(child.get_price() for child in self.children)
