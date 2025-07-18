# services/client_service.py
from typing import List, Optional, Dict, Any
# Importamos el modelo Client
from data.models.user_models import Client
# Importamos el repositorio de clientes
from repos.client_repo import ClientRepository


class ClientService:
    """
    Clase de servicio para manejar la lógica de negocio relacionada con los clientes.
    Interactúa con ClientRepository para la persistencia de datos.
    """

    def __init__(self):
        # El servicio depende del repositorio de clientes
        self.client_repo = ClientRepository()

    async def create_new_client(self, first_name: str, last_name: str, email: Optional[str] = None,
                                phone: Optional[str] = None) -> Client:
        """
        Crea un nuevo cliente después de aplicar validaciones de negocio.
        Args:
            first_name, last_name, email, phone: Datos del nuevo cliente.
        Returns:
            La instancia de Client creada.
        Raises:
            ValueError: Si alguna validación de negocio falla.
        """
        # Validaciones de negocio
        if not first_name or not last_name:
            raise ValueError("El nombre y el apellido del cliente son obligatorios.")

        if email:
            # Verificar si el email ya existe para asegurar unicidad
            existing_client = await self.client_repo.get_by_email(email)
            if existing_client:
                raise ValueError(f"Ya existe un cliente con el email '{email}'.")

        # Crear una instancia del modelo Client
        client = Client(
            first_name=first_name,
            last_name=last_name,
            email=email,
            phone=phone
        )

        # Usar el repositorio para persistir el cliente
        return await self.client_repo.create(client)

    async def get_clients_list(self) -> List[Client]:
        """
        Obtiene la lista de todos los clientes.
        Returns:
            Una lista de instancias de Client.
        """
        return await self.client_repo.get_all()

    async def get_client_details(self, client_id: int) -> Optional[Client]:
        """
        Obtiene los detalles de un cliente específico por su ID.
        Args:
            client_id: El ID del cliente.
        Returns:
            La instancia de Client sí se encuentra, de lo contrario None.
        """
        return await self.client_repo.get_by_id(client_id)

    async def update_existing_client(self, client_id: int, new_data: Dict[str, Any]) -> Client:
        """
        Actualiza un cliente existente.
        Args:
            client_id: El ID del cliente a actualizar.
            new_data: Un diccionario con los campos y nuevos valores a actualizar.
        Returns:
            La instancia de Client actualizada.
        Raises:
            ValueError: Si el cliente no se encuentra o si alguna validación falla.
        """
        # Primero, verificar si el cliente existe
        existing_client = await self.client_repo.get_by_id(client_id)
        if not existing_client:
            raise ValueError(f"Cliente con ID {client_id} no encontrado.")

        # Aplicar validaciones de negocio a los datos que se intentan actualizar
        if 'email' in new_data and new_data['email'] != existing_client.email:
            # Si se intenta cambiar el email, verificar unicidad
            client_with_new_email = await self.client_repo.get_by_email(new_data['email'])
            if client_with_new_email and client_with_new_email.id != client_id:
                raise ValueError(f"El email '{new_data['email']}' ya está en uso por otro cliente.")

        # Usar el repositorio para actualizar el cliente
        updated_client = await self.client_repo.update(client_id, new_data)
        if not updated_client:  # Esto no debería ocurrir si ya verificamos la existencia
            raise ValueError(f"No se pudo actualizar el cliente con ID {client_id}.")
        return updated_client

    async def remove_client(self, client_id: int) -> bool:
        """
        Elimina un cliente por su ID.
        Args:
            client_id: El ID del cliente a eliminar.
        Returns:
            True si el cliente fue eliminado, False si no se encontró.
        """
        # Opcional: Podrías añadir lógica de negocio aquí, como verificar
        # si el cliente tiene transacciones asociadas antes de eliminarlo.
        return await self.client_repo.delete(client_id)

    # Métodos de búsqueda (podrían usar el global_search_db o métodos específicos del repo)
    async def search_clients(self, query: str) -> List[Client]:
        """
        Busca clientes por nombre, apellido, o email.
        Args:
            query: La cadena de búsqueda.
        Returns:
            Una lista de instancias de Client que coinciden con la búsqueda.
        """
        # Similar al ProductService, si global_search_db se usa,
        # devolverá un dict con 'products' y 'clients'.
        # Aquí, para mantener la responsabilidad del servicio de clientes,
        # solo devolveremos los clientes.
        from services.search import global_search  # Importar aquí para evitar dependencia circular si es necesario
        search_results = await global_search(self.client_repo.session_provider, query)
        client_dicts = search_results.get("clients", [])
        # Convertir los diccionarios a instancias de Client
        client = [Client.from_dict(c) for c in client_dicts]
        return client  # Devuelve solo la parte de clientes
