from data.models.base_model import Base
from sqlalchemy.orm import relationship
from datetime import datetime
import enum
from sqlalchemy import Table, Column, Integer, ForeignKey, Enum, String, DateTime



# Enum para roles
class UserRole(enum.Enum):
    CLIENT = "client"
    ADMIN = "admin"

class User(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True, autoincrement=True)
    username = Column(String(50), unique=True, nullable=False)
    password_hash = Column(String(128), nullable=False)
    first_name = Column(String(100), nullable=True)
    last_name = Column(String(100), nullable=True)
    email = Column(String(100), unique=True, nullable=True)
    phone_number = Column(String(14), nullable=False)
    date_of_birth = Column(DateTime, nullable=False)
    creation_date = Column(DateTime, default=datetime.now)
    modification_date = Column(DateTime, onupdate=datetime.now)
    delete_date = Column(DateTime, nullable=True)
    role = Column(Enum(UserRole), nullable=False)
    product = relationship('Product', back_populates='supplier')
    status = Column(Enum('active', 'inactive', name='user_status'), default='active')

    __mapper_args__ = {
        'polymorphic_on': role,
        'polymorphic_identity': 'user'
    }

    def to_dict(self):
        return {
            'id': self.id,
            'username': self.username,
            'first_name': self.name,
            'last_name': self.lastname,
            'email': self.email,
            'phone_number': self.phone_number,
            'date_of_birth': self.date_of_birth.isoformat() if self.date_of_birth else None,
            'creation_date': self.creation_date.isoformat(),
            'modification_date': self.modification_date.isoformat() if self.modification_date else None,
            'delete_date': self.delete_date.isoformat() if self.delete_date else None,
            'role': self.role.value,
            'status': self.status

        }

# Subtipo: Cliente
class Client(User):
    __tablename__ = 'clients'

    id = Column(Integer, ForeignKey('users.id'), primary_key=True)
    shipping_address = Column(String)
    billing_address = Column(String)
    # preferred_contact_method = Column(String)  # 'email', 'phone', etc.
    # preferred_language = Column(String)  # 'en', 'es', etc.
    # loyalty_points = Column(Integer, default=0)
    # purchase_history = Column(String)  # JSON or similar format for purchase history
    # preferred_payment_method = Column(String)  # 'credit_card', 'PayPal', etc.
    # preferred_shipping_method = Column(String)  # 'standard', 'express', etc.
    # newsletter_subscription = Column(String)  # 'subscribed', 'unsubscribed'
    # preferred_currency = Column(String)  # 'USD', 'EUR', etc.

    def __repr__(self):
        """Representación de cadena para depuración."""
        return f"<Client(id={self.id}, name='{self.first_name} {self.last_name}', email='{self.email}')>"

    __mapper_args__ = {
        'polymorphic_identity': UserRole.CLIENT,
    }

    def to_dict(self):
        data = super().to_dict()
        data.update({
            'shipping_address': self.shipping_address,
            'billing_address': self.billing_address,
            # 'preferred_contact_method': self.preferred_contact_method,
            # 'preferred_language': self.preferred_language,
            # 'loyalty_points': self.loyalty_points,
            # 'purchase_history': self.purchase_history,
            # 'preferred_payment_method': self.preferred_payment_method,
            # 'preferred_shipping_method': self.preferred_shipping_method,
            # 'newsletter_subscription': self.newsletter_subscription,
            # 'preferred_currency': self.preferred_currency
        })


class DepartmentEnum(enum.Enum):
    IT = "IT"
    HR = "HR"
    FINANCE = "Finance"
    SALES = "Sales"
    DESING = "Design"
    PRODUCTION = "Production"


class PermissionEnum(enum.Enum):
    READ = "read"
    WRITE = "write"
    DELETE = "delete"
    ADMIN = "admin"

admin_departments = Table(
    'admin_departments', Base.metadata,
    Column ('admin_id', Integer, ForeignKey('admins.id'), primary_key=True),
    Column('department', Enum(DepartmentEnum), primary_key=True)
)

admin_permissions = Table(
    'admin_permissions', Base.metadata,
    Column('admin_id', Integer, ForeignKey('admins.id'), primary_key=True),
    Column('permission', Enum(PermissionEnum), primary_key=True)
)

# Subtipo: Admin
class Admin(User):
    __tablename__ = 'admins'

    id = Column(Integer, ForeignKey('users.id'), primary_key=True)
    permissions = Column(Enum(PermissionEnum), nullable=False)  # JSON or similar format for permissions
    department = Column(Enum(DepartmentEnum), nullable=False)
    # department = Column(String)  # 'IT', 'HR', 'Finance', etc.


    __mapper_args__ = {
        'polymorphic_identity': UserRole.ADMIN,
    }

    def to_dict(self):
        data = super().to_dict()
        data.update({
            'permissions': self.permissions,
            'department': self.department,
        })
        return data