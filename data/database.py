# Añadir al final de test_assets_config1.py
import os
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from data.models.base_model import Base


# Configuración de base de datos
DB_NAME = "gemtrack.db"
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATABASE_URL = f"sqlite:///{os.path.join(BASE_DIR, DB_NAME)}"

# Ruta de la base de datos
DB_FILE = os.path.abspath(os.path.join(BASE_DIR, DB_NAME))
DB_URL = f"sqlite+aiosqlite:///{DB_FILE}"

# print(BASE_DIR)

# Engine y sesión asíncrona
async_engine = create_async_engine(DB_URL, echo=False, future=True)
AsyncSessionLocal = async_sessionmaker(
    bind=async_engine,
    expire_on_commit=False,
    autoflush=False,
    autocommit=False,
    class_=AsyncSession
)


# 1. Asegura el directorio de la base de datos
def ensure_assets_dir():
    os.makedirs(os.path.dirname(DB_FILE), exist_ok=True)

# 2. Verifica si el archivo de la base de datos existe
def db_file_exists():
    return os.path.exists(DB_FILE)

# 3. Inicializa la base de datos si no existe el archivo
async def init_db():
    """
    Inicializa la base de datos.
    Crea todas las tablas definidas en los modelos si no existen.
    Debe ser llamada al inicio de la aplicación.
    """
    async with async_engine.begin() as conn:
        # run_sync permite ejecutar operaciones síncronas de SQLAlchemy
        # dentro de un contexto asíncrono. Base.metadata.create_all es síncrono.
        await conn.run_sync(Base.metadata.create_all)
    print("Base de datos inicializada y tablas creadas (si no existían).")

# 4. Notifica el estado de la base de datos
def notify_db_status(exists):
    if exists:
        print(f"La base de datos '{DB_FILE}' ya existe y está lista para usarse.")
    else:
        print(f"Se ha creado la base de datos '{DB_FILE}' y sus tablas.")

# 5. Verifica si el archivo de la base de datos es accesible
def check_db_file():
    """Verifica si el archivo de la base de datos existe y es accesible."""
    if not os.path.exists(DB_FILE):
        raise FileNotFoundError(f"El archivo de la base de datos '{DB_FILE}' no existe.")
    if not os.access(DB_FILE, os.R_OK | os.W_OK):
        raise PermissionError(f"No se tienen permisos para acceder al archivo '{DB_FILE}'.")
    else:
        print(f"El archivo de la base de datos '{DB_FILE}' está accesible.")

# 6. Función para obtener la sesión de la base de datos
async def get_db_session():
    """
        Proporciona una sesión de base de datos asíncrona.
        Este es un generador asíncrono que se puede usar con 'async with' o 'yield'.
    """
    async with AsyncSessionLocal() as session:
        yield session

# 7. Lógica de inicialización
def setup_database():
    ensure_assets_dir()
    exists = db_file_exists()
    if not exists:
        init_db()
    notify_db_status(exists)
    check_db_file()


# Llama a setup_database() al inicio de tu aplicación

"""scoped_session se utiliza para gestionar sesiones de base de datos de manera segura en aplicaciones 
multihilo o multiproceso. Proporciona una sesión única por hilo o contexto, evitando conflictos y asegurando
 que cada hilo/proceso trabaje con su propia sesión independiente. Esto es útil en aplicaciones web 
 o servicios concurrentes donde varias solicitudes pueden acceder a la base de datos al mismo tiempo.

 sync_SessionLocal = scoped_session(sessionmaker(autocommit=False, autoflush=False, bind=sync_engine))
 """


