# services/user_service.py
from typing import List, Optional
import bcrypt  # Usaremos bcrypt para el manejo de contraseñas

# Importamos el modelo y el repositorio
from data.models.user_models import User
from repos.user_repo import UserRepository


class UserService:
    """
    Servicio para manejar la lógica de negocio relacionada con los usuarios del sistema,
    como la autenticación y la gestión de perfiles.
    """

    def __init__(self):
        self.user_repo = UserRepository()

    async def authenticate_user(self, username: str, password: str) -> Optional[User]:
        """
        Autentíca a un usuario.
        1. Busca al usuario por su nombre de usuario.
        2. Si existe, compara la contraseña proporcionada con el hash almacenado.
        """
        user = await self.user_repo.get_by_username(username)
        if not user:
            return None  # Usuario no encontrado

        # Verificar la contraseña usando bcrypt
        # La contraseña del formulario se codifica a bytes para la comparación
        if bcrypt.checkpw(password.encode('utf-8'), user.password_hash.encode('utf-8')):
            return user  # Contraseña correcta

        return None  # Contraseña incorrecta

    async def get_all_users(self) -> List[User]:
        """
        Obtiene una lista de todos los usuarios.
        """
        return await self.user_repo.get_all()

    # Aquí irían otras funciones como:

    # async def create_user(...)
    # async def change_password(...)
