# views/product_form_view.py
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
from services.product_service import ProductService

# Obtiene la ruta absoluta al directorio de assets usando pathlib y os
assets_dir = os.path.join(Path(os.path.dirname(__file__)).parent, "assets") # Asumiendo que estás en views/product_form_view.py

class   ProductFormView(ft.View):
    """
    Una vista dedicada para agregar o editar un producto.
    """
    def __init__(self, page: ft.Page, product_id: Optional[int] = None, image_path: Optional[str] = None):
        super().__init__(
            # La ruta será dinámica para manejar la edición
            route=f"/product/edit/{product_id}" if product_id else "/product/add",
            bgcolor=ft.Colors.BLACK,
            vertical_alignment=ft.MainAxisAlignment.START,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
        )
        self.page = page
        self.controller = InventoryController(page)
        self.product_id_to_edit = product_id

        # ¡NUEVO! Instanciamos los servicios directamente para obtener datos (ej. proveedores)
        self.supplier_service = SupplierService()
        self.product_service = ProductService()

        # --- Controles del formulario ---

        # --- FilePicker para imágenes ---
        self.file_picker = ft.FilePicker(on_result=self._on_file_picker_result)

        # Es importante añadir el FilePicker al overlay de la página
        page.overlay.append(self.file_picker)

        # CORRECCIÓN: Inicializar el atributo correctamente:
        self.image_path = image_path   # Para guardar la ruta de la imagen
        self.image_preview = ft.Image(
            src="assets/images/placeholder.png",  # Placeholder inicial
            width=100, height=100, fit=ft.ImageFit.COVER, border_radius=10
        )
        self.name_field = ft.TextField(label="Nombre", expand=True, filled=True, fill_color=ft.Colors.GREY_900,
                                       border_radius=10, border_color=ft.Colors.GREY_800,
                                       label_style=ft.TextStyle(color=ft.Colors.GREY_400),
                                       text_style=ft.TextStyle(color=ft.Colors.WHITE))
        self.description_field = ft.TextField(label="Descripción", multiline=True, min_lines=3, max_lines=5,
                                              expand=True, filled=True, fill_color=ft.Colors.GREY_900, border_radius=10,
                                              border_color=ft.Colors.GREY_800,
                                              label_style=ft.TextStyle(color=ft.Colors.GREY_400),
                                              text_style=ft.TextStyle(color=ft.Colors.WHITE))
        self.sku_field = ft.TextField(label="SKU", expand=True, filled=True, fill_color=ft.Colors.GREY_900,
                                      border_radius=10, border_color=ft.Colors.GREY_800,
                                      label_style=ft.TextStyle(color=ft.Colors.GREY_400),
                                      text_style=ft.TextStyle(color=ft.Colors.WHITE))
        self.suggested_price_field = ft.TextField(label="Precio Sugerido", keyboard_type=ft.KeyboardType.NUMBER,
                                                  expand=True, filled=True, fill_color=ft.Colors.GREY_900,
                                                  border_radius=10, border_color=ft.Colors.GREY_800,
                                                  label_style=ft.TextStyle(color=ft.Colors.GREY_400),
                                                  text_style=ft.TextStyle(color=ft.Colors.WHITE))
        self.availability_status_dropdown = ft.Dropdown(
            label="Disponibilidad",
            options=[
                ft.dropdown.Option("en_stock"),
                ft.dropdown.Option("agotado"),
                ft.dropdown.Option("bajo_stock"),
            ],
            value="en_stock",
            expand=True,
            filled=True, fill_color=ft.Colors.GREY_900, border_radius=10, border_color=ft.Colors.GREY_800,
            label_style=ft.TextStyle(color=ft.Colors.GREY_400), text_style=ft.TextStyle(color=ft.Colors.WHITE),
        )
        self.supplier_dropdown = ft.Dropdown(
            label="Proveedor",
            options=[  ],
            value="Proveedor A",  # Valor por defecto
            expand=True,
            filled=True, fill_color=ft.Colors.GREY_900, border_radius=10, border_color=ft.Colors.GREY_800,
            label_style=ft.TextStyle(color=ft.Colors.GREY_400), text_style=ft.TextStyle(color=ft.Colors.WHITE),
        )
        self.category_field = ft.TextField(label="Categoría", expand=True, filled=True, fill_color=ft.Colors.GREY_900,
                                           border_radius=10, border_color=ft.Colors.GREY_800,
                                           label_style=ft.TextStyle(color=ft.Colors.GREY_400),
                                           text_style=ft.TextStyle(color=ft.Colors.WHITE))
        self.stock_field = ft.TextField(label="Stock", keyboard_type=ft.KeyboardType.NUMBER, expand=True, filled=True,
                                        fill_color=ft.Colors.GREY_900, border_radius=10,
                                        border_color=ft.Colors.GREY_800,
                                        label_style=ft.TextStyle(color=ft.Colors.GREY_400),
                                        text_style=ft.TextStyle(color=ft.Colors.WHITE))

        self.save_button = ft.ElevatedButton(
            text="Guardar Producto",
            icon=ft.Icons.SAVE,
            on_click=self._on_save_click,
            bgcolor=ft.Colors.BLUE_ACCENT_700,
            color=ft.Colors.WHITE,
            style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=10)),
            height=50,
            expand=True
        )

        self._build_ui()
        self.on_mount = self._load_data_for_editing # Cargar datos si estamos editando

    def _build_ui(self):
        # Título dinámico para la vista
        title_text = "Editar Producto" if self.product_id_to_edit else "Agregar Producto"

        self.appbar = ft.AppBar(
            leading=ft.IconButton(
                icon=ft.Icons.ARROW_BACK,
                icon_color=ft.Colors.WHITE,
                on_click=lambda e: self.page.go("/inventory"), # Volver a la lista
                tooltip="Volver"
            ),
            title=ft.Text(title_text, color=ft.Colors.WHITE),
            bgcolor=ft.Colors.BLACK,
        )

        # SOLUCIÓN: Construir una única lista de controles para la vista
        self.controls = [
            ft.Container(
                content=ft.Column(
                    [
                        # Fila para la carga de imágenes
                        ft.Row([
                            self.image_preview,
                            ft.ElevatedButton(
                                "Subir Imagen",
                                icon=ft.Icons.UPLOAD_FILE,
                                on_click=lambda _: self.file_picker.pick_files(
                                    allow_multiple=False,
                                    allowed_extensions=["png", "jpg", "jpeg"]
                                ),
                                style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=10)),
                                height=50,
                                expand=True
                            ),
                        ], alignment=ft.MainAxisAlignment.START, vertical_alignment=ft.CrossAxisAlignment.CENTER),
                        ft.Container(height=10),

                        # Resto de los campos del formulario
                        self.name_field,
                        self.sku_field,
                        self.description_field,
                        self.suggested_price_field,
                        self.stock_field,
                        self.category_field,
                        self.availability_status_dropdown,
                        self.supplier_dropdown,
                        ft.Container(height=20),
                        self.save_button,
                    ],
                    spacing=15,
                    scroll=ft.ScrollMode.ADAPTIVE,
                ),
                padding=20,
                expand=True
            )
        ]

    def _on_file_picker_result(self, e: ft.FilePickerResultEvent):
        if e.files:
            selected_file = e.files[0]
            # Crear una carpeta 'uploads' dentro de 'assets' si no existe

            uploads_dir = os.path.join(assets_dir, "uploads")
            os.makedirs(uploads_dir, exist_ok=True)

            # Copiar el archivo seleccionado a la carpeta de subidas
            destination_path = os.path.join(uploads_dir, selected_file.name)
            shutil.copy(selected_file.path, destination_path)

            # Guardar la ruta relativa para la base de datos
            self.image_path = f"/uploads/{selected_file.name}"

            # Actualizar la vista previa de la imagen
            self.image_preview.src = self.image_path
            self.image_preview.update()
            logging.info(f"Imagen guardada en: {self.image_path}")
        else:
            logging.info("Selección de archivo cancelada.")

    async def _load_data_for_editing(self, e):
        """Si estamos en modo edición, carga los datos del producto."""

        # --- Cargar proveedores ---
        suppliers = await self.controller.get_all_suppliers()
        supplier_options = []
        for supplier in suppliers:
            # El `key` es el ID que guardaremos, el `text` es lo que ve el usuario
            supplier_options.append(
                ft.dropdown.Option(key=supplier.id, text=f"{supplier.first_name} {supplier.last_name}"))
        self.supplier_dropdown.options = supplier_options

        if self.product_id_to_edit:
            logging.info(f"Cargando datos para editar producto ID: {self.product_id_to_edit}")
            product = await self.controller.get_product_details(self.product_id_to_edit)
            if product:
                self.name_field.value = product.name
                self.description_field.value = product.description
                self.sku_field.value = product.sku
                self.suggested_price_field.value = str(product.suggested_price)
                self.availability_status_dropdown.value = product.availability_status
                self.category_field.value = product.category
                self.stock_field.value = str(product.stock)

                # Seleccionar el proveedor actual en el dropdown
                if product and product.supplier_id:
                    self.supplier_dropdown.value = product.supplier_id

                # Cargar la imagen si existe
                if product.image_path:
                    self.image_path = product.image_path
                    self.image_preview.src = self.image_path

                self.page.update()
            else:
                logging.error(f"No se encontró el producto con ID {self.product_id_to_edit} para editar.")
                self.page.snack_bar = ft.SnackBar(ft.Text("Error: Producto no encontrado."), bgcolor=ft.Colors.RED)
                self.page.snack_bar.open = True
                self.page.go("/inventory")

    async def _on_save_click(self, e):
        """Maneja el clic en el botón de guardar."""
        product_data = {
            "image_url": self.image_path,  # Añadimos la ruta de la imagen
            "name": self.name_field.value,
            "description": self.description_field.value,
            "sku": self.sku_field.value,
            "suggested_price": self.suggested_price_field.value,
            "availability_status": self.availability_status_dropdown.value,
            "category": self.category_field.value,
            "stock": self.stock_field.value,
            "measurement_unity": "unidad",  # Valor por defecto, puedes cambiarlo según tu lógica
            "supplier_id": self.supplier_dropdown.value,  # ID del proveedor seleccionado

        }

        if self.product_id_to_edit is None:
            # Agregar nuevo producto
            await self.controller.add_product_clicked(e, product_data)
        else:
            # Actualizar producto existente
            await self.controller.update_product_clicked(e, self.product_id_to_edit, product_data)

        # Guardar mensaje de éxito para la siguiente vista
        self.page.client_storage.set("snackbar_message",
                                     f"Producto '{product_data['name']}' guardado exitosamente.")
        # Después de guardar, volver a la lista de inventario
        self.page.go("/inventory")
