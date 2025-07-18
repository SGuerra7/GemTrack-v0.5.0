# repositories/product_repository.py
from typing import List, Optional, Dict, Any
from sqlalchemy.future import select
from sqlalchemy import and_, or_
# Importamos el modelo Product
from data.models.product_models import Product
# Importamos el proveedor de sesiones de la base de datos
from data.database import AsyncSessionLocal
# Importamos las funciones CRUD genéricas
from data.crud_operations import create_record, get_record_by_id, get_all_records, update_record, delete_record
from sqlalchemy.orm import selectinload  # ¡CAMBIO CLAVE! Importar selectinload

class ProductRepository:
    """
    Clase de repositorio para manejar las operaciones de persistencia
    relacionadas con el modelo Product.
    Encapsula la lógica de acceso a datos para los productos.
    """
    def __init__(self):
        # El repositorio "conoce" cómo obtener una sesión asíncrona.
        # AsyncSessionLocal es la fábrica de sesiones que se pasará a las funciones CRUD.
        self.session_provider = AsyncSessionLocal

    async def create(self, product: Product) -> Product:
        """
        Crea un nuevo producto en la base de datos.
        Args:
            product: Una instancia de Product a ser creada.
        Returns:
            La instancia de Product creada con su ID asignado.
        """
        return await create_record(self.session_provider, product)

    async def update(self, product_id: int, new_data: Dict[str, Any]) -> Optional[Product]:
        """
        Actualiza un producto existente por su ID.
        Args:
            product_id: El ID del producto a actualizar.
            new_data: Un diccionario con los campos y nuevos valores a actualizar.
        Returns:
            La instancia de Product actualizada si se encuentra, de lo contrario None.
        """
        return await update_record(self.session_provider, Product, product_id, new_data)

    async def delete(self, product_id: int) -> bool:
        """
        Elimina un producto por su ID.
        Args:
            product_id: El ID del producto a eliminar.
        Returns:
            True si el producto fue eliminado, False si no se encontró.
        """
        return await delete_record(self.session_provider, Product, product_id)

    async def get_by_id(self, product_id: int) -> Optional[Product]:
        """
        Obtiene un producto por su ID, cargando ansiosamente sus relaciones.
        """
        async with self.session_provider() as session:
            result = await session.execute(
                select(Product)
                .options(
                    selectinload(Product.categories),  # Cargar la lista de categorías
                    selectinload(Product.supplier)     # Cargar el objeto proveedor
                )
                .filter(Product.id == product_id)
            )
            return result.scalars().first()

    async def get_all(self) -> List[Product]:
        """
        Obtiene todos los productos, cargando ansiosamente sus relaciones.
        """
        async with self.session_provider() as session:
            result = await session.execute(
                select(Product)
                .options(
                    selectinload(Product.categories),  # Cargar la lista de categorías
                    selectinload(Product.supplier)     # Cargar el objeto proveedor
                )
                .order_by(Product.name) # Es buena práctica ordenar los resultados
            )
            return result.scalars().all()

    # Aquí se pueden añadir métodos de consulta más específicos si son necesarios,
    # que no encajen en las operaciones CRUD genéricas.
    # Por ejemplo, buscar por SKU, por categoría, etc.
    async def get_by_sku(self, sku: str) -> Optional[Product]:
        """
        Obtiene un producto por su SKU, cargando ansiosamente sus relaciones.
        """
        async with self.session_provider() as session:
            result = await session.execute(
                select(Product)
                .options(
                    selectinload(Product.categories),  # Cargar la lista de categorías
                    selectinload(Product.supplier)     # Cargar el objeto proveedor
                )
                .filter(and_(Product.sku == sku))
            )
            return result.scalars().first()

        # ¡NUEVO!

    async def get_filtered(self, filter_type: str) -> List[Product]:
        """
        Obtiene una lista de productos basada en un filtro específico,
        cargando ansiosamente sus relaciones.
        """
        async with self.session_provider() as session:
            # ¡CAMBIO CLAVE! Añadir options() a la consulta base.
            query = select(Product).options(
                selectinload(Product.categories),
                selectinload(Product.supplier)
            )

            if filter_type == "low_stock":
                query = query.filter(or_(Product.stock < 10, Product.stock == 0))
            elif filter_type == "location":
                # Placeholder: podrías filtrar por una ubicación específica
                pass  # No se aplica filtro adicional

            result = await session.execute(query.order_by(Product.name))
            return result.scalars().all()

