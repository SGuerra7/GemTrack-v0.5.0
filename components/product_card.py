# components/product_card.py
import flet as ft
from typing import Callable
from data.models.product_models import Product  # Importamos el modelo Product


class ProductCard(ft.Card):
    """
    Componente de tarjeta para mostrar los detalles de un producto en la lista.
    Incluye botones para editar y eliminar.
    """

    def __init__(self, product: Product, on_edit_click: Callable, on_delete_click: Callable):
        super().__init__(
            elevation=0,  # Sin sombra para un look más plano
            color=ft.Colors.BLACK,  # Fondo de la tarjeta oscuro
        )
        self.product = product
        self.on_edit_click = on_edit_click
        self.on_delete_click = on_delete_click

        self.content = ft.Container(
            content=ft.Column(
                [
                    ft.Text(f"Nombre: {product.name}", weight=ft.FontWeight.BOLD, color=ft.Colors.WHITE),
                    ft.Text(f"SKU: {product.sku}", color=ft.Colors.GREY_400),
                    ft.Text(f"Precio: ${product.suggested_price:.2f}", color=ft.Colors.GREY_400),
                    ft.Text(f"Stock: {product.stock}", color=ft.Colors.GREY_400),
                    ft.Text(f"Categoría: {product.category if product.category else 'N/A'}", color=ft.Colors.GREY_400),
                    ft.Text(f"Disponibilidad: {product.availability_status}", color=ft.Colors.GREY_400),
                    ft.Row(
                        [
                            ft.IconButton(
                                icon=ft.Icons.EDIT,
                                icon_color=ft.Colors.BLUE_ACCENT_200,
                                tooltip="Editar",
                                on_click=lambda e: self.on_edit_click(e, self.product.id, self.product.to_dict()),
                            ),
                            ft.IconButton(
                                icon=ft.Icons.DELETE,
                                icon_color=ft.Colors.RED_ACCENT_200,
                                tooltip="Eliminar",
                                on_click=lambda e: self.on_delete_click(e, self.product.id),
                            ),
                        ],
                        alignment=ft.MainAxisAlignment.END
                    )
                ],
                spacing=5,
            ),
            padding=ft.padding.all(15),
            border=ft.border.all(1, ft.Colors.GREY_800),
            border_radius=ft.border_radius.all(10),
        )

