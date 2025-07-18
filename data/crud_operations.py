from sqlalchemy.future import select
from typing import Type, TypeVar, List, Dict, Any, Optional
from sqlalchemy import and_

# Importamos la Base declarativa de nuestros modelos
from data.database import Base


# Define el tipo genérico para los modelos de SQLAlchemy
ModelType = TypeVar("ModelType", bound=Base)

# Esta función get_session_context será proporcionada por database.py
# para que las operaciones CRUD puedan obtener una sesión.
# La definimos aquí solo para fines de tipado y claridad.
# En la práctica, se inyectará o se pasará una función que la provea.
# Para este archivo, asumiremos que se le pasará una función que devuelva AsyncSessionLocal
SessionProvider = TypeVar("SessionProvider")


async def create_record(session_provider: SessionProvider, model: ModelType) -> ModelType:
    """
    Crea un nuevo registro en la base de datos.
    Args:
        session_provider: Una función o contexto que proporciona una AsyncSession.
        model: Una instancia del modelo de SQLAlchemy a ser creada.
    Returns:
        La instancia del modelo con su ID asignado después de la creación.
    """
    async with session_provider() as session: # Usamos el proveedor de sesión
        session.add(model)
        await session.commit()
        await session.refresh(model)
        return model

async def get_record_by_id(session_provider: SessionProvider, model_type: Type[ModelType], record_id: Any) -> Optional[ModelType]:
    """
    Obtiene un registro por su ID.
    Args:
        session_provider: Una función o contexto que proporciona una AsyncSession.
        model_type: La clase del modelo (ej. Product, Client).
        record_id: El ID del registro a buscar.
    Returns:
        La instancia del modelo si se encuentra, de lo contrario None.
    """
    async with session_provider() as session:
        result = await session.execute(
            select(model_type).filter(and_(model_type.id == record_id))
        )
        return result.scalars().first()

async def get_all_records(session_provider: SessionProvider, model_type: Type[ModelType]) -> List[ModelType]:
    """
    Obtiene todos los registros de un tipo de modelo.
    Args:
        session_provider: Una función o contexto que proporciona una AsyncSession.
        model_type: La clase del modelo (ej. Product, Client).
    Returns:
        Una lista de instancias del modelo.
    """
    async with session_provider() as session:
        result = await session.execute(select(model_type))
        return result.scalars().all()

async def update_record(session_provider: SessionProvider, model_type: Type[ModelType], record_id: Any, new_data: Dict[str, Any]) -> Optional[ModelType]:
    """
    Actualiza un registro existente por su ID.
    Args:
        session_provider: Una función o contexto que proporciona una AsyncSession.
        model_type: La clase del modelo.
        record_id: El ID del registro a actualizar.
        new_data: Un diccionario con los campos y nuevos valores a actualizar.
    Returns:
        La instancia del modelo actualizada si se encuentra, de lo contrario None.
    """
    async with session_provider() as session:
        # Aquí necesitamos obtener el registro dentro de la misma sesión
        record = await session.execute(
            select(model_type).filter(and_(model_type.id == record_id))
        )
        record = record.scalars().first()

        if record:
            for key, value in new_data.items():
                if hasattr(record, key):
                    setattr(record, key, value)
            await session.commit()
            await session.refresh(record)
            return record
        return None

async def delete_record(session_provider: SessionProvider, model_type: Type[ModelType], record_id: Any) -> bool:
    """
    Elimina un registro por su ID.
    Args:
        session_provider: Una función o contexto que proporciona una AsyncSession.
        model_type: La clase del modelo.
        record_id: El ID del registro a eliminar.
    Returns:
        True si el registro fue eliminado, False si no se encontró.
    """
    async with session_provider() as session:
        # Obtener el registro dentro de la misma sesión para eliminarlo
        record = await session.execute(
            select(model_type).filter(and_(model_type.id == record_id))
        )
        record = record.scalars().first()

        if record:
            await session.delete(record)
            await session.commit()
            return True
        return False

