from pydantic import BaseModel
from typing import List, Optional

class Item(BaseModel):
    nombre: str
    precio: float

class Recibo(BaseModel):
    cliente: str
    items: List[Item]
    total: float

class PrintData(BaseModel):
    data: str

class MarkdownData(BaseModel):
    markdown: str
    target: str = "emulator" # "emulator" o "physical"
    physical_key: Optional[str] = None

class LuckyData(BaseModel):
    nombre: str
    target: str = "emulator"
    physical_key: Optional[str] = None
