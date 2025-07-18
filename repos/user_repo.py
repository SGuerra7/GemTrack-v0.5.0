# repos/user_repo.py
from typing import List, Optional
from sqlalchemy.future import select
from sqlalchemy import and_

# Importamos los modelos y la configuración de la base de datos
from data.models.user_models import User, UserRole
from data.database import AsyncSessionLocal
from data.crud_operations import get_all_records

class UserRepository:
    """
    Repositorio para manejar las operaciones de persistencia de datos para los usuarios.
    """
    def __init__(self):
        self.session_provider = AsyncSessionLocal

    async def get_all(self) -> List[User]:
        """
        Obtiene todos los usuarios.
        """
        return await get_all_records(self.session_provider, User)

    async def get_by_username(self, username: str) -> Optional[User]:
        """
        Obtiene un usuario por su nombre de usuario (esencial para el login).
        """
        async with self.session_provider() as session:
            result = await session.execute(
                select(User).filter(and_(User.username == username))
            )
            return result.scalars().first()

    async def get_by_id(self, user_id: int) -> Optional[User]:
        """
        Obtiene un usuario por su ID.
        """
        async with self.session_provider() as session:
            return await session.get(User, user_id)

