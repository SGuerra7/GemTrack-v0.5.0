import flet as ft


def main(page: ft.Page):

    padding = 12

    # Texto para mostrar tamaño de ventana en tiempo real
    window_size_text = ft.Text()

    # Crear las 4 tarjetas como Containers con expand=True para que ocupen espacio disponible
    cardsr1 = ft.ResponsiveRow(
        spacing=padding,
        controls=[
            ft.Container(
                content=ft.Text("Tarjeta 1", size=20),
                bgcolor=ft.Colors.BLUE_200,
                alignment=ft.alignment.center,
                padding=padding,
                border_radius=10,
                col=6,
            ),
            ft.Container(
                content=ft.Text("Tarjeta 2", size=20),
                bgcolor=ft.Colors.GREEN_200,
                alignment=ft.alignment.center,
                padding=padding,
                border_radius=10,
                col=6,
            ),
        ],
        columns=12,
        expand=True,
        vertical_alignment=ft.CrossAxisAlignment.CENTER,
        alignment=ft.MainAxisAlignment.CENTER,
    )
    cardsr2 = ft.ResponsiveRow(
        spacing=padding,
        controls=[
            ft.Container(
                content=ft.Text("Tarjeta 3", size=20),
                bgcolor=ft.Colors.RED_200,
                alignment=ft.alignment.center,
                padding=padding,
                border_radius=10,
                col=6,

            ),
            ft.Container(
                content=ft.Text("Tarjeta 4", size=20),
                bgcolor=ft.Colors.YELLOW_200,
                alignment=ft.alignment.center,
                padding=padding,
                border_radius=10,
                col=6,
            ),
        ],
        columns=12,
        expand=True,
        vertical_alignment=ft.CrossAxisAlignment.CENTER,
        alignment=ft.MainAxisAlignment.CENTER,
    )

    def on_resize(e):
        if page.window.width > 800:
            cardsr1.aspect_ratio = 16/9
            cardsr2.aspect_ratio = 16/9
        else:
            cardsr1.aspect_ratio = 1
            cardsr2.aspect_ratio = 1
        cardsr1.update()
        cardsr2.update()

        # Obtener tamaño actual de la ventana
        w, h = page.window.width, page.window.height
        window_size_text.value = f"Ancho: {w}px, Alto: {h}px"
        window_size_text.update()


    # Asignar el evento de redimensionamiento
    page.on_resize = on_resize

    page.padding = padding
    page.add(window_size_text, cardsr1, cardsr2)

    # Inicializar texto con tamaño actual
    on_resize(None)

ft.app(target=main)
