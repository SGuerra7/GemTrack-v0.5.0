# GemTrack/components/navigation_card.py
import flet as ft
from typing import Callable, Optional

class NavigationCard(ft.Card):
    def __init__(
        self,
        img: Optional[ft.Image] = None,
        icon: Optional[ft.Control] = None,
        title: str = "",
        description: str = "",
        on_click: Optional[Callable] = None,
        route: Optional[str] = None,
        page: Optional[ft.Page] = None,
        card_height: int = 180, # Nuevo parámetro para la altura de la tarjeta
    ):
        self._on_click_callback = on_click
        self._route = route
        self._page = page

        # Calcular tamaños de fuente e icono basados en la altura de la tarjeta
        # Definir un rango de crecimiento: min_size + (max_size - min_size) * (card_height - min_card_height) / (max_card_height - min_card_height)
        # Asumiendo que la altura mínima de la tarjeta es 180 y la máxima es 400 (ejemplo)
        min_card_height = 160
        max_card_height = 400 # Puedes ajustar este valor según tus necesidades

        # Asegurarse de que card_height esté dentro del rango definido
        scaled_card_height = max(min_card_height, min(max_card_height, card_height))

        # Calcular el factor de escalado
        # Se asegura que el factor de escalado no sea negativo y no exceda 1
        scale_card_factor = (scaled_card_height - min_card_height) / (max_card_height - min_card_height) if (max_card_height - min_card_height) > 0 else 0
        scale_factor = max(0, min(1, scale_card_factor)) # Asegura que el factor esté entre 0 y 1

        # Tamaños base (para min_card_height)
        base_title_size = 16
        base_description_size = 8

        # Tamaños máximos (para max_card_height)
        max_title_size = 48
        max_description_size = 30

        # Calcular tamaños escalados
        title_size = base_title_size + (max_title_size - base_title_size) * scale_factor
        description_size = base_description_size + (max_description_size - base_description_size) * scale_factor

        # Mostrar imagen o icono en el mismo lugar
        main_visual = img if img is not None else icon

        # Contenedor con GestureDetector para manejar clic y cursor
        content = ft.GestureDetector(
            mouse_cursor=ft.MouseCursor.CLICK,
            on_tap=self._handle_click if on_click or route else None,
            content=ft.Container(
                content=ft.Column(
                    [
                        ft.Container(
                            content=main_visual,
                            alignment=ft.alignment.center,
                            padding=ft.padding.only(bottom=0),
                        ),
                        ft.Text(
                            title,
                            color=ft.Colors.WHITE,
                            size=title_size,
                            weight=ft.FontWeight.BOLD,
                            text_align=ft.TextAlign.CENTER
                        ),
                        ft.Text(
                            description,
                            color=ft.Colors.GREY_500,
                            size=description_size,
                            text_align=ft.TextAlign.CENTER
                        ),
                    ],
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                    spacing=5,
                    alignment=ft.MainAxisAlignment.CENTER,
                    expand=True,
                ),
                padding=ft.padding.all(20),
                alignment=ft.alignment.center,
                border=ft.border.all(1, ft.Colors.GREY_800),
                border_radius=ft.border_radius.all(10),
            ),
        )

        super().__init__(
            elevation=0,
            color=ft.Colors.BLACK,
            content=content,
        )

    async def _handle_click(self, e):
        if self._on_click_callback:
            await self._on_click_callback(e)
        elif self._route and self._page:
            self._page.go(self._route)
            self._page.update()


