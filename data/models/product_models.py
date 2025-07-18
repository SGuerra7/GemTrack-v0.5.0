from typing import Dict, Any
from data.models.base_model import Base
from sqlalchemy.orm import relationship
from datetime import datetime
from sqlalchemy import Table, Column, Integer, ForeignKey, String, Float, DateTime


# Asociación entre productos y categorías
product_category_association = Table('product_category_association', Base.metadata,
    Column('product_id', Integer, ForeignKey('products.id'), primary_key=True),
    Column('category_id', Integer, ForeignKey('categories.id'), primary_key=True)
)

class Category(Base):
    __tablename__ = 'categories'
    id = Column(Integer, primary_key=True)
    name = Column(String(50), unique=True, nullable=False)

    # Esta relación está bien.
    products = relationship(
        "Product",
        secondary=product_category_association,
        back_populates="categories"
    )

class Product(Base):
    __tablename__ = 'products'

    id = Column(Integer, primary_key=True, autoincrement=True)
    image_path = Column(String, nullable=True)  # NUEVO CAMPO PARA LA IMAGEN
    sku = Column(String(50), unique=True, nullable=False)
    name = Column(String(100), nullable=False)
    description = Column(String(500), nullable=True)
    categories = relationship(
        "Category",
        secondary=product_category_association,
        back_populates="products"  # Necesitas añadir una relación inversa en Category
    )
    buying_price = Column(Float, default=0.0, nullable=True)
    suggested_price = Column(Float, default=0.0, nullable=True)
    stock = Column(Integer, default=0, nullable=True)
    availability_status = Column(String, default="en_stock", )  # 'en_stock', 'agotado'
    measurement_unity = Column(String(20), nullable=True)

    supplier_id = Column(Integer, ForeignKey('suppliers.id'), nullable=True)
    supplier = relationship('Supplier', back_populates='products')

    location = Column(String(100), nullable=True)
    creation_date = Column(DateTime, default=datetime.now)
    modification_date = Column(DateTime, onupdate=datetime.now)

    def __repr__(self):
        return f"<Product(id={self.id}, name='{self.name}', sku='{self.sku}')>"

    def to_dict(self):
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}

    @classmethod
    def from_dict(cls, data: Dict[str, Any]):
        # Obtiene los nombres de las columnas válidas para este modelo
        valid_keys = {c.name for c in cls.__table__.columns}
        # Crea un nuevo diccionario solo con las claves que existen en el modelo
        filtered_data = {key: value for key, value in data.items() if key in valid_keys}
        # Llama al constructor solo con los datos filtrados y válidos
        return cls(**filtered_data)







