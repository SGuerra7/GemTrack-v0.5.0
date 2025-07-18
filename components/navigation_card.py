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
        card_height: int = 180,  # Nuevo parámetro para la altura de la tarjeta
    ):
        self._on_click_callback = on_click
        self._route = route
        self._page = page

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
                            size=32,
                            weight=ft.FontWeight.BOLD,
                            text_align=ft.TextAlign.CENTER
                        ),
                        ft.Text(
                            description,
                            color=ft.Colors.GREY_500,
                            size=22,
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