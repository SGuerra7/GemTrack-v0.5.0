# repos/category_repo.py
from typing import List, Optional
from sqlalchemy.future import select
from data.models.product_models import Category
from data.database import AsyncSessionLocal
from data.crud_operations import get_all_records, get_record_by_id

class CategoryRepository:
    """
    Repositorio para manejar las operaciones de persistencia de datos para las categorías.
    """
    def __init__(self):
        self.session_provider = AsyncSessionLocal

    async def get_all(self) -> List[Category]:
        """
        Obtiene todas las categorías de la base de datos.
        """
        return await get_all_records(self.session_provider, Category)

    async def get_by_id(self, category_id: int) -> Optional[Category]:
        """
        Obtiene una categoría por su ID.
        """
        return await get_record_by_id(self.session_provider, Category, category_id)

    # Aquí podrías añadir en el futuro métodos para crear, actualizar o eliminar categorías.

    # ¡NUEVO MÉTODO!
    async def get_by_ids(self, category_ids: List[int]) -> List[Category]:
        """
        Obtiene una lista de categorías a partir de una lista de IDs.
        Es eficiente porque usa una única consulta a la base de datos.
        """
        # Si la lista de IDs está vacía, devolvemos una lista vacía para evitar una consulta innecesaria.
        if not category_ids:
            return []
        # Usamos una sesión asíncrona para ejecutar la consulta.

        async with self.session_provider() as session:
            # Usamos el operador 'in_' de SQLAlchemy para crear una cláusula 'WHERE id IN (...)'.
            result = await session.execute(
                select(Category).filter(Category.id.in_(category_ids))
            )
            return result.scalars().all()