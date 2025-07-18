# views/inventory_crud_view.py
import flet as ft
from typing import List, Dict, Any

# Importamos el controlador de inventario
from GemTrack.controllers.inventory_controller import InventoryController
# Importamos el modelo Product para tipado
from GemTrack.data.models import Product
# Importamos el componente ProductCard
from GemTrack.components.product_card import ProductCard


class InventoryCRUDView(ft.View):
    """
    Vista para la gestión CRUD de productos (Agregar, Listar, Actualizar, Eliminar).
    Esta es una sub-vista de InventoryMainView.
    """

    def __init__(self, page: ft.Page):
        super().__init__(
            route="/inventory_crud",  # Nueva ruta para esta vista
            appbar=ft.AppBar(
                leading=ft.IconButton(
                    icon=ft.Icons.ARROW_BACK,
                    icon_color=ft.Colors.WHITE,
                    on_click=lambda e: page.go("/inventory_main"),  # Volver a InventoryMainView
                    tooltip="Volver"
                ),
                title=ft.Text("Gestión de Productos", color=ft.Colors.WHITE),
                bgcolor=ft.Colors.BLACK,  # Fondo oscuro para el AppBar
            ),
            bgcolor=ft.Colors.BLACK,  # Fondo oscuro para toda la vista
            vertical_alignment=ft.MainAxisAlignment.START,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
        )
        self.page = page
        self.controller = InventoryController(page)

        # Controles del formulario de agregar/editar producto
        self.name_field = ft.TextField(label="Nombre", expand=True, filled=True, fill_color=ft.Colors.GREY_900,
                                       border_radius=10, border_color=ft.Colors.GREY_800,
                                       label_style=ft.TextStyle(color=ft.Colors.GREY_400),
                                       text_style=ft.TextStyle(color=ft.Colors.WHITE))
        self.description_field = ft.TextField(label="Descripción", multiline=True, min_lines=2, max_lines=3,
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
            bgcolor=ft.Colors.GREY_900,  # Color del menú desplegable
            # text_style=ft.TextStyle(color=ft.Colors.WHITE)  # Color del texto de las opciones
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

        self.product_id_to_edit = None  # Para saber qué producto estamos editando
        self.add_edit_button = ft.ElevatedButton(
            text="Agregar Producto",
            icon=ft.Icons.ADD,
            on_click=self._on_add_edit_product_click,
            bgcolor=ft.Colors.BLUE_ACCENT_700,  # Color del botón
            color=ft.Colors.WHITE,  # Color del texto del botón
            style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=10))
        )

        # Campo de búsqueda
        self.search_field = ft.TextField(
            label="Buscar producto por nombre o SKU",
            on_change=self.controller.search_products_changed,
            suffix_icon=ft.Icons.CLEAR,
            on_submit=lambda e: setattr(self.search_field, "value", "") or self.page.update(),
            prefix_icon=ft.Icons.SEARCH,
            expand=True,
            filled=True, fill_color=ft.Colors.GREY_900, border_radius=10, border_color=ft.Colors.GREY_800,
            label_style=ft.TextStyle(color=ft.Colors.GREY_400), text_style=ft.TextStyle(color=ft.Colors.WHITE)
        )

        # Contenedor para la lista de productos
        self.products_container = ft.Column(
            controls=[],
            scroll=ft.ScrollMode.ADAPTIVE,
            expand=True,
            spacing=10  # Espacio entre las tarjetas de producto
        )
        # Pasamos la referencia del contenedor de productos al controlador para que pueda actualizarlo
        self.controller.set_product_list_view(self)

        self._build_ui()
        self.on_mount = self._load_initial_data  # Cargar datos al montar la vista

    def _build_ui(self):
        """
        Construye la interfaz de usuario de la vista de inventario.
        """
        self.controls = [
            ft.Container(
                content=ft.Column(
                    [
                        ft.Text("Formulario de Producto", size=20, weight=ft.FontWeight.BOLD, color=ft.Colors.WHITE),
                        ft.ResponsiveRow(  # Usamos ResponsiveRow para el formulario
                            [
                                self.name_field,
                                self.sku_field,
                                self.description_field,
                                self.suggested_price_field,
                                self.stock_field,
                                self.category_field,
                                self.availability_status_dropdown,
                            ],
                            spacing=10,
                            run_spacing=10,

                        ),
                        self.add_edit_button,
                    ],
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                    spacing=15
                ),
                padding=20,
                margin=ft.margin.all(10),
                border_radius=ft.border_radius.all(10),
                bgcolor=ft.Colors.GREY_900,  # Fondo oscuro para el contenedor del formulario
                width=600 if self.page.width > 600 else self.page.width * 0.9  # Ancho adaptable
            ),
            ft.Divider(color=ft.Colors.GREY_800),
            ft.Container(
                content=ft.Column(
                    [
                        ft.Text("Lista de Productos", size=20, weight=ft.FontWeight.BOLD, color=ft.Colors.WHITE),
                        self.search_field,
                        self.products_container,
                    ],
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                    spacing=15
                ),
                padding=20,
                margin=ft.margin.all(10),
                border_radius=ft.border_radius.all(10),
                bgcolor=ft.Colors.GREY_900,  # Fondo oscuro para el contenedor de la lista
                expand=True  # Para que ocupe el espacio restante
            )
        ]

    async def _load_initial_data(self, e):
        """
        Carga los productos iniciales cuando la vista se monta.
        """
        self.update_list(await self.controller.load_products())

    async def _on_add_edit_product_click(self, e):
        """
        Maneja el clic en el botón de agregar/editar producto.
        Determina si es una operación de agregar o editar.
        """
        product_data = {
            "name": self.name_field.value,
            "description": self.description_field.value,
            "sku": self.sku_field.value,
            "suggested_price": self.suggested_price_field.value,
            "availability_status": self.availability_status_dropdown.value,
            "category": self.category_field.value,
            "stock": self.stock_field.value,
        }

        if self.product_id_to_edit is None:
            await self.controller.add_product_clicked(e, product_data)
        else:
            await self.controller.update_product_clicked(e, self.product_id_to_edit, product_data)
            self._clear_form()  # Limpiar formulario después de editar

    async def _on_edit_product_click(self, e, product_id: int, product_data: Dict[str, Any]):
        """
        Rellena el formulario con los datos del producto para editar.
        """
        self.product_id_to_edit = product_id
        self.name_field.value = product_data.get("name", "")
        self.description_field.value = product_data.get("description", "")
        self.sku_field.value = product_data.get("sku", "")
        self.suggested_price_field.value = str(product_data.get("suggested_price", 0.0))
        self.availability_status_dropdown.value = product_data.get("availability_status", "en_stock")
        self.category_field.value = product_data.get("category", "")
        self.stock_field.value = str(product_data.get("stock", 0))

        self.add_edit_button.text = "Actualizar Producto"
        self.add_edit_button.icon = ft.Icons.SAVE
        self.page.update()

    async def _on_delete_product_click(self, e, product_id: int):
        """
        Maneja el clic en el botón de eliminar producto.
        """
        await self.controller.delete_product_clicked(e, product_id)

    def update_list(self, products: List[Product]):
        """
        Actualiza la lista de productos mostrada en la UI.
        Este método es llamado por el controlador.
        """
        self.products_container.controls.clear()
        if products:
            for product in products:
                self.products_container.controls.append(
                    ProductCard(
                        product,
                        on_edit_click=self._on_edit_product_click,
                        on_delete_click=self._on_delete_product_click
                    )
                )
        else:
            self.products_container.controls.append(ft.Text("No hay productos para mostrar.", color=ft.Colors.GREY_400))
        self.products_container.update()  # Usar update_async para actualizar el control

    def _clear_form(self):
        """
        Limpia los campos del formulario y restablece el botón.
        """
        self.name_field.value = ""
        self.description_field.value = ""
        self.sku_field.value = ""
        self.suggested_price_field.value = ""
        self.availability_status_dropdown.value = "en_stock"
        self.category_field.value = ""
        self.stock_field.value = ""
        self.product_id_to_edit = None
        self.add_edit_button.text = "Agregar Producto"
        self.add_edit_button.icon = ft.Icons.ADD
        self.page.update()

