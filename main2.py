# main.py
import re

import flet as ft
import os
import logging # Importar el módulo logging

from views.product_form_view import ProductFormView
# Importar las vistas
from views.dashboard_view4 import DashboardView # Asegúrate de que esta es la ruta correcta
from views.inventory_view2 import InventoryView
from views.product_add_view import ProductAddView
# Importar la función de inicialización de la base de datos
from data.database import init_db

# Configurar el logger básico
# Puedes ajustar el nivel (DEBUG, INFO, WARNING, ERROR, CRITICAL)
# y el formato según tus necesidades.
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Obtiene la ruta absoluta al directorio de assets
assets_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "assets"))

logging.info(f"Directorio de assets configurado: {assets_dir}")
print(os.path.dirname(__file__))



async def main(page: ft.Page):
    logging.info("Iniciando función main de Flet.")
    # Configuración inicial de la página
    page.title = "GemTrack"
    page.vertical_alignment = ft.CrossAxisAlignment.START
    page.horizontal_alignment = ft.CrossAxisAlignment.CENTER
    page.bgcolor = ft.Colors.BLACK  # Fondo global de la aplicación
    page.window_min_width = 400  # Ancho inicial para simular un móvil
    page.window_min_height = 800  # Alto inicial para simular un móvil
    page.window_resizable = True  # Permitir redimensionar la ventana

    # Inicializar la base de datos al inicio de la aplicación
    try:
        await init_db()
        logging.info("Base de datos inicializada correctamente.")
    except Exception as e:
        logging.error(f"Error crítico al inicializar la base de datos: {e}", exc_info=True)
        # Aquí podrías añadir una UI de error o salir de la aplicación
        page.add(ft.Text(f"Error al iniciar la aplicación: {e}", color=ft.Colors.RED_500))
        page.update()
        return # Detener la ejecución si la DB no se inicializa


    # Función para actualizar la vista al cambiar el tamaño
    def on_resize(e):
        logging.debug(f"Evento de redimensionamiento detectado. Nuevo tamaño: {page.width}x{page.height}")
        try:
            # Reconstruir la vista actual para que se adapte al nuevo tamaño
            # Esta lógica es la que tenías y la mantenemos.
            if page.views and hasattr(page.views[-1], "build_ui"):
                logging.debug(f"Llamando a build_ui en la vista actual: {page.views[-1].route}")
                page.views[-1].build_ui()
            page.update()
            logging.debug("Página actualizada después de redimensionamiento.")
        except Exception as ex:
            logging.error(f"Error al redimensionar la vista: {ex}", exc_info=True)

    page.on_resize = on_resize
    logging.info("Manejador on_resize configurado.")


    # Función para manejar los cambios de ruta
    def route_change(route):
        logging.info(f"Cambio de ruta detectado. Nueva ruta: {page.route}")
        page.views.clear()
        try:
            # Ruta para el formulario de edición (ej. /product/edit/123)
            edit_match = re.match(r"/product/edit/(\d+)", page.route)

            if page.route == "/":
                logging.info("Añadiendo DashboardView a las vistas.")
                page.views.append(DashboardView(page))
            elif page.route == "/inventory":
                logging.info("Añadiendo InventoryView a las vistas.")
                # 1. Crear la instancia de la vista
                inventory_view = InventoryView(page)
                page.views.append(inventory_view)
                # 2. ¡CAMBIO CLAVE! Llamar explícitamente a la carga de datos
                # Usamos page.run_task para ejecutar la corutina sin bloquear la UI
                logging.info("Llamando explícitamente a load_data para InventoryView.")
                page.run_task(inventory_view.load_data)
            elif page.route == "/product/add":  # Ruta para agregar un nuevo producto
                # Esta ruta ahora es manejada por el flujo del BottomSheet,
                # pero la mantenemos por si la necesitamos.
                # Podemos redirigir o manejarla de forma diferente.
                logging.info("Ruta /product/add alcanzada, esperando flujo de imagen.")
                page.views.append(ProductFormView(page))
            elif page.route == "/product/add_new":  # ¡NUEVA RUTA!
                logging.info("Añadiendo ProductAddView a las vistas.")
                page.views.append(ProductAddView(page))
            elif edit_match:  # Si la ruta coincide con el patrón de edición
                product_id = int(edit_match.group(1))
                logging.info(f"Añadiendo ProductFormView para editar producto ID: {product_id}")
                page.views.append(ProductFormView(page, product_id=product_id))
            else:
                logging.warning(f"Ruta no reconocida: {page.route}. Volviendo a la raíz.")
                page.views.append(DashboardView(page))  # Fallback a Dashboard

            # Después de cambiar la ruta, forzar una actualización de la vista
            # para que se adapte al tamaño actual de la ventana.
            # Esta lógica es la que tenías y la mantenemos.
            if page.views and hasattr(page.views[-1], "build_ui"):
                logging.debug(f"Llamando a build_ui en la nueva vista: {page.views[-1].route}")
                page.views[-1].build_ui()
            page.update()
            logging.info(f"Página actualizada para la ruta: {page.route}")
        except Exception as ex:
            logging.error(f"Error crítico en route_change para ruta {page.route}: {ex}", exc_info=True)
            # Aquí podrías añadir una UI de error o un mensaje más visible
            page.views.clear()
            page.views.append(ft.View(
                "/error",
                [ft.Text(f"Ocurrió un error al navegar: {ex}", color=ft.Colors.RED_500)],
                bgcolor=ft.Colors.BLACK
            ))

    page.on_route_change = route_change
    logging.info("Manejador on_route_change configurado.")

    # Ir a la ruta inicial
    logging.info(f"Navegando a la ruta inicial: {page.route}")
    page.go(page.route)


# Ejecutar la aplicación Flet
logging.info("Iniciando aplicación Flet.")
ft.app(target=main, assets_dir=assets_dir)
logging.info("Aplicación Flet finalizada.")

