# En un nuevo archivo data/models/supplier_models.py o similar
from data.models.base_model import Base
from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship


class Supplier(Base):
    __tablename__ = 'suppliers'

    id = Column(Integer, primary_key=True)
    name = Column(String(150), nullable=False, unique=True)
    contact_person = Column(String(100))
    email = Column(String(100))
    phone = Column(String(20))

    # Relación inversa: Un proveedor puede suministrar muchos productos
    products = relationship("Product", back_populates="supplier")

    def to_dict(self):
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}
