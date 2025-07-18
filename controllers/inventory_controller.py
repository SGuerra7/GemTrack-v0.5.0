# controllers/inventory_controller.py
import flet as ft
from typing import List, Dict, Any, Optional
import logging # Importar el módulo logging

# Importamos el servicio de productos
from services.product_service import ProductService
from services.supplier_service import SupplierService

# Importamos el modelo Product (para tipado y quizás para pasar objetos completos)
from data.models.product_models import Product
from data.models.supplier_models import Supplier


# Configurar el logger para este módulo
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class InventoryController:
    """
    Controlador para la gestión del inventario.
    Actúa como intermediario entre la vista de inventario (UI) y el servicio de productos (lógica de negocio).
    """
    def __init__(self, page: ft.Page):
        logging.info("Iniciando constructor de InventoryController.")
        self.page = page

        try:
            self.product_service = ProductService()
            self.supplier_service = SupplierService()
            logging.info("ProductService y SupplierService inicializados en InventoryController.")
        except Exception as e:
            logging.error(f"Error al inicializar servicios en InventoryController: {e}", exc_info=True)
            raise # lanzar la excepción para que la vista pueda manejarla

        self.product_list_view = None # Se asignará cuando la vista lo proporcione
        # ¡CAMBIO IMPORTANTE! Renombrar para mayor claridad
        self.view = None

    # ¡CAMBIO IMPORTANTE! Renombrar para mayor claridad
    def set_view(self, view):
        """Establece una referencia a la vista de inventario para poder actualizarla."""
        logging.info("Referencia a InventoryView establecida en el controlador.")
        self.inventory_view = view

    def set_product_list_view(self, product_list_view_control: ft.Control):
        """
        Permite al controlador tener una referencia al control de la lista de productos en la UI,
        para poder actualizarla.
        """
        logging.info("Referencia a product_list_view establecida en InventoryController.")
        self.product_list_view = product_list_view_control

    async def load_products(self) -> List[Product]:
        """
        Carga todos los productos desde el servicio y los devuelve.
        Este método será llamado por la vista para poblar la lista.
        """
        logging.info("Cargando productos desde el servicio.")
        try:
            products = await self.product_service.get_products_list()
            logging.info(f"Productos cargados exitosamente: {len(products)}.")
            return products
        except Exception as e:
            logging.error(f"Error al cargar productos en InventoryController: {e}", exc_info=True)
            self._show_snackbar(f"Error al cargar productos: {e}", ft.Colors.RED_500)
            return []

    async def add_product_clicked(self, e: ft.ControlEvent, product_data: Dict[str, Any]):
        """
        Maneja la creación de un producto Y la respuesta a la UI.
        """
        logging.info("Evento add_product_clicked recibido.")
        try:
            # Validaciones básicas de entrada (ej. que no estén vacíos campos críticos)
            if not product_data.get("name") or not product_data.get("sku"):
                self._show_snackbar("Nombre y SKU son obligatorios.", ft.Colors.AMBER_500)
                logging.warning("Validación fallida: Nombre o SKU vacíos al agregar producto.")
                return

            # ¡CORRECCIÓN!
            # En lugar de pasar cada argumento por separado, pasamos el diccionario completo.
            # El ProductService ahora es responsable de desempacar y manejar estos datos.
            # Llamar al servicio para crear el producto
            new_product = await self.product_service.create_new_product(product_data)  # Puede ser None si no se proporciona
            # ¡CAMBIO! Ya no mostramos el SnackBar aquí. La vista lo hará.
            self._show_snackbar(f"Producto '{new_product.name}' agregado exitosamente!", ft.Colors.GREEN_500)

            logging.info(f"Producto '{new_product.name}' agregado exitosamente.")

            # Navegar de vuelta a la lista de inventario DESDE el controlador.
            self.page.go("/inventory")

            # ¡CAMBIO CLAVE! Devolvemos el producto creado para que la vista lo use.
            return new_product
        except ValueError as ve:
            # Manejar errores de validación (como SKU duplicado)
            logging.warning(f"Error de validación al agregar producto: {ve}")
            self._show_snackbar(f"Error: {ve}", ft.Colors.RED_500)
            return None
        except Exception as ex:
            # Manejar otros errores inesperados
            logging.error(f"Error inesperado al agregar producto: {ex}", exc_info=True)
            self._show_snackbar(f"Error inesperado: {ex}", ft.Colors.RED_500)
            return None
        finally:
            self.page.update()

    async def update_product_clicked(self, e: ft.ControlEvent, product_id: int, new_data: Dict[str, Any]):
        """
        Maneja el evento de clic del botón "Actualizar Producto".
        Recibe el ID del producto y los datos actualizados del formulario.
        """
        logging.info(f"Evento update_product_clicked recibido para ID: {product_id}.")
        try:
            updated_product = await self.product_service.update_existing_product(product_id, new_data)
            # ¡LÓGICA DE RESPUESTA AHORA AQUÍ!
            logging.info(f"Producto '{updated_product.name}' actualizado. Navegando a /inventory.")
            self._show_snackbar(f"Producto '{updated_product.name}' actualizado exitosamente!", ft.Colors.GREEN_500)

            self.page.go("/inventory")
        except ValueError as ve:
            self._show_snackbar(f"Error de validación: {ve}", ft.Colors.RED_500)
            logging.warning(f"Error de validación al actualizar producto: {ve}")
        except Exception as ex:
            logging.error(f"Error inesperado al actualizar producto: {ex}", exc_info=True)
            self._show_snackbar(f"Error inesperado: {ex}", ft.Colors.RED_500)

        self.page.update()

    async def delete_product_clicked(self, e: ft.ControlEvent, product_id: int):
        """
        Maneja la lógica de eliminación de un producto, incluyendo un diálogo de confirmación.
        """
        logging.info(f"Solicitud para eliminar producto con ID: {product_id}")

        # Función que se ejecutará si el usuario confirma la eliminación.
        async def handle_delete_confirm(e_confirm):
            try:
                # 1. Llamar al servicio para eliminar el producto
                success = await self.product_service.remove_product(product_id)

                if success:
                    self._show_snackbar(f"Producto eliminado exitosamente.")
                    logging.info(f"Producto con ID {product_id} eliminado de la DB.")

                    # 2. Actualizar la vista de inventario para reflejar el cambio
                    if self.view:
                        # Usamos run_task para no bloquear el hilo de la UI
                        self.page.run_task(self.view.load_data)
                else:
                    self._show_snackbar("Error: No se pudo encontrar el producto a eliminar.", ft.Colors.RED)
                    logging.warning(f"No se encontró el producto con ID {product_id} para eliminar.")

            except Exception as ex:
                self._show_snackbar(f"Error crítico al eliminar: {ex}", ft.Colors.RED)
                logging.error(f"Error al eliminar producto {product_id}: {ex}", exc_info=True)

            # Cerrar el diálogo de confirmación
            confirm_dialog.open = False
            self.page.update()

        # Función que se ejecutará si el usuario cancela.
        def handle_delete_cancel(e_cancel):
            confirm_dialog.open = False
            self.page.update()
            logging.info(f"Eliminación del producto {product_id} cancelada por el usuario.")

        # Crear el diálogo de confirmación
        confirm_dialog = ft.AlertDialog(
            modal=True,
            title=ft.Text("Confirmar Eliminación"),
            content=ft.Text("¿Estás seguro de que quieres eliminar este producto? Esta acción no se puede deshacer."),
            actions=[
                ft.TextButton("Cancelar", on_click=handle_delete_cancel),
                ft.FilledButton("Eliminar", on_click=handle_delete_confirm, bgcolor=ft.Colors.RED_700),
            ],
            actions_alignment=ft.MainAxisAlignment.END,
        )

        # Abrir el diálogo
        self.page.dialog = confirm_dialog
        confirm_dialog.open = True
        self.page.update()

    async def search_products_changed(self, e: ft.ControlEvent):
        """
        Maneja el evento de cambio en el campo de búsqueda de productos.
        """
        query = e.control.value
        logging.info(f"Evento search_products_changed recibido. Query: '{query}'.")
        try:
            # El servicio de productos ya filtra por productos, aunque use global_search_db
            found_products = await self.product_service.search_products(query)
            # Actualizar la UI con los resultados de la búsqueda
            if self.product_list_view:
                await self.product_list_view.update_list(found_products) # Asume que la vista tiene este método
                logging.info(f"Lista de productos actualizada con {len(found_products)} resultados de búsqueda.")
            else:
                logging.warning("product_list_view no está asignado en el controlador durante la búsqueda.")
        except Exception as ex:
            self._show_snackbar(f"Error al buscar productos: {ex}", ft.Colors.RED_500)
            logging.error(f"Error al buscar productos: {ex}", exc_info=True)

    async def _refresh_product_list(self):
        """
        Método interno para recargar la lista de productos en la UI.
        """
        logging.info("Refrescando lista de productos.")
        if self.product_list_view:
            products = await self.load_products()
            await self.product_list_view.update_list(products) # Asume que la vista tiene este método
            logging.info("Lista de productos refrescada.")
        else:
            logging.warning("product_list_view no está asignado en el controlador durante el refresco.")

    def _show_snackbar(self, message: str, color: str = ft.Colors.BLUE_500):
        """
        Muestra un SnackBar en la página de Flet.
        """
        logging.info(f"Mostrando SnackBar: '{message}' con color {color}.")
        self.page.snack_bar = ft.SnackBar(
            ft.Text(message, color=ft.Colors.WHITE), # Asegurar que el texto del snackbar sea blanco
            bgcolor=color,
            open=True
        )
        self.page.snack_bar.open = True
        self.page.update()

    async def get_product_details(self, product_id: int) -> Optional[Product]:
        """
        Obtiene los detalles de un producto específico por su ID.
        Args:
            product_id: El ID del producto.
        Returns:
            La instancia de Product si se encuentra, de lo contrario None.
        """
        logging.info(f"Obteniendo detalles del producto con ID: {product_id}.")
        try:
            product = await self.product_service.get_product_by_id(product_id)
            if product:
                logging.info(f"Producto encontrado: {product.name}.")
            else:
                logging.warning(f"Producto con ID {product_id} no encontrado.")
            return product
        except Exception as e:
            logging.error(f"Error al obtener detalles del producto ID {product_id}: {e}", exc_info=True)
            self._show_snackbar(f"Error al obtener detalles del producto: {e}", ft.Colors.RED_500)
            return None

    async def get_all_suppliers(self) -> List[Supplier]:
        """
        Obtiene la lista de todos los proveedores desde el SupplierService.
        Este método es llamado por la vista del formulario para poblar el dropdown.
        """
        logging.info("Controlador obteniendo la lista de proveedores.")
        try:
            return await self.supplier_service.get_all_suppliers()
        except Exception as e:
            logging.error(f"Error al obtener proveedores en InventoryController: {e}", exc_info=True)
            self._show_snackbar(f"Error al cargar proveedores: {e}", ft.Colors.RED_500)
            return []

    # ¡NUEVO!
    async def filter_products(self, filter_type: str):
        """
        Maneja la lógica de filtrado de productos y actualiza la vista.
        """
        logging.info(f"Controlador aplicando filtro: {filter_type}")
        try:
            # La lógica de "scan" es diferente, la manejamos aquí
            if filter_type == "scan":
                self._show_snackbar("Funcionalidad de escaneo pendiente.", ft.Colors.BLUE_GREY)
                return

            filtered_products = await self.product_service.get_products_by_filter(filter_type)
            if self.product_list_view:
                await self.product_list_view.update_list(filtered_products)
        except Exception as e:
            logging.error(f"Error al filtrar productos: {e}", exc_info=True)
            self._show_snackbar(f"Error al aplicar filtro: {e}", ft.Colors.RED_500)

    # ¡NUEVO!
    async def search_products(self, query: str):
        """
        Busca productos según un texto y actualiza la vista.
        Si la consulta está vacía, carga todos los productos.
        """
        logging.info(f"Controlador buscando por: '{query}'")
        try:
            if query:
                results = await self.product_service.search_products(query)
            else:
                # Si la búsqueda está vacía, mostrar todos los productos
                results = await self.product_service.get_products_list()

            if self.product_list_view:
                await self.product_list_view.update_list(results)
        except Exception as e:
            logging.error(f"Error al buscar productos: {e}", exc_info=True)
            self._show_snackbar(f"Error en la búsqueda: {e}", ft.Colors.RED_500)


