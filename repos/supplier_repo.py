# repos/supplier_repo.py
from typing import List, Optional, Dict, Any
from sqlalchemy.future import select

# Importamos el modelo Supplier y la configuración de la base de datos
from data.models.supplier_models import Supplier
from data.database import AsyncSessionLocal
# Importamos las operaciones CRUD genéricas
from data.crud_operations import get_all_records, get_record_by_id

class SupplierRepository:
    """
    Repositorio para manejar las operaciones de persistencia de datos para los proveedores.
    """
    def __init__(self):
        self.session_provider = AsyncSessionLocal

    async def get_all(self) -> List[Supplier]:
        """
        Obtiene todos los proveedores de la base de datos.
        """
        return await get_all_records(self.session_provider, Supplier)

    async def get_by_id(self, supplier_id: int) -> Optional[Supplier]:
        """
        Obtiene un proveedor por su ID.
        """
        return await get_record_by_id(self.session_provider, Supplier, supplier_id)

    # Aquí podrías añadir en el futuro métodos específicos como:
    # async def create(self, supplier_data: Dict[str, Any]) -> Supplier: ...
    # async def update(self, supplier_id: int, supplier_data: Dict[str, Any]) -> Optional[Supplier]: ...
