# --- Funciones de Búsqueda Específicas (ejemplo para búsqueda global) ---

from sqlalchemy.future import select
from typing import List, Dict, Any, Callable
from data.models.product_models import Product
from data.models.user_models import Client# Importar modelos específicos para la búsqueda

# Función de búsqueda global que utiliza un proveedor de sesión para realizar consultas
async def global_search(session_provider: Callable, query: str) -> Dict[str, List[Dict[str, Any]]]:
    """
    Realiza una búsqueda global de productos y clientes usando un proveedor de sesión.
    Args:
        session_provider: Función que retorna una AsyncSession.
        query: La cadena de búsqueda.
    Returns:
        Un diccionario con listas de productos y clientes que coinciden.
    """
    async with session_provider() as session:
        search_query_like = f"%{query}%"

        products_result = await session.execute(
            select(Product).filter(
                (Product.name.like(search_query_like)) |
                (Product.sku.like(search_query_like)) |
                (Product.description.like(search_query_like))
            )
        )
        products = [p.to_dict() for p in products_result.scalars().all()]

        clients_result = await session.execute(
            select(Client).filter(
                (Client.first_name.like(search_query_like)) |
                (Client.last_name.like(search_query_like)) |
                (Client.email.like(search_query_like))
            )
        )
        clients = [c.to_dict() for c in clients_result.scalars().all()]

        return {"products": products, "clients": clients}