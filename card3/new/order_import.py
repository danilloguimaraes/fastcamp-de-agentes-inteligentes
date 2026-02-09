from __future__ import annotations

from datetime import datetime
from decimal import Decimal
from typing import Any

from pydantic import (
    BaseModel,
    ConfigDict,
    EmailStr,
    Field,
    ValidationError,
    computed_field,
    condecimal,
    conint,
    field_serializer,
    field_validator,
    model_validator,
)


class Customer(BaseModel):
    name: str
    email: EmailStr

    @field_validator("name")
    @classmethod
    def name_must_not_be_blank(cls, value: str) -> str:
        value = value.strip()
        if not value:
            raise ValueError("name cannot be blank")
        return value

    @field_validator("email")
    @classmethod
    def normalize_email(cls, value: EmailStr) -> EmailStr:
        return value.lower()


class Item(BaseModel):
    sku: str
    quantity: conint(gt=0)
    unit_price: condecimal(gt=0, max_digits=10, decimal_places=2)


class Order(BaseModel):
    id: str
    created_at: datetime
    customer: Customer
    items: list[Item]
    coupon: str | None = None

    @field_validator("items")
    @classmethod
    def must_have_items(cls, value: list[Item]) -> list[Item]:
        if not value:
            raise ValueError("order must have at least one item")
        return value

    @computed_field
    @property
    def total(self) -> Decimal:
        return sum(item.quantity * item.unit_price for item in self.items)

    @model_validator(mode="after")
    def coupon_requires_min_total(self) -> "Order":
        if self.coupon and self.total < Decimal("30.00"):
            raise ValueError("coupon requires minimum total of 30.00")
        return self


class ShippingLabel(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    order_id: str = Field(alias="orderId")
    created_at: datetime = Field(alias="createdAt")
    customer_email: EmailStr = Field(alias="email")

    @field_serializer("created_at")
    def serialize_created_at(self, value: datetime) -> str:
        return value.strftime("%Y-%m-%d")


def parse_orders(raw_orders: list[dict[str, Any]]) -> list[Order]:
    return [Order.model_validate(raw) for raw in raw_orders]


def serialize_public_order(order: Order) -> dict[str, Any]:
    return order.model_dump(
        mode="json",
        exclude={"customer": {"email"}},
    )


def serialize_shipping_label(order: Order) -> dict[str, Any]:
    label = ShippingLabel(
        order_id=order.id,
        created_at=order.created_at,
        customer_email=order.customer.email,
    )
    return label.model_dump(by_alias=True)


if __name__ == "__main__":
    valid_raw = [
        {
            "id": "A100",
            "created_at": "2026-02-08T10:30:00",
            "customer": {"name": "  Ana  ", "email": "ANA@EXAMPLE.COM"},
            "coupon": "SAVE10",
            "items": [
                {"sku": "SKU-1", "quantity": 2, "unit_price": "19.90"},
                {"sku": "SKU-2", "quantity": 1, "unit_price": "5.50"},
            ],
        },
    ]
    invalid_raw = [
        {
            "id": "A101",
            "created_at": "08/02/2026 11:00",
            "customer": {"name": "Bob", "email": "bob@example.com"},
            "items": [],
        }
    ]

    try:
        orders = parse_orders(valid_raw)
    except ValidationError as exc:
        print(exc)
    else:
        for order in orders:
            print(serialize_public_order(order))
            print(serialize_shipping_label(order))

    try:
        parse_orders(invalid_raw)
    except ValidationError as exc:
        print(exc)
