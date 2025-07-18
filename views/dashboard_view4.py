import flet as ft
from components.navigation_card2 import NavigationCard
from flet import NavigationBarDestination


class DashboardView(ft.View):
    def __init__(self, page: ft.Page):
        super().__init__(
            route="/",
            bgcolor=ft.Colors.BLACK,
            vertical_alignment=ft.MainAxisAlignment.START,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
        )
        # self.page se asigna automáticamente por Flet cuando la vista se añade a page.views
        # No es necesario asignarlo aquí, pero lo mantenemos por claridad en otros métodos.
        self.page = page
        self.cards = []
        self.cards_area = None

        # --- CORRECCIÓN CLAVE 1: Registrar eventos en el ciclo de vida ---
        # Se registra el manejador cuando la vista se monta.
        self.on_mount = self.view_did_mount
        # Se limpia el manejador cuando la vista se desmonta.
        self.on_unmount = self.view_did_unmount

    def view_did_mount(self, e):
        """Se ejecuta cuando la vista se añade a la página."""
        # Registra el evento de redimensionamiento solo cuando esta vista está activa.
        self.page.on_resize = self.on_resize
        # Construye la UI inicial.
        self.build_ui()

    def view_did_unmount(self, e):
        """Se ejecuta cuando la vista se elimina de la página."""
        # Limpia el manejador de eventos para evitar llamadas "fantasma".
        # Esto es crucial para prevenir el error.
        self.page.on_resize = None

    def on_resize(self, e):
        """Manejador de redimensionamiento, ahora solo se llama si la vista está montada."""
        # --- CORRECCIÓN CLAVE 2: Comprobación de seguridad ---
        # Aunque on_unmount debería prevenirlo, una comprobación extra no hace daño.
        if self.page is None:
            return
        self.build_ui()

    def build_ui(self):
        # Lista de tarjetas
        self.controls.clear()
        self.cards = [
            dict(
                icon=ft.Image(src="/images/Inventory_1.png", width=90, height=90, fit=ft.ImageFit.CONTAIN),
                title="Inventory",
                description="Manage stock levels",
                route="/inventory",
                page=self.page,
            ),
            dict(
                icon=ft.Image(src="/images/Catalog_1.png", width=90, height=90, fit=ft.ImageFit.CONTAIN),
                title="Catalog",
                description="Browse jewelry items",
            ),
            dict(
                icon=ft.Image(src="/images/Sales_1.png", width=90, height=90, fit=ft.ImageFit.CONTAIN),
                title="Sales",
                description="View sales data",
            ),
            dict(
                icon=ft.Image(src="/images/Customers_1.png", width=90, height=90, fit=ft.ImageFit.CONTAIN),
                title="Customers",
                description="Manage client information",
            ),
        ]
        self.cards_area = self.build_cards_area()

        # Encabezado
        header = ft.Container(
            content=ft.Text(
                "GemTrack",
                color=ft.Colors.WHITE,
                size=48,
                weight=ft.FontWeight.BOLD,
            ),
            alignment=ft.alignment.center,
            padding=ft.padding.only(left=0, top=20, bottom=30),
        )

        # Barra de navegación
        nav_bar = ft.Container(
            content=ft.NavigationBar(
                selected_index=0,
                bgcolor=ft.Colors.BLACK,
                destinations=[
                    NavigationBarDestination(icon=ft.Icons.HOME, label="Home"),
                    NavigationBarDestination(icon=ft.Icons.LIST_ALT, label="Orders"),
                    NavigationBarDestination(icon=ft.Icons.SEARCH, label="Search"),
                    NavigationBarDestination(icon=ft.Icons.PERSON, label="Profile"),
                ],
            ),
            padding=ft.padding.only(bottom=0)
        )

        self.controls.extend([
            header,
            self.cards_area,
            nav_bar
        ])

        # --- CORRECCIÓN CLAVE 3: Actualizar solo si la página existe ---
        if self.page:
            self.page.update()

    def build_cards_area(self):
        return ft.Container(
            content=self.build_cards(),
            padding=ft.padding.symmetric(horizontal=20, vertical=10),
            expand=True,
        )

    def build_cards(self):
        num_cards = len(self.cards)
        cards_per_row = 2
        num_rows = (num_cards + cards_per_row - 1) // cards_per_row

        spacing = 20
        min_card_height = 180
        max_card_height_ratio = 0.325

        header_height = 70
        nav_bar_height = 70
        vertical_padding = 20 * 2
        total_spacing = spacing * (num_rows - 1)

        if self.page is not None:
            page_height = getattr(self.page, "window_height", None) or self.page.height or 800
        else:
            page_height = 800

        available_height = max(page_height - header_height - nav_bar_height - vertical_padding - total_spacing,
                               min_card_height * num_rows)

        calculated_card_height = available_height // num_rows
        max_allowed_card_height = page_height * max_card_height_ratio
        card_height = max(min_card_height, min(calculated_card_height, max_allowed_card_height))

        return ft.Column(
            [
                ft.ResponsiveRow(
                    [
                        ft.Container(
                            content=NavigationCard(card_height=card_height, **card),
                            col=6,
                            height=card_height,
                            alignment=ft.alignment.center,
                        )
                        for card in self.cards
                    ],
                    spacing=spacing,
                    run_spacing=spacing,
                    alignment=ft.MainAxisAlignment.CENTER,
                    vertical_alignment=ft.CrossAxisAlignment.CENTER,
                    columns=12,
                )
            ],
            scroll=ft.ScrollMode.AUTO,
            expand=True
        )