# components/inventory_product_card.py
import flet as ft
from typing import Callable # Dict y Any son necesarios para product.to_dict()
from data.models.product_models import Product # Importamos el modelo Product

class InventoryProductCard(ft.Card):
    def __init__(self, product: Product, on_edit_click: Callable, on_delete_click: Callable):
        super().__init__(
            elevation=0,
            color=ft.Colors.BLACK,  # Fondo oscuro para la tarjeta
            margin=ft.margin.only(bottom=10)  # Espacio entre tarjetas
        )
        self.product = product
        self.on_edit_click = on_edit_click
        self.on_delete_click = on_delete_click

        # El IconButton de MORE_VERT será un PopupMenuButton para mostrar opciones
        self.options_button = ft.PopupMenuButton(
            icon=ft.Icons.MORE_VERT,
            icon_color=ft.Colors.GREY_500,
            tooltip="Más opciones",
            items=[
                ft.PopupMenuItem(
                    text="Editar",
                    icon=ft.Icons.EDIT,
                    on_click=lambda e: self.on_edit_click(e, self.product.id) # Pasar None como evento
                ),
                ft.PopupMenuItem(
                    text="Eliminar",
                    icon=ft.Icons.DELETE,
                    on_click=lambda e: self.on_delete_click(e, self.product.id) # Pasar None como evento
                ),
            ]
        )

        # Determinar la ruta de la imagen
        image_src = product.image_path if product.image_path else "assets/images/placeholder.png"

        # ¡CAMBIO CLAVE! Lógica para mostrar las categorías.
        # Unimos los nombres de todas las categorías en la lista con una coma.
        # Si no hay categorías, mostramos "N/A".
        categories_text = ", ".join([cat.name for cat in product.categories]) if product.categories else "Sin categoría"

        self.content = ft.Container(
            content=ft.Row(
                [
                    # Imagen del producto (placeholder por ahora)
                    ft.Container(
                        content=ft.Image(
                            src=image_src, # Placeholder de imagen
                            width=60,
                            height=60,
                            fit=ft.ImageFit.COVER,
                            error_content = ft.Icon(ft.Icons.IMAGE_NOT_SUPPORTED)  # Mostrar icono si la imagen falla
                        ),
                        width=80,
                        height=80,
                        border_radius=ft.border_radius.all(10),
                        bgcolor=ft.Colors.GREY_900, # Fondo para la imagen
                        alignment=ft.alignment.center
                    ),
                    # Detalles del producto
                    ft.Column(
                        [
                            ft.Text(self.product.name, weight=ft.FontWeight.BOLD, color=ft.Colors.WHITE, size=18),
                            ft.Text(f"Qty: {self.product.stock}", color=ft.Colors.GREY_400, size=14),
                            ft.Text(categories_text, color=ft.Colors.GREY_400,size=14, overflow=ft.TextOverflow.ELLIPSIS
                                    ), # Usamos categoría como ubicación temporal
                        ],
                        spacing=2,
                        expand=True
                    ),
                    # Iconos de acción (QR y menú de 3 puntos)
                    ft.Column(
                        [
                            ft.IconButton(
                                icon=ft.Icons.QR_CODE_2,
                                icon_color=ft.Colors.GREY_500,
                                tooltip="Ver QR",
                                on_click=lambda e: print(f"Ver QR de {self.product.name}") # Placeholder
                            ),
                            self.options_button, # Usamos el PopupMenuButton aquí
                        ],
                        horizontal_alignment=ft.CrossAxisAlignment.END,
                        spacing=0
                    )
                ],
                alignment=ft.MainAxisAlignment.START,
                vertical_alignment=ft.CrossAxisAlignment.CENTER,
                spacing=15
            ),
            padding=ft.padding.all(10),
            border=ft.border.all(1, ft.Colors.GREY_800),
            border_radius=ft.border_radius.all(10),
        )

