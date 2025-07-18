from typing import List, Optional, Dict, Any
from sqlalchemy.future import select
from sqlalchemy import and_
# Importamos el modelo Client
from data.models.user_models import Client
# Importamos el proveedor de sesiones de la base de datos
from data.database import AsyncSessionLocal
# Importamos las funciones CRUD genéricas
from data.crud_operations import create_record, get_record_by_id, get_all_records, update_record, delete_record

class ClientRepository:
    """
    Clase de repositorio para manejar las operaciones de persistencia relacionadas con el modelo Client.
    Encapsula la lógica de acceso a datos para los clientes.
    """
    def __init__(self):
        # El repositorio "conoce" cómo obtener una sesión asíncrona.
        # AsyncSessionLocal es la fábrica de sesiones que se pasará a las funciones CRUD.
        self.session_provider = AsyncSessionLocal

    async def create(self, client: Client) -> Client:
        """
        Crea un nuevo cliente en la base de datos.
        Args:
            client: Una instancia de Client a ser creada.
        Returns:
            La instancia de Client creada con su ID asignado.
        """
        return await create_record(self.session_provider, client)

    async def get_by_id(self, client_id: int) -> Optional[Client]:
        """
        Obtiene un cliente por su ID.
        Args:
            client_id: El ID del cliente a buscar.
        Returns:
            La instancia de Client si se encuentra, de lo contrario None.
        """
        return await get_record_by_id(self.session_provider, Client, client_id)

    async def get_all(self) -> List[Client]:
        """
        Obtiene todos los clientes de la base de datos.
        Returns:
            Una lista de instancias de Client.
        """
        return await get_all_records(self.session_provider, Client)

    async def update(self, client_id: int, new_data: Dict[str, Any]) -> Optional[Client]:
        """
        Actualiza un cliente existente por su ID.
        Args:
            client_id: El ID del cliente a actualizar.
            new_data: Un diccionario con los campos y nuevos valores a actualizar.
        Returns:
            La instancia de Client actualizada si se encuentra, de lo contrario None.
        """
        return await update_record(self.session_provider, Client, client_id, new_data)

    async def delete(self, client_id: int) -> bool:
        """
        Elimina un cliente por su ID.
        Args:
            client_id: El ID del cliente a eliminar.
        Returns:
            True si el cliente fue eliminado, False si no se encontró.
        """
        return await delete_record(self.session_provider, Client, client_id)

    # Aquí se pueden añadir métodos de consulta más específicos si son necesarios,
    # que no encajen en las operaciones CRUD genéricas.
    # Por ejemplo, buscar por email, por nombre, etc.
    async def get_by_email(self, email: str) -> Optional[Client]:
        """
        Obtiene un cliente por su dirección de correo electrónico.
        Args:
            email: La dirección de correo electrónico del cliente a buscar.
        Returns:
            La instancia de Client si se encuentra, de lo contrario None.
        """
        async with self.session_provider() as session:
            result = await session.execute(
                select(Client).filter(and_(Client.email == email))
            )
            return result.scalars().first()
