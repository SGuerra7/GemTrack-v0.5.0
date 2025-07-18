import flet as ft

def main(page: ft.Page):
    page.title = "Gestión de Archivos"
    page.scroll = "auto"

    archivos = []
    lista_archivos = ft.Column(expand=True)

    def actualizar_lista():
        lista_archivos.controls.clear()
        for idx, archivo in enumerate(archivos):
            btn_reemplazar = ft.IconButton(
                icon=ft.Icons.EDIT,
                tooltip="Reemplazar archivo",
                on_click=lambda e, i=idx: seleccionar_reemplazo(i)
            )
            btn_eliminar = ft.IconButton(
                icon=ft.Icons.DELETE,
                tooltip="Eliminar archivo",
                on_click=lambda e, i=idx: eliminar_archivo(i)
            )
            fila = ft.Row([
                ft.Text(archivo["nombre"], expand=True),
                btn_reemplazar,
                btn_eliminar
            ])
            lista_archivos.controls.append(fila)
        page.update()

    def eliminar_archivo(index):
        archivos.pop(index)
        actualizar_lista()

    def agregar_archivos(e):
        if e.files:
            for f in e.files:
                archivos.append({"nombre": f.name, "ruta": f.path})
            actualizar_lista()

    # --- Inicialización del FilePicker para agregar archivos ---
    file_picker_agregar = ft.FilePicker(on_result=agregar_archivos)
    page.overlay.append(file_picker_agregar)
    page.update()  # IMPORTANTE para que funcione correctamente

    boton_agregar = ft.ElevatedButton(
        text="Agregar archivo(s)",
        icon=ft.Icons.FILE_UPLOAD,
        on_click=lambda e: file_picker_agregar.pick_files(allow_multiple=True)
    )

    # --- Inicialización del FilePicker para reemplazo ---
    file_picker_reemplazo = ft.FilePicker()
    page.overlay.append(file_picker_reemplazo)
    page.update()

    def seleccionar_reemplazo(index):
        def on_result(e):
            if e.files:
                archivos[index] = {"nombre": e.files[0].name, "ruta": e.files[0].path}
                actualizar_lista()
        file_picker_reemplazo.on_result = on_result
        file_picker_reemplazo.pick_files(allow_multiple=False)

    page.add(
        ft.Text("Gestor de Archivos", size=24, weight=ft.FontWeight.BOLD),
        boton_agregar,
        lista_archivos
    )

ft.app(target=main)
