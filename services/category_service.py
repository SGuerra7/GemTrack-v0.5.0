# services/category_service.py
from typing import List, Optional
from data.models.product_models import Category
from repos.category_repo import CategoryRepository

class CategoryService:
    """
    Servicio para manejar la lógica de negocio relacionada con las categorías de productos.
    """
    def __init__(self):
        self.category_repo = CategoryRepository()

    async def get_all_categories(self) -> List[Category]:
        """
        Obtiene una lista de todas las categorías.
        """
        return await self.category_repo.get_all()

    async def get_category_by_id(self, category_id: int) -> Optional[Category]:
        """
        Obtiene una categoría por su ID.

        Args:
            category_id (int): El ID de la categoría a buscar.

        Returns:
            Optional[Category]: La categoría encontrada o None si no existe.
        """
        return await self.category_repo.get_by_id(category_id)

    async def create_category(self, name: str, description: str) -> Category:
        """
        Crea una nueva categoría.

        Args:
            name (str): El nombre de la categoría.
            description (str): Una descripción de la categoría.

        Returns:
            Category: La categoría creada.
        """
        new_category = Category(name=name, description=description)
        return await self.category_repo.create(new_category)

    async def update_category(self, category_id: int, name: str, description: str) -> Optional[Category]:
        """
        Actualiza una categoría existente.

        Args:
            category_id (int): El ID de la categoría a actualizar.
            name (str): El nuevo nombre de la categoría.
            description (str): La nueva descripción de la categoría.

        Returns:
            Optional[Category]: La categoría actualizada o None si no existe.
        """
        category = await self.get_category_by_id(category_id)
        if category:
            category.name = name
            category.description = description
            return await self.category_repo.update(category)
        return None

    async def delete_category(self, category_id: int) -> bool:
        """
        Elimina una categoría por su ID.

        Args:
            category_id (int): El ID de la categoría a eliminar.

        Returns:
            bool: True si la eliminación fue exitosa, False si no existe la categoría.
        """
        return await self.category_repo.delete(category_id)

    async def get_categories_by_product_id(self, product_id: int) -> List[Category]:
        """
        Obtiene todas las categorías asociadas a un producto por su ID.

        Args:
            product_id (int): El ID del producto.

        Returns:
            List[Category]: Lista de categorías asociadas al producto.
        """
        return await self.category_repo.get_by_product_id(product_id)


