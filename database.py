
import oracledb
import bcrypt 
from registro import Registro
import getpass
from empleado import Empleado
from proyecto import Proyecto
import os
from dotenv import load_dotenv
from datetime import datetime


load_dotenv()

# Leer credenciales de entorno
DB_USER = os.getenv('DB_USER')
DB_PASSWORD = os.getenv('DB_PASSWORD')
DB_DSN = os.getenv('DB_DSN')


def get_connection():
    try:
        return oracledb.connect(user=DB_USER, password=DB_PASSWORD, dsn=DB_DSN)
    except oracledb.DatabaseError as e:
        print(f"Error al conectar a la Base de Datos: {e}")
        return None


def inicializar_admin_por_defecto():
    """
    Verifica si existe al menos un administrador en la base de datos.
    Si no existe ninguno, crea un usuario, empleado y administrador por defecto.
    
    Credenciales por defecto:
    - Usuario: admin
    - Contraseña: admin123
    """
    conn = get_connection()
    if not conn:
        print("No se pudo conectar a la base de datos para verificar admin.")
        return False
    
    cursor = conn.cursor()
    
    try:
        # Verificar si ya existe al menos un administrador
        cursor.execute("SELECT COUNT(*) FROM administradores")
        count = cursor.fetchone()[0]
        
        if count > 0:
            print("Ya existe al menos un administrador. No se requiere crear uno por defecto.")
            return True
        
        print("No se encontró ningún administrador. Creando admin por defecto")
        
        # Datos del admin por defecto
        id_usuario = 1
        id_empleado = 1
        id_admin = 1
        usuario_admin = "admin"
        clave_plana = "admin123"
        
        # Verificar si el usuario base ya existe
        cursor.execute("SELECT COUNT(*) FROM usuarios WHERE idUsuario = :1", (id_usuario,))
        if cursor.fetchone()[0] == 0:
            # Crear usuario base
            cursor.execute("""
                INSERT INTO usuarios (idUsuario, nombre, direccion, telefono, correo)
                VALUES (:1, :2, :3, :4, :5)
            """, (id_usuario, "Administrador", "Sistema", "0000000000", "admin@sistema.com"))
        
        # Verificar si el empleado ya existe
        cursor.execute("SELECT COUNT(*) FROM empleados WHERE idEmpleado = :1", (id_empleado,))
        if cursor.fetchone()[0] == 0:
            # Crear empleado
            cursor.execute("""
                INSERT INTO empleados (idEmpleado, fechaInicioContrato, salario, idUsuario, idDepartamento)
                VALUES (:1, SYSDATE, 0, :2, NULL)
            """, (id_empleado, id_usuario))
        
        # Generar hash de la contraseña
        clave_hash = bcrypt.hashpw(clave_plana.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
        
        # Crear administrador
        cursor.execute("""
            INSERT INTO administradores (idAdmin, usuario, clave, idEmpleado)
            VALUES (:1, :2, :3, :4)
        """, (id_admin, usuario_admin, clave_hash, id_empleado))
        
        conn.commit()
        print("=" * 50)
        print("¡Administrador por defecto creado exitosamente!")
        print("Usuario: admin")
        print("Contraseña: admin123")
        print("¡IMPORTANTE: Cambie la contraseña después del primer inicio de sesión!")
        print("=" * 50)
        return True
        
    except oracledb.DatabaseError as e:
        print(f"Error al crear admin por defecto: {e}")
        conn.rollback()
        return False
    finally:
        cursor.close()
        conn.close()


def selectUsuarios():
    conn = get_connection()

    if not conn: return
    cursor = conn.cursor()
    
    cursor.execute("select * from registros r join empleados e on e.idEmpleado = r.idEmpleado")
    for row in cursor:
        print(row)
    cursor.close()
    conn.close()


def db_cambiar_clave_admin(usuario: str, clave_actual: str, clave_nueva: str):
    """
    Cambia la contraseña de un administrador.
    Primero verifica que la clave actual sea correcta.
    
    Returns:
        True si el cambio fue exitoso
        str con mensaje de error si falla
    """
    conn = get_connection()
    if not conn:
        return "Error de conexión a la base de datos"
    
    cursor = conn.cursor()
    
    try:
        # Verificar que el usuario existe y la clave actual es correcta
        cursor.execute("SELECT clave FROM administradores WHERE usuario = :1", (usuario,))
        resultado = cursor.fetchone()
        
        if not resultado:
            return "Usuario no encontrado"
        
        clave_hash_bd = resultado[0]
        
        # Verificar clave actual
        if not bcrypt.checkpw(clave_actual.encode('utf-8'), clave_hash_bd.encode('utf-8')):
            return "La contraseña actual es incorrecta"
        
        # Generar hash de la nueva clave
        nueva_clave_hash = bcrypt.hashpw(clave_nueva.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
        
        # Actualizar la clave
        cursor.execute("UPDATE administradores SET clave = :1 WHERE usuario = :2", (nueva_clave_hash, usuario))
        conn.commit()
        
        return True
        
    except oracledb.DatabaseError as e:
        conn.rollback()
        return f"Error de base de datos: {e}"
    finally:
        cursor.close()
        conn.close()


def db_crear_nuevo_admin(id_admin: int, usuario: str, clave_plana: str, id_empleado: int):
    """
    Crea un nuevo administrador en la base de datos.
    
    Args:
        id_admin: ID único del administrador
        usuario: Nombre de usuario para login
        clave_plana: Contraseña sin encriptar
        id_empleado: ID del empleado asociado
    
    Returns:
        True si se creó exitosamente
        str con mensaje de error si falla
    """
    conn = get_connection()
    if not conn:
        return "Error de conexión a la base de datos"
    
    cursor = conn.cursor()
    
    try:
        # Verificar que el empleado existe
        cursor.execute("SELECT COUNT(*) FROM empleados WHERE idEmpleado = :1", (id_empleado,))
        if cursor.fetchone()[0] == 0:
            return "El empleado especificado no existe"
        
        # Verificar que el ID de admin no existe
        cursor.execute("SELECT COUNT(*) FROM administradores WHERE idAdmin = :1", (id_admin,))
        if cursor.fetchone()[0] > 0:
            return "Ya existe un administrador con ese ID"
        
        # Verificar que el usuario no existe
        cursor.execute("SELECT COUNT(*) FROM administradores WHERE usuario = :1", (usuario,))
        if cursor.fetchone()[0] > 0:
            return "Ya existe un administrador con ese nombre de usuario"
        
        # Verificar que el empleado no es ya un admin
        cursor.execute("SELECT COUNT(*) FROM administradores WHERE idEmpleado = :1", (id_empleado,))
        if cursor.fetchone()[0] > 0:
            return "El empleado ya es administrador"
        
        # Generar hash de la contraseña
        clave_hash = bcrypt.hashpw(clave_plana.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
        
        # Insertar el nuevo admin
        sql = "INSERT INTO administradores (idAdmin, usuario, clave, idEmpleado) VALUES (:1, :2, :3, :4)"
        cursor.execute(sql, (id_admin, usuario, clave_hash, id_empleado))
        conn.commit()
        
        return True
        
    except oracledb.DatabaseError as e:
        conn.rollback()
        return f"Error de base de datos: {e}"
    finally:
        cursor.close()
        conn.close()


def db_obtener_siguiente_id_admin():
    """
    Obtiene el siguiente ID disponible para un nuevo administrador.
    """
    conn = get_connection()
    if not conn:
        return 1
    
    cursor = conn.cursor()
    
    try:
        cursor.execute("SELECT MAX(idAdmin) FROM administradores")
        resultado = cursor.fetchone()
        if resultado[0] is None:
            return 1
        return resultado[0] + 1
    except oracledb.DatabaseError:
        return 1
    finally:
        cursor.close()
        conn.close()


def db_obtener_usuario_admin_por_id_empleado(id_empleado: int):
    """
    Obtiene el nombre de usuario del administrador asociado a un empleado.
    """
    conn = get_connection()
    if not conn:
        return None
    
    cursor = conn.cursor()
    
    try:
        cursor.execute("SELECT usuario FROM administradores WHERE idEmpleado = :1", (id_empleado,))
        resultado = cursor.fetchone()
        if resultado:
            return resultado[0]
        return None
    except oracledb.DatabaseError:
        return None
    finally:
        cursor.close()
        conn.close()


def db_listar_administradores():
    """
    Retorna una lista de todos los administradores.
    """
    conn = get_connection()
    if not conn:
        return []
    
    cursor = conn.cursor()
    
    try:
        cursor.execute("""
            SELECT a.idAdmin, a.usuario, a.idEmpleado, u.nombre
            FROM administradores a
            LEFT JOIN empleados e ON a.idEmpleado = e.idEmpleado
            LEFT JOIN usuarios u ON e.idUsuario = u.idUsuario
            ORDER BY a.idAdmin
        """)
        admins = []
        for row in cursor.fetchall():
            admins.append({
                'idAdmin': row[0],
                'usuario': row[1],
                'idEmpleado': row[2],
                'nombreEmpleado': row[3] or "Sin nombre"
            })
        return admins
    except oracledb.DatabaseError:
        return []
    finally:
        cursor.close()
        conn.close()


# =============================================================================
# --- FUNCIONES DE INDICADORES ECONÓMICOS ---
# =============================================================================

def db_obtener_siguiente_id_indicador():
    """Obtiene el siguiente ID disponible para un indicador."""
    conn = get_connection()
    if not conn:
        return 1
    
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT MAX(idIndicadorRegistro) FROM indicadores_registrados")
        resultado = cursor.fetchone()
        if resultado[0] is None:
            return 1
        return resultado[0] + 1
    except oracledb.DatabaseError:
        return 1
    finally:
        cursor.close()
        conn.close()


def db_registrar_indicador(nombre_indicador: str, valor: float, fecha_valor: str, id_admin: int):
    """
    Registra un indicador económico en la base de datos.
    
    Args:
        nombre_indicador: Nombre del indicador (ej: "UF", "Dólar Observado")
        valor: Valor del indicador
        fecha_valor: Fecha del valor en formato string
        id_admin: ID del admin que registra
    
    Returns:
        True si se registró exitosamente, str con error si falla
    """
    conn = get_connection()
    if not conn:
        return "Error de conexión a la base de datos"
    
    cursor = conn.cursor()
    
    try:
        id_registro = db_obtener_siguiente_id_indicador()
        
        # Convertir fecha del indicador
        if isinstance(fecha_valor, str):
            # El formato viene como "2025-12-03T03:00:00.000Z" de la API
            try:
                fecha_val = datetime.strptime(fecha_valor[:10], "%Y-%m-%d").date()
            except ValueError:
                fecha_val = datetime.now().date()
        else:
            fecha_val = fecha_valor
        
        fecha_consulta = datetime.now().date()
        
        cursor.execute("""
            INSERT INTO indicadores_registrados 
            (idIndicadorRegistro, nombre_indicador, valor_indicador, fecha_valor, fecha_consulta, sitio_proveedor, id_admin_consulta)
            VALUES (:1, :2, :3, :4, :5, :6, :7)
        """, (id_registro, nombre_indicador, valor, fecha_val, fecha_consulta, "mindicador.cl", id_admin))
        
        conn.commit()
        return True
        
    except oracledb.DatabaseError as e:
        conn.rollback()
        return f"Error de base de datos: {e}"
    finally:
        cursor.close()
        conn.close()


def db_registrar_multiples_indicadores(indicadores: dict, id_admin: int):
    """
    Registra múltiples indicadores de una vez.
    
    Args:
        indicadores: Diccionario con objetos Mindicador
        id_admin: ID del admin que registra
    
    Returns:
        dict con resultados: {'exitosos': int, 'fallidos': int, 'errores': list}
    """
    resultados = {'exitosos': 0, 'fallidos': 0, 'errores': []}
    
    for nombre, indicador in indicadores.items():
        resultado = db_registrar_indicador(
            indicador.nombre,
            indicador.valor,
            indicador.fecha,
            id_admin
        )
        
        if resultado is True:
            resultados['exitosos'] += 1
        else:
            resultados['fallidos'] += 1
            resultados['errores'].append(f"{indicador.nombre}: {resultado}")
    
    return resultados


def db_obtener_historial_indicadores(limite: int = 50):
    """
    Obtiene el historial de indicadores registrados.
    
    Args:
        limite: Número máximo de registros a retornar
    
    Returns:
        Lista de diccionarios con los indicadores
    """
    conn = get_connection()
    if not conn:
        return []
    
    cursor = conn.cursor()
    
    try:
        cursor.execute("""
            SELECT i.idIndicadorRegistro, i.nombre_indicador, i.valor_indicador, 
                   i.fecha_valor, i.fecha_consulta, i.sitio_proveedor, 
                   a.usuario as admin_usuario
            FROM indicadores_registrados i
            LEFT JOIN administradores a ON i.id_admin_consulta = a.idAdmin
            ORDER BY i.fecha_consulta DESC, i.idIndicadorRegistro DESC
            FETCH FIRST :1 ROWS ONLY
        """, (limite,))
        
        indicadores = []
        for row in cursor.fetchall():
            indicadores.append({
                'id': row[0],
                'nombre': row[1],
                'valor': row[2],
                'fecha_valor': row[3],
                'fecha_consulta': row[4],
                'proveedor': row[5],
                'admin': row[6] or "Desconocido"
            })
        return indicadores
        
    except oracledb.DatabaseError as e:
        print(f"Error al obtener historial: {e}")
        return []
    finally:
        cursor.close()
        conn.close()


def db_limpiar_historial_indicadores():
    """
    Elimina todos los registros del historial de indicadores.
    
    Returns:
        True si se eliminaron correctamente, mensaje de error en caso contrario
    """
    conn = get_connection()
    if not conn:
        return "Error de conexión a la base de datos"
    
    cursor = conn.cursor()
    
    try:
        cursor.execute("DELETE FROM indicadores_registrados")
        conn.commit()
        return True
    except oracledb.DatabaseError as e:
        conn.rollback()
        return f"Error al limpiar historial: {e}"
    finally:
        cursor.close()
        conn.close()


def db_obtener_ultimo_valor_indicador(nombre_indicador: str):
    """
    Obtiene el último valor registrado de un indicador específico.
    
    Args:
        nombre_indicador: Nombre del indicador a buscar
    
    Returns:
        Diccionario con los datos o None si no existe
    """
    conn = get_connection()
    if not conn:
        return None
    
    cursor = conn.cursor()
    
    try:
        cursor.execute("""
            SELECT valor_indicador, fecha_valor, fecha_consulta
            FROM indicadores_registrados
            WHERE nombre_indicador = :1
            ORDER BY fecha_consulta DESC
            FETCH FIRST 1 ROWS ONLY
        """, (nombre_indicador,))
        
        row = cursor.fetchone()
        if row:
            return {
                'valor': row[0],
                'fecha_valor': row[1],
                'fecha_consulta': row[2]
            }
        return None
        
    except oracledb.DatabaseError:
        return None
    finally:
        cursor.close()
        conn.close()


def db_obtener_id_admin_por_id_empleado(id_empleado: int):
    """Obtiene el ID del admin asociado a un empleado."""
    conn = get_connection()
    if not conn:
        return None
    
    cursor = conn.cursor()
    
    try:
        cursor.execute("SELECT idAdmin FROM administradores WHERE idEmpleado = :1", (id_empleado,))
        resultado = cursor.fetchone()
        if resultado:
            return resultado[0]
        return None
    except oracledb.DatabaseError:
        return None
    finally:
        cursor.close()
        conn.close()


def crear_nuevo_admin(id_admin: int, usuario: str, clave_plana: str, id_empleado: int):
    from registro import Registro
    id_admin = int(input("ID de Admin: "))
    usuario = input("Usuario: ")
    clave_plana = getpass.getpass("Clave: ")
    id_empleado = int(input("ID de Empleado asociado: "))

    clave_plana_bytes = clave_plana.encode('utf-8')
    salt = bcrypt.gensalt()
    clave_hash_bytes = bcrypt.hashpw(clave_plana_bytes, salt)
    clave_hash_para_db = clave_hash_bytes.decode('utf-8')

    # 2. GUARDAR EL HASH EN LA BD
    conn = get_connection()
    if not conn: return False
    cursor = conn.cursor()
    
    ### CAMBIO AQUÍ: Nombres de columnas ###
    # Usamos "idAdmin" y "idEmpleado" exactamente como en tu DDL
    sql = "INSERT INTO administradores (idAdmin, usuario, clave, idEmpleado) VALUES (:1, :2, :3, :4)"
    
    try:
        # Los valores pasados aquí coinciden con los :1, :2, :3, :4
        cursor.execute(sql, (id_admin, usuario, clave_hash_para_db, id_empleado))
        conn.commit()
        print(f"¡Admin '{usuario}' (ID: {id_admin}) creado exitosamente!")
        return True
        
    except oracledb.DatabaseError as e:
        # Si da error de "clave única" (unique constraint), 
        # significa que el idAdmin o el usuario ya existen.
        print(f"Error al crear admin: {e}")
        conn.rollback()
        return False
    finally:
        cursor.close()
        conn.close()


# --- 1. Métodos de Login y Búsqueda (SELECT) ---

def db_login_admin(usuario: str, clave_plana: str):
    conn = get_connection()
    if not conn: return None
    cursor = conn.cursor()
    
    sql = "SELECT clave, idEmpleado FROM administradores WHERE usuario = :1"
    try:
        cursor.execute(sql, (usuario,))
        resultado = cursor.fetchone() # (clave_hash_bd, idEmpleado)
        
        if resultado:
            clave_hash_bd = resultado[0] # La clave HASH guardada
            id_empleado_admin = resultado[1]
            
            # Comparamos la clave plana con el hash de la BD
            if bcrypt.checkpw(clave_plana.encode('utf-8'), clave_hash_bd.encode('utf-8')):
                print(f"Login exitoso para {usuario}")

                return id_empleado_admin # Retornamos el ID de empleado
            else:
                print("Usuario o Contraseña no encontrado.")
                return None
        else:
            print("Usuario o Contraseña no encontrado.")
            return None
            
    except oracledb.DatabaseError as e:
        print(f"Error en login: {e}")
        return None
    finally:
        cursor.close()
        conn.close()
        
def db_buscar_proyecto_por_id(id_proyecto):
    """
    Busca un proyecto por su ID y devuelve un objeto Proyecto,
    incluyendo la lista de empleados asociados al proyecto.
    """
    from proyecto import Proyecto
    from empleado import Empleado
    conn = get_connection()
    if not conn:
        return None
    cursor = conn.cursor()

    try:
        # 1. Buscar detalles básicos del proyecto
        cursor.execute("""
            SELECT idProyecto, nombre, fechaInicioProyecto, descripcion
            FROM proyectos
            WHERE idProyecto = :1
        """, (id_proyecto,))
        proyecto_row = cursor.fetchone()
        if not proyecto_row:
            return None  # Proyecto no existe

        # 2. Buscar empleados asociados al proyecto (JOIN con usuarios)
        cursor.execute("""
            SELECT e.idEmpleado, e.fechaInicioContrato, e.salario, u.idUsuario,
                   u.nombre, u.direccion, u.telefono, u.correo
            FROM proyecto_empleados pe
            JOIN empleados e ON pe.idEmpleado = e.idEmpleado
            JOIN usuarios u ON e.idUsuario = u.idUsuario
            WHERE pe.idProyecto = :1
        """, (id_proyecto,))
        empleados_en_proyecto = []
        for row in cursor.fetchall():
            (idEmp, fechaInicio, salario, idUser, nombre, direccion, telefono, correo) = row
            emp_obj = Empleado(
                idEmpleado=idEmp,
                fechaInicioContrato=fechaInicio,
                salario=salario,
                nombre=nombre,
                direccion=direccion,
                telefono=telefono,
                correo=correo
            )
            empleados_en_proyecto.append(emp_obj)

        # 3. Crear el objeto Proyecto, incluyendo empleados (igual que departamento)
        proyecto_obj = Proyecto(
            idProyecto=proyecto_row[0],
            nombre=proyecto_row[1],
            fechaInicioProyecto=proyecto_row[2],
            descripcion=proyecto_row[3],
            empleados=empleados_en_proyecto
        )

        return proyecto_obj

    except Exception as e:
        print(f"Error al buscar proyecto: {e}")
        return None
    finally:
        cursor.close()
        conn.close()


def db_buscar_departamento_por_id(id_depto_buscado: int):
    """
    Busca un departamento por su ID en la BD y devuelve un OBJETO Departamento.
    (Necesita info de tablas 'departamentos' y 'empleados' para el gerente)
    """
    from departamento import Departamento
    conn = get_connection()
    if not conn: return None
    cursor = conn.cursor()
    
    # Unimos departamentos y empleados para tener todos los datos del gerente
    sql = """
        SELECT d.idDepartamento, d.nombre, e.idEmpleado, e.fechaInicioContrato, e.salario,
        u.idUsuario, u.nombre, u.direccion, u.telefono, u.correo
        FROM departamentos d
        LEFT JOIN empleados e ON d.idGerenteResponsable = e.idEmpleado
        LEFT JOIN usuarios u ON e.idUsuario = u.idUsuario
        WHERE d.idDepartamento = :1

    """
    sql_2 = """
        SELECT d.idDepartamento, d.nombre, e.idEmpleado, e.fechaInicioContrato, e.salario,
        u.idUsuario, u.nombre, u.direccion, u.telefono, u.correo
        FROM departamentos d
        JOIN empleados e ON d.idDepartamento = e.idDepartamento
        JOIN usuarios u ON e.idUsuario = u.idUsuario
        WHERE d.idDepartamento = :1
    """    


    empleados_en_depto = []

    try:
        cursor.execute(sql_2, (id_depto_buscado,))
        rows = cursor.fetchall()

        if not rows:
            pass
        for row in rows:
            (_, _, idEmp, fechaInicio, salario, _, nombreEmp, direccion, telefono, correo) = row
            

            empleado_obj = Empleado(
                nombre=nombreEmp,
                direccion=direccion,
                telefono=telefono,
                correo=correo,
                idEmpleado=idEmp,
                fechaInicioContrato=fechaInicio,
                salario=salario
            )
                
            empleados_en_depto.append(empleado_obj)
                
    except oracledb.DatabaseError as e:
        print(f"Error al buscar empleados en depto: {e}")
        return None


            

    try:
        cursor.execute(sql, (id_depto_buscado,))
        resultado = cursor.fetchone() 
        
        if resultado:
            # Desempaquetamos los datos
            (idDepto, nombreDepto, idEmp, fecha, salario, idUser, nombreEmp, dir, tel, correo) = resultado
            
            # Creamos el objeto Empleado para el gerente

            if idEmp is None:
                gerente_obj = None
                
            else:
                gerente_obj = Empleado(
                    nombre=nombreEmp,
                    direccion=dir, 
                    telefono=tel, 
                    correo=correo,
                    idEmpleado=idEmp, 
                    fechaInicioContrato=fecha, 
                    salario=salario
                )
            
            # ¡Creamos el objeto Departamento con los datos de la BD!
            departamento_encontrado = Departamento(
                idDepartamento=idDepto,
                nombre=nombreDepto,
                gerente=gerente_obj,
                empleados=empleados_en_depto # Pendiente: podrías cargar los empleados asignados si quieres
            )
            return departamento_encontrado
        else:
            return None # No se encontró
            
    except oracledb.DatabaseError as e:
        print(f"Error al buscar departamento: {e}")
        return None
    finally:
        cursor.close()
        conn.close()

def db_buscar_id_empleado_por_rut(rut: str):
    """
    Busca el empleado asociado a un RUT.
    El RUT se almacena como VARCHAR2 en la BD (ej: "12312-1").
    Retorna el objeto Empleado si existe, o None si no.
    """
    conn = get_connection()
    if not conn: return None
    cursor = conn.cursor()
    
    sql = "SELECT idEmpleado FROM empleados WHERE idUsuario = :1"
    
    try:
        cursor.execute(sql, (rut,))
        resultado = cursor.fetchone()
        
        if resultado:
            emp_obj = db_buscar_empleado_por_id(resultado[0])
            if type(emp_obj) is Empleado:
                return emp_obj
        else:
            return None
            
    except oracledb.DatabaseError as e:
        print(f"Error al buscar empleado por RUT: {e}")
        return None
    finally:
        cursor.close()
        conn.close()

def db_buscar_empleado_por_id(id_empleado_buscado: int):
    """
    Busca un empleado por su ID en la BD y devuelve un OBJETO Empleado.
    (Necesita info de tablas 'empleados' y 'usuarios')
    """
    conn = get_connection()
    if not conn: return None
    cursor = conn.cursor()
    
    # Unimos empleados y usuarios para tener todos los datos
    sql = """
        SELECT u.idusuario, e.idEmpleado, TO_CHAR(e.fechaInicioContrato, 'YYYY-MM-DD'), e.salario,
                u.nombre, u.direccion, u.telefono, u.correo, e.idDepartamento
        FROM empleados e
        JOIN usuarios u ON e.idUsuario = u.idUsuario
        WHERE e.idEmpleado = :1
    """
    
    try:
        cursor.execute(sql, (id_empleado_buscado,))
        resultado = cursor.fetchone() # (idEmp, fecha, salario, idUser, nombre, dir, tel, correo)
        
        if resultado:
            # Desempaquetamos los datos
            (idUsuario, idEmp, fecha, salario, nombre, dir, tel, correo, idDepartamento) = resultado
            
            # ¡Creamos el objeto Empleado con los datos de la BD!
            # Nota: El constructor de tu clase Empleado debe coincidir
            empleado_encontrado = Empleado(
                rut=idUsuario,
                nombre=nombre, 
                direccion=dir, 
                telefono=tel, 
                correo=correo,
                idEmpleado=idEmp, 
                fechaInicioContrato=fecha, 
                salario=salario,
                departamento=db_buscar_departamento_por_id(idDepartamento) if idDepartamento else None)
                # idUsuario=idUser (quizás lo necesites también)
            return empleado_encontrado
        else:
            return None # No se encontró
            
    except oracledb.DatabaseError as e:
        print(f"Error al buscar empleado: {e}")
        return None
    finally:
        cursor.close()
        conn.close()

def db_buscar_usuario_por_id(id_usuario_buscado: int):
    """
    Busca un empleado por su ID en la BD y devuelve un OBJETO Empleado.
    (Necesita info de tablas 'empleados' y 'usuarios')
    """
    conn = get_connection()
    if not conn: return None
    cursor = conn.cursor()
    
    # Unimos empleados y usuarios para tener todos los datos
    sql = """
        SELECT u.idUsuario, e.idEmpleado, e.fechaInicioContrato, e.salario,
                u.nombre, u.direccion, u.telefono, u.correo, e.idDepartamento
        FROM empleados e
        JOIN usuarios u ON e.idUsuario = u.idUsuario
        WHERE u.idusuario = :1
    """
    
    try:
        cursor.execute(sql, (id_usuario_buscado,))
        resultado = cursor.fetchone() # (idEmp, fecha, salario, idUser, nombre, dir, tel, correo)
        
        if resultado:
            # Desempaquetamos los datos
            (idUsuario, idEmp, fecha, salario, nombre, dir, tel, correo, idDepartamento) = resultado
            
            # ¡Creamos el objeto Empleado con los datos de la BD!
            # Nota: El constructor de tu clase Empleado debe coincidir
            empleado_encontrado = Empleado(
                rut=idUsuario,
                nombre=nombre, 
                direccion=dir, 
                telefono=tel, 
                correo=correo,
                idEmpleado=idEmp, 
                fechaInicioContrato=fecha, 
                salario=salario,
                departamento=db_buscar_departamento_por_id(idDepartamento) if idDepartamento else None)
                # idUsuario=idUser (quizás lo necesites también)
            return empleado_encontrado
        else:
            return None # No se encontró
            
    except oracledb.DatabaseError as e:
        print(f"Error al buscar empleado: {e}")
        return None
    finally:
        cursor.close()
        conn.close()
        
def db_buscar_admin_completo(id_empleado_admin: int):
    """
    Busca toda la info de un admin (de 3 tablas) y devuelve
    un OBJETO Administrador construido.
    """
    from administrador import Administrador
    conn = get_connection()
    if not conn: return None
    cursor = conn.cursor()
    
    # Esta SQL une las 3 tablas para tener toda la info
    sql = """
        SELECT 
            u.nombre, u.direccion, u.telefono, u.correo,
            e.idEmpleado, e.fechaInicioContrato, e.salario,
            a.idAdmin, a.usuario, a.clave
        FROM administradores a
        JOIN empleados e ON a.idEmpleado = e.idEmpleado
        JOIN usuarios u ON e.idUsuario = u.idUsuario
        WHERE a.idEmpleado = :1
    """
    
    try:
        cursor.execute(sql, (id_empleado_admin,))
        resultado = cursor.fetchone() 
        
        if resultado:
            # Los 10 argumentos se pasan en el orden exacto 
            # que tu __init__ espera
            admin_obj = Administrador(
                resultado[0],  # nombre
                resultado[1],  # direccion
                resultado[2],  # telefono
                resultado[3],  # correo
                resultado[4],  # idEmpleado
                resultado[5],  # fechaInicioContrato
                resultado[6],  # salario
                resultado[7],  # idAdmin
                resultado[8],  # usuario
                resultado[9]   # clave (hash)
            )
            return admin_obj
        else:
            return None # No se encontró
            
    except oracledb.DatabaseError as e:
        print(f"Error al buscar admin completo: {e}")
        return None
    finally:
        cursor.close()
        conn.close()
# (Aquí irían 'db_buscar_departamento' y 'db_buscar_proyecto' que son iguales)

# --- 2. Métodos de Creación (INSERT) ---

def db_crear_empleado(id_usuario: str, empleado_obj, id_depto: int):
    #pendiente
    """
    Crea un usuario y un empleado.
    (Método: Empleado.crearEmpleado)
    """
    conn = get_connection()
    if not conn: return None
    cursor = conn.cursor()
    
    try:
        sql_usuario = """
        INSERT INTO usuarios (idUsuario, nombre, direccion, telefono, correo) 
        VALUES (:1, :2, :3, :4, :5)
        """
        datos_usuario = (id_usuario, empleado_obj.nombre, empleado_obj.direccion, 
                         empleado_obj.telefono, empleado_obj.correo)
        cursor.execute(sql_usuario, datos_usuario)
        
        sql_empleado = """
        INSERT INTO empleados (idEmpleado, fechaInicioContrato, salario, idUsuario, idDepartamento)
        VALUES (:1, TO_DATE(:2, 'DD/MM/YYYY'), :3, :4, :5)
        """
        datos_empleado = (empleado_obj.idEmpleado, empleado_obj.fechaInicioContrato,
                          empleado_obj.salario, id_usuario, id_depto)
        cursor.execute(sql_empleado, datos_empleado)
        
        conn.commit()
        print(f"Empleado '{empleado_obj.nombre}' creado.")

        return True
    except oracledb.DatabaseError as e:
        print(f"Error al crear empleado: {e}")
        conn.rollback()
    finally:
        cursor.close()
        conn.close()


# (Aquí irían 'db_crear_departamento' y 'db_crear_proyecto')

def db_registrar_horas(id_empleado, id_proyecto, fecha, horas, descripcion):
    """
    Guarda un nuevo registro de horas en la BD.
    Recibe directamente los IDs y datos necesarios.
    """
    conn = get_connection()
    if not conn: return "Error de conexión"
    cursor = conn.cursor()
    
   

    sql = """
    INSERT INTO registros (fechaRegistro, horasTrabajadas, descripcionTrabajo, idEmpleado, idProyecto)
    VALUES (TO_DATE(:1, 'YYYY-MM-DD'), :2, :3, :4, :5)
    """

    try:
        datos = (
            fecha,
            horas,
            descripcion,
            id_empleado,
            id_proyecto
        )
        cursor.execute(sql, datos)
        conn.commit()
        return True
    except oracledb.DatabaseError as e:
        print(f"Error al registrar horas: {e}")
        conn.rollback()
        return f"Error BD: {e}"
    finally:
        cursor.close()
        conn.close()
def db_crear_proyecto(id_proyecto: int, proyecto_obj):
    """
    Crea un nuevo proyecto.
    (Método: Administrador.crearProyecto)
    """
    conn = get_connection()
    if not conn: return
    cursor = conn.cursor()
    
    try:
        sql_proyecto = """
        INSERT INTO proyectos (idProyecto, nombre, fechaInicioProyecto, descripcion) 
        VALUES (:1, :2, TO_DATE(:3, 'DD/MM/YYYY'), :4)
        """
        datos_proyecto = (id_proyecto, proyecto_obj.nombre, proyecto_obj.fechaInicioProyecto,
                          proyecto_obj.descripcion)
        cursor.execute(sql_proyecto, datos_proyecto)
        
        conn.commit()
        print(f"Proyecto '{proyecto_obj.nombre}' creado.")
    except oracledb.DatabaseError as e:
        print(f"Error al crear proyecto: {e}")
        conn.rollback()
    finally:
        cursor.close()
        conn.close()
def db_crear_departamento(id_depto: int, departamento_obj):

    conn = get_connection()
    if not conn: return
    cursor = conn.cursor()
    
    try:
        sql_depto = """
        INSERT INTO departamentos (idDepartamento, nombre, idGerenteResponsable) 
        VALUES (:1, :2, :3)
        """
        datos_depto = (id_depto, departamento_obj.nombre, departamento_obj.gerente.idEmpleado)
        cursor.execute(sql_depto, datos_depto)
        
        conn.commit()
    except oracledb.DatabaseError as e:
        print(f"Error al crear departamento: {e}")
        conn.rollback()
    finally:
        cursor.close()
        conn.close()
    
# --- 3. Métodos de Asignación (INSERT / UPDATE) ---

def db_asignar_proyecto_empleado(id_empleado: int, id_proyecto: int):
    """
    Asigna un empleado a un proyecto.
    (Método: Administrador.asignarProyectoEmpleado)
    """
    conn = get_connection()
    if not conn: return
    cursor = conn.cursor()
    
    sql_ver = "SELECT idEmpleado from empleados where idEmpleado = :1"
    try:
        cursor.execute(sql_ver, (id_empleado,))
        cursor.fetchone()
        if cursor.rowcount == 0:
            return "Error: El empleado especificado y/o proyecto no existe."
    
        sql = "INSERT INTO proyecto_empleados (idEmpleado, idProyecto) VALUES (:1, :2)"

        cursor.execute(sql, (id_empleado, id_proyecto))
        conn.commit()
        return True
    
    except oracledb.DatabaseError as e:
        error_obj, = e.args
        error_code = error_obj.code
        error_message = error_obj.message

        conn.rollback()

        if error_code == 1:
            # Unique constraint violated (ej. duplicado)
            return "Error: Ya existe esta asignación para el empleado en el proyecto."
        elif error_code == 2291:
            # Foreign key violation (ej. idEmpleado o idProyecto no existen)
            return "Error: El empleado o proyecto especificado no existen."
        elif error_code == 1400:
            # Cannot insert NULL (dato obligatorio no proporcionado)
            return "Error: Falta un dato obligatorio para la asignación."
        else:
            # Otros errores genéricos
            return f"Error de base de datos Oracle {error_code}: {error_message}"

def db_verificar_empleado_en_depto(id_empleado: int, id_depto: int):
    """
    Verifica si un empleado ya está asignado a un departamento.
    Retorna True si está asignado, False si no está asignado (idDepartamento es NULL o diferente).
    """
    conn = get_connection()
    if not conn:
        return False
    cursor = conn.cursor()

    sql = "SELECT idDepartamento FROM empleados WHERE idEmpleado = :1"

    try:
        cursor.execute(sql, (id_empleado,))
        resultado = cursor.fetchone()

        if resultado is None:
            # No existe el empleado
            return False

        id_departamento_empleado = resultado[0]  # Extraer el valor del tuple

        if id_departamento_empleado is None:
            # El empleado no está asignado a ningún departamento
            return False

        return id_departamento_empleado == id_depto

    except oracledb.DatabaseError as e:
        print(f"Error al verificar empleado: {e}")
        return False
    finally:
        cursor.close()
        conn.close()


def db_asignar_departamento_empleado(id_empleado: int, id_depto: int):
    """
    Asigna un empleado a un departamento (UPDATE en la tabla empleados).
    Retorna True si fue exitoso, False si falló.
    """
    conn = get_connection()
    if not conn: 
        return False
    cursor = conn.cursor()
    
    sql = "UPDATE empleados SET idDepartamento = :1 WHERE idEmpleado = :2"
    
    try:
        cursor.execute(sql, (id_depto, id_empleado))
        conn.commit()
        return True
    except oracledb.DatabaseError as e:
        print(f"Error al asignar departamento: {e}")
        return False


# --- 4. Métodos de Eliminación (DELETE / UPDATE) ---
def db_actualizar_departamento(id_depto: int, nombre: str, id_gerente: int):
    """
    Actualiza el nombre y gerente de un departamento existente.
    Retorna True si fue exitoso, False si falló.
    """
    conn = get_connection()
    if not conn:
        return False
    cursor = conn.cursor()

    sql = "UPDATE departamentos SET nombre = :1, idGerenteResponsable = :2 WHERE idDepartamento = :3"

    try:
        cursor.execute(sql, (nombre, id_gerente, id_depto))
        conn.commit()
        return True
    except oracledb.DatabaseError as e:
        print(f"Error al actualizar departamento: {e}")
        return False
    finally:
        cursor.close()
        conn.close()
def db_actualizar_proyecto(id_proyecto: int, nombre: str, fecha_inicio: str, descripcion: str):
    """
    Actualiza un proyecto existente.
    Verifica primero si el proyecto existe.
    Retorna True si fue exitoso, False si falló o no existe.
    """
    conn = get_connection()
    if not conn:
        return False
    cursor = conn.cursor()

    # ✅ VERIFICAR que el proyecto existe
    sql_verificar = "SELECT idProyecto FROM proyectos WHERE idProyecto = :1"
    
    try:
        cursor.execute(sql_verificar, (id_proyecto,))
        resultado = cursor.fetchone()
        
        if resultado is None:
            print(f"Aviso: El proyecto {id_proyecto} no existe.")
            cursor.close()
            conn.close()
            return False
        
        # ✅ Si existe, proceder a actualizarlo
        sql_actualizar = """
            UPDATE proyectos 
            SET nombre = :1, fechaInicioProyecto = TO_DATE(:2, 'DD/MM/YYYY'), descripcion = :3
            WHERE idProyecto = :4
        """
        cursor.execute(sql_actualizar, (nombre, fecha_inicio, descripcion, id_proyecto))
        conn.commit()
        print(f"Proyecto {id_proyecto} actualizado exitosamente.")
        return True
        
    except oracledb.DatabaseError as e:
        print(f"Error al actualizar proyecto: {e}")
        conn.rollback()
        return False
    finally:
        cursor.close()
        conn.close()
def db_eliminar_proyecto(id_proyecto: int):
    """
    Elimina un proyecto de la base de datos.
    Primero elimina:
    1. Los registros asociados al proyecto (tabla registros)
    2. Las relaciones con empleados (tabla proyecto_empleados)
    3. Finalmente el proyecto (tabla proyectos)
    Retorna True si fue exitoso, False si falló o no existe.
    """
    conn = get_connection()
    if not conn:
        return False
    cursor = conn.cursor()

    # ✅ VERIFICAR que el proyecto existe
    sql_verificar = "SELECT idProyecto FROM proyectos WHERE idProyecto = :1"
    
    try:
        cursor.execute(sql_verificar, (id_proyecto,))
        resultado = cursor.fetchone()
        
        if resultado is None:
            print(f"Aviso: El proyecto {id_proyecto} no existe.")
            cursor.close()
            conn.close()
            return False
        
        # ✅ Primero eliminar los registros asociados al proyecto
        sql_eliminar_registros = "DELETE FROM registros WHERE idProyecto = :1"
        cursor.execute(sql_eliminar_registros, (id_proyecto,))
        conn.commit()
        print(f"Registros del proyecto {id_proyecto} eliminados.")
        
        # ✅ Luego eliminar las relaciones con empleados en tabla intermedia
        sql_eliminar_relaciones = "DELETE FROM proyecto_empleados WHERE idProyecto = :1"
        cursor.execute(sql_eliminar_relaciones, (id_proyecto,))
        conn.commit()
        print(f"Relaciones del proyecto {id_proyecto} eliminadas.")
        
        # ✅ Finalmente eliminar el proyecto
        sql_eliminar = "DELETE FROM proyectos WHERE idProyecto = :1"
        cursor.execute(sql_eliminar, (id_proyecto,))
        conn.commit()
        print(f"Proyecto {id_proyecto} eliminado exitosamente.")
        return True
        
    except oracledb.DatabaseError as e:
        print(f"Error al eliminar proyecto: {e}")
        conn.rollback()
        return False
    finally:
        cursor.close()
        conn.close()
def db_eliminar_proyecto_empleado(id_proyecto: int, id_empleado: int):
    """
    Quita un empleado de un proyecto.
    """
    conn = get_connection()
    if not conn: return None # Retornar False si falla conexión
    cursor = conn.cursor()
    
    # Eliminamos la f-string innecesaria, el string normal basta
    sql = "DELETE FROM proyecto_empleados WHERE idProyecto = :1 AND idEmpleado = :2"
    
    try:
        cursor.execute(sql, (id_proyecto, id_empleado))
        
        # --- AQUÍ ESTÁ LA MAGIA ---
        # Verificamos cuántas filas se borraron ANTES de hacer commit
        filas_afectadas = cursor.rowcount
        
        conn.commit()
        
        # Cerramos todo
        cursor.close()
        conn.close()
        
        if filas_afectadas > 0:
            print(f"Éxito: Se eliminó la relación Proyecto {id_proyecto} - Empleado {id_empleado}")
            return True
        else:
            print(f"Aviso: No se encontró la relación Proyecto {id_proyecto} - Empleado {id_empleado}. No se borró nada.")
            return None

    except oracledb.DatabaseError as e:
        print(f"Error crítico al quitar de proyecto: {e}")
        conn.rollback()
        cursor.close()
        conn.close()
        return None
def db_actualizar_empleado(id_empleado, nombre, direccion, telefono, correo, salario, rut=None):
    """
    Actualiza SOLO los datos del usuario (nombre, dirección, teléfono, correo, salario).
    NO actualiza: fecha de inicio de contrato, departamento.
    
    Args:
        id_empleado: ID del empleado a actualizar
        nombre: Nuevo nombre
        direccion: Nueva dirección
        telefono: Nuevo teléfono
        correo: Nuevo correo
        salario: Nuevo salario
        rut: RUT del usuario (para actualizar en tabla usuarios)
    
    Returns:
        True si la actualización fue exitosa, False en caso contrario
    """
    try:
        conexion = get_connection()
        if not conexion: return
        cursor = conexion.cursor()
        
        # Actualizar solo salario en empleados (los demás datos están en usuarios)
        query = """
            UPDATE empleados
            SET salario = :1
            WHERE idEmpleado = :2
        """
        
        # Actualizar datos en la tabla usuarios
        query2 = """
            UPDATE usuarios
            SET nombre = :1,
                direccion = :2, 
                telefono = :3, 
                correo = :4
            WHERE idUsuario = :5
        """
        
        cursor.execute(query, (salario, id_empleado))
        conexion.commit()
        
        if rut:
            cursor.execute(query2, (nombre, direccion, telefono, correo, rut))
            conexion.commit()
        
        cursor.close()
        conexion.close()
        
        return True
        
    except Exception as e:
        print(f"Error al actualizar empleado: {e}")
        return False
def db_eliminar_departamento_empleado(id_empleado: int):
    """
    Quita un empleado de su departamento (lo deja NULO).
    (Método: Administrador.eliminarDepartamentoEmpleado)
    """
    conn = get_connection()
    if not conn: return
    cursor = conn.cursor()

    sql_verificar = "SELECT idDepartamento FROM empleados WHERE idEmpleado = :1"

    cursor.execute(sql_verificar, (id_empleado,))
    resultado = cursor.fetchone()

    if resultado is None or resultado[0] is None:
        print("El empleado no está asignado a ningún departamento.")
        cursor.close()
        conn.close()
        return f"Aviso: El empleado {id_empleado} no existe o no está asignado a ningún departamento."
    
    sql = "UPDATE empleados SET idDepartamento = NULL WHERE idEmpleado = :1"

    try:
        cursor.execute(sql, (id_empleado,))
        print("Eliminacion exitosa")
        conn.commit()
        return True
    except oracledb.DatabaseError as e:
        print(f"Error al quitar de depto: {e}")
        conn.rollback()
        return e
        
def db_eliminar_departamento(id_depto: int):
    """
    1. Verifica si el departamento existe.
    2. Si existe, actualiza a NULL el departamento de los empleados asociados.
    3. Elimina el departamento.
    Retorna True si fue exitoso, False si falló o no existía.
    """
    conn = get_connection()
    if not conn:
        return False
    
    cursor = conn.cursor()

    # Consultas SQL
    sql_verificar = "SELECT COUNT(*) FROM departamentos WHERE idDepartamento = :1"
    sql_desvincular = "UPDATE empleados SET idDepartamento = NULL WHERE idDepartamento = :1"
    sql_eliminar = "DELETE FROM departamentos WHERE idDepartamento = :1"

    try:
        # PASO 1: Verificar existencia
        cursor.execute(sql_verificar, (id_depto,))
        resultado = cursor.fetchone()
        
        # resultado[0] contiene el conteo. Si es 0, no existe.
        if resultado[0] == 0:
            print(f"Error: El departamento con ID {id_depto} no existe.")
            return False

        # PASO 2: Desvincular empleados (Poner en NULL)
        # Esto cumple tu requisito de NO borrar a los empleados
        cursor.execute(sql_desvincular, (id_depto,))

        # PASO 3: Eliminar el departamento
        cursor.execute(sql_eliminar, (id_depto,))

        # Si todo salió bien, guardamos los cambios
        conn.commit()
        print(f"Departamento {id_depto} eliminado y empleados liberados.")
        return True

    except oracledb.DatabaseError as e:
        # Si algo falla, deshacemos cualquier cambio pendiente
        conn.rollback()
        print(f"Error al eliminar departamento: {e}")
        return False
        
    finally:
        cursor.close()
        conn.close()


def get_lista_datos_tabla(tabla, dato):
    conn = get_connection()
    if not conn: return None
    cursor = conn.cursor()

    sql = f"SELECT {dato} FROM {tabla}"

    cursor.execute(sql)

    listaDato = []
    for row in cursor:
        listaDato.append(row[0])

    return listaDato


