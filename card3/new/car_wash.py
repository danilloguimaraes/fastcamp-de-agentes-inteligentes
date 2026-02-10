"""
Lavajato

Esse exemplo é de um lavajato. Ele permite adicionar carros, serviços e ordens de lavagem.

Depois de as informações é possível operar sobre o sistema de lavagem.

- Adicionar carros
- Adicionar serviços
- Adicionar ordens de lavagem
- Obter carros
- Obter serviços
- Obter ordens de lavagem
- Obter total de preço
"""

from pydantic import BaseModel, Field, PositiveFloat, ValidationError, field_validator, model_validator, field_serializer, computed_field
import re
from enum import Enum

# Marcas de carros
class CarBrand(str, Enum):
    TOYOTA = "toyota"
    HONDA = "honda"
    FORD = "ford"
    BMW = "bmw"
    AUDI = "audi"

# Cores de carros
class CarColor(str, Enum):
    WHITE = "white"
    BLACK = "black"
    SILVER = "silver"
    BLUE = "blue"
    RED = "red"

# Instância de um carro
class Car(BaseModel):
    brand: CarBrand = Field(..., description="The brand of the car")
    model: str = Field(..., description="The model of the car")
    color: CarColor = Field(..., description="The color of the car")
    plate: str = Field(..., description="The plate of the car")
    owner: "CarOwner" = Field(default_factory=lambda: CarOwner())

    # Validar placa do carro, deve ser uma string que contenha 3 letras maiúsculas e 4 números. Exemplo: AAA1234
    @field_validator("plate")
    @classmethod
    def validate_plate(cls, v: str) -> str:
        plate = v.upper().strip()
        if not re.fullmatch(r"[A-Z]{3}\d{4}", plate):
            raise ValueError("car_plate must match AAA1234")
        return plate

    # Validar marca do carro, deve ser uma marca de carro válida. Exemplo: TOYOTA, HONDA, FORD, BMW, AUDI (enum)
    @field_validator("brand")
    @classmethod
    def validate_brand(cls, v: CarBrand) -> CarBrand:
        if v not in CarBrand:
            raise ValueError("brand must be a valid brand")
        return v

    # Validar cor do carro, deve ser uma cor de carro válida. Exemplo: WHITE, BLACK, SILVER, BLUE, RED
    # Aqui utilizamos o field_validator para validação customizada.
    @field_validator("color")
    @classmethod
    def validate_color(cls, v: CarColor) -> CarColor:
        if v not in CarColor:
            raise ValueError("color must be a valid color")
        return v

    # Validar regra de negócio: a marca é obrigatória para que o modelo seja informado.
    # Aqui utilizamos o model_validator para validar a regra de negócio, pois depende de mais de um campo.
    @model_validator(mode="after")
    def validate_brand_required(self):
        if self.brand is None and self.model is not None:
            raise ValueError("brand is required if model is not blank")
        return self

    # Serializar o carro para uma string, omitindo o proprietário
    # Aqui utilizamos o field_serializer para serializar o carro para uma string, omitindo o proprietário.
    # when_used: json indica que a serialização será feita para o formato JSON.
    @field_serializer("owner", when_used="json")
    def serialize_owner(self, v: "CarOwner") -> str:
        return v.model_dump_json(exclude={"cars"})


# Informações do proprietário do carro
class CarOwner(BaseModel):
    name: str = Field(..., description="The name of the car owner")
    email: str = Field(..., description="The email of the car owner")
    phone: str = Field(..., description="The phone number of the car owner")
    cars: list[Car] = Field(default_factory=list, description="The cars of the car owner")
    cpf: str = Field(description="The CPF of the car owner")


# Serviços de lavagem e preços
class CarWashService(BaseModel):
    name: str = Field(..., description="The name of the car wash service")
    price: PositiveFloat = Field(..., description="The price of the car wash service")


# Requisição de lavagem de carros
class CarWashRequest(BaseModel):
    cars: list[Car] = Field(default_factory=list, description="The cars to be washed")
    services: list[CarWashService] = Field(default_factory=list, description="The services to be used")


# Ordem de lavagem de carros
class WashOrder(BaseModel):
    car: Car = Field(..., description="The car to be washed")
    services: list[CarWashService] = Field(default_factory=list, description="The services to be used")

    # Validar regra de negócio: ao menos um serviço é obrigatório.
    # Aqui utilizamos o model_validator para validar a regra de negócio, pois depende de mais de um campo.
    @model_validator(mode="after")
    def validate_services_required(self):
        if not self.services:
            raise ValueError("at least one service is required")
        return self

    # Serializar a ordem de lavagem para uma string, omitindo o carro
    # Aqui utilizamos o field_serializer para serializar a ordem de lavagem para uma string, omitindo o carro.
    # when_used: json indica que a serialização será feita para o formato JSON.
    @field_serializer("car", when_used="json")
    def serialize_car(self, v: Car) -> str:
        return v.model_dump_json(exclude={"owner"})

    # Calcular o total da ordem de lavagem
    # Aqui utilizamos o computed_field para calcular o total da ordem de lavagem.
    # Ele é calculado quando o campo for acessado.
    @computed_field
    @property
    def total_price(self) -> PositiveFloat:
        return sum(service.price for service in self.services)


# Sistema de lavagem de carros
class CarWashSystem(BaseModel):

    # Campos do sistema de lavagem de carros
    cars: list[Car] = Field(default_factory=list, description="The cars to be washed")
    services: list[CarWashService] = Field(default_factory=list, description="The services to be used")
    orders: list[WashOrder] = Field(default_factory=list, description="The orders to be processed")

    # Adicionar um carro ao sistema
    def add_car(self, car: Car) -> None:
        self.cars.append(car)

    # Adicionar um serviço ao sistema
    def add_service(self, service: CarWashService) -> None:
        self.services.append(service)

    # Adicionar uma ordem de lavagem ao sistema
    def add_order(self, order: WashOrder) -> None:
        self.orders.append(order)

    # Obter os carros no sistema
    def get_cars(self) -> list[Car]:
        return self.cars
        
    # Obter os serviços no sistema
    def get_services(self) -> list[CarWashService]:
        return self.services

    # Obter as ordens de lavagem no sistema
    def get_orders(self) -> list[WashOrder]:
        return self.orders

    # Obter o total de preço das ordens de lavagem no sistema
    def get_total_price(self) -> PositiveFloat:
        return sum(order.total_price for order in self.orders)

    # Obter o total de preço dos serviços no sistema
    def get_total_price_of_services(self) -> PositiveFloat:
        return sum(service.price for service in self.services)

def main():
    print("\n=== Pydantic practice: Car Wash ===")

    # Proprietário base usado em todos os cenários
    owner = CarOwner(
        name="John Doe",
        email="john.doe@example.com",
        phone="1234567890",
        cpf="1234567890",
    )

    # 1) Field validator (placa): entrada válida
    print("\n1) Field validator (plate)")
    car_ok = Car(
        brand=CarBrand.TOYOTA,
        model="Corolla",
        color=CarColor.WHITE,
        plate="aaa1234",
        owner=owner,
    )
    print(f"Valid plate normalized: {car_ok.plate}")

    # 2) Field validator (placa): entrada inválida gera ValidationError
    print("\n2) Invalid plate")
    try:
        Car(
            brand=CarBrand.HONDA,
            model="Civic",
            color=CarColor.BLACK,
            plate="AA12345",
            owner=owner,
        )
    except ValidationError as exc:
        print(f"Plate error: {exc.errors()[0]['msg']}")

    # 3) Enum validation: valor enum inválido
    print("\n3) Enum validation")
    try:
        Car(
            brand="fiat",
            model="Uno",
            color=CarColor.RED,
            plate="BBB1234",
            owner=owner,
        )
    except ValidationError as exc:
        print(f"Brand enum error: {exc.errors()[0]['msg']}")

    # 4) model_validator + computed_field na Ordem de Lavagem
    print("\n4) model_validator + computed_field")
    basic = CarWashService(name="Basic Wash", price=10.0)
    premium = CarWashService(name="Premium Wash", price=25.0)
    order_ok = WashOrder(car=car_ok, services=[basic, premium])
    print(f"Computed total_price: {order_ok.total_price}")

    # model_validator deve falhar quando a lista de serviços estiver vazia
    try:
        WashOrder(car=car_ok, services=[])
    except ValidationError as exc:
        print(f"Order error: {exc.errors()[0]['msg']}")

    # 5) field_serializer: comparar dump python vs JSON dump
    print("\n5) field_serializer in action")
    print("model_dump():")
    print(order_ok.model_dump())
    print("model_dump_json():")
    print(order_ok.model_dump_json())

    # Opcional: usar a classe sistema com uma ordem de lavagem válida
    print("\n6) CarWashSystem aggregate")
    car_wash_system = CarWashSystem()
    car_wash_system.add_car(car_ok)
    car_wash_system.add_service(basic)
    car_wash_system.add_service(premium)
    car_wash_system.add_order(order_ok)
    print(f"System total order price: {car_wash_system.get_total_price()}")

if __name__ == "__main__":
    main()