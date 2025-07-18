# views/inventory_view.py
from pathlib import Path
import flet as ft
from typing import Optional
import logging
import os
import shutil
# Importamos los componentes y controladores necesarios
from components.inventory_product_card import InventoryProductCard
from controllers.inventory_controller import InventoryController

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Obtiene la ruta absoluta al directorio de assets usando pathlib y os
assets_dir = os.path.join(Path(os.path.dirname(__file__)).parent, "assets") # Asumiendo que estás en views/product_form_view.py

class InventoryView(ft.View):
    """
    Vista unificada para la gestión completa del inventario.
    AHORA se enfoca únicamente en mostrar la lista de productos y la navegación.
    La lógica del formulario ha sido eliminada.
    """

    def __init__(self, page: ft.Page):
        logging.info("Iniciando constructor de InventoryView (refactorizado).")
        super().__init__(
            route="/inventory",
            bgcolor=ft.Colors.BLACK,
            vertical_alignment=ft.MainAxisAlignment.START,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
        )
        self.page = page
        try:
            self.controller = InventoryController(page)
            logging.info("InventoryController inicializado en InventoryView.")
        except Exception as e:
            logging.error(f"Error al inicializar InventoryController: {e}", exc_info=True)
            self.controls.append(ft.Text("Error crítico al cargar el controlador.", color=ft.Colors.RED_500))
            return

        # ¡ELIMINADO! - Toda la definición de los campos del formulario y el AlertDialog
        # self.name_field, self.description_field, self.add_item_dialog, etc., han sido eliminados.
        # Esta vista ya no es responsable de la lógica del formulario.

        # ¡NUEVO! Campo de búsqueda, inicialmente invisible.
        self.search_field = ft.TextField(
            label="Buscar por nombre, SKU...",
            visible=False,
            on_change=self._on_search_change,  # Llama al handler cuando el texto cambia
            bgcolor=ft.Colors.GREY_900,
            border_radius=10,
            text_style=ft.TextStyle(color=ft.Colors.WHITE),
            label_style=ft.TextStyle(color=ft.Colors.GREY_400),
        )

        # ¡NUEVO! - FilePicker para la opción de "Subir desde el Dispositivo"
        self.file_picker = ft.FilePicker(on_result=self._on_file_picker_result)
        self.page.overlay.append(self.file_picker)

        # ¡NUEVO! - Definición del BottomSheet para las opciones de "Add Item"
        self.add_item_bs = ft.BottomSheet(
            ft.Container(
                ft.Column(
                    [
                        ft.Text("Agregar Nuevo Producto", weight=ft.FontWeight.BOLD, size=18, color=ft.Colors.WHITE),
                        ft.ListTile(
                            title=ft.Text("Tomar Foto o Video", color=ft.Colors.WHITE),
                            leading=ft.Icon(ft.Icons.CAMERA_ALT, color=ft.Colors.WHITE),
                            on_click=self._handle_take_photo,  # Placeholder
                        ),
                        ft.ListTile(
                            title=ft.Text("Subir desde el Dispositivo", color=ft.Colors.WHITE),
                            leading=ft.Icon(ft.Icons.UPLOAD_FILE, color=ft.Colors.WHITE),
                            on_click=lambda e: self.file_picker.pick_files(
                                allow_multiple=True,
                                allowed_extensions=["png", "jpg", "jpeg", "mp4"]
                            )
                        ),
                    ],
                    tight=True,
                ),
                padding=20,
            ),
            bgcolor=ft.Colors.BLACK,
        )
        # Añadir el BottomSheet al overlay de la página para que pueda mostrarse
        self.page.overlay.append(self.add_item_bs)

        # ¡CAMBIO CLAVE! Añadimos un ProgressRing para la retroalimentación de carga.
        self.progress_ring = ft.ProgressRing(visible=False)

        # El contenedor de la lista ahora también contiene el anillo de progreso.
        self.products_list_container = ft.Column(
            controls=[self.progress_ring],  # El anillo está aquí para alinearse
            scroll=ft.ScrollMode.ADAPTIVE,
            expand=True,
            spacing=10,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER  # Centrar el anillo
        )
        self.controller.set_view(self)

        self._build_ui()
        logging.info("UI de InventoryView (refactorizada) construida.")


    def _build_ui(self):
        logging.info("Ejecutando _build_ui en InventoryView (refactorizado).")
        self.controls = [
            # Encabezado (se mantiene)
            ft.Container(
                content=ft.Row(
                    [
                        ft.IconButton(icon=ft.Icons.ARROW_BACK, icon_color=ft.Colors.WHITE,
                                      on_click=lambda e: self.page.go("/")),
                        ft.Text("Inventory", color=ft.Colors.WHITE, size=32, weight=ft.FontWeight.BOLD, expand=True),

                        # Botón "+ Add item" (ahora abre el menú)
                        ft.Container(
                            content=ft.ElevatedButton(
                                text="Add item",
                                icon=ft.Icons.ADD,
                                on_click=self._open_add_item_menu,  # ¡CAMBIO!
                                bgcolor=ft.Colors.BLACK,
                                color=ft.Colors.WHITE,
                                height=80,
                                width=135,
                            ),
                            padding=ft.padding.symmetric(horizontal=5, vertical=5),
                        ),
                        ft.IconButton(icon=ft.Icons.SEARCH, icon_color=ft.Colors.WHITE,
                                      on_click=self._handle_search_click),

                    ],
                    vertical_alignment=ft.CrossAxisAlignment.CENTER,
                ),
                padding=ft.padding.only(left=10, right=10, top=40, bottom=5),
            ),

            # Fila de botones de filtro/acción (se mantiene, pero sin la pestaña de conciliación)
            ft.Container(
                content=ft.Row(
                    [
                        ft.ElevatedButton(
                            content=ft.Row([ft.Icon(ft.Icons.DIAMOND), ft.Text("All")]),
                            on_click=lambda e: self._filter_products("all"),
                            style=ft.ButtonStyle(bgcolor=ft.Colors.GREY_900)),
                        ft.ElevatedButton(
                            content=ft.Row([ft.Icon(ft.Icons.WARNING_AMBER), ft.Text("Low stock")]),
                            on_click=lambda e: self._filter_products("low_stock"),
                            style=ft.ButtonStyle(bgcolor=ft.Colors.GREY_900)),
                        ft.ElevatedButton(
                            content=ft.Row([ft.Icon(ft.Icons.LOCATION_ON), ft.Text("Location")]),
                            on_click=lambda e: self._filter_products("location"),
                            style=ft.ButtonStyle(bgcolor=ft.Colors.GREY_900)),
                        ft.ElevatedButton(
                            content=ft.Row([ft.Icon(ft.Icons.QR_CODE_SCANNER), ft.Text("Scan")]),
                            on_click=lambda e: self._filter_products("scan"),
                            style=ft.ButtonStyle(bgcolor=ft.Colors.GREY_900)),
                    ],
                    spacing=15,
                    alignment=ft.MainAxisAlignment.CENTER,
                ),
                padding=ft.padding.symmetric(horizontal=10, vertical=10),
            ),

            # Campo de búsqueda (inicialmente invisible)
            ft.Container(
                self.search_field,
                padding=ft.padding.symmetric(horizontal=20)
            ),

            # Lista de productos (se mantiene)
            ft.Container(
                content=self.products_list_container,
                expand=True,
                padding=ft.padding.symmetric(horizontal=20),
            ),

            # Barra de navegación inferior (igual que en el dashboard)
            ft.Container(
                content=ft.NavigationBar(
                    selected_index=0,
                    bgcolor=ft.Colors.BLACK,
                    destinations=[
                        ft.NavigationBarDestination(icon=ft.Icons.HOME, label="Home"),
                        ft.NavigationBarDestination(icon=ft.Icons.LIST_ALT, label="Orders"),
                        ft.NavigationBarDestination(icon=ft.Icons.SEARCH, label="Search"),
                        ft.NavigationBarDestination(icon=ft.Icons.PERSON, label="Profile"),
                    ],
                ),
                padding=ft.padding.only(bottom=0)
            )
        ]

    # --- ¡NUEVOS MÉTODOS para el flujo de "Add Item"! ---

    def _open_add_item_menu(self, e):
        """Abre el menú de opciones para agregar un nuevo item."""
        self.add_item_bs.open = True
        self.add_item_bs.update()

    def _handle_take_photo(self, e):
        """Manejador para la opción de tomar foto (placeholder)."""
        self.add_item_bs.open = False
        self.add_item_bs.update()
        self.page.snack_bar = ft.SnackBar(ft.Text("Funcionalidad de cámara pendiente."), bgcolor=ft.Colors.BLUE_GREY)
        self.page.snack_bar.open = True
        self.page.update()

    def _copy_and_get_relative_path(self, file_path: str, file_name: str) -> Optional[str]:
        """Copia un archivo a la carpeta de assets/uploads y devuelve la ruta relativa."""
        # Asegúrate de que self.page.assets_dir esté disponible
        if not assets_dir:
            logging.error("El directorio de assets no está configurado en la página.")
            return None
        uploads_dir = os.path.join(assets_dir, "uploads")
        os.makedirs(uploads_dir, exist_ok=True)
        destination_path = os.path.join(uploads_dir, file_name)
        shutil.copy(file_path, destination_path)
        return f"uploads/{file_name}"

    def _on_file_picker_result(self, e: ft.FilePickerResultEvent):
        if e.files:
            # ¡CAMBIO! Copiar el archivo y obtener la ruta relativa aquí
            relative_path = self._copy_and_get_relative_path(e.files[0].path, e.files[0].name)
            if relative_path:
                self.page.client_storage.set("new_product_image_path", relative_path)
                self.page.go("/product/add_new")
            else:
                # Manejar el error si no se pudo copiar
                self.page.snack_bar = ft.SnackBar(ft.Text("Error al procesar la imagen."), bgcolor=ft.Colors.RED)
                self.page.snack_bar.open = True
                self.page.update()
        else:
            logging.info("Selección de archivo cancelada.")

    # --- Métodos existentes que se mantienen o se simplifican ---

    # ¡MÉTODO MODIFICADO Y UNIFICADO!
    async def load_data(self, e=None):
        """
        Implementa el patrón 'Cargar y Luego Mostrar' para una carga de datos robusta.
        """
        logging.info("Ejecutando load_data en InventoryView (con patrón de carga).")

        # --- FASE 1: Mostrar Carga y Mensaje (si existe) ---
        self.products_list_container.controls.clear()
        self.progress_ring.visible = True

        # ¡CAMBIO CLAVE! Forzar la actualización de la UI ANTES de cualquier operación async.
        # Esto muestra el ProgressRing inmediatamente y libera el hilo de la UI.
        self.page.update()

        # --- FASE 2: Cargar Datos (la parte lenta) ---
        product_cards = []
        try:
            products = await self.controller.load_products()
            logging.info(f"Productos cargados: {len(products)}.")

            if products:
                for product in products:
                    product_cards.append(
                        InventoryProductCard(
                            product,
                            on_edit_click=self._on_edit_product_click,
                            on_delete_click=self._on_delete_product_click
                        )
                    )
            else:
                product_cards.append(
                    ft.Text("No hay productos para mostrar.", color=ft.Colors.GREY_400)
                )
        except Exception as ex:
            logging.error(f"Error al construir las tarjetas de producto:  {ex}", exc_info=True)
            product_cards.append(ft.Text("Error al cargar la lista de productos.", color=ft.Colors.RED))

        # --- FASE 3: Mostrar Resultados ---
        self.progress_ring.visible = False
        self.products_list_container.controls = product_cards  # Asignar la lista completa de una vez

        # Actualizar la UI para mostrar la lista final
        self.page.update()
        logging.info("Lista de productos renderizada en la UI.")

    def _on_edit_product_click(self, e, product_id: int):
        """
            Manejador síncrono que navega a la página de edición.
        """
        logging.info(f"Navegando para editar producto ID: {product_id}.")
        self.page.go(f"/product/edit/{product_id}")

    def _on_delete_product_click(self, e, product_id: int):
        """
            Manejador síncrono que le pide a la página que ejecute la
            corutina de eliminación del controlador en segundo plano.
        """
        logging.info(f"Clic en eliminar producto ID: {product_id}.")
        self.page.run_task(self.controller.delete_product_clicked, e, product_id)

    # ¡MODIFICADO!
    def _filter_products(self, filter_type: str):
        """
        Captura el evento de clic en un botón de filtro y lo delega al controlador.
        """
        logging.info(f"Evento de filtro '{filter_type}' capturado en la vista.")
        # Usamos page.run_task para ejecutar la corutina del controlador en segundo plano
        self.page.run_task(self.controller.filter_products, filter_type)
        self.page.update()

    # ¡MODIFICADO!
    def _handle_search_click(self, e):
        """Muestra u oculta el campo de búsqueda."""
        self.search_field.visible = not self.search_field.visible
        if not self.search_field.visible and self.search_field.value:
            # Si se oculta el campo y tenía texto, limpiar la búsqueda
            self.search_field.value = ""
            self.page.run_task(self.controller.search_products, "")
        self.page.update()

    def _handle_bottom_navigation(self, e):
        # ... (lógica de navegación)
        if e.control.selected_index == 0:
            self.page.go("/")
        # ... etc.

    # ¡NUEVO!
    def _on_search_change(self, e):
        """Delega la búsqueda al controlador cada vez que el texto cambia."""
        self.page.run_task(self.controller.search_products, e.control.value)
