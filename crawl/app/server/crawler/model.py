from typing import List
from pydantic import BaseModel, Field, root_validator, validator
from datetime import datetime
from enum import Enum
from server.database import database
collection = database.crawler 
class Status(str, Enum):
    start = "start"
    stop = "stops"
    complete = "complete"
    queue = "queue"

class Type(str, Enum):
    aliexpress = "aliexpress"
    google = "google"

class CrawlerSchema(BaseModel):
    url: str = Field(...)
    status: Status = Field(default=Status.queue)
    quantity: int = Field(default=0)
    created_at: datetime = Field(default=datetime.now())
    updated_at: datetime = Field(default=datetime.now())
    type: Type  = Field(default=Type.aliexpress)
    @validator("updated_at", pre=True, always=True)
    def set_updated_at(cls, value: datetime):
        if value is None:
            return datetime.now()
        return value