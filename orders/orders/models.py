import datetime

from sqlalchemy import (
    DECIMAL, Column, DateTime, ForeignKey, Integer, String,
)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship


class Base(object):
    created_at = Column(
        DateTime,
        default=datetime.datetime.utcnow,
        nullable=False
    )
    updated_at = Column(
        DateTime,
        default=datetime.datetime.utcnow,
        onupdate=datetime.datetime.utcnow,
        nullable=False
    )


DeclarativeBase = declarative_base(cls=Base)


class Order(DeclarativeBase):
    __tablename__ = "orders"

    id = Column(Integer, primary_key=True, autoincrement=True)


class OrderDetail(DeclarativeBase):
    __tablename__ = "order_details"

    id = Column(Integer, primary_key=True, autoincrement=True)
    order_id = Column(
        Integer,
        ForeignKey("orders.id", name="fk_order_details_orders"),
        nullable=False
    )
    order = relationship(Order, backref="order_details")
    product_id = Column(
        String, 
        ForeignKey("products.id"), 
        nullable=False)
    product = relationship("Product") 
    price = Column(DECIMAL(18, 2), nullable=False)
    quantity = Column(Integer, nullable=False)

class Product(DeclarativeBase):
    __tablename__ = "products"

    id = Column(String, primary_key=True)
    title = Column(String, nullable=False)
    maximum_speed = Column(Integer, nullable=False)
    in_stock = Column(Integer, nullable=False)
    passenger_capacity = Column(Integer, nullable=False)
