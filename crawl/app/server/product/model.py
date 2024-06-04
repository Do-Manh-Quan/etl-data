from typing import List
from pydantic import BaseModel, Field, validator
from datetime import datetime
class Review(BaseModel):
    start: float = Field(..., ge=0, le=5)
    sku: str = Field(...)
    review: str = Field(...)
    images: List[str] = Field(...)

class SKUItem(BaseModel):
    label: str = Field(...)
    value: str = Field(...)

class SKU(BaseModel):
    type: str = Field(...)
    item: List[SKUItem]

class AliexpressProductSchema(BaseModel):
    title: str = Field(...)
    images: List[str] = Field(...)
    price: str = Field(...)
    sku: List[SKU] = Field(default=[])
    reviews: List[Review] = Field(default=[])
    des: str = Field(...)
    url: str = Field(...)
    root: str = Field(...)
    created_at: datetime = Field(default=datetime.now())
    updated_at: datetime = Field(default=datetime.now())
    @validator("updated_at", pre=True, always=True)
    def set_updated_at(cls, value: datetime):
        if value is None:
            return datetime.now()
        return value