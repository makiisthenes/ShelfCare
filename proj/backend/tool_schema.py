from pydantic import BaseModel
from typing import Optional


class DBOverviewSchema(BaseModel):
	days: Optional[str] = 7


class ProductSchema(BaseModel):
	product_name: str
	supplier: Optional[str]
	category: Optional[str] = "Medicine"
	stock_count: int
	cost: Optional[float | int] = 0.00
	description: Optional[str]