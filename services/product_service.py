# services/product_service.py
from datetime import datetime
from typing import List, Optional, Dict, Any

# Importamos el modelo Product
from data.models.product_models import Product
# Importamos el repositorio de productos
from repos.product_repo import ProductRepository
from repos.category_repo import CategoryRepository # ¡NUEVO! Dependencia necesaria
from price_parser import parse_price # Importaremos la utilidad de precios


class ProductService:
    """
    Clase de servicio para manejar la lógica de negocio relacionada con los productos.
    Interactúa con ProductRepository para la persistencia de datos.
    """

    def __init__(self):
        # El servicio depende del repositorio de productos
        self.product_repo = ProductRepository()
        self.category_repo = CategoryRepository()  # ¡NUEVO!

    async def create_new_product(self, product_data: Dict[str, Any]) -> Product:
        """
        Crea un nuevo producto a partir de un diccionario de datos.
        Esta firma es más limpia y escalable.
        """
        # --- 1. Validación de Reglas de Negocio ---
        sku = product_data.get("sku")
        if not product_data.get("name") or not sku:
            raise ValueError("El nombre y el SKU del producto son obligatorios.")

        # Validar precios y stock (asumiendo que ya son float/int desde el controlador)
        if product_data.get("suggested_price", 0.0) < 0:
            raise ValueError("El precio sugerido no puede ser negativo.")
        if product_data.get("buying_price", 0.0) < 0:
            raise ValueError("El precio de compra no puede ser negativo.")
        if product_data.get("stock", 0) < 0:
            raise ValueError("El stock no puede ser negativo.")

        # Verificar si el SKU ya existe para asegurar unicidad
        existing_product = await self.product_repo.get_by_sku(sku)
        if existing_product:
            raise ValueError(f"Ya existe un producto con el SKU '{sku}'.")


        # --- 2. Manejo de Relaciones (Muchos a Muchos con Category) ---
        # Extraemos los IDs de las categorías del diccionario. No se guardan directamente en Product.
        category_ids = product_data.pop('category_ids', [])

        # --- 3. Creación de la Instancia del Modelo ---
        # Usamos el método de clase `from_dict` que ya tienes en tu modelo Product.
        # Esto crea una instancia de Product solo con los campos que coinciden,
        # ignorando 'category_ids' que ya hemos extraído.
        product = Product.from_dict(product_data)

        # --- 4. Asignación de las Relaciones ---

        # Si se proporcionaron IDs de categorías, buscamos los objetos y los asignamos.
        if category_ids:
            # Asegurarse de que sea una lista (si el dropdown no es multiselección)
            if not isinstance(category_ids, list):
                category_ids = [category_ids]

            # Usamos el CategoryRepository para obtener las instancias de Category
            categories = await self.category_repo.get_by_ids(category_ids)
            product.categories = categories  # SQLAlchemy manejará la tabla de asociación


        # Usar el repositorio para persistir el producto
        return await self.product_repo.create(product)

    async def get_products_list(self) -> List[Product]:
        """
        Obtiene la lista de todos los productos.
        Returns:
            Una lista de instancias de Product.
        """
        return await self.product_repo.get_all()

    async def get_product_details(self, product_id: int) -> Optional[Product]:
        """
        Obtiene los detalles de un producto específico por su ID.
        Args:
            product_id: El ID del producto.
        Returns:
            La instancia de Product si se encuentra, de lo contrario None.
        """
        return await self.product_repo.get_by_id(product_id)

    async def update_existing_product(self, product_id: int, new_data: Dict[str, Any]) -> Product:
        """
        Actualiza un producto existente.
        Args:
            product_id: El ID del producto a actualizar.
            new_data: Un diccionario con los campos y nuevos valores a actualizar.
        Returns:
            La instancia de Product actualizada.
        Raises:
            ValueError: Si el producto no se encuentra o si alguna validación falla.
        """
        # Primero, verificar si el producto existe
        existing_product = await self.product_repo.get_by_id(product_id)
        if not existing_product:
            raise ValueError(f"Producto con ID {product_id} no encontrado.")

        # Aplicar validaciones de negocio a los datos que se intentan actualizar
        if 'suggested_price' in new_data and new_data['suggested_price'] < 0:
            raise ValueError("El precio sugerido no puede ser negativo.")
        if 'stock' in new_data and new_data['stock'] < 0:
            raise ValueError("El stock no puede ser negativo.")
        if 'sku' in new_data and new_data['sku'] != existing_product.sku:
            # Si se intenta cambiar el SKU, verificar unicidad
            product_with_new_sku = await self.product_repo.get_by_sku(new_data['sku'])
            if product_with_new_sku and product_with_new_sku.id != product_id:
                raise ValueError(f"El SKU '{new_data['sku']}' ya está en uso por otro producto.")

        # Usar el repositorio para actualizar el producto
        updated_product = await self.product_repo.update(product_id, new_data)
        if not updated_product:  # Esto no debería ocurrir si ya verificamos la existencia
            raise ValueError(f"No se pudo actualizar el producto con ID {product_id}.")
        return updated_product

    async def remove_product(self, product_id: int) -> bool:
        """
        Elimina un producto por su ID.
        Args:
            product_id: El ID del producto a eliminar.
        Returns:
            True si el producto fue eliminado, False si no se encontró.
        """
        # Opcional: Podrías añadir lógica de negocio aquí, como verificar
        # si el producto está asociado a alguna venta activa antes de eliminarlo.
        return await self.product_repo.delete(product_id)

    # Métodos de búsqueda (podrían usar el global_search_db o métodos específicos del repo)
    async def search_products(self, query: str) -> List[Product]:
        """
        Busca productos por nombre, descripción o SKU.
        Args:
            query: La cadena de búsqueda.
        Returns:
            Una lista de instancias de Product que coinciden con la búsqueda.
        """
        # Para una búsqueda más compleja, podríamos usar el global_search_db
        # o implementar un método de búsqueda específico en ProductRepository.
        # Por simplicidad, aquí asumimos que el repositorio puede manejarlo.
        # Si global_search_db se usa, devolverá un dict con 'products' y 'clients'.
        # Aquí, para mantener la responsabilidad del servicio de productos,
        # solo devolveremos los productos.

        # Opción 1: Si ProductRepository tuviera un método search_by_text
        # return await self.product_repo.search_by_text(query)

        # Opción 2: Usando global_search_db y filtrando solo productos
        from services.search import global_search  # Importar aquí para evitar dependencia circular si es necesario
        search_results = await global_search(self.product_repo.session_provider, query)
        product_dicts = search_results.get("products", [])

        # Convertir cada dict a Product
        products = [Product.from_dict(prod) for prod in product_dicts]

        # global_search devuelve diccionarios, convertirlos a objetos Product si es necesario
        # Esto requeriría un método Product.from_dict() o similar, o simplemente devolver los dicts.
        # Por ahora, asumimos que los resultados de global_search son suficientes.
        return products # Devuelve solo la parte de productos

    async def get_product_by_id(self, product_id: int) -> Optional[Product]:
        """
        Obtiene un producto por su ID.
        Args:
            product_id: El ID del producto a buscar.
        Returns:
            La instancia de Product si se encuentra, de lo contrario None.
        """
        return await self.product_repo.get_by_id(product_id)

    # ¡NUEVO!
    async def get_products_by_filter(self, filter_type: str) -> List[Product]:
        """
        Obtiene productos según un filtro, aplicando lógica de negocio si es necesario.
        """
        if filter_type not in ["all", "low_stock", "location", "scan"]:
            raise ValueError("Tipo de filtro no válido.")

        if filter_type == "all":
            return await self.product_repo.get_all()
        else:
            return await self.product_repo.get_filtered(filter_type)