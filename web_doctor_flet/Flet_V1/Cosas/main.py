import flet as ft
import CRUD_Supabase as crud
#import processprint as pdf
from datetime import datetime
import pdfkit
import tempfile
import os

SECCION_INICIAL = "dashboard"

#------------------------------------------------[ Usuario id ]------------------------------------------------

def obtener_doctor_id(page):
    usuario = page.session.get("usuario")

    if not usuario or "id" not in usuario:
        page.go("/login")
        return ft.Text("Redirigiendo al inicio de sesión...")

    id = usuario["id"]
    return id

#------------------------------------------------[ Dialogos ]------------------------------------------------

def mostrar_dialogos(page, dialog):
    dialog.open = True
    page.update()


def cerrar_dialogos(page):
    page.dialog.open = False
    page.update()

#------------------------------------------------------------------------------------------------------------

def login_form(page: ft.Page):
    consultas = crud.Consultas()
    correo_input = ft.TextField(
        label="Correo electrónico",
        hint_text="ejemplo@correo.com",
        keyboard_type=ft.KeyboardType.EMAIL,
        width=400
    )
    password_input = ft.TextField(
        label="Contraseña",
        password=True,
        can_reveal_password=True,
        width=400
    )
    mensaje = ft.Text("", color=ft.Colors.RED)

    def iniciar_sesion(e):
        correo = correo_input.value.strip()
        contraseña = password_input.value.strip()

        if not correo or not contraseña:
            mensaje.value = "Por favor, completa todos los campos."
            page.update()
            return

        usuario = consultas.autenticar_usuario(correo, str(contraseña))

        if usuario:
            page.session.set("usuario", usuario)  # Puedes guardar sesión aquí
            mensaje.value = ""
            page.go("/dashboard")
        else:
            mensaje.value = "Correo o contraseña incorrectos."
            page.update()

    return ft.Column(
        [
            ft.Text("Bienvenido a la App de Salud", size=24, weight="bold"),
            ft.Text("Inicia sesión para continuar", size=16, italic=True),
            correo_input,
            password_input,
            ft.ElevatedButton(
                text="Iniciar sesión",
                width=200,
                on_click=iniciar_sesion
            ),
            mensaje,
            ft.Row(
                [
                    ft.TextButton(
                        text="¿Olvidaste tu contraseña?",
                        on_click=lambda e: print("Recuperar contraseña")
                    ),
                    ft.TextButton(
                        text="¿No tienes cuenta? Regístrate aquí",
                        on_click=lambda e: page.go("/registro")
                    )
                ],
                alignment=ft.MainAxisAlignment.CENTER
            )
        ],
        alignment=ft.MainAxisAlignment.CENTER,
        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
        spacing=20
    )

def registro_form(page: ft.Page):
    consultas = crud.Consultas()
    nombre_input = ft.TextField(label="Nombre completo", width=400)
    correo_input = ft.TextField(label="Correo electrónico", keyboard_type=ft.KeyboardType.EMAIL, width=400)
    password_input = ft.TextField(label="Contraseña", password=True, can_reveal_password=True, width=400)
    mensaje = ft.Text("", color=ft.Colors.RED)

    def registrar_usuario(e):
        nombre = nombre_input.value.strip()
        correo = correo_input.value.strip()
        contraseña = password_input.value.strip()

        if not nombre or not correo or not contraseña:
            mensaje.value = "Por favor, completa todos los campos."
            page.update()
            return

        exito = consultas.Crear_usuario(nombre, correo, contraseña, "medico")

        if exito:
            mensaje.value = ""
            page.go("/login")
        else:
            mensaje.value = "Error al registrar. ¿Ya existe este usuario?"
            page.update()

    return ft.Column(
        [
            ft.Text("Crear nueva cuenta", size=24, weight="bold"),
            nombre_input,
            correo_input,
            password_input,
            ft.ElevatedButton(
                text="Registrarse",
                width=200,
                on_click=registrar_usuario
            ),
            mensaje,
            ft.Row(
                [
                    ft.Text("¿Ya tienes cuenta?"),
                    ft.TextButton(
                        text="Inicia sesión",
                        on_click=lambda e: page.go("/login")
                    )
                ],
                alignment=ft.MainAxisAlignment.CENTER
            )
        ],
        alignment=ft.MainAxisAlignment.CENTER,
        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
        spacing=20
    )


def actualizar_datos_dashboard(page: ft.Page, doctor_id):
    transacciones = crud.Consultas()

    total_pacientes = transacciones.obtener_pacientes_por_doctor(doctor_id, cantidad=True)
    total_medicamentos = transacciones.obtener_medicamentos(cantidad=True)
    total_citas = transacciones.obtener_citas_del_doctor(doctor_id, cantidad=True)

    page.session.set("dashboard_datos", {
        "pacientes": total_pacientes,
        "medicamentos": total_medicamentos,
        "citas": total_citas
    })

    return total_pacientes, total_medicamentos, total_citas


def dashboard_form(page: ft.Page, forzar_recarga=False):
    transacciones = crud.Consultas()

    doctor_id = obtener_doctor_id(page)

    if forzar_recarga or not page.session.get("dashboard_datos"):
        total_pacientes, total_medicamentos, total_citas = actualizar_datos_dashboard(page, doctor_id)
    else:
        datos = page.session.get("dashboard_datos")
        total_pacientes = datos["pacientes"]
        total_medicamentos = datos["medicamentos"]
        total_citas = datos["citas"]

    def cerrar_sesion(e):
        page.session.clear()  # Limpia la sesión
        page.go("/login")     # Redirige al login

    return ft.Column(
        [
            ft.Text("Panel de Control", size=24, weight="bold"),
            ft.Text("Resumen general de la aplicación", size=16),
            ft.Row(
                [
                    ft.Container(
                        ft.Text(f"Total de Pacientes: {total_pacientes}"),
                        padding=20, bgcolor=ft.Colors.BLUE_100, border_radius=10
                    ),
                    ft.Container(
                        ft.Text(f"Medicamentos Activos: {total_medicamentos}"),
                        padding=20, bgcolor=ft.Colors.GREEN_100, border_radius=10
                    ),
                    ft.Container(
                        ft.Text(f"Citas Programadas: {total_citas}"),
                        padding=20, bgcolor=ft.Colors.ORANGE_100, border_radius=10
                    ),
                ],
                spacing=20,
                alignment=ft.MainAxisAlignment.CENTER
            ),
            ft.Container(
                ft.ElevatedButton(
                    "Cerrar Sesión",
                    icon=ft.Icons.EXIT_TO_APP,
                    bgcolor=ft.Colors.RED_300,
                    color="white",
                    on_click=cerrar_sesion
                ),
                margin=20
            )
        ],
        spacing=30,
        horizontal_alignment=ft.CrossAxisAlignment.CENTER
    )



def pacientes_form(page: ft.Page):
    transacciones = crud.Consultas()
    doctor_id = obtener_doctor_id(page)

    # --- Controles del formulario
    nombre = ft.TextField(label="Nombre completo", width=300)
    telefono = ft.TextField(label="Teléfono", width=300)
    domicilio = ft.TextField(label="Domicilio", width=300)
    correo = ft.TextField(label="Correo electrónico", width=300)

    dialog = ft.AlertDialog(
        modal=True,
        title=ft.Text("Nuevo Paciente"),
        content=ft.Column([nombre, telefono, domicilio, correo], spacing=10),
        actions=[
            ft.TextButton("Cancelar", on_click=lambda e: cerrar_dialogos(page)),
            ft.TextButton(
                "Guardar", 
                on_click=lambda e: guardar_paciente(page, doctor_id, nombre, telefono, domicilio, correo)
            ),
        ],
        actions_alignment=ft.MainAxisAlignment.END,
    )

    page.dialog = dialog
    page.overlay.append(dialog)

    # Contenedor para recargar la lista de pacientes
    lista_container = ft.Column()
    page.pacientes_container = lista_container

    cargar_lista_pacientes(page, doctor_id)

    return ft.Column([
        ft.Text("Gestión de Pacientes", size=24, weight="bold"),
        ft.ElevatedButton("Agregar nuevo paciente", on_click=lambda e: mostrar_dialogos(page, dialog)),
        ft.Divider(),
        ft.Text("Lista de pacientes registrados:", size=18),
        lista_container
    ], spacing=20)


def cargar_lista_pacientes(page: ft.Page, doctor_id):
    transacciones = crud.Consultas()
    pacientes = transacciones.obtener_pacientes_por_doctor(doctor_id)

    if not pacientes:
        lista = [ft.Text("No hay pacientes registrados.")]
    else:
        lista = [
            ft.Container(
                content=ft.Row([
                    ft.Text(f"{p['nombre']} - {p['telefono']} - {p['correo_electronico']} - {p['domicilio']}"),
                    ft.IconButton(
                        icon=ft.Icons.DELETE,
                        icon_color=ft.Colors.RED,
                        tooltip="Eliminar",
                        on_click=lambda e, id=p["id"]: eliminar_paciente(page, doctor_id, id)
                    )
                ]),
                padding=10,
                bgcolor=ft.Colors.GREY_100,
                border_radius=10
            )
            for p in pacientes
        ]
    
    page.pacientes_container.controls = lista
    page.update()
    
    doctor_id = obtener_doctor_id(page)
    actualizar_datos_dashboard(page, doctor_id)
    if hasattr(page, "dashboard_container"):
        page.dashboard_container.content = dashboard_form(page)
        page.update()



def guardar_paciente(page, doctor_id, nombre, telefono, domicilio, correo):
    transacciones = crud.Consultas()

    if not all([nombre.value, telefono.value, domicilio.value, correo.value]):
        page.snack_bar = ft.SnackBar(ft.Text("Completa todos los campos."), bgcolor=ft.Colors.RED)
        page.snack_bar.open = True
        page.update()
        return

    exito = transacciones.crear_paciente(
        nombre.value.strip(), telefono.value.strip(), domicilio.value.strip(), correo.value.strip(), doctor_id
    )

    if exito:
        cerrar_dialogos(page)
        page.snack_bar = ft.SnackBar(ft.Text("Paciente registrado correctamente."), bgcolor=ft.Colors.GREEN)
        page.snack_bar.open = True

        cargar_lista_pacientes(page, doctor_id)

    else:
        page.snack_bar = ft.SnackBar(ft.Text("Error al registrar paciente."), bgcolor=ft.Colors.RED)
        page.snack_bar.open = True
        page.update()


def eliminar_paciente(page: ft.Page, doctor_id, paciente_id):
    transacciones = crud.Consultas()

    if transacciones.eliminar_paciente(paciente_id):
        page.snack_bar = ft.SnackBar(ft.Text("Paciente eliminado."), bgcolor=ft.Colors.GREEN)
        page.snack_bar.open = True

        cargar_lista_pacientes(page, doctor_id)

    else:
        page.snack_bar = ft.SnackBar(ft.Text("Error al eliminar paciente."), bgcolor=ft.Colors.RED)
        page.snack_bar.open = True
        page.update()

def medicamentos_form(page: ft.Page):
    transacciones = crud.Consultas()

    def construir_lista_medicamentos():
        medicamentos = transacciones.obtener_medicamentos()
        if not medicamentos:
            return ft.Column([ft.Text("No hay medicamentos registrados.")])
        return ft.Column([
            ft.Container(
                content=ft.Row([
                    ft.Text(f"{m['id']} - {m['nombre']} - {m['ingrediente_activo']} - {m['fecha_caducidad']}"),
                    ft.IconButton(
                        icon=ft.Icons.DELETE,
                        icon_color=ft.Colors.RED_400,
                        tooltip="Eliminar",
                        on_click=lambda e, id=m["id"]: eliminar_medicamento(page, id)
                    ),
                ]),
                padding=10,
                bgcolor=ft.Colors.GREY_100,
                border_radius=10
            ) for m in medicamentos
        ])

    # Contenedor para insertar la lista actualizable
    page.medicamentos_container = ft.Container(content=construir_lista_medicamentos())

    # Campos del formulario
    nombre = ft.TextField(label="Nombre del medicamento", width=300)
    ingrediente_activo = ft.TextField(label="Ingrediente activo", width=300)
    fecha_caducidad = ft.TextField(label="Fecha de caducidad (YYYY-MM-DD)", width=300)

    # Crear diálogo
    dialog = ft.AlertDialog(
        modal=True,
        title=ft.Text("Nuevo Medicamento"),
        content=ft.Column(
            controls=[nombre, ingrediente_activo, fecha_caducidad],
            spacing=10,
            tight=True
        ),
        actions=[
            ft.TextButton("Cancelar", on_click=lambda e: cerrar_dialogos(page)),
            ft.TextButton("Guardar", on_click=lambda e: guardar_medicamento(page, dialog, nombre, ingrediente_activo, fecha_caducidad))
        ],
        actions_alignment=ft.MainAxisAlignment.END
    )

    page.dialog = dialog
    page.overlay.append(dialog)

    return ft.Column(
        [
            ft.Text("Gestión de Medicamentos", size=24, weight="bold"),
            ft.ElevatedButton(
                text="Registrar nuevo medicamento",
                on_click=lambda e: mostrar_dialogos(page, dialog)
            ),
            ft.Divider(),
            ft.Text("Lista de medicamentos disponibles:", size=18),
            page.medicamentos_container
        ],
        spacing=20
    )


def guardar_medicamento(page, dialog, nombre, ingrediente_activo, fecha_caducidad):
    transacciones = crud.Consultas()

    if not all([nombre.value, ingrediente_activo.value, fecha_caducidad.value]):
        page.snack_bar = ft.SnackBar(ft.Text("Completa todos los campos."), bgcolor=ft.Colors.RED)
        page.snack_bar.open = True
        page.update()
        return

    exito = transacciones.crear_medicamento(
        nombre.value.strip(), ingrediente_activo.value.strip(), fecha_caducidad.value.strip()
    )

    if exito:
        cerrar_dialogos(page)
        page.snack_bar = ft.SnackBar(ft.Text("Medicamento registrado correctamente."), bgcolor=ft.Colors.GREEN)
        page.snack_bar.open = True

        actualizar_lista_medicamentos(page)

    else:
        page.snack_bar = ft.SnackBar(ft.Text("Error al registrar medicamento."), bgcolor=ft.Colors.RED)
        page.snack_bar.open = True
        page.update()


def eliminar_medicamento(page: ft.Page, medicamento_id):
    transacciones = crud.Consultas()
    if transacciones.eliminar_medicamento(medicamento_id):
        page.snack_bar = ft.SnackBar(ft.Text("Medicamento eliminado."), bgcolor=ft.Colors.GREEN)
        page.snack_bar.open = True
        actualizar_lista_medicamentos(page)
    else:
        page.snack_bar = ft.SnackBar(ft.Text("Error al eliminar medicamento."), bgcolor=ft.Colors.RED)
        page.snack_bar.open = True
        page.update()


def actualizar_lista_medicamentos(page):
    transacciones = crud.Consultas()
    medicamentos = transacciones.obtener_medicamentos()

    if not medicamentos:
        page.medicamentos_container.content = ft.Column([ft.Text("No hay medicamentos registrados.")])
    else:
        page.medicamentos_container.content = ft.Column([
            ft.Container(
                content=ft.Row([
                    ft.Text(f"{m['id']} - {m['nombre']} - {m['ingrediente_activo']} - {m['fecha_caducidad']}"),
                    ft.IconButton(
                        icon=ft.Icons.DELETE,
                        icon_color=ft.Colors.RED_400,
                        tooltip="Eliminar",
                        on_click=lambda e, id=m["id"]: eliminar_medicamento(page, id)
                    ),
                ]),
                padding=10,
                bgcolor=ft.Colors.GREY_100,
                border_radius=10
            )
            for m in medicamentos
        ])
    page.update()

    doctor_id = obtener_doctor_id(page)
    actualizar_datos_dashboard(page, doctor_id)

    if hasattr(page, "dashboard_container"):
        page.dashboard_container.content = dashboard_form(page)
        page.update()



def citas_form(page: ft.Page, doctor_id=None):
    transacciones = crud.Consultas()
    usuario = page.session.get("usuario")

    if not usuario or "id" not in usuario:
        page.go("/login")
        return ft.Text("Redirigiendo al inicio de sesión...")

    doctor_id = usuario["id"]

    citas = transacciones.obtener_citas_del_doctor(doctor_id)

    def boton_eliminar_cita(cita_id):
        return ft.IconButton(
            icon=ft.Icons.DELETE,
            icon_color=ft.Colors.RED,
            tooltip="Eliminar cita",
            on_click=lambda e: eliminar_cita(page, cita_id)
        )

    if not citas:
        lista_citas = [ft.Text("No hay citas registradas.")]
    else:
        lista_citas = [
            ft.Container(
                content=ft.Row([
                    ft.Text(
                        f"{cita['pacientes']['nombre']} - {cita['fecha']} {cita['hora']} - "
                        f"{cita['especialidad']} - {cita['diagnostico']}"
                    ),
                    boton_eliminar_cita(cita["id"])
                ]),
                padding=10,
                bgcolor=ft.Colors.GREY_100,
                border_radius=10
            )
            for cita in citas
        ]

    # Obtener lista de pacientes
    pacientes = transacciones.obtener_pacientes_por_doctor(doctor_id)
    dropdown_pacientes = ft.Dropdown(
        label="Seleccionar paciente",
        options=[ft.dropdown.Option(str(p["id"]), text=p["nombre"]) for p in pacientes],
        width=250
    )

    # Obtener lista de medicamentos
    medicamentos = transacciones.obtener_medicamentos()
    dropdown_medicamentos = ft.Dropdown(
        label="Seleccionar medicamento",
        options=[
            ft.dropdown.Option(str(m["id"]), text=f"{m['id']} - {m['nombre']}: {m['ingrediente_activo']}")
            for m in medicamentos
        ],
        width=250
    )

    # Campos del formulario
    fecha = ft.TextField(label="Fecha de cita (YYYY-MM-DD)", width=250)
    hora = ft.TextField(label="Hora de cita (HH:MM)", width=250)
    especialidad = ft.TextField(label="Especialidad", width=250)
    diagnostico = ft.TextField(label="Diagnóstico (opcional)", width=250)

    fecha_toma = ft.TextField(label="Fecha de toma (YYYY-MM-DD)", width=250)
    hora_toma = ft.TextField(label="Hora de toma (HH:MM)", width=250)

    dialog = ft.AlertDialog(
        modal=True,
        title=ft.Text("Programar nueva cita"),
        content=ft.Column(
            controls=[
                fecha, hora, especialidad, dropdown_pacientes,
                dropdown_medicamentos, fecha_toma, hora_toma, diagnostico
            ],
            spacing=10
        ),
        actions=[
            ft.TextButton("Cerrar", on_click=lambda e: cerrar_dialogos(page)),
            ft.TextButton("Guardar", on_click=lambda e: guardar_cita(
                page, dialog, fecha, hora, especialidad,
                dropdown_pacientes, dropdown_medicamentos,
                fecha_toma, hora_toma, doctor_id, diagnostico
            ))
        ],
        actions_alignment=ft.MainAxisAlignment.END
    )

    page.dialog = dialog
    if dialog not in page.overlay:
        page.overlay.append(dialog)

    citas_container = ft.Container(
        content=ft.ListView(
            controls=lista_citas,
            expand=True,
            spacing=10
        )
    )
    page.citas_container = citas_container

    return ft.Column(
        [
            ft.Text("Agenda de Citas", size=24, weight="bold"),
            ft.ElevatedButton(text="Programar nueva cita", on_click=lambda e: mostrar_dialogos(page, dialog)),
            ft.Divider(),
            ft.Text("Citas programadas:", size=18),
            citas_container
        ],
        spacing=20
    )
    
def guardar_cita(page, dialog, fecha, hora, especialidad,
                 dropdown_pacientes, dropdown_medicamentos,
                 fecha_toma, hora_toma, doctor_id, diagnostico):
    transacciones = crud.Consultas()

    campos_obligatorios = [
        fecha.value, hora.value, especialidad.value,
        dropdown_pacientes.value, dropdown_medicamentos.value,
        fecha_toma.value, hora_toma.value
    ]

    if not all(campos_obligatorios):
        page.snack_bar = ft.SnackBar(ft.Text("Completa todos los campos obligatorios."), bgcolor=ft.Colors.RED)
        page.snack_bar.open = True
        page.update()
        return

    exito = transacciones.crear_cita_y_registrar_toma(
        fecha.value.strip(),
        hora.value.strip(),
        especialidad.value.strip(),
        doctor_id,
        int(dropdown_pacientes.value),
        int(dropdown_medicamentos.value),
        fecha_toma.value.strip(),
        hora_toma.value.strip(),
        diagnostico.value.strip() or ""
    )

    if exito:

        # Actualiza solo la lista de citas sin reconstruir todo
        nuevas_citas = transacciones.obtener_citas_del_doctor(doctor_id)

        page.citas_container.content.controls = [
            ft.Container(
                content=ft.Row([
                    ft.Text(
                        f"{cita['pacientes']['nombre']} - {cita['fecha']} {cita['hora']} - "
                        f"{cita['especialidad']} - {cita['diagnostico']}"
                    ),
                    ft.IconButton(
                        icon=ft.Icons.DELETE,
                        icon_color=ft.Colors.RED,
                        tooltip="Eliminar cita",
                        on_click=lambda e, cita_id=cita["id"]: eliminar_cita(page, cita_id)
                    )
                ]),
                padding=10,
                bgcolor=ft.Colors.GREY_100,
                border_radius=10
            )
            for cita in nuevas_citas
        ]

        # Notificación y actualización
        page.snack_bar = ft.SnackBar(ft.Text("Cita registrada correctamente."), bgcolor=ft.Colors.GREEN)
        page.snack_bar.open = True
        page.update()
    
        doctor_id = obtener_doctor_id(page)
        actualizar_datos_dashboard(page, doctor_id)
    
        if hasattr(page, "dashboard_container"):
            page.dashboard_container.content = dashboard_form(page)
            page.update()

    else:
        page.snack_bar = ft.SnackBar(ft.Text("Error al registrar la cita."), bgcolor=ft.Colors.RED)
        page.snack_bar.open = True
        page.update()


def eliminar_cita(page: ft.Page, cita_id):
    transacciones = crud.Consultas()
    if transacciones.eliminar_cita(cita_id):
        page.snack_bar = ft.SnackBar(ft.Text("Cita eliminada."), bgcolor=ft.Colors.GREEN)
        page.snack_bar.open = True

        # Recuperar el doctor_id desde la sesión
        usuario = page.session.get("usuario")
        doctor_id = usuario["id"] if usuario else None

        # Actualizar solo la lista de citas
        nuevas_citas = transacciones.obtener_citas_del_doctor(doctor_id)
        page.citas_container.content.controls = [
            ft.Container(
                content=ft.Row([
                    ft.Text(
                        f"{cita['pacientes']['nombre']} - {cita['fecha']} {cita['hora']} - "
                        f"{cita['especialidad']} - {cita['diagnostico']}"
                    ),
                    ft.IconButton(
                        icon=ft.Icons.DELETE,
                        icon_color=ft.Colors.RED,
                        tooltip="Eliminar cita",
                        on_click=lambda e, cita_id=cita["id"]: eliminar_cita(page, cita_id)
                    )
                ]),
                padding=10,
                bgcolor=ft.Colors.GREY_100,
                border_radius=10
            )
            for cita in nuevas_citas
        ]
        page.update()
    
        doctor_id = obtener_doctor_id(page)
        actualizar_datos_dashboard(page, doctor_id)

        if hasattr(page, "dashboard_container"):
            page.dashboard_container.content = dashboard_form(page)
            page.update()


    else:
        page.snack_bar = ft.SnackBar(ft.Text("Error al eliminar la cita."), bgcolor=ft.Colors.RED)
        page.snack_bar.open = True
        page.update()


def reportes_form(page: ft.Page):
    transacciones = crud.Consultas()
    usuario = page.session.get("usuario")

    # Redirigir si no hay usuario válido
    if not usuario or "id" not in usuario:
        page.go("/login")
        return ft.Text("Redirigiendo al inicio de sesión...")

    doctor_id = usuario["id"]
    pacientes = transacciones.obtener_pacientes_por_doctor(doctor_id)

    # Dropdown para seleccionar paciente
    dropdown_pacientes = ft.Dropdown(
        label="Seleccionar paciente",
        options=[ft.dropdown.Option(str(p["id"]), text=p["nombre"]) for p in pacientes],
        width=300,
        autofocus=True
    )

    # Dropdown para seleccionar tipo de reporte
    dropdown_reporte = ft.Dropdown(
        label="Seleccionar tipo de reporte",
        options=[
            ft.dropdown.Option("medicamentos", "Historial de medicamentos"),
            ft.dropdown.Option("citas", "Citas médicas"),
            ft.dropdown.Option("signos", "Signos vitales"),
        ],
        width=300,
    )

    # Contenedor para mostrar el reporte
    reporte_resultado = ft.Column(spacing=10)

    # Función para mostrar mensajes Snackbar reutilizable
    def mostrar_snackbar(texto: str, color=ft.Colors.RED):
        page.snack_bar = ft.SnackBar(content=ft.Text(texto), bgcolor=color)
        page.snack_bar.open = True
        page.update()

    # Función para cargar y mostrar reporte según selección
    def actualizar_reporte(e):
        paciente_id = dropdown_pacientes.value
        tipo_reporte = dropdown_reporte.value
        reporte_resultado.controls.clear()

        if not paciente_id or not tipo_reporte:
            mostrar_snackbar("Selecciona un paciente y un tipo de reporte.")
            return

        paciente_id_int = int(paciente_id)

        if tipo_reporte == "citas":
            datos = transacciones.obtener_citas(paciente_id_int, usar_vista=True)
            if datos:
                for cita in datos:
                    reporte_resultado.controls.append(
                        ft.Text(f"[{cita['fecha']}]-({cita['hora']}) - {cita['especialidad']} - {cita.get('diagnostico') or 'Sin diagnóstico'}")
                    )
            else:
                reporte_resultado.controls.append(ft.Text("No hay citas registradas."))

        elif tipo_reporte == "medicamentos":
            datos = transacciones.obtener_tomas(paciente_id_int, usar_vista=True)
            if datos:
                citas = {}
                for toma in datos:
                    cita_id = toma["cita_id"]
                    if cita_id not in citas:
                        citas[cita_id] = {
                            "fecha_cita": toma["fecha_cita"],
                            "hora_cita": toma["hora_cita"],
                            "especialidad": toma["especialidad"],
                            "diagnostico": toma.get("diagnostico"),
                            "tomas": []
                        }
                    citas[cita_id]["tomas"].append(toma)

                for info in citas.values():
                    reporte_resultado.controls.append(
                        ft.Text(
                            f"Cita: {info['fecha_cita']} {info['hora_cita']} - {info['especialidad']} - {info['diagnostico'] or 'Sin diagnóstico'}",
                            weight="bold"
                        )
                    )
                    for toma in info["tomas"]:
                        confirmado = "Confirmado" if toma["confirmacion"] else "No confirmado"
                        reporte_resultado.controls.append(
                            ft.Text(
                                f"  {toma['fecha_toma']} {toma['hora_toma']} - {toma['medicamento']} ({toma['ingrediente_activo']}) - {confirmado}"
                            )
                        )
            else:
                reporte_resultado.controls.append(ft.Text("No hay registros de medicamentos."))

        elif tipo_reporte == "signos":
            datos = transacciones.obtener_signos(paciente_id_int, usar_vista=True)
            if datos:
                for signo in datos:
                    reporte_resultado.controls.append(
                        ft.Text(f"{signo['fecha_hora']} - {signo['tipo']}: {signo['valor']}")
                    )
            else:
                reporte_resultado.controls.append(ft.Text("No hay signos vitales registrados."))

        page.update()

    def generar_pdf_click(e):
        print("Entra a generar_pdf_click...")
        paciente_id = dropdown_pacientes.value
        tipo_reporte = dropdown_reporte.value

        if not paciente_id or not tipo_reporte:
            mostrar_snackbar("Selecciona un paciente y un tipo de reporte.")
            return

        # Obtener nombre del paciente desde el Dropdown
        nombre_paciente = next(
            (opt.text for opt in dropdown_pacientes.options if opt.key == paciente_id),
            "paciente"
        ).lower().replace(" ", "_")

        #datos = transacciones.obtener_citas(paciente_id, usar_vista=True)

        fecha_str = datetime.now().strftime("%Y-%m-%d_%H-%M")
        filename = f"[{fecha_str}]_({tipo_reporte})_{nombre_paciente}.pdf"

        titulo = f"Reporte de {tipo_reporte.capitalize()}"
        datos_html = ""

        for control in reporte_resultado.controls:
            if isinstance(control, ft.Text):
                datos_html += f'<div class="linea">{control.value}</div>'

        try:
            print("Mandamos los datos")
            if generar_reporte_pdf(titulo, datos_html, filename):
                mostrar_snackbar(f"PDF generado como {filename}", color=ft.Colors.GREEN)
                print("PDF generado correctamente")
            else:
                print("Algo salio mal en generar_pdf_click...")
            
        except Exception as ex:
            mostrar_snackbar(f"Error al generar el PDF: {str(ex)}")
            print("Sale de generar_pdf_click...")


    # Botones para ver reporte y generar PDF
    btn_ver_reporte = ft.ElevatedButton("Ver reporte", on_click=actualizar_reporte)
    btn_generar_pdf = ft.ElevatedButton(
        text="Generar PDF",
        icon=ft.Icons.PICTURE_AS_PDF,
        on_click=generar_pdf_click,
        bgcolor=ft.Colors.BLUE,
        color=ft.Colors.WHITE
    )

    # Composición final del formulario
    return ft.Column(
        [
            ft.Text("Generar Reportes en PDF", size=24, weight="bold"),
            ft.Row([dropdown_pacientes, dropdown_reporte, btn_ver_reporte], spacing=10),
            ft.Divider(),
            ft.Text("Resultado del reporte:", size=18),
            reporte_resultado,
            btn_generar_pdf
        ],
        spacing=20
    )


#---------------------------------------------------------------------------------------------------------------------------------
def generar_reporte_pdf(titulo, contenido_html, nombre_archivo="reporte.pdf"):
    
    print("Entra a la función generar_pdf_click...")
    html = f'''
    <html>
    <head>
        <title>Reporte</title>
        <style>
            body {{
                font-family: Arial, sans-serif;
                margin: 20px;
            }}
            h1 {{
                font-size: 24px;
                margin-bottom: 20px;
            }}
            .linea {{
                margin-bottom: 8px;
                font-size: 14px;
                color: #333;
            }}
        </style>
    </head>
    <body>
        <h1>{titulo}</h1>
        {contenido_html}
    </body>
    </html>
    '''
    try:
        with tempfile.NamedTemporaryFile(delete=False, suffix=".html", mode="w", encoding="utf-8") as tmpfile:
            tmpfile.write(html)
            tmpfile_path = tmpfile.name
        options = {
            'page-size': "Letter",
            'margin-top': '0.5in',
            'margin-left': '0.5in',
            'margin-bottom': '0.5in',
            'margin-right': '0.5in',
            'encoding': 'UTF-8',
            'no-outline': None
        }
        pdfkit.from_file(tmpfile_path, nombre_archivo, options=options)
        if os.path.exists(tmpfile_path):
            os.remove(tmpfile_path)
        return True
    except Exception as ex:
        if os.path.exists(tmpfile_path):
            os.remove(tmpfile_path)
        print(f"Exception capturada: {ex}")
        print(f"Error al generar el PDF: {str(ex)}")
        return None
    finally:
        if os.path.exists(tmpfile_path):
            os.remove(tmpfile_path)
            print("Termina generar_pdf_click...")

#---------------------------------------------------------------------------------------------------------------------------------


def main(page: ft.Page):
    page.title = "Aplicación de Salud"
    page.theme_mode = ft.ThemeMode.LIGHT
    page.window_width = 1000
    page.window_height = 700

    # Diccionario de secciones y sus funciones correspondientes
    secciones = {
        "dashboard": (0, dashboard_form),
        "pacientes": (1, pacientes_form),
        "medicamentos": (2, medicamentos_form),
        "citas": (3, citas_form),
        "reportes": (4, reportes_form),
    }

    index_inicial, contenido_func = secciones.get(SECCION_INICIAL, (0, dashboard_form))

    # Referencias globales dentro de main
    nav_rail = None
    contenedor_principal = None
    index_actual = index_inicial

    def redirigir_por_sesion():
        if page.session.get("usuario"):
            page.go("/dashboard")
        else:
            page.go("/login")

    def navegar_a(index):
        nonlocal index_actual
        index_actual = index
        if contenedor_principal is not None:
            formularios = [
                dashboard_form,
                pacientes_form,
                medicamentos_form,
                citas_form,
                reportes_form
            ]
            contenedor_principal.content = formularios[index](page)
            contenedor_principal.update()
        if nav_rail is not None:
            nav_rail.selected_index = index
            nav_rail.update()

    def route_change(e):
        nonlocal nav_rail, contenedor_principal, index_actual
        route = e.route or "/login"
        print(f"Navegando a: {route}")

        if route.startswith("/dashboard") and not page.session.get("usuario"):
            redirigir_por_sesion()
            return

        if route not in ["/login", "/registro"] and not page.session.get("usuario"):
            redirigir_por_sesion()
            return

        page.views.clear()

        if route == "/login":
            page.views.append(
                ft.View(route="/login", controls=[login_form(page)])
            )
        elif route == "/registro":
            page.views.append(
                ft.View(route="/registro", controls=[registro_form(page)])
            )
        elif route.startswith("/dashboard"):
            # Obtener el índice del dashboard actual o usar index_inicial
            index_actual = index_inicial if route == "/dashboard" else index_actual

            nav_rail = ft.NavigationRail(
                selected_index=index_actual,
                label_type=ft.NavigationRailLabelType.ALL,
                destinations=[
                    ft.NavigationRailDestination(icon=ft.Icons.HOME, label="Dashboard"),
                    ft.NavigationRailDestination(icon=ft.Icons.PEOPLE, label="Pacientes"),
                    ft.NavigationRailDestination(icon=ft.Icons.LOCAL_PHARMACY, label="Medicamentos"),
                    ft.NavigationRailDestination(icon=ft.Icons.EVENT, label="Citas"),
                    ft.NavigationRailDestination(icon=ft.Icons.PICTURE_AS_PDF, label="Reportes"),
                ],
                on_change=lambda e: navegar_a(e.control.selected_index),
            )

            contenedor_principal = ft.Container(
                content=contenido_func(page),
                expand=True,
                padding=20
            )

            page.views.append(
                ft.View(
                    route=route,
                    controls=[
                        ft.Row(
                            [
                                nav_rail,
                                ft.VerticalDivider(width=3),
                                contenedor_principal
                            ],
                            expand=True
                        )
                    ]
                )
            )
        else:
            redirigir_por_sesion()

        page.update()

    def view_pop(e):
        if len(page.views) > 1:
            page.views.pop()
            page.update()

    page.on_route_change = route_change
    page.on_view_pop = view_pop

    if not page.route or page.route == "/":
        redirigir_por_sesion()
    else:
        if page.route in ["/login", "/registro", "/dashboard"] or page.route.startswith("/dashboard"):
            route_change(ft.RouteChangeEvent(route=page.route))
        else:
            redirigir_por_sesion()





if __name__ == "__main__":
    ft.app(target=main, view=ft.WEB_BROWSER)