# Строитель (Builder)

## Предназначение
**Строитель** — это порождающий шаблон проектирования, который используется для создания сложных объектов. Он позволяет создавать различные представления объекта, используя один и тот же процесс строительства.

## Схема
1. **Director**: Класс, определяющий порядок вызова шагов строительства.
2. **Builder**: Интерфейс с методами для создания частей сложного объекта.
3. **ConcreteBuilder**: Классы, реализующие `Builder` и предоставляющие конкретные реализации.
4. **Product**: Конечный объект, который будет построен.

## Пример использования
Шаблон применяется при создании пользовательских интерфейсов, сложных запросов или документов.

## Пример кода
```python
class Car:
    def __init__(self):
        self.wheels = 4
        self.engine = None
        self.seats = None

class CarBuilder:
    def __init__(self):
        self.car = Car()

    def add_engine(self, engine_type):
        self.car.engine = engine_type
        return self

    def add_seats(self, number_of_seats):
        self.car.seats = number_of_seats
        return self

    def get_result(self):
        return self.car

class Director:
    def construct_sports_car(self, builder):
        builder.add_engine('V8').add_seats(2)
        return builder.get_result()

    def construct_family_van(self, builder):
        builder.add_engine('V6').add_seats(7)
        return builder.get_result()

# Использование
director = Director()
builder = CarBuilder()
sports_car = director.construct_sports_car(builder)
family_van = director.construct_family_van(builder)
```