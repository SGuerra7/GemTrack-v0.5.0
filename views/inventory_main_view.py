# views/inventory_main_view.py
import flet as ft
from GemTrack.components.navigation_card import NavigationCard # Reutilizamos el componente de tarjeta
from flet import NavigationBarDestination

class InventoryMainView(ft.View):
    """
    Vista principal de Inventario, mostrando las subsecciones como en la imagen.
    """
    def __init__(self, page: ft.Page):
        super().__init__(
            route="/inventory_main", # Ruta para esta vista
            bgcolor=ft.Colors.BLACK, # Fondo oscuro
            vertical_alignment=ft.MainAxisAlignment.START,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
        )
        self.page = page
        self._build_ui()

    def _build_ui(self):
        """
        Construye la interfaz de usuario de la vista principal de Inventario.
        """
        self.controls = [
            ft.Container(
                content=ft.Row(
                    [
                        ft.IconButton(
                            icon=ft.Icons.ARROW_BACK,
                            icon_color=ft.Colors.WHITE,
                            on_click=lambda e: self.page.go("/"), # Volver al dashboard
                            tooltip="Volver"
                        ),
                        ft.Text(
                            "Inventory",
                            color=ft.Colors.WHITE,
                            size=40, # Tamaño de fuente grande para el título
                            weight=ft.FontWeight.BOLD,
                            expand=True # Para que el texto ocupe el espacio restante
                        ),
                        ft.Text( # "Add item" placeholder
                            "Add item",
                            color=ft.Colors.GREY_500,
                            size=16,
                            text_align=ft.TextAlign.RIGHT
                        )
                    ],
                    vertical_alignment=ft.CrossAxisAlignment.CENTER,
                    spacing=10
                ),
                alignment=ft.alignment.center_left,
                padding=ft.padding.only(left=10, right=20, top=40, bottom=30),
                width=self.page.width
            ),
            ft.Container(
                content=ft.Column( # Usamos Column para apilar las tarjetas verticalmente
                    [
                        # Tarjeta de Categorías
                        NavigationCard(
                            icon=ft.Image(src="/images/Categories_1.png", width=90, height=90, fit=ft.ImageFit.CONTAIN),
                            title="Categories",
                            description="Organize by type",
                            # on_click=lambda e: print("Navegar a Categorías") # Placeholder
                        ),
                        # Tarjeta de Niveles de Stock (aquí irá nuestra vista de CRUD de productos)
                        NavigationCard(
                            icon=ft.Image(src="/images/Stock_1.png", width=90, height=90, fit=ft.ImageFit.CONTAIN),
                            title="Stock Levels",
                            description="Low stock notifications",
                            route="/inventory_crud", # Ruta a la vista de CRUD de productos
                            page=self.page
                        ),
                        # Tarjeta de Ubicaciones
                        NavigationCard(
                            icon=ft.Image(src="/images/Locations_1.png", width=90, height=90, fit=ft.ImageFit.CONTAIN),
                            title="Locations",
                            description="Track storage areas",
                            # on_click=lambda e: print("Navegar a Ubicaciones") # Placeholder
                        ),
                        # Tarjeta de Escanear y Contar
                        NavigationCard(
                            icon=ft.Image(src="/images/Scan_1.png", width=90, height=90, fit=ft.ImageFit.CONTAIN),
                            title="Scan & Count",
                            description="Use QR or barcodes",
                            # on_click=lambda e: print("Navegar a Escanear") # Placeholder
                        ),
                        # Tarjeta de Reconciliación
                        NavigationCard(
                            icon=ft.Image(src="/images/Reconciliation_1.png", width=90, height=90, fit=ft.ImageFit.CONTAIN),
                            title="Reconciliation",
                            description="Match physical & digital",
                            # on_click=lambda e: print("Navegar a Reconciliación") # Placeholder
                        ),
                    ],
                    spacing=15, # Espacio entre las tarjetas
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                    width=self.page.width * 0.9,
                    scroll=ft.ScrollMode.AUTO,# Ocupa el 90% del ancho de la página
                    # Para que las tarjetas no se estiren demasiado en pantallas muy anchas
                    # podríamos usar un ft.Container con un ancho máximo alrededor de este Column.
                ),
                expand=True,
                alignment=ft.alignment.top_center,
                padding=ft.padding.symmetric(horizontal=20, vertical=10),

            ),

            # Barra de navegación inferior (igual que en el dashboard)
            ft.Container(
                content=ft.NavigationBar(
                    selected_index=0, # Asumimos que Home es el seleccionado por defecto
                    bgcolor=ft.Colors.BLACK,
                    destinations=[
                        NavigationBarDestination(icon=ft.Icons.HOME, label="Home"),
                        NavigationBarDestination(icon=ft.Icons.LIST_ALT, label="Orders"),
                        NavigationBarDestination(icon=ft.Icons.SEARCH, label="Search"),
                        NavigationBarDestination(icon=ft.Icons.PERSON, label="Profile"),
                    ],
                    # on_change=self._handle_navigation_change # Manejar la navegación
                ),
                padding=ft.padding.only(bottom=10)
            )
        ]

