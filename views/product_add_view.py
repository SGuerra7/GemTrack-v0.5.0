# views/product_add_view.py
import flet as ft
from typing import Optional
import logging
import os
import shutil
from pathlib import Path
from controllers.inventory_controller import InventoryController
# ¡CAMBIO! Importamos los servicios directamente para desacoplar la vista del controlador
# La vista solo necesita los datos, no toda la lógica del controlador.
from services.supplier_service import SupplierService
from services.category_service import CategoryService

# --- Definición de Colores y Estilos para mantener consistencia ---
APP_BG_COLOR = "#000000"
PRIMARY_TEXT_COLOR = "#E0E0E0"
SECONDARY_TEXT_COLOR = "#A0A0A0"
FIELD_BG_COLOR = "#1C1C1C"
ACCENT_COLOR = "#2F80ED"
BORDER_COLOR_FOCUSED = "#2F80ED"

# Obtiene la ruta absoluta al directorio de assets usando pathlib y os
assets_dir = os.path.join(Path(os.path.dirname(__file__)).parent, "assets") # Asumiendo que estás en views/product_form_view.py

class ProductAddView(ft.View):
    """
    Vista de formulario rediseñada para agregar un nuevo producto,
    con una estética premium y layout responsivo.
    """

    def __init__(self, page: ft.Page, product_id: Optional[int] = None):
        logging.info(f"Iniciando constructor de ProductAddView. product_id: {product_id}")
        super().__init__(
            route="/product/add_new",
            bgcolor=APP_BG_COLOR,
            padding=0,
            scroll=ft.ScrollMode.ADAPTIVE
        )
        self.page = page
        self.product_id_to_edit = product_id

        # --- Inicialización de Servicios y Controlador ---
        try:
            self.supplier_service = SupplierService()
            self.category_service = CategoryService()
            self.controller = InventoryController(page)
            logging.info("Servicios y controlador inicializados correctamente.")
        except Exception as e:
            logging.error(f"Error al inicializar servicios/controlador: {e}", exc_info=True)
            # Mostrar error en la UI si falla la inicialización
            self.controls.append(ft.Text("Error crítico al inicializar la vista.", color=ft.Colors.RED))
            return

        # --- Lógica de Imágenes ---
        self.image_paths = []  # Lista para guardar las rutas de todas las imágenes
        self.main_image_index = 0  # ¡NUEVO! Para rastrear qué imagen se muestra en grande.

        # ¡CORRECCIÓN! Recoger la ruta de la imagen del almacenamiento del cliente
        # Esta ruta ya debería ser la ruta relativa copiada a 'assets/uploads'
        initial_image_path = self.page.client_storage.get("new_product_image_path")
        if initial_image_path:
            self.image_paths.append(initial_image_path)
            self.page.client_storage.remove("new_product_image_path")

        self.main_image_preview = ft.Image(
            # ¡CORRECCIÓN! Usar la ruta inicial si existe, si no, el placeholder
            src=self.image_paths[0] if self.image_paths else "assets/images/placeholder.png",
            border_radius=ft.border_radius.all(10),
            fit=ft.ImageFit.CONTAIN,
        )
        self.thumbnails_row = ft.Row(scroll=ft.ScrollMode.ADAPTIVE)

        # FilePicker para agregar nuevas imágenes
        self.add_image_picker = ft.FilePicker(on_result=self._on_add_image_result)
        self.page.overlay.append(self.add_image_picker)

        # FilePicker para reemplazar la imagen principal
        self.replace_image_picker = ft.FilePicker(on_result=self._on_replace_image_result)
        self.page.overlay.append(self.replace_image_picker)
        logging.info("FilePickers añadidos al overlay de la página.")

        # --- Controles del Formulario ---
        self.sku_field = ft.TextField(label="SKU*", border_color=ft.Colors.GREY_700, bgcolor=FIELD_BG_COLOR,
                                      text_style=ft.TextStyle(color=PRIMARY_TEXT_COLOR),
                                      label_style=ft.TextStyle(color=SECONDARY_TEXT_COLOR),
                                      focused_border_color=BORDER_COLOR_FOCUSED,
                                      suffix=ft.IconButton(icon=ft.Icons.QR_CODE_SCANNER, icon_color=ft.Colors.WHITE))

        self.title_field = ft.TextField(label="Nombre/Título del producto*", border_color=ft.Colors.GREY_700,
                                        bgcolor=FIELD_BG_COLOR, text_style=ft.TextStyle(color=PRIMARY_TEXT_COLOR),
                                        label_style=ft.TextStyle(color=SECONDARY_TEXT_COLOR),
                                        focused_border_color=BORDER_COLOR_FOCUSED)

        self.description_field = ft.TextField(label="Descripción", multiline=True, min_lines=3, max_length=300,
                                              counter_style=ft.TextStyle(color=SECONDARY_TEXT_COLOR),
                                              border_color=ft.Colors.GREY_700, bgcolor=FIELD_BG_COLOR,
                                              text_style=ft.TextStyle(color=PRIMARY_TEXT_COLOR),
                                              label_style=ft.TextStyle(color=SECONDARY_TEXT_COLOR),
                                              focused_border_color=BORDER_COLOR_FOCUSED)

        self.price_field = ft.TextField(label="Precio de compra", prefix_text="$", keyboard_type=ft.KeyboardType.NUMBER,
                                        border_color=ft.Colors.GREY_700, bgcolor=FIELD_BG_COLOR,
                                        text_style=ft.TextStyle(color=PRIMARY_TEXT_COLOR),
                                        label_style=ft.TextStyle(color=SECONDARY_TEXT_COLOR),
                                        focused_border_color=BORDER_COLOR_FOCUSED)

        self.suggested_price_field = ft.TextField(label="Precio sugerido", prefix_text="$",
                                                  keyboard_type=ft.KeyboardType.NUMBER, border_color=ft.Colors.GREY_700,
                                                  bgcolor=FIELD_BG_COLOR,
                                                  text_style=ft.TextStyle(color=PRIMARY_TEXT_COLOR),
                                                  label_style=ft.TextStyle(color=SECONDARY_TEXT_COLOR),
                                                  focused_border_color=BORDER_COLOR_FOCUSED)

        self.stock_field = ft.TextField(label="Stock", keyboard_type=ft.KeyboardType.NUMBER,
                                        border_color=ft.Colors.GREY_700, bgcolor=FIELD_BG_COLOR,
                                        text_style=ft.TextStyle(color=PRIMARY_TEXT_COLOR),
                                        label_style=ft.TextStyle(color=SECONDARY_TEXT_COLOR),
                                        focused_border_color=BORDER_COLOR_FOCUSED)

        self.location_field = ft.TextField(label="Ubicación", border_color=ft.Colors.GREY_700, bgcolor=FIELD_BG_COLOR,
                                           text_style=ft.TextStyle(color=PRIMARY_TEXT_COLOR),
                                           label_style=ft.TextStyle(color=SECONDARY_TEXT_COLOR),
                                           focused_border_color=BORDER_COLOR_FOCUSED)

        self.availability_group = ft.RadioGroup(
            content=ft.Row([ft.Radio(value="en_stock", label="En Stock"), ft.Radio(value="agotado", label="Agotado"),
                            ft.Radio(value="low_stock", label="Bajo Stock")]), value="en_stock")

        self.category_dropdown = ft.Dropdown(label="Categorías", border_color=ft.Colors.GREY_700,
                                             bgcolor=FIELD_BG_COLOR, text_style=ft.TextStyle(color=PRIMARY_TEXT_COLOR),
                                             label_style=ft.TextStyle(color=SECONDARY_TEXT_COLOR),
                                             focused_border_color=BORDER_COLOR_FOCUSED, width=200,)

        self.supplier_dropdown = ft.Dropdown(label="Proveedor", border_color=ft.Colors.GREY_700, bgcolor=FIELD_BG_COLOR,
                                             text_style=ft.TextStyle(color=PRIMARY_TEXT_COLOR),
                                             label_style=ft.TextStyle(color=SECONDARY_TEXT_COLOR),
                                             focused_border_color=BORDER_COLOR_FOCUSED, width=200,)


        self.unit_dropdown = ft.Dropdown(label="Unidad de medida",
                                         options=[ft.dropdown.Option("unidades"), ft.dropdown.Option("gramos")],
                                         border_color=ft.Colors.GREY_700, bgcolor=FIELD_BG_COLOR,
                                         text_style=ft.TextStyle(color=PRIMARY_TEXT_COLOR),
                                         label_style=ft.TextStyle(color=SECONDARY_TEXT_COLOR),
                                         focused_border_color=BORDER_COLOR_FOCUSED, width=200,)


        self.creation_date_text = ft.Text(value="Se asigna al crear", color=SECONDARY_TEXT_COLOR, italic=True)
        self.modification_date_text = ft.Text(value="Se asigna al editar", color=SECONDARY_TEXT_COLOR, italic=True)

        self._build_ui()

        # ¡CAMBIO! La lógica de carga de datos ahora se divide en dos.
        # on_mount se usará para las operaciones de red (async).
        self.on_mount = self._load_async_data

        # ¡CORRECCIÓN! La actualización inicial de la UI se hace aquí,
        # después de que _build_ui ha asignado los controles.
        # Esto es síncrono y prepara la vista antes de las llamadas de red.
        self._update_image_previews()

        logging.info("Constructor de ProductAddView finalizado.")

    def _build_ui(self):
        logging.info("Construyendo la UI de ProductAddView.")
        # --- Encabezado ---
        self.appbar = ft.AppBar(
            leading=ft.TextButton(
                "Cancelar",
                on_click=lambda e: self.page.go("/inventory"),
                style=ft.ButtonStyle(color=PRIMARY_TEXT_COLOR)),
            leading_width=100, title=ft.Text(""),
            center_title=False,
            bgcolor=APP_BG_COLOR,
            elevation=0
        )

        # --- Sección de Imagen ---
        image_section = ft.Container(
            content=ft.Stack([
                ft.Container(
                    self.main_image_preview,
                    bgcolor="#111111",
                    alignment=ft.alignment.center,
                    border_radius=10, expand=True),
                ft.Container(
                    ft.IconButton(
                    icon=ft.Icons.EDIT,
                        icon_color=ft.Colors.WHITE,
                        bgcolor=ACCENT_COLOR,
                        on_click=lambda _: self.replace_image_picker.pick_files(
                            allow_multiple=False,
                            allowed_extensions=["png", "jpg","jpeg"])),
                    alignment=ft.alignment.top_right, padding=10),
            ]), height=self.page.height * 0.3 if self.page.height else 350,
        )

        # --- Botón para agregar más imágenes ---
        add_image_button = ft.Container(
            content=ft.Icon(
                ft.Icons.ADD,
                color=ft.Colors.WHITE),
            width=50, height=50,
            padding=20,
            bgcolor=APP_BG_COLOR,
            border_radius=10,
            on_click=lambda _: self.add_image_picker.pick_files(
                allow_multiple=True,
                allowed_extensions=["png", "jpg", "jpeg"]),
            alignment=ft.alignment.center,
        )

        # --- Layout Principal ---
        self.controls = [
            ft.Column([
                image_section,
                ft.Row([add_image_button, self.thumbnails_row], vertical_alignment=ft.CrossAxisAlignment.CENTER,
                       spacing=10,),
                ft.Container(
                    ft.Column([
                        ft.ElevatedButton("Agregar descripción con AI", icon=ft.Icons.STARS, bgcolor=ACCENT_COLOR,
                                          color=ft.Colors.WHITE,
                                          style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=12)), height=50),
                        self.sku_field,
                        self.title_field,
                        self.description_field,
                        # ... (Más Atributos)
                        self.price_field,
                        self.suggested_price_field,
                        self.stock_field,
                        self.location_field,
                        self.availability_group,
                        ft.Row([self.unit_dropdown, self.category_dropdown, self.supplier_dropdown,]),
                        ft.Row([ft.Text("Fecha de creación:", color=SECONDARY_TEXT_COLOR), self.creation_date_text,
                                ft.Text("Última modificación:", color=SECONDARY_TEXT_COLOR), self.modification_date_text],
                               spacing=10),
                    ], spacing=20),
                    padding=20,
                ),
            ], scroll=ft.ScrollMode.AUTO, expand=True, spacing=20),
            ft.Container(ft.ElevatedButton("Guardar Producto", bgcolor=ACCENT_COLOR, color=ft.Colors.WHITE,
                                           style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=14)), height=55,
                                           width=float('inf'), on_click=self._on_save_click),
                         padding=ft.padding.symmetric(horizontal=20, vertical=10), alignment=ft.alignment.bottom_center)
        ]
        logging.info("UI de ProductAddView construida.")

    async def _load_async_data(self, e):
        """
        Carga datos que requieren llamadas de red (async) después de que la vista se monta.
        """
        logging.info("Cargando datos asíncronos para el formulario (on_mount).")
        try:
            # Cargar datos para dropdowns
            suppliers = await self.supplier_service.get_all_suppliers()
            self.supplier_dropdown.options = [ft.dropdown.Option(key=s.id, text=s.name) for s in suppliers]
            logging.info(f"{len(suppliers)} proveedores cargados.")

            categories = await self.category_service.get_all_categories()
            self.category_dropdown.options = [ft.dropdown.Option(key=c.id, text=c.name) for c in categories]
            logging.info(f"{len(categories)} categorías cargadas.")

            # Si estamos editando, cargar datos existentes
            if self.product_id_to_edit:
                logging.info(f"Modo edición: cargando datos para producto ID {self.product_id_to_edit}.")
                # ... (lógica para cargar datos del producto)

            self.page.update()
            logging.info("Datos asíncronos cargados y UI actualizada.")
        except Exception as e:
            logging.error(f"Error en _load_async_data: {e}", exc_info=True)

    def _copy_and_get_relative_path(self, file_path: str, file_name: str) -> str:
        """Copia un archivo a la carpeta de assets/uploads y devuelve la ruta relativa."""
        uploads_dir = os.path.join(assets_dir, "uploads")
        os.makedirs(uploads_dir, exist_ok=True)
        destination_path = os.path.join(uploads_dir, file_name)
        shutil.copy(file_path, destination_path)
        return f"uploads/{file_name}"

    def _on_add_image_result(self, e: ft.FilePickerResultEvent):
        if e.files:
            logging.info(f"Agregando {len(e.files)} nueva(s) imagen(es).")
            for file in e.files:
                relative_path = self._copy_and_get_relative_path(file.path, file.name)
                self.image_paths.append(relative_path)
            self._update_image_previews()
        else:
            logging.warning("Selección de archivo para agregar cancelada.")
        self.page.update()

    def _on_replace_image_result(self, e: ft.FilePickerResultEvent):
        if e.files:
            logging.info("Reemplazando la imagen principal.")
            relative_path = self._copy_and_get_relative_path(e.files[0].path, e.files[0].name)
            if self.image_paths:
                self.image_paths[0] = relative_path  # Reemplaza la primera imagen (la principal)
            else:
                self.image_paths.append(relative_path)
            self._update_image_previews()
        else:
            logging.warning("Selección de archivo para reemplazar cancelada.")
        self.page.update()

    def _update_image_previews(self):
        """Actualiza la imagen principal y las miniaturas."""
        logging.info(f"Actualizando vistas previas. Índice principal: {self.main_image_index}")
        if self.image_paths:
            # border = ft.border.all(2, ACCENT_COLOR) if i == self.main_image_index else None,
            # ¡CAMBIO! La imagen principal ahora es la que está en el índice seleccionado.
            self.main_image_preview.src = self.image_paths[self.main_image_index]
            # El borde ahora depende del índice seleccionado.

            self.thumbnails_row.controls = [
                ft.Container(
                    # ¡CAMBIO! La imagen principal ahora es la que está en el índice seleccionado.
                    content=ft.Image(src=path, width=50, height=50, fit=ft.ImageFit.COVER, border_radius=8),
                    border=ft.border.all(2, ACCENT_COLOR) if i == 0 else None,  # Resaltar la principal
                    padding=2, on_click=lambda e,  index=i: self._set_main_image(index)
                ) for i, path in enumerate(self.image_paths)
            ]
        else:
            self.main_image_preview.src = "assets/images/placeholder.png"
            self.thumbnails_row.controls = []
        # self.page.update()

        # No es necesario llamar a page.update() aquí, ya que se llamará después de
        # que el constructor termine o después de una acción del usuario.
        # Los controles individuales se actualizan si es necesario.
        if self.main_image_preview.page: self.main_image_preview.update()
        if self.thumbnails_row.page: self.thumbnails_row.update()

        logging.info(f"Vistas previas actualizadas. Imagen principal actualizada a: {self.main_image_preview.src}")

    # ¡NUEVO! Añade este método a tu clase ProductAddView si no lo tienes.
    def _set_main_image(self, index: int):
        """
        Establece la imagen seleccionada de la miniatura como la imagen principal.
        SIN reordenar la lista.
        """

        logging.info(f"Visualizando imagen del índice {index}.")
        self.main_image_index = index
        # Simplemente volvemos a renderizar las vistas previas.
        # _update_image_previews ahora usará el nuevo índice para determinar
        # qué imagen mostrar en grande y cuál resaltar.
        self._update_image_previews()

    async def _on_save_click(self, e):
        """
                Ahora solo recolecta datos y delega TODA la operación al controlador.
                Ya no maneja excepciones ni la navegación.
                """
        logging.info("Botón 'Guardar Producto' presionado.")
        # --- ¡CORRECCIÓN! Validar y convertir los datos ANTES de enviarlos ---
        try:
            # Limpiar el formato de miles (ej. '500.000' -> '500000') y convertir a float
            buying_price = float(
                self.price_field.value.replace(
                    '.', '').replace(',', '')) if self.price_field.value else 0.0
            suggested_price = float(
                self.suggested_price_field.value.replace(
                    '.', '').replace(',','')) if self.suggested_price_field.value else 0.0
            stock = int(self.stock_field.value) if self.stock_field.value else 0
            supplier_id = self.supplier_dropdown.value

        except ValueError as ve:
            logging.error(f"Error de conversión de tipo en el formulario: {ve}")
            self.page.snack_bar = ft.SnackBar(ft.Text("Por favor, introduce números válidos para precios y stock."),
                                              bgcolor=ft.Colors.RED)
            self.page.snack_bar.open = True
            return  # Detener la ejecución si los datos no son válidos
        self.page.update()

        product_data = {
            "image_path": self.image_paths[0] if self.image_paths else None,
            "sku": self.sku_field.value,
            "name": self.title_field.value,
            "description": self.description_field.value,
            "category_ids": self.category_dropdown.value,
            "buying_price": buying_price,  # Enviar el float
            "suggested_price": suggested_price,  # Enviar el float
            "stock": stock,  # Enviar el int
            "measurement_unity": self.unit_dropdown.value,
            "availability_status": self.availability_group.value,
            "supplier_id": supplier_id,
            "location": self.location_field.value,
        }

        logging.info(f"Datos recolectados y validados: {product_data}")

        try:
            if self.product_id_to_edit is None:
                # ¡CAMBIO CLAVE! El controlador ahora devuelve el producto creado.
                new_product = await self.controller.add_product_clicked(e, product_data)

                # Si la operación fue exitosa (no devolvió None)
                if new_product:
                    # ¡CAMBIO CLAVE! Llamamos al snackbar del controlador directamente.
                    # Esto muestra el mensaje ANTES de cambiar de vista.
                    self.controller._show_snackbar(f"Producto '{new_product.name}' guardado exitosamente.")
                    # Navegar de vuelta al inventario
                    self.page.go("/inventory")
                else:
                    # Si hubo un error, el controlador ya mostró el snackbar de error.
                    # No hacemos nada más para no navegar fuera del formulario.
                    pass
            else:
                # Lógica para actualizar (también debería devolver el producto actualizado)
                updated_product = await self.controller.update_product_clicked(e, self.product_id_to_edit, product_data)
                if updated_product:
                    self.controller._show_snackbar(f"Producto '{updated_product.name}' actualizado exitosamente.")
                    self.page.go("/inventory")

        except Exception as ex:
            logging.error(f"Error inesperado en _on_save_click: {ex}", exc_info=True)
            self.controller._show_snackbar(f"Error crítico: {ex}", ft.Colors.RED)




