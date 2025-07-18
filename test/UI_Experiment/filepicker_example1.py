import flet as ft

def main(page: ft.Page):
    page.title = "Gestión de Archivos"
    page.scroll = "auto"

    archivos = []  # Lista para almacenar los archivos seleccionados
    lista_archivos = ft.Column()  # Contenedor para mostrar los archivos

    # Función para actualizar la vista de archivos
    def actualizar_lista():
        lista_archivos.controls.clear()
        for i, archivo in enumerate(archivos):
            def crear_reemplazo_handler(index):
                def handler(e):
                    reemplazar_archivo(index)
                return handler

            def crear_eliminar_handler(index):
                def handler(e):
                    eliminar_archivo(index)
                return handler

            lista_archivos.controls.append(
                ft.Row([
                    ft.Text(archivo["nombre"], expand=True),
                    ft.IconButton(
                        icon="edit",
                        tooltip="Reemplazar archivo",
                        on_click=crear_reemplazo_handler(i)  # Corregido
                    ),
                    ft.IconButton(
                        icon="delete",
                        tooltip="Eliminar archivo",
                        on_click=crear_eliminar_handler(i)  # Corregido
                    ),
                ])
            )
        page.update()

    # Función para eliminar un archivo de la lista
    def eliminar_archivo(index):
        archivos.pop(index)
        actualizar_lista()

    # FilePicker para seleccionar nuevos archivos
    file_picker = ft.FilePicker(on_result=lambda e: agregar_archivos(e.files))
    page.overlay.append(file_picker)

    # Función para agregar archivos a la lista
    def agregar_archivos(files):
        if files:
            for f in files:
                archivos.append({"nombre": f.name, "ruta": f.path})
            actualizar_lista()

    # Botón para abrir el FilePicker y seleccionar archivos
    boton_agregar = ft.ElevatedButton(
        text="Agregar archivo(s)",
        icon="file_upload",
        on_click=lambda e: file_picker.pick_files(allow_multiple=True)
    )

    # FilePicker para reemplazar un archivo existente
    file_picker_reemplazo = ft.FilePicker()
    page.overlay.append(file_picker_reemplazo)

    # Función para reemplazar un archivo en la lista
    def reemplazar_archivo(index):
        def on_file_selected(e):
            if e.files:
                archivos[index] = {"nombre": e.files[0].name, "ruta": e.files[0].path}
                actualizar_lista()
        file_picker_reemplazo.on_result = on_file_selected
        file_picker_reemplazo.pick_files(allow_multiple=False)

    # Agregar los controles a la página
    page.add(
        ft.Text("Gestor de Archivos", size=24),
        boton_agregar,
        lista_archivos
    )

ft.app(target=main)