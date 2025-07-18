import flet as ft

def main(page: ft.Page):
    def on_resize(e):
        ancho = page.cli
        alto = page.window_height
        print(f"Ventana redimensionada: Ancho={ancho}px, Alto={alto}px")

    page.on_resize = on_resize

    print(f"Tamaño inicial: Ancho={page.window_width}px, Alto={page.window_height}px")

    page.add(ft.Text("Redimensiona la ventana y mira la consola."))

ft.app(target=main)
