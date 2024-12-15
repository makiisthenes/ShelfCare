from typing import List, Optional
from datetime import date
from sqlalchemy import ForeignKey, String, Text, Date, Numeric
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column
from sqlalchemy.orm import relationship


class Base(DeclarativeBase):
	pass


class Product(Base):
    __tablename__ = "products"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    product_name: Mapped[Optional[str]] = mapped_column(String(100))
    supplier: Mapped[Optional[str]] = mapped_column(String(100))
    category: Mapped[Optional[str]] = mapped_column(String(12))
    stock_count: Mapped[Optional[int]]
    cost: Mapped[Optional[float]] = mapped_column(Numeric(5, 2))
    description: Mapped[Optional[str]] = mapped_column(Text)

    # Relationships
    orders: Mapped[List["Order"]] = relationship(back_populates="product", cascade="all, delete-orphan")
    expiry_dates: Mapped[List["ProductExpiry"]] = relationship(back_populates="product", cascade="all, delete-orphan")



class Order(Base):
	__tablename__ = "orders"

	order_id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
	product_id: Mapped[int] = mapped_column(ForeignKey("products.id", ondelete="CASCADE"))
	order_date: Mapped[date] = mapped_column(Date)
	quantity: Mapped[int]
	date_expected: Mapped[Optional[date]] = mapped_column(Date)

	# Relationship
	product: Mapped["Product"] = relationship(back_populates="orders")


class ProductExpiry(Base):
    __tablename__ = "expiry"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    product_id: Mapped[int] = mapped_column(ForeignKey("products.id", ondelete="CASCADE"), nullable=False)
    expiry_date: Mapped[date] = mapped_column(Date, nullable=False)
    quantity: Mapped[int] = mapped_column(nullable=False)

    # Relationship
    product: Mapped["Product"] = relationship(back_populates="expiry_dates")
