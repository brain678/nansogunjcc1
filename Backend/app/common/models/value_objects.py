# app/common/models/value_objects.py

from pydantic import BaseModel, field_validator, EmailStr
from typing import Optional, List
from enum import Enum


class Email(BaseModel):
    """Email value object"""
    value: EmailStr

    @field_validator("value", mode="before")
    @classmethod
    def normalize_email(cls, v):
        if not isinstance(v, str):
            v = str(v)
        return v.strip().lower()
    
    def __str__(self) -> str:
        return self.value
    
    def __hash__(self) -> int:
        return hash(self.value)
    
    def __eq__(self, other) -> bool:
        if isinstance(other, Email):
            return self.value == other.value
        return self.value == other


class Phone(BaseModel):
    """Phone value object"""
    value: str
    country_code: Optional[str] = None
    
    @field_validator('value')
    @classmethod
    def validate_phone(cls, v):
        if not isinstance(v, str):
            v = str(v)

        cleaned_value = v.strip()
        if not cleaned_value:
            raise ValueError('Phone number cannot be empty')

        digits = ''.join(filter(str.isdigit, cleaned_value))
        if len(digits) < 10:
            raise ValueError('Invalid phone number')
        return cleaned_value
    
    def __str__(self) -> str:
        return self.value.strip()
    
    def __hash__(self) -> int:
        return hash(self.value)


class Address(BaseModel):
    """Address value object"""
    street: str
    city: str
    state: str
    zip_code: str
    country: str = "USA"
    
    def __str__(self) -> str:
        return f"{self.street}, {self.city}, {self.state} {self.zip_code}, {self.country}"


class Permission(BaseModel):
    """Permission value object"""
    resource: str
    action: str  # create, read, update, delete
    scope: str   # own, organization, national
    
    def __str__(self) -> str:
        return f"{self.resource}:{self.action}:{self.scope}"
    
    def __hash__(self) -> int:
        return hash(str(self))
    
    def __eq__(self, other) -> bool:
        if isinstance(other, Permission):
            return str(self) == str(other)
        return str(self) == other


class CurrencyType(str, Enum):
    """Currency types"""
    USD = "USD"
    EUR = "EUR"
    GBP = "GBP"


class Money(BaseModel):
    """Money value object"""
    amount: float
    currency: CurrencyType = CurrencyType.USD
    
    def __str__(self) -> str:
        return f"{self.currency} {self.amount:.2f}"
    
    @field_validator('amount')
    @classmethod
    def validate_amount(cls, v):
        if v < 0:
            raise ValueError('Amount cannot be negative')
        return round(v, 2)


class Percentage(BaseModel):
    """Percentage value object"""
    value: float
    
    @field_validator('value')
    @classmethod
    def validate_percentage(cls, v):
        if v < 0 or v > 100:
            raise ValueError('Percentage must be between 0 and 100')
        return round(v, 2)
    
    def __str__(self) -> str:
        return f"{self.value}%"
