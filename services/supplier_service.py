# services/supplier_service.py
from typing import List, Optional

# Importamos el modelo y el repositorio
from data.models.supplier_models import Supplier
from repos.supplier_repo import SupplierRepository

class SupplierService:
    """
    Servicio para manejar la lógica de negocio relacionada con los proveedores.
    """
    def __init__(self):
        self.supplier_repo = SupplierRepository()

    async def get_all_suppliers(self) -> List[Supplier]:
        """
        Obtiene una lista de todos los proveedores.
        En el futuro, podría añadir lógica aquí (ej. filtrar proveedores inactivos).
        """
        return await self.supplier_repo.get_all()

    async def get_supplier_by_id(self, supplier_id: int) -> Optional[Supplier]:
        """
        Obtiene un proveedor por su ID.
        """
        return await self.supplier_repo.get_by_id(supplier_id)
