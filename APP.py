import tkinter as tk
from tkinter import messagebox
import datetime

# --- Importaciones de Módulos Propios ---
# Asegúrate de que estos archivos existan en tu carpeta
import database as dbFunciones
from departamento import Departamento
from proyecto import Proyecto
from empleado import Empleado
from api_indicador import obtener_indicadores, Mindicador

# =============================================================================
# --- CONFIGURACIÓN DE ESTILOS Y CONSTANTES ---
# =============================================================================
# Modifica estos valores para cambiar la apariencia de TODA la aplicación

FONT_TITULO = ("Segoe UI", 18, "bold")
FONT_SUBTITULO = ("Segoe UI", 12, "bold", "underline")
FONT_TEXTO = ("Segoe UI", 10)
FONT_BOTON = ("Segoe UI", 10, "bold")

COLOR_FONDO = "#f0f0f0"
COLOR_BOTON = "#e1e1e1"
COLOR_BOTON_ACTIVO = "#d4d4d4"
COLOR_TEXTO_ERROR = "#d9534f"  # Rojo suave
COLOR_TEXTO_EXITO = "#5cb85c"  # Verde suave

ANCHO_BOTON = 35           # Ancho estándar para botones
ANCHO_ENTRY = 40           # Ancho estándar para campos de texto
PADDING_ESTANDAR = 10      # Separación vertical estándar

# Variables Globales de Estado
admin_logeado = None
obj_depto_actual = None
obj_proy_actual = None


# =============================================================================
# --- FUNCIONES DE UTILIDAD (HELPERS) ---
# =============================================================================

def limpiar_formulario(lista_widgets):
    """
    Limpia el contenido de Entries y Labels de mensaje.
    """
    global obj_depto_actual, obj_proy_actual
    
    for widget in lista_widgets:
        if isinstance(widget, tk.Entry):
            widget.config(state='normal') # Asegurar que se pueda borrar aunque esté disabled
            widget.delete(0, tk.END)
        elif isinstance(widget, tk.Label):
            widget.config(text="")
    
    # Resetear objetos seleccionados al limpiar búsquedas
    obj_depto_actual = None
    obj_proy_actual = None

def cambiar_frame(frame_destino, frame_origen=None, funcion_limpieza=None):
    """
    Oculta el frame actual y muestra el destino.
    Ejecuta una función de limpieza si se proporciona.
    """
    if frame_origen:
        frame_origen.pack_forget()
    
    if funcion_limpieza:
        funcion_limpieza()
        
    frame_destino.pack(fill="both", expand=True, padx=20, pady=20)

def crear_popup_lista(titulo, datos, encabezado):
    """
    Genera una ventana emergente genérica para mostrar listas.
    Usa fuente monoespaciada para alinear columnas.
    """
    popup = tk.Toplevel(ventana)
    popup.title(titulo)
    popup.geometry("600x450")
    popup.grab_set() # Bloquea la ventana principal

    frame_lista = tk.Frame(popup)
    frame_lista.pack(pady=10, padx=10, fill="both", expand=True)

    # Scrollbars vertical y horizontal
    scrollbar_y = tk.Scrollbar(frame_lista, orient="vertical")
    scrollbar_x = tk.Scrollbar(frame_lista, orient="horizontal")
    
    # Usar fuente monoespaciada (Consolas) para alinear columnas
    lista_widget = tk.Listbox(frame_lista, 
                               yscrollcommand=scrollbar_y.set,
                               xscrollcommand=scrollbar_x.set,
                               font=("Consolas", 10),
                               width=70)
    
    scrollbar_y.config(command=lista_widget.yview)
    scrollbar_x.config(command=lista_widget.xview)
    
    scrollbar_y.pack(side="right", fill="y")
    scrollbar_x.pack(side="bottom", fill="x")
    lista_widget.pack(side="left", fill="both", expand=True)

    lista_widget.insert(tk.END, encabezado)
    lista_widget.insert(tk.END, "-" * 70)

    if not datos:
        lista_widget.insert(tk.END, "No hay datos para mostrar.")
    else:
        for item in datos:
            lista_widget.insert(tk.END, item)

    tk.Button(popup, text="Cerrar", font=FONT_BOTON, command=popup.destroy).pack(pady=10)

# --- Constructores de UI (Para no repetir código) ---

def crear_titulo(padre, texto):
    tk.Label(padre, text=texto, font=FONT_TITULO, bg=COLOR_FONDO).pack(pady=(10, 20))

def crear_input(padre, etiqueta):
    """Crea un Label y un Entry, retorna el objeto Entry"""
    tk.Label(padre, text=etiqueta, font=FONT_TEXTO, bg=COLOR_FONDO).pack(pady=(5, 0))
    entry = tk.Entry(padre, width=ANCHO_ENTRY, font=FONT_TEXTO)
    entry.pack(pady=5)
    return entry

def crear_boton(padre, texto, comando, color_texto="black"):
    btn = tk.Button(padre, text=texto, font=FONT_BOTON, width=ANCHO_BOTON, 
                    command=comando, fg=color_texto, bg=COLOR_BOTON)
    btn.pack(pady=PADDING_ESTANDAR)
    return btn

def crear_label_mensaje(padre):
    """Retorna un label vacío para mostrar errores o éxitos"""
    lbl = tk.Label(padre, text="", font=FONT_TEXTO, bg=COLOR_FONDO)
    lbl.pack(pady=5)
    return lbl


# =============================================================================
# --- LÓGICA DE NEGOCIO (Controladores) ---
# =============================================================================

# --- Admin ---

def procesar_login_admin():
    global admin_logeado
    usuario = entry_login_usuario.get()
    clave = entry_login_clave.get()
    
    resultado = dbFunciones.db_login_admin(usuario, clave)
    
    if resultado:
        admin_logeado = dbFunciones.db_buscar_admin_completo(resultado)
        if admin_logeado:
            lbl_bienvenida_admin.config(text=f"¡Bienvenido, {admin_logeado.nombre}!")
            cambiar_frame(frame_panel_admin, frame_login_admin)
            lbl_mensaje_login_admin.config(text="")
        else:
            lbl_mensaje_login_admin.config(text="Error: Datos de admin corruptos", fg=COLOR_TEXTO_ERROR)
    else:
        lbl_mensaje_login_admin.config(text="Credenciales incorrectas", fg=COLOR_TEXTO_ERROR)


def accion_cambiar_clave():
    """Procesa el cambio de contraseña del admin logueado"""
    clave_actual = entry_cambiar_clave_actual.get()
    clave_nueva = entry_cambiar_clave_nueva.get()
    clave_confirmar = entry_cambiar_clave_confirmar.get()
    
    # Validaciones
    if not admin_logeado:
        lbl_msg_cambiar_clave.config(text="Error: No hay sesión activa", fg=COLOR_TEXTO_ERROR)
        return
    
    if not clave_actual or not clave_nueva or not clave_confirmar:
        lbl_msg_cambiar_clave.config(text="Todos los campos son obligatorios", fg=COLOR_TEXTO_ERROR)
        return
    
    if clave_nueva != clave_confirmar:
        lbl_msg_cambiar_clave.config(text="Las contraseñas nuevas no coinciden", fg=COLOR_TEXTO_ERROR)
        return
    
    if len(clave_nueva) < 6:
        lbl_msg_cambiar_clave.config(text="La contraseña debe tener al menos 6 caracteres", fg=COLOR_TEXTO_ERROR)
        return
    
    # Obtener el usuario del admin logueado
    usuario_admin = dbFunciones.db_obtener_usuario_admin_por_id_empleado(admin_logeado.idEmpleado)
    
    if not usuario_admin:
        lbl_msg_cambiar_clave.config(text="Error: No se encontró el usuario", fg=COLOR_TEXTO_ERROR)
        return
    
    resultado = dbFunciones.db_cambiar_clave_admin(usuario_admin, clave_actual, clave_nueva)
    
    if resultado is True:
        lbl_msg_cambiar_clave.config(text="¡Contraseña cambiada exitosamente!", fg=COLOR_TEXTO_EXITO)
        limpiar_formulario([entry_cambiar_clave_actual, entry_cambiar_clave_nueva, entry_cambiar_clave_confirmar])
    else:
        lbl_msg_cambiar_clave.config(text=str(resultado), fg=COLOR_TEXTO_ERROR)


def accion_crear_nuevo_admin():
    """Procesa la creación de un nuevo administrador"""
    try:
        id_admin = int(entry_nuevo_admin_id.get())
        usuario = entry_nuevo_admin_usuario.get()
        clave = entry_nuevo_admin_clave.get()
        clave_confirmar = entry_nuevo_admin_clave_confirm.get()
        id_empleado = int(entry_nuevo_admin_id_emp.get())
        
        # Validaciones
        if not usuario or not clave:
            lbl_msg_crear_admin.config(text="Usuario y contraseña son obligatorios", fg=COLOR_TEXTO_ERROR)
            return
        
        if clave != clave_confirmar:
            lbl_msg_crear_admin.config(text="Las contraseñas no coinciden", fg=COLOR_TEXTO_ERROR)
            return
        
        if len(clave) < 6:
            lbl_msg_crear_admin.config(text="La contraseña debe tener al menos 6 caracteres", fg=COLOR_TEXTO_ERROR)
            return
        
        if len(usuario) < 3:
            lbl_msg_crear_admin.config(text="El usuario debe tener al menos 3 caracteres", fg=COLOR_TEXTO_ERROR)
            return
        
        resultado = dbFunciones.db_crear_nuevo_admin(id_admin, usuario, clave, id_empleado)
        
        if resultado is True:
            lbl_msg_crear_admin.config(text=f"¡Admin '{usuario}' creado exitosamente!", fg=COLOR_TEXTO_EXITO)
            limpiar_formulario([entry_nuevo_admin_id, entry_nuevo_admin_usuario, 
                              entry_nuevo_admin_clave, entry_nuevo_admin_clave_confirm, 
                              entry_nuevo_admin_id_emp])
            # Actualizar el ID sugerido
            nuevo_id = dbFunciones.db_obtener_siguiente_id_admin()
            entry_nuevo_admin_id.insert(0, str(nuevo_id))
        else:
            lbl_msg_crear_admin.config(text=str(resultado), fg=COLOR_TEXTO_ERROR)
            
    except ValueError:
        lbl_msg_crear_admin.config(text="ID Admin e ID Empleado deben ser números", fg=COLOR_TEXTO_ERROR)


def ver_lista_admins_popup():
    """Muestra un popup con la lista de administradores"""
    admins = dbFunciones.db_listar_administradores()
    datos = []
    
    if admins:
        for admin in admins:
            datos.append(f"ID: {admin['idAdmin']} | Usuario: {admin['usuario']} | Empleado: {admin['nombreEmpleado']}")
    else:
        datos.append("No hay administradores registrados.")
    
    crear_popup_lista("Lista de Administradores", datos, "ID | Usuario | Empleado Asociado")


# --- Indicadores Económicos ---

def accion_consultar_indicadores():
    """Consulta los indicadores desde la API y los muestra"""
    lbl_msg_indicadores.config(text="Consultando API...", fg="blue")
    ventana.update()
    
    indicadores = obtener_indicadores()
    
    if not indicadores:
        lbl_msg_indicadores.config(text="Error al consultar la API", fg=COLOR_TEXTO_ERROR)
        return
    
    # Limpiar el listbox
    listbox_indicadores.delete(0, tk.END)
    
    # Mostrar los indicadores
    for nombre, ind in indicadores.items():
        valor_formateado = f"${ind.valor:,.2f}" if ind.valor else "N/A"
        listbox_indicadores.insert(tk.END, f"{ind.nombre}: {valor_formateado}")
    
    lbl_msg_indicadores.config(text=f"Se encontraron {len(indicadores)} indicadores", fg=COLOR_TEXTO_EXITO)


def accion_guardar_indicadores():
    """Guarda todos los indicadores consultados en la base de datos"""
    if not admin_logeado:
        lbl_msg_indicadores.config(text="Error: No hay sesión activa", fg=COLOR_TEXTO_ERROR)
        return
    
    # Verificar si hay indicadores en el listbox
    if listbox_indicadores.size() == 0:
        lbl_msg_indicadores.config(text="Primero debe consultar los indicadores", fg=COLOR_TEXTO_ERROR)
        return
    
    lbl_msg_indicadores.config(text="Guardando indicadores...", fg="blue")
    ventana.update()
    
    # Obtener indicadores de la API
    indicadores = obtener_indicadores()
    
    if not indicadores:
        lbl_msg_indicadores.config(text="Error al consultar la API", fg=COLOR_TEXTO_ERROR)
        return
    
    # Obtener el ID del admin
    id_admin = dbFunciones.db_obtener_id_admin_por_id_empleado(admin_logeado.idEmpleado)
    
    if not id_admin:
        lbl_msg_indicadores.config(text="Error: No se encontró el ID del admin", fg=COLOR_TEXTO_ERROR)
        return
    
    # Guardar los indicadores
    resultados = dbFunciones.db_registrar_multiples_indicadores(indicadores, id_admin)
    
    if resultados['exitosos'] > 0:
        lbl_msg_indicadores.config(
            text=f"Guardados: {resultados['exitosos']} | Fallidos: {resultados['fallidos']}", 
            fg=COLOR_TEXTO_EXITO
        )
    else:
        lbl_msg_indicadores.config(text="Error al guardar los indicadores", fg=COLOR_TEXTO_ERROR)


def ver_historial_indicadores_popup():
    """Muestra el historial de indicadores guardados en un popup con tabla ordenada"""
    historial = dbFunciones.db_obtener_historial_indicadores(100)
    
    # Crear ventana popup
    popup = tk.Toplevel(ventana)
    popup.title("Historial de Indicadores")
    popup.geometry("700x500")
    popup.grab_set()
    popup.config(bg=COLOR_FONDO)
    
    # Título
    tk.Label(popup, text="Historial de Indicadores Económicos", 
             font=FONT_TITULO, bg=COLOR_FONDO).pack(pady=10)
    
    # Frame para la tabla con scrollbar
    frame_tabla = tk.Frame(popup, bg=COLOR_FONDO)
    frame_tabla.pack(pady=10, padx=15, fill="both", expand=True)
    
    # Scrollbars
    scroll_y = tk.Scrollbar(frame_tabla, orient="vertical")
    scroll_x = tk.Scrollbar(frame_tabla, orient="horizontal")
    
    # Listbox con fuente monoespaciada para alineación
    lista = tk.Listbox(frame_tabla, 
                       yscrollcommand=scroll_y.set,
                       xscrollcommand=scroll_x.set,
                       font=("Consolas", 10),
                       width=80,
                       height=18)
    
    scroll_y.config(command=lista.yview)
    scroll_x.config(command=lista.xview)
    
    scroll_y.pack(side="right", fill="y")
    scroll_x.pack(side="bottom", fill="x")
    lista.pack(side="left", fill="both", expand=True)
    
    if historial:
        # Agrupar por fecha de consulta
        fecha_consulta_actual = None
        
        for ind in historial:
            fecha_consulta = ind['fecha_consulta'].strftime("%d/%m/%Y") if ind['fecha_consulta'] else "N/A"
            
            # Si cambia la fecha de consulta, agregar separador
            if fecha_consulta != fecha_consulta_actual:
                if fecha_consulta_actual is not None:
                    lista.insert(tk.END, "")
                    lista.insert(tk.END, "─" * 75)
                    lista.insert(tk.END, "")
                
                # Encabezado de la consulta
                lista.insert(tk.END, f"📅 Consulta del {fecha_consulta}")
                lista.insert(tk.END, f"{'Indicador':<35} {'Valor':>15} {'Fecha Valor':>12} {'Admin':>10}")
                lista.insert(tk.END, "─" * 75)
                fecha_consulta_actual = fecha_consulta
            
            fecha_val = ind['fecha_valor'].strftime("%d/%m/%Y") if ind['fecha_valor'] else "N/A"
            valor_fmt = f"${ind['valor']:>,.2f}" if ind['valor'] else "N/A"
            nombre = ind['nombre'][:33] + ".." if len(ind['nombre']) > 35 else ind['nombre']
            admin = ind['admin'][:8] + ".." if len(ind['admin']) > 10 else ind['admin']
            
            linea = f"{nombre:<35} {valor_fmt:>15} {fecha_val:>12} {admin:>10}"
            lista.insert(tk.END, linea)
    else:
        lista.insert(tk.END, "")
        lista.insert(tk.END, "      No hay indicadores registrados.")
    
    # Información adicional
    tk.Label(popup, text=f"Total de registros: {len(historial)}", 
             font=FONT_TEXTO, bg=COLOR_FONDO, fg="gray").pack(pady=5)
    
    # Botón cerrar
    tk.Button(popup, text="Cerrar", font=FONT_BOTON, width=15,
              command=popup.destroy, bg=COLOR_BOTON).pack(pady=10)


# --- Empleado ---

def procesar_ingreso_empleado():
    """Valida el RUT y lleva al panel de registro de horas"""
    rut = entry_login_rut_empleado.get()
    
    if not rut:
        lbl_mensaje_login_emp.config(text="Debe ingresar un RUT", fg=COLOR_TEXTO_ERROR)
        return

    empleado_obj = dbFunciones.db_buscar_id_empleado_por_rut(rut)
    
    if isinstance(empleado_obj, Empleado):
        # Pre-llenar formulario de horas
        entry_horas_id_emp.config(state='normal')
        entry_horas_id_emp.delete(0, tk.END)
        entry_horas_id_emp.insert(0, str(empleado_obj.idEmpleado))
        entry_horas_id_emp.config(state='disabled')
        
        fecha_hoy = datetime.datetime.now().strftime("%Y-%m-%d")
        entry_horas_fecha.config(state='normal')
        entry_horas_fecha.delete(0, tk.END)
        entry_horas_fecha.insert(0, fecha_hoy)
        entry_horas_fecha.config(state='disabled')
        
        cambiar_frame(frame_registrar_horas, frame_login_empleado)
        entry_login_rut_empleado.delete(0, tk.END)
    else:
        lbl_mensaje_login_emp.config(text="RUT no encontrado", fg=COLOR_TEXTO_ERROR)

def procesar_busqueda_editar_empleado():
    """Busca empleado por RUT para llenar el formulario de edición"""
    rut = entry_editar_rut_busqueda.get()
    
    if not rut:
        lbl_mensaje_editar_busqueda.config(text="Ingrese RUT", fg=COLOR_TEXTO_ERROR)
        return
        
    empleado_obj = dbFunciones.db_buscar_id_empleado_por_rut(rut)
    
    if isinstance(empleado_obj, Empleado):
        # Llenar campos
        campos_map = {
            entry_ed_rut: rut,
            entry_ed_nombre: empleado_obj.nombre,
            entry_ed_direccion: empleado_obj.direccion,
            entry_ed_telefono: empleado_obj.telefono,
            entry_ed_correo: empleado_obj.correo,
            entry_ed_salario: str(empleado_obj.salario),
            entry_ed_id_emp: str(empleado_obj.idEmpleado),
            entry_ed_fecha: empleado_obj.fechaInicioContrato
        }
        
        # ID Depto es especial porque puede ser None
        id_depto = str(empleado_obj.departamento.idDepartamento) if empleado_obj.departamento else ""
        campos_map[entry_ed_id_depto] = id_depto

        for widget, valor in campos_map.items():
            widget.config(state='normal')
            widget.delete(0, tk.END)
            widget.insert(0, valor)
            
        # Bloquear campos que no deben editarse
        entry_ed_rut.config(state='disabled')
        entry_ed_id_emp.config(state='disabled')
        entry_ed_fecha.config(state='disabled')
        entry_ed_id_depto.config(state='disabled')
        
        cambiar_frame(frame_form_editar_empleado, frame_editar_busqueda_empleado)
    else:
        lbl_mensaje_editar_busqueda.config(text="Empleado no encontrado", fg=COLOR_TEXTO_ERROR)

# --- Departamentos ---

def accion_crear_departamento():
    id_str = entry_crear_depto_id.get().strip()
    nombre = entry_crear_depto_nombre.get().strip()
    id_gerente_str = entry_crear_depto_gerente.get().strip()

    if not (id_str and nombre):
        lbl_msg_crear_depto.config(text="ID y Nombre son obligatorios", fg=COLOR_TEXTO_ERROR)
        return

    try:
        id_d = int(id_str)
        
        # Gerente es opcional
        gerente = None
        if id_gerente_str:
            id_g = int(id_gerente_str)
            gerente = dbFunciones.db_buscar_empleado_por_id(id_g)
            if not gerente:
                lbl_msg_crear_depto.config(text="El gerente especificado no existe", fg=COLOR_TEXTO_ERROR)
                return
        
        if admin_logeado is not None:
            if admin_logeado.crearDepartamento(id_d, nombre, gerente):
                msg = "Departamento Creado" if gerente else "Departamento Creado (sin gerente)"
                lbl_msg_crear_depto.config(text=msg, fg=COLOR_TEXTO_EXITO)
                limpiar_formulario([entry_crear_depto_id, entry_crear_depto_nombre, entry_crear_depto_gerente])
            else:
                lbl_msg_crear_depto.config(text="Error al crear (¿ID Duplicado?)", fg=COLOR_TEXTO_ERROR)
        else:
            lbl_msg_crear_depto.config(text="Error: No hay sesión activa", fg=COLOR_TEXTO_ERROR)
    except ValueError:
        lbl_msg_crear_depto.config(text="IDs deben ser números", fg=COLOR_TEXTO_ERROR)
    except Exception as e:
        lbl_msg_crear_depto.config(text=f"Error: {e}", fg=COLOR_TEXTO_ERROR)

def accion_buscar_departamento():
    global obj_depto_actual
    try:
        id_d = int(entry_buscar_depto_id.get())
        depto = dbFunciones.db_buscar_departamento_por_id(id_d)
        
        if depto:
            nombre_gerente = depto.gerente.nombre if depto.gerente else "Sin Asignar"
            lbl_res_depto_nombre.config(text=f"Departamento: {depto.nombre}")
            lbl_res_depto_gerente.config(text=f"Gerente: {nombre_gerente}")
            obj_depto_actual = depto
            lbl_msg_buscar_depto.config(text="")
        else:
            lbl_msg_buscar_depto.config(text="No encontrado", fg=COLOR_TEXTO_ERROR)
            obj_depto_actual = None
    except ValueError:
        lbl_msg_buscar_depto.config(text="ID inválido", fg=COLOR_TEXTO_ERROR)

def ver_empleados_depto_popup():
    datos = []
    if obj_depto_actual and obj_depto_actual.empleados:
        for emp in obj_depto_actual.empleados:
            # Formateo con anchos fijos para alineación
            id_fmt = str(emp.idEmpleado).ljust(5)
            nombre_fmt = emp.nombre[:20].ljust(20)
            correo_fmt = (emp.correo or "N/A")[:25].ljust(25)
            datos.append(f"{id_fmt} | {nombre_fmt} | {correo_fmt}")
    elif not obj_depto_actual:
        datos.append("Seleccione un departamento primero.")
    else:
        datos.append("Este departamento no tiene empleados.")
    
    crear_popup_lista("Empleados del Departamento", datos, f"{'ID':<5} | {'Nombre':<20} | {'Correo':<25}")

def ver_todos_departamentos_popup():
    """Muestra un popup con la lista de todos los departamentos"""
    try:
        departamentos = dbFunciones.db_listar_todos_departamentos()
        datos = []
        
        if departamentos and len(departamentos) > 0:
            for depto in departamentos:
                # Formateo con anchos fijos para alineación
                id_fmt = str(depto['idDepartamento']).ljust(5)
                nombre_fmt = depto['nombre'][:25].ljust(25)
                gerente_fmt = depto['gerente'][:20].ljust(20)
                datos.append(f"{id_fmt} | {nombre_fmt} | {gerente_fmt}")
        else:
            datos.append("No hay departamentos registrados.")
        
        crear_popup_lista("Todos los Departamentos", datos, f"{'ID':<5} | {'Nombre':<25} | {'Gerente':<20}")
    except Exception as e:
        crear_popup_lista("Error", [f"Error al cargar departamentos: {str(e)}"], "Error")

def ver_todos_empleados_popup():
    """Muestra un popup con la lista de todos los empleados"""
    try:
        empleados = dbFunciones.db_listar_todos_empleados()
        datos = []
        
        if empleados and len(empleados) > 0:
            for emp in empleados:
                # Formateo con anchos fijos para alineación
                id_fmt = str(emp['idEmpleado']).ljust(5)
                nombre_fmt = emp['nombre'][:18].ljust(18)
                correo_fmt = (emp['correo'] or "N/A")[:20].ljust(20)
                salario_fmt = f"${emp['salario']:>10,.0f}" if emp['salario'] else "N/A".rjust(11)
                depto_fmt = emp['departamento'][:12].ljust(12)
                datos.append(f"{id_fmt} | {nombre_fmt} | {correo_fmt} | {salario_fmt} | {depto_fmt}")
        else:
            datos.append("No hay empleados registrados.")
        
        crear_popup_lista("Todos los Empleados", datos, f"{'ID':<5} | {'Nombre':<18} | {'Correo':<20} | {'Salario':>11} | {'Depto':<12}")
    except Exception as e:
        crear_popup_lista("Error", [f"Error al cargar empleados: {str(e)}"], "Error")

def ver_todos_proyectos_popup():
    """Muestra un popup con la lista de todos los proyectos"""
    try:
        proyectos = dbFunciones.db_listar_todos_proyectos()
        datos = []
        
        if proyectos and len(proyectos) > 0:
            for proy in proyectos:
                # Formateo con anchos fijos para alineación
                id_fmt = str(proy['idProyecto']).ljust(5)
                nombre_fmt = proy['nombre'][:25].ljust(25)
                fecha_fmt = proy['fechaInicio'].ljust(12)
                emp_fmt = str(proy['numEmpleados']).rjust(3)
                datos.append(f"{id_fmt} | {nombre_fmt} | {fecha_fmt} | {emp_fmt}")
        else:
            datos.append("No hay proyectos registrados.")
        
        crear_popup_lista("Todos los Proyectos", datos, f"{'ID':<5} | {'Nombre':<25} | {'Fecha':<12} | {'#Emp':>3}")
    except Exception as e:
        crear_popup_lista("Error", [f"Error al cargar proyectos: {str(e)}"], "Error")

def accion_editar_departamento():
    try:
        id_d = int(entry_edit_depto_id.get())
        nom = entry_edit_depto_nom.get()
        id_g = int(entry_edit_depto_ger.get())
        
        if not nom: raise ValueError("Falta nombre")
        
        gerente = dbFunciones.db_buscar_empleado_por_id(id_g)
        if not gerente:
             lbl_msg_edit_depto.config(text="Gerente no existe", fg=COLOR_TEXTO_ERROR)
             return

        if dbFunciones.db_actualizar_departamento(id_d, nom, id_g):
            lbl_msg_edit_depto.config(text="Actualizado correctamente", fg=COLOR_TEXTO_EXITO)
            limpiar_formulario([entry_edit_depto_id, entry_edit_depto_nom, entry_edit_depto_ger])
        else:
            lbl_msg_edit_depto.config(text="Error al actualizar", fg=COLOR_TEXTO_ERROR)
            
    except ValueError:
        lbl_msg_edit_depto.config(text="Datos inválidos", fg=COLOR_TEXTO_ERROR)

def accion_eliminar_departamento():
    try:
        id_d = int(entry_elim_depto_id.get())
        if dbFunciones.db_eliminar_departamento(id_d):
            lbl_msg_elim_depto.config(text="Eliminado correctamente", fg=COLOR_TEXTO_EXITO)
            limpiar_formulario([entry_elim_depto_id])
        else:
            lbl_msg_elim_depto.config(text="No se pudo eliminar", fg=COLOR_TEXTO_ERROR)
    except ValueError:
        lbl_msg_elim_depto.config(text="ID inválido", fg=COLOR_TEXTO_ERROR)

# --- Proyectos ---

def accion_crear_proyecto():
    try:
        id_p = int(entry_crear_proy_id.get())
        nom = entry_crear_proy_nom.get()
        fec = entry_crear_proy_fec.get()
        desc = entry_crear_proy_desc.get()

        if admin_logeado is not None:

            if admin_logeado.crearProyecto(id_p, nom, fec, desc):
                lbl_msg_crear_proy.config(text="Proyecto Creado", fg=COLOR_TEXTO_EXITO)
                limpiar_formulario([entry_crear_proy_id, entry_crear_proy_nom, entry_crear_proy_fec, entry_crear_proy_desc])
            else:
                lbl_msg_crear_proy.config(text="Error al crear", fg=COLOR_TEXTO_ERROR)
    except ValueError:
        lbl_msg_crear_proy.config(text="Datos inválidos", fg=COLOR_TEXTO_ERROR)

def accion_buscar_proyecto():
    global obj_proy_actual
    try:
        id_p = int(entry_buscar_proy_id.get())
        proy = dbFunciones.db_buscar_proyecto_por_id(id_p)
        
        if proy:
            lbl_res_proy_nombre.config(text=f"Proyecto: {proy.nombre}")
            lbl_res_proy_fecha.config(text=f"Inicio: {proy.fechaInicioProyecto}")
            lbl_res_proy_desc.config(text=f"Desc: {proy.descripcion}")
            obj_proy_actual = proy
            lbl_msg_buscar_proy.config(text="")
        else:
            lbl_msg_buscar_proy.config(text="No encontrado", fg=COLOR_TEXTO_ERROR)
            obj_proy_actual = None
    except ValueError:
        lbl_msg_buscar_proy.config(text="ID inválido", fg=COLOR_TEXTO_ERROR)

def ver_empleados_proy_popup():
    datos = []
    if obj_proy_actual and hasattr(obj_proy_actual, 'empleados') and obj_proy_actual.empleados:
        for emp in obj_proy_actual.empleados:
            datos.append(f"{emp.idEmpleado} | {emp.nombre} | {emp.correo}")
    elif not obj_proy_actual:
        datos.append("Seleccione un proyecto primero.")
    else:
        datos.append("Sin empleados asignados.")
        
    crear_popup_lista("Equipo del Proyecto", datos, "ID | Nombre | Correo")

def accion_editar_proyecto():
    try:
        id_p = int(entry_edit_proy_id.get())
        if dbFunciones.db_actualizar_proyecto(id_p, entry_edit_proy_nom.get(), entry_edit_proy_fec.get(), entry_edit_proy_desc.get()):
            lbl_msg_edit_proy.config(text="Actualizado", fg=COLOR_TEXTO_EXITO)
        else:
            lbl_msg_edit_proy.config(text="Error al actualizar", fg=COLOR_TEXTO_ERROR)
    except ValueError:
        lbl_msg_edit_proy.config(text="Datos inválidos", fg=COLOR_TEXTO_ERROR)

def accion_eliminar_proyecto():
    try:
        if dbFunciones.db_eliminar_proyecto(int(entry_elim_proy_id.get())):
            lbl_msg_elim_proy.config(text="Eliminado", fg=COLOR_TEXTO_EXITO)
        else:
            lbl_msg_elim_proy.config(text="Error al eliminar", fg=COLOR_TEXTO_ERROR)
    except ValueError:
        lbl_msg_elim_proy.config(text="ID inválido", fg=COLOR_TEXTO_ERROR)

# --- Relaciones (Asignaciones) ---

def accion_asignar_empleado_proyecto():
    try:
        res = dbFunciones.db_asignar_proyecto_empleado(int(entry_asig_ep_idemp.get()), int(entry_asig_ep_idproy.get()))
        if res is True:
             lbl_msg_asig_ep.config(text="Asignado correctamente", fg=COLOR_TEXTO_EXITO)
        else:
             lbl_msg_asig_ep.config(text=str(res), fg=COLOR_TEXTO_ERROR)
    except ValueError:
        lbl_msg_asig_ep.config(text="Datos numéricos requeridos", fg=COLOR_TEXTO_ERROR)

def accion_eliminar_empleado_proyecto():
    try:
        if dbFunciones.db_eliminar_proyecto_empleado(int(entry_elim_ep_idproy.get()), int(entry_elim_ep_idemp.get())):
             lbl_msg_elim_ep.config(text="Desvinculado correctamente", fg=COLOR_TEXTO_EXITO)
        else:
             lbl_msg_elim_ep.config(text="No existe relación", fg=COLOR_TEXTO_ERROR)
    except ValueError:
        lbl_msg_elim_ep.config(text="Datos numéricos requeridos", fg=COLOR_TEXTO_ERROR)

def accion_asignar_empleado_depto():
    try:
        id_e = int(entry_asig_ed_idemp.get())
        id_d = int(entry_asig_ed_iddepto.get())
        
        if dbFunciones.db_verificar_empleado_en_depto(id_e, id_d):
             lbl_msg_asig_ed.config(text="Ya pertenece al depto", fg="orange")
             return
             
        if dbFunciones.db_asignar_departamento_empleado(id_e, id_d) is True:
             lbl_msg_asig_ed.config(text="Asignado correctamente", fg=COLOR_TEXTO_EXITO)
        else:
             lbl_msg_asig_ed.config(text="Error al asignar", fg=COLOR_TEXTO_ERROR)
    except ValueError:
         lbl_msg_asig_ed.config(text="Datos numéricos requeridos", fg=COLOR_TEXTO_ERROR)

def accion_eliminar_empleado_depto():
    try:
        res = dbFunciones.db_eliminar_departamento_empleado(int(entry_elim_ed_idemp.get()))
        if res is True:
            lbl_msg_elim_ed.config(text="Eliminado del depto", fg=COLOR_TEXTO_EXITO)
        else:
            lbl_msg_elim_ed.config(text=str(res), fg=COLOR_TEXTO_ERROR)
    except ValueError:
        lbl_msg_elim_ed.config(text="ID inválido", fg=COLOR_TEXTO_ERROR)

# --- Empleados CRUD ---

def accion_crear_empleado():
    try:
        nuevo = Empleado(
            entry_crear_emp_nom.get(), 
            entry_crear_emp_dir.get(), 
            entry_crear_emp_tel.get(),
            entry_crear_emp_cor.get(),
            int(entry_crear_emp_id.get()),
            entry_crear_emp_fec.get(),
            int(entry_crear_emp_sal.get())
        )
        # Departamento es opcional - si está vacío, usar None
        depto_str = entry_crear_emp_depto.get().strip()
        id_depto = int(depto_str) if depto_str else None
        
        if dbFunciones.db_crear_empleado(entry_crear_emp_rut.get(), nuevo, id_depto):
            lbl_msg_crear_emp.config(text="Empleado Creado", fg=COLOR_TEXTO_EXITO)
            # Limpiar campos aquí si se desea
        else:
            lbl_msg_crear_emp.config(text="Error al crear", fg=COLOR_TEXTO_ERROR)
    except ValueError:
        lbl_msg_crear_emp.config(text="Verifique los datos numéricos", fg=COLOR_TEXTO_ERROR)

def accion_buscar_empleado():
    try:
        emp = dbFunciones.db_buscar_empleado_por_id(int(entry_buscar_emp_id.get()))
        if emp:
            lbl_res_emp_nombre.config(text=f"Nombre: {emp.nombre}")
            lbl_res_emp_correo.config(text=f"Correo: {emp.correo}")
            lbl_res_emp_salario.config(text=f"Salario: ${emp.salario}")
            dept_nom = emp.departamento.nombre if emp.departamento else "Sin Depto"
            lbl_res_emp_depto.config(text=f"Depto: {dept_nom}")
            lbl_msg_buscar_emp.config(text="")
        else:
             lbl_msg_buscar_emp.config(text="No encontrado", fg=COLOR_TEXTO_ERROR)
    except ValueError:
         lbl_msg_buscar_emp.config(text="ID inválido", fg=COLOR_TEXTO_ERROR)

def accion_actualizar_empleado():
    try:
        rut = entry_ed_rut.get()
        
        if not rut or rut == "None":
            lbl_msg_ed_emp.config(text="Error: No se encontró el RUT del usuario", fg=COLOR_TEXTO_ERROR)
            return
        
        exito = dbFunciones.db_actualizar_empleado(
            int(entry_ed_id_emp.get()),
            entry_ed_nombre.get(),
            entry_ed_direccion.get(),
            entry_ed_telefono.get(),
            entry_ed_correo.get(),
            float(entry_ed_salario.get()),
            rut
        )
        if exito:
            lbl_msg_ed_emp.config(text="Datos actualizados correctamente", fg=COLOR_TEXTO_EXITO)
            # Esperar un momento antes de volver a la búsqueda
            ventana.after(1500, lambda: cambiar_frame(frame_editar_busqueda_empleado, frame_form_editar_empleado, 
                                                       lambda: limpiar_formulario([entry_editar_rut_busqueda, lbl_mensaje_editar_busqueda, lbl_msg_ed_emp])))
        else:
            lbl_msg_ed_emp.config(text="Error al actualizar", fg=COLOR_TEXTO_ERROR)
    except ValueError as e:
        lbl_msg_ed_emp.config(text=f"Datos inválidos: {str(e)}", fg=COLOR_TEXTO_ERROR)
    except Exception as e:
        lbl_msg_ed_emp.config(text=f"Error: {str(e)}", fg=COLOR_TEXTO_ERROR)

def accion_registrar_horas():
    try:
        res = dbFunciones.db_registrar_horas(
            int(entry_horas_id_emp.get()),
            int(entry_horas_id_proy.get()),
            entry_horas_fecha.get(),
            int(entry_horas_cant.get()),
            entry_horas_desc.get()
        )
        if res is True:
            lbl_msg_horas.config(text="Horas registradas", fg=COLOR_TEXTO_EXITO)
        else:
            lbl_msg_horas.config(text=f"Error: {res}", fg=COLOR_TEXTO_ERROR)
    except ValueError:
        lbl_msg_horas.config(text="Datos numéricos inválidos", fg=COLOR_TEXTO_ERROR)


# =============================================================================
# --- CONSTRUCCIÓN DE LA INTERFAZ GRÁFICA ---
# =============================================================================

ventana = tk.Tk()
ventana.title("Sistema de Gestión Empresarial")
ventana.geometry("550x800")
ventana.config(bg=COLOR_FONDO)

# -----------------------------------------------------------------------------
# 1. FRAME INICIO
# -----------------------------------------------------------------------------
frame_inicio = tk.Frame(ventana, bg=COLOR_FONDO)
crear_titulo(frame_inicio, "Sistema de Gestión")
crear_boton(frame_inicio, "Entrar como Administrador", lambda: cambiar_frame(frame_login_admin, frame_inicio))
crear_boton(frame_inicio, "Entrar como Empleado", lambda: cambiar_frame(frame_login_empleado, frame_inicio))
frame_inicio.pack(fill="both", expand=True, padx=20, pady=20)

# -----------------------------------------------------------------------------
# 2. FRAME LOGIN ADMIN
# -----------------------------------------------------------------------------
frame_login_admin = tk.Frame(ventana, bg=COLOR_FONDO)
crear_titulo(frame_login_admin, "Acceso Administrativo")
entry_login_usuario = crear_input(frame_login_admin, "Usuario:")
entry_login_clave = crear_input(frame_login_admin, "Contraseña:")
entry_login_clave.config(show="*")
lbl_mensaje_login_admin = crear_label_mensaje(frame_login_admin)

crear_boton(frame_login_admin, "Ingresar", procesar_login_admin)
crear_boton(frame_login_admin, "Volver", 
            lambda: cambiar_frame(frame_inicio, frame_login_admin, lambda: limpiar_formulario([entry_login_usuario, entry_login_clave, lbl_mensaje_login_admin])))

# -----------------------------------------------------------------------------
# 3. FRAME PANEL ADMIN PRINCIPAL
# -----------------------------------------------------------------------------
frame_panel_admin = tk.Frame(ventana, bg=COLOR_FONDO)
lbl_bienvenida_admin = tk.Label(frame_panel_admin, text="Bienvenido Admin", font=FONT_TITULO, bg=COLOR_FONDO)
lbl_bienvenida_admin.pack(pady=20)

crear_boton(frame_panel_admin, "Gestión de Departamentos", lambda: cambiar_frame(frame_gest_deptos, frame_panel_admin))
crear_boton(frame_panel_admin, "Gestión de Proyectos", lambda: cambiar_frame(frame_gest_proyectos, frame_panel_admin))
crear_boton(frame_panel_admin, "Gestión de Empleados", lambda: cambiar_frame(frame_gest_empleados, frame_panel_admin))
crear_boton(frame_panel_admin, "Gestión de Administradores", lambda: cambiar_frame(frame_gest_admins, frame_panel_admin))
crear_boton(frame_panel_admin, "Indicadores Económicos", lambda: cambiar_frame(frame_indicadores, frame_panel_admin))
crear_boton(frame_panel_admin, "Cambiar mi Contraseña", lambda: cambiar_frame(frame_cambiar_clave, frame_panel_admin))
crear_boton(frame_panel_admin, "Cerrar Sesión", lambda: cambiar_frame(frame_inicio, frame_panel_admin, lambda: limpiar_formulario([entry_login_usuario, entry_login_clave, lbl_mensaje_login_admin])), color_texto=COLOR_TEXTO_ERROR)

# -----------------------------------------------------------------------------
# 3.1 FRAME INDICADORES ECONÓMICOS
# -----------------------------------------------------------------------------
frame_indicadores = tk.Frame(ventana, bg=COLOR_FONDO)
crear_titulo(frame_indicadores, "Indicadores Económicos")

tk.Label(frame_indicadores, text="Datos desde mindicador.cl", font=FONT_SUBTITULO, bg=COLOR_FONDO).pack(pady=5)

# Frame para el listbox con scrollbar
frame_lista_ind = tk.Frame(frame_indicadores, bg=COLOR_FONDO)
frame_lista_ind.pack(pady=10, padx=20, fill="both", expand=True)

scrollbar_ind = tk.Scrollbar(frame_lista_ind, orient="vertical")
listbox_indicadores = tk.Listbox(frame_lista_ind, yscrollcommand=scrollbar_ind.set, font=FONT_TEXTO, height=10, width=50)
scrollbar_ind.config(command=listbox_indicadores.yview)
scrollbar_ind.pack(side="right", fill="y")
listbox_indicadores.pack(side="left", fill="both", expand=True)

lbl_msg_indicadores = crear_label_mensaje(frame_indicadores)

def limpiar_indicadores():
    """Limpia el listbox y el mensaje de indicadores"""
    listbox_indicadores.delete(0, tk.END)
    lbl_msg_indicadores.config(text="")
    ventana.update()

def accion_limpiar_historial():
    """Limpia todo el historial de indicadores de la base de datos"""
    respuesta = messagebox.askyesno(
        "Confirmar", 
        "¿Está seguro de que desea eliminar TODO el historial de indicadores?\n\nEsta acción no se puede deshacer."
    )
    if respuesta:
        resultado = dbFunciones.db_limpiar_historial_indicadores()
        if resultado is True:
            lbl_msg_indicadores.config(text="Historial limpiado correctamente", fg=COLOR_TEXTO_EXITO)
        else:
            lbl_msg_indicadores.config(text=str(resultado), fg=COLOR_TEXTO_ERROR)

crear_boton(frame_indicadores, "Consultar Indicadores (API)", accion_consultar_indicadores)
crear_boton(frame_indicadores, "Guardar en Base de Datos", accion_guardar_indicadores)
crear_boton(frame_indicadores, "Ver Historial Guardado", ver_historial_indicadores_popup)
crear_boton(frame_indicadores, "Limpiar Historial", accion_limpiar_historial, color_texto=COLOR_TEXTO_ERROR)

def volver_panel_desde_indicadores():
    limpiar_indicadores()
    cambiar_frame(frame_panel_admin, frame_indicadores)

crear_boton(frame_indicadores, "Volver al Panel", volver_panel_desde_indicadores)

# -----------------------------------------------------------------------------
# 3.2 FRAME CAMBIAR CONTRASEÑA
# -----------------------------------------------------------------------------
frame_cambiar_clave = tk.Frame(ventana, bg=COLOR_FONDO)
crear_titulo(frame_cambiar_clave, "Cambiar Contraseña")

entry_cambiar_clave_actual = crear_input(frame_cambiar_clave, "Contraseña Actual:")
entry_cambiar_clave_actual.config(show="*")
entry_cambiar_clave_nueva = crear_input(frame_cambiar_clave, "Nueva Contraseña:")
entry_cambiar_clave_nueva.config(show="*")
entry_cambiar_clave_confirmar = crear_input(frame_cambiar_clave, "Confirmar Nueva Contraseña:")
entry_cambiar_clave_confirmar.config(show="*")

lbl_msg_cambiar_clave = crear_label_mensaje(frame_cambiar_clave)
crear_boton(frame_cambiar_clave, "Cambiar Contraseña", accion_cambiar_clave)
crear_boton(frame_cambiar_clave, "Volver", lambda: cambiar_frame(frame_panel_admin, frame_cambiar_clave, 
            lambda: limpiar_formulario([entry_cambiar_clave_actual, entry_cambiar_clave_nueva, 
                                        entry_cambiar_clave_confirmar, lbl_msg_cambiar_clave])))

# -----------------------------------------------------------------------------
# 3.3 FRAME GESTIÓN DE ADMINISTRADORES
# -----------------------------------------------------------------------------
frame_gest_admins = tk.Frame(ventana, bg=COLOR_FONDO)
crear_titulo(frame_gest_admins, "Gestión de Administradores")

crear_boton(frame_gest_admins, "Crear Nuevo Administrador", lambda: ir_a_crear_admin())
crear_boton(frame_gest_admins, "Ver Lista de Administradores", ver_lista_admins_popup)
crear_boton(frame_gest_admins, "Volver al Panel", lambda: cambiar_frame(frame_panel_admin, frame_gest_admins))

def ir_a_crear_admin():
    """Prepara el formulario de creación de admin con el siguiente ID"""
    limpiar_formulario([entry_nuevo_admin_id, entry_nuevo_admin_usuario, 
                       entry_nuevo_admin_clave, entry_nuevo_admin_clave_confirm, 
                       entry_nuevo_admin_id_emp, lbl_msg_crear_admin])
    nuevo_id = dbFunciones.db_obtener_siguiente_id_admin()
    entry_nuevo_admin_id.insert(0, str(nuevo_id))
    cambiar_frame(frame_crear_admin, frame_gest_admins)

# Frame Crear Nuevo Admin
frame_crear_admin = tk.Frame(ventana, bg=COLOR_FONDO)
crear_titulo(frame_crear_admin, "Crear Nuevo Administrador")

entry_nuevo_admin_id = crear_input(frame_crear_admin, "ID Admin (sugerido):")
entry_nuevo_admin_usuario = crear_input(frame_crear_admin, "Nombre de Usuario:")
entry_nuevo_admin_clave = crear_input(frame_crear_admin, "Contraseña:")
entry_nuevo_admin_clave.config(show="*")
entry_nuevo_admin_clave_confirm = crear_input(frame_crear_admin, "Confirmar Contraseña:")
entry_nuevo_admin_clave_confirm.config(show="*")
entry_nuevo_admin_id_emp = crear_input(frame_crear_admin, "ID Empleado Asociado:")

lbl_msg_crear_admin = crear_label_mensaje(frame_crear_admin)
crear_boton(frame_crear_admin, "Crear Administrador", accion_crear_nuevo_admin)
crear_boton(frame_crear_admin, "Volver", lambda: cambiar_frame(frame_gest_admins, frame_crear_admin, 
            lambda: limpiar_formulario([entry_nuevo_admin_id, entry_nuevo_admin_usuario, 
                                        entry_nuevo_admin_clave, entry_nuevo_admin_clave_confirm, 
                                        entry_nuevo_admin_id_emp, lbl_msg_crear_admin])))

# -----------------------------------------------------------------------------
# 4. SUB-MENU: GESTIÓN DEPARTAMENTOS
# -----------------------------------------------------------------------------
frame_gest_deptos = tk.Frame(ventana, bg=COLOR_FONDO)
crear_titulo(frame_gest_deptos, "Menú Departamentos")

crear_boton(frame_gest_deptos, "Ver Todos los Departamentos", ver_todos_departamentos_popup)
crear_boton(frame_gest_deptos, "Crear Departamento", 
            lambda: cambiar_frame(frame_crear_depto, frame_gest_deptos))
crear_boton(frame_gest_deptos, "Buscar / Ver Departamento", 
            lambda: cambiar_frame(frame_buscar_depto, frame_gest_deptos))
crear_boton(frame_gest_deptos, "Editar Departamento", 
            lambda: cambiar_frame(frame_editar_depto, frame_gest_deptos))
crear_boton(frame_gest_deptos, "Eliminar Departamento", 
            lambda: cambiar_frame(frame_eliminar_depto, frame_gest_deptos))
crear_boton(frame_gest_deptos, "Asignar Empleado a Depto", 
            lambda: cambiar_frame(frame_asig_emp_depto, frame_gest_deptos))
crear_boton(frame_gest_deptos, "Quitar Empleado de Depto", 
            lambda: cambiar_frame(frame_elim_emp_depto, frame_gest_deptos))

crear_boton(frame_gest_deptos, "Volver al Panel", lambda: cambiar_frame(frame_panel_admin, frame_gest_deptos))

# --- Formularios Depto ---

# Crear
frame_crear_depto = tk.Frame(ventana, bg=COLOR_FONDO)
crear_titulo(frame_crear_depto, "Crear Departamento")
entry_crear_depto_id = crear_input(frame_crear_depto, "ID Departamento:")
entry_crear_depto_nombre = crear_input(frame_crear_depto, "Nombre:")
entry_crear_depto_gerente = crear_input(frame_crear_depto, "ID Gerente (opcional):")
tk.Label(frame_crear_depto, text="* Si no se coloca gerente, se asignará como nulo", 
         font=("Segoe UI", 9, "italic"), fg="gray", bg=COLOR_FONDO).pack(pady=(0, 5))
lbl_msg_crear_depto = crear_label_mensaje(frame_crear_depto)
crear_boton(frame_crear_depto, "Guardar", accion_crear_departamento)
crear_boton(frame_crear_depto, "Volver", lambda: cambiar_frame(frame_gest_deptos, frame_crear_depto, lambda: limpiar_formulario([entry_crear_depto_id, entry_crear_depto_nombre, entry_crear_depto_gerente, lbl_msg_crear_depto])))

# Buscar
frame_buscar_depto = tk.Frame(ventana, bg=COLOR_FONDO)
crear_titulo(frame_buscar_depto, "Buscar Departamento")
entry_buscar_depto_id = crear_input(frame_buscar_depto, "ID Departamento:")
crear_boton(frame_buscar_depto, "Buscar", accion_buscar_departamento)
lbl_msg_buscar_depto = crear_label_mensaje(frame_buscar_depto)
# Resultados
lbl_res_depto_nombre = tk.Label(frame_buscar_depto, text="", font=FONT_TEXTO, bg=COLOR_FONDO); lbl_res_depto_nombre.pack()
lbl_res_depto_gerente = tk.Label(frame_buscar_depto, text="", font=FONT_TEXTO, bg=COLOR_FONDO); lbl_res_depto_gerente.pack()
crear_boton(frame_buscar_depto, "Ver Lista Empleados", ver_empleados_depto_popup)
crear_boton(frame_buscar_depto, "Volver", lambda: cambiar_frame(frame_gest_deptos, frame_buscar_depto, lambda: limpiar_formulario([entry_buscar_depto_id, lbl_msg_buscar_depto, lbl_res_depto_nombre, lbl_res_depto_gerente])))

# Editar
frame_editar_depto = tk.Frame(ventana, bg=COLOR_FONDO)
crear_titulo(frame_editar_depto, "Editar Departamento")
entry_edit_depto_id = crear_input(frame_editar_depto, "ID Departamento (Original):")
entry_edit_depto_nom = crear_input(frame_editar_depto, "Nuevo Nombre:")
entry_edit_depto_ger = crear_input(frame_editar_depto, "Nuevo ID Gerente:")
lbl_msg_edit_depto = crear_label_mensaje(frame_editar_depto)
crear_boton(frame_editar_depto, "Actualizar", accion_editar_departamento)
crear_boton(frame_editar_depto, "Volver", lambda: cambiar_frame(frame_gest_deptos, frame_editar_depto, lambda: limpiar_formulario([entry_edit_depto_id, entry_edit_depto_nom, entry_edit_depto_ger, lbl_msg_edit_depto])))

# Eliminar
frame_eliminar_depto = tk.Frame(ventana, bg=COLOR_FONDO)
crear_titulo(frame_eliminar_depto, "Eliminar Departamento")
entry_elim_depto_id = crear_input(frame_eliminar_depto, "ID Departamento:")
lbl_msg_elim_depto = crear_label_mensaje(frame_eliminar_depto)
crear_boton(frame_eliminar_depto, "Eliminar Definitivamente", accion_eliminar_departamento)
crear_boton(frame_eliminar_depto, "Volver", lambda: cambiar_frame(frame_gest_deptos, frame_eliminar_depto, lambda: limpiar_formulario([entry_elim_depto_id, lbl_msg_elim_depto])))

# Asignar Empleado a Depto
frame_asig_emp_depto = tk.Frame(ventana, bg=COLOR_FONDO)
crear_titulo(frame_asig_emp_depto, "Agregar Empleado a Depto")
entry_asig_ed_idemp = crear_input(frame_asig_emp_depto, "ID Empleado:")
entry_asig_ed_iddepto = crear_input(frame_asig_emp_depto, "ID Departamento:")
lbl_msg_asig_ed = crear_label_mensaje(frame_asig_emp_depto)
crear_boton(frame_asig_emp_depto, "Asignar", accion_asignar_empleado_depto)
crear_boton(frame_asig_emp_depto, "Volver", lambda: cambiar_frame(frame_gest_deptos, frame_asig_emp_depto, lambda: limpiar_formulario([entry_asig_ed_idemp, entry_asig_ed_iddepto, lbl_msg_asig_ed])))

# Eliminar Empleado de Depto
frame_elim_emp_depto = tk.Frame(ventana, bg=COLOR_FONDO)
crear_titulo(frame_elim_emp_depto, "Quitar Empleado de Depto")
entry_elim_ed_idemp = crear_input(frame_elim_emp_depto, "ID Empleado:")
lbl_msg_elim_ed = crear_label_mensaje(frame_elim_emp_depto)
crear_boton(frame_elim_emp_depto, "Desvincular", accion_eliminar_empleado_depto)
crear_boton(frame_elim_emp_depto, "Volver", lambda: cambiar_frame(frame_gest_deptos, frame_elim_emp_depto, lambda: limpiar_formulario([entry_elim_ed_idemp, lbl_msg_elim_ed])))


# -----------------------------------------------------------------------------
# 5. SUB-MENU: GESTIÓN PROYECTOS
# -----------------------------------------------------------------------------
frame_gest_proyectos = tk.Frame(ventana, bg=COLOR_FONDO)
crear_titulo(frame_gest_proyectos, "Menú Proyectos")
crear_boton(frame_gest_proyectos, "Ver Todos los Proyectos", ver_todos_proyectos_popup)
crear_boton(frame_gest_proyectos, "Crear Proyecto", lambda: cambiar_frame(frame_crear_proy, frame_gest_proyectos))
crear_boton(frame_gest_proyectos, "Buscar / Ver Proyecto", lambda: cambiar_frame(frame_buscar_proy, frame_gest_proyectos))
crear_boton(frame_gest_proyectos, "Editar Proyecto", lambda: cambiar_frame(frame_editar_proy, frame_gest_proyectos))
crear_boton(frame_gest_proyectos, "Eliminar Proyecto", lambda: cambiar_frame(frame_eliminar_proy, frame_gest_proyectos))
crear_boton(frame_gest_proyectos, "Asignar Empleado a Proyecto", lambda: cambiar_frame(frame_asig_emp_proy, frame_gest_proyectos))
crear_boton(frame_gest_proyectos, "Quitar Empleado de Proyecto", lambda: cambiar_frame(frame_elim_emp_proy, frame_gest_proyectos))
crear_boton(frame_gest_proyectos, "Volver al Panel", lambda: cambiar_frame(frame_panel_admin, frame_gest_proyectos))

# --- Formularios Proyecto ---

# Crear
frame_crear_proy = tk.Frame(ventana, bg=COLOR_FONDO)
crear_titulo(frame_crear_proy, "Crear Proyecto")
entry_crear_proy_id = crear_input(frame_crear_proy, "ID Proyecto:")
entry_crear_proy_nom = crear_input(frame_crear_proy, "Nombre:")
entry_crear_proy_fec = crear_input(frame_crear_proy, "Fecha Inicio:")
entry_crear_proy_desc = crear_input(frame_crear_proy, "Descripción:")
lbl_msg_crear_proy = crear_label_mensaje(frame_crear_proy)
crear_boton(frame_crear_proy, "Guardar", accion_crear_proyecto)
crear_boton(frame_crear_proy, "Volver", lambda: cambiar_frame(frame_gest_proyectos, frame_crear_proy, lambda: limpiar_formulario([entry_crear_proy_id, entry_crear_proy_nom, entry_crear_proy_fec, entry_crear_proy_desc, lbl_msg_crear_proy])))

# Buscar
frame_buscar_proy = tk.Frame(ventana, bg=COLOR_FONDO)
crear_titulo(frame_buscar_proy, "Buscar Proyecto")
entry_buscar_proy_id = crear_input(frame_buscar_proy, "ID Proyecto:")
crear_boton(frame_buscar_proy, "Buscar", accion_buscar_proyecto)
lbl_msg_buscar_proy = crear_label_mensaje(frame_buscar_proy)
lbl_res_proy_nombre = tk.Label(frame_buscar_proy, text="", font=FONT_TEXTO, bg=COLOR_FONDO); lbl_res_proy_nombre.pack()
lbl_res_proy_fecha = tk.Label(frame_buscar_proy, text="", font=FONT_TEXTO, bg=COLOR_FONDO); lbl_res_proy_fecha.pack()
lbl_res_proy_desc = tk.Label(frame_buscar_proy, text="", font=FONT_TEXTO, bg=COLOR_FONDO); lbl_res_proy_desc.pack()
crear_boton(frame_buscar_proy, "Ver Equipo Asignado", ver_empleados_proy_popup)
crear_boton(frame_buscar_proy, "Volver", lambda: cambiar_frame(frame_gest_proyectos, frame_buscar_proy, lambda: limpiar_formulario([entry_buscar_proy_id, lbl_msg_buscar_proy, lbl_res_proy_nombre, lbl_res_proy_fecha, lbl_res_proy_desc])))

# Editar
frame_editar_proy = tk.Frame(ventana, bg=COLOR_FONDO)
crear_titulo(frame_editar_proy, "Editar Proyecto")
entry_edit_proy_id = crear_input(frame_editar_proy, "ID Proyecto (Original):")
entry_edit_proy_nom = crear_input(frame_editar_proy, "Nuevo Nombre:")
entry_edit_proy_fec = crear_input(frame_editar_proy, "Nueva Fecha:")
entry_edit_proy_desc = crear_input(frame_editar_proy, "Nueva Descripción:")
lbl_msg_edit_proy = crear_label_mensaje(frame_editar_proy)
crear_boton(frame_editar_proy, "Actualizar", accion_editar_proyecto)
crear_boton(frame_editar_proy, "Volver", lambda: cambiar_frame(frame_gest_proyectos, frame_editar_proy, lambda: limpiar_formulario([entry_edit_proy_id, entry_edit_proy_nom, entry_edit_proy_fec, entry_edit_proy_desc, lbl_msg_edit_proy])))

# Eliminar
frame_eliminar_proy = tk.Frame(ventana, bg=COLOR_FONDO)
crear_titulo(frame_eliminar_proy, "Eliminar Proyecto")
entry_elim_proy_id = crear_input(frame_eliminar_proy, "ID Proyecto:")
lbl_msg_elim_proy = crear_label_mensaje(frame_eliminar_proy)
crear_boton(frame_eliminar_proy, "Eliminar", accion_eliminar_proyecto)
crear_boton(frame_eliminar_proy, "Volver", lambda: cambiar_frame(frame_gest_proyectos, frame_eliminar_proy, lambda: limpiar_formulario([entry_elim_proy_id, lbl_msg_elim_proy])))

# Asignaciones Proyectos
frame_asig_emp_proy = tk.Frame(ventana, bg=COLOR_FONDO)
crear_titulo(frame_asig_emp_proy, "Asignar a Proyecto")
entry_asig_ep_idproy = crear_input(frame_asig_emp_proy, "ID Proyecto:")
entry_asig_ep_idemp = crear_input(frame_asig_emp_proy, "ID Empleado:")
lbl_msg_asig_ep = crear_label_mensaje(frame_asig_emp_proy)
crear_boton(frame_asig_emp_proy, "Asignar", accion_asignar_empleado_proyecto)
crear_boton(frame_asig_emp_proy, "Volver", lambda: cambiar_frame(frame_gest_proyectos, frame_asig_emp_proy, lambda: limpiar_formulario([entry_asig_ep_idproy, entry_asig_ep_idemp, lbl_msg_asig_ep])))

frame_elim_emp_proy = tk.Frame(ventana, bg=COLOR_FONDO)
crear_titulo(frame_elim_emp_proy, "Desvincular de Proyecto")
entry_elim_ep_idproy = crear_input(frame_elim_emp_proy, "ID Proyecto:")
entry_elim_ep_idemp = crear_input(frame_elim_emp_proy, "ID Empleado:")
lbl_msg_elim_ep = crear_label_mensaje(frame_elim_emp_proy)
crear_boton(frame_elim_emp_proy, "Eliminar Relación", accion_eliminar_empleado_proyecto)
crear_boton(frame_elim_emp_proy, "Volver", lambda: cambiar_frame(frame_gest_proyectos, frame_elim_emp_proy, lambda: limpiar_formulario([entry_elim_ep_idproy, entry_elim_ep_idemp, lbl_msg_elim_ep])))

# -----------------------------------------------------------------------------
# 6. SUB-MENU: GESTIÓN EMPLEADOS (CRUD)
# -----------------------------------------------------------------------------
frame_gest_empleados = tk.Frame(ventana, bg=COLOR_FONDO)
crear_titulo(frame_gest_empleados, "Menú Empleados")
crear_boton(frame_gest_empleados, "Ver Todos los Empleados", ver_todos_empleados_popup)
crear_boton(frame_gest_empleados, "Crear Nuevo Empleado", lambda: cambiar_frame(frame_crear_empleado, frame_gest_empleados))
crear_boton(frame_gest_empleados, "Buscar Empleado", lambda: cambiar_frame(frame_buscar_empleado, frame_gest_empleados))
crear_boton(frame_gest_empleados, "Editar Empleado", lambda: cambiar_frame(frame_editar_busqueda_empleado, frame_gest_empleados))
crear_boton(frame_gest_empleados, "Volver al Panel", lambda: cambiar_frame(frame_panel_admin, frame_gest_empleados))

# Crear Empleado
frame_crear_empleado = tk.Frame(ventana, bg=COLOR_FONDO)
crear_titulo(frame_crear_empleado, "Crear Empleado")
entry_crear_emp_rut = crear_input(frame_crear_empleado, "RUT (ID Usuario):")
entry_crear_emp_nom = crear_input(frame_crear_empleado, "Nombre:")
entry_crear_emp_dir = crear_input(frame_crear_empleado, "Dirección:")
entry_crear_emp_tel = crear_input(frame_crear_empleado, "Teléfono:")
entry_crear_emp_cor = crear_input(frame_crear_empleado, "Correo:")
entry_crear_emp_id = crear_input(frame_crear_empleado, "ID Ficha Empleado:")
entry_crear_emp_sal = crear_input(frame_crear_empleado, "Salario:")
entry_crear_emp_fec = crear_input(frame_crear_empleado, "Fecha Contrato:")
entry_crear_emp_depto = crear_input(frame_crear_empleado, "ID Depto Inicial (opcional):")
tk.Label(frame_crear_empleado, text="* Si no se coloca departamento, se asignará como nulo", 
         font=("Segoe UI", 9, "italic"), fg="gray", bg=COLOR_FONDO).pack(pady=(0, 5))
lbl_msg_crear_emp = crear_label_mensaje(frame_crear_empleado)
crear_boton(frame_crear_empleado, "Guardar", accion_crear_empleado)
crear_boton(frame_crear_empleado, "Volver", lambda: cambiar_frame(frame_gest_empleados, frame_crear_empleado, lambda: limpiar_formulario([lbl_msg_crear_emp, entry_crear_emp_rut, entry_crear_emp_nom, entry_crear_emp_dir, entry_crear_emp_tel, entry_crear_emp_cor, entry_crear_emp_id, entry_crear_emp_sal, entry_crear_emp_fec, entry_crear_emp_depto])))

# Buscar Empleado
frame_buscar_empleado = tk.Frame(ventana, bg=COLOR_FONDO)
crear_titulo(frame_buscar_empleado, "Buscar Empleado")
entry_buscar_emp_id = crear_input(frame_buscar_empleado, "ID Ficha Empleado:")
crear_boton(frame_buscar_empleado, "Buscar", accion_buscar_empleado)
lbl_msg_buscar_emp = crear_label_mensaje(frame_buscar_empleado)
# Resultados
lbl_res_emp_nombre = tk.Label(frame_buscar_empleado, text="", font=FONT_TEXTO, bg=COLOR_FONDO); lbl_res_emp_nombre.pack()
lbl_res_emp_correo = tk.Label(frame_buscar_empleado, text="", font=FONT_TEXTO, bg=COLOR_FONDO); lbl_res_emp_correo.pack()
lbl_res_emp_salario = tk.Label(frame_buscar_empleado, text="", font=FONT_TEXTO, bg=COLOR_FONDO); lbl_res_emp_salario.pack()
lbl_res_emp_depto = tk.Label(frame_buscar_empleado, text="", font=FONT_TEXTO, bg=COLOR_FONDO); lbl_res_emp_depto.pack()
crear_boton(frame_buscar_empleado, "Volver", lambda: cambiar_frame(frame_gest_empleados, frame_buscar_empleado, lambda: limpiar_formulario([entry_buscar_emp_id, lbl_msg_buscar_emp, lbl_res_emp_nombre, lbl_res_emp_correo])))

# Editar Empleado (Paso 1: Busqueda por RUT)
frame_editar_busqueda_empleado = tk.Frame(ventana, bg=COLOR_FONDO)
crear_titulo(frame_editar_busqueda_empleado, "Editar Empleado - Paso 1")
entry_editar_rut_busqueda = crear_input(frame_editar_busqueda_empleado, "Ingrese RUT del Empleado:")
lbl_mensaje_editar_busqueda = crear_label_mensaje(frame_editar_busqueda_empleado)
crear_boton(frame_editar_busqueda_empleado, "Buscar y Editar", procesar_busqueda_editar_empleado)
crear_boton(frame_editar_busqueda_empleado, "Volver", lambda: cambiar_frame(frame_gest_empleados, frame_editar_busqueda_empleado, lambda: limpiar_formulario([entry_editar_rut_busqueda, lbl_mensaje_editar_busqueda])))

# Editar Empleado (Paso 2: Formulario)
frame_form_editar_empleado = tk.Frame(ventana, bg=COLOR_FONDO)
crear_titulo(frame_form_editar_empleado, "Editando Datos")
entry_ed_rut = crear_input(frame_form_editar_empleado, "RUT (Bloqueado):")
entry_ed_nombre = crear_input(frame_form_editar_empleado, "Nombre:")
entry_ed_direccion = crear_input(frame_form_editar_empleado, "Dirección:")
entry_ed_telefono = crear_input(frame_form_editar_empleado, "Teléfono:")
entry_ed_correo = crear_input(frame_form_editar_empleado, "Correo:")
entry_ed_id_emp = crear_input(frame_form_editar_empleado, "ID Ficha (Bloqueado):")
entry_ed_salario = crear_input(frame_form_editar_empleado, "Salario:")
entry_ed_fecha = crear_input(frame_form_editar_empleado, "Fecha (Bloqueado):")
entry_ed_id_depto = crear_input(frame_form_editar_empleado, "ID Depto (Bloqueado):")
lbl_msg_ed_emp = crear_label_mensaje(frame_form_editar_empleado)
crear_boton(frame_form_editar_empleado, "Guardar Cambios", accion_actualizar_empleado)
crear_boton(frame_form_editar_empleado, "Volver", lambda: cambiar_frame(frame_editar_busqueda_empleado, frame_form_editar_empleado, lambda: limpiar_formulario([lbl_msg_ed_emp, entry_editar_rut_busqueda, lbl_mensaje_editar_busqueda])))

# -----------------------------------------------------------------------------
# 7. LOGIN EMPLEADO Y REGISTRO HORAS
# -----------------------------------------------------------------------------
frame_login_empleado = tk.Frame(ventana, bg=COLOR_FONDO)
crear_titulo(frame_login_empleado, "Acceso Empleado")
entry_login_rut_empleado = crear_input(frame_login_empleado, "Ingrese su RUT:")
lbl_mensaje_login_emp = crear_label_mensaje(frame_login_empleado)
crear_boton(frame_login_empleado, "Ingresar", procesar_ingreso_empleado)
crear_boton(frame_login_empleado, "Volver", lambda: cambiar_frame(frame_inicio, frame_login_empleado, lambda: limpiar_formulario([entry_login_rut_empleado, lbl_mensaje_login_emp])))

# Registro Horas
frame_registrar_horas = tk.Frame(ventana, bg=COLOR_FONDO)
crear_titulo(frame_registrar_horas, "Registro de Actividades")
entry_horas_id_emp = crear_input(frame_registrar_horas, "ID Empleado:")
entry_horas_id_proy = crear_input(frame_registrar_horas, "ID Proyecto:")
entry_horas_fecha = crear_input(frame_registrar_horas, "Fecha:")
entry_horas_cant = crear_input(frame_registrar_horas, "Cantidad Horas:")
entry_horas_desc = crear_input(frame_registrar_horas, "Descripción Actividad:")
lbl_msg_horas = crear_label_mensaje(frame_registrar_horas)
crear_boton(frame_registrar_horas, "Registrar", accion_registrar_horas)
crear_boton(frame_registrar_horas, "Salir", lambda: cambiar_frame(frame_login_empleado, frame_registrar_horas, lambda: limpiar_formulario([entry_horas_id_proy, entry_horas_cant, entry_horas_desc, lbl_msg_horas])))

# =============================================================================
# --- ARRANQUE ---
# =============================================================================

# Inicializar admin por defecto si no existe ninguno
dbFunciones.inicializar_admin_por_defecto()

# Iniciar en frame inicio
frame_inicio.pack(fill="both", expand=True, padx=20, pady=20)
ventana.mainloop()