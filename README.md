# 🏢 Sistema de Gestión de Empresa

Sistema de gestión empresarial desarrollado en Python con interfaz gráfica Tkinter y base de datos Oracle. Permite administrar empleados, departamentos, proyectos, registro de horas trabajadas e indicadores económicos en tiempo real.

---

## 📋 Tabla de Contenidos

1. [Descripción General](#-descripción-general)
2. [Características](#-características)
3. [Requisitos Previos](#-requisitos-previos)
4. [Instalación](#-instalación)
5. [Configuración](#-configuración)
6. [Uso de la Aplicación](#-uso-de-la-aplicación)
7. [Arquitectura del Proyecto](#-arquitectura-del-proyecto)
8. [Modelo de Datos](#-modelo-de-datos)
9. [API de Indicadores Económicos](#-api-de-indicadores-económicos)
10. [Documentación de Clases](#-documentación-de-clases)
11. [Documentación de Funciones de BD](#-documentación-de-funciones-de-bd)
12. [Interfaz Gráfica](#-interfaz-gráfica)
13. [Solución de Problemas](#-solución-de-problemas)
14. [Autores](#-autores)

---

## 📝 Descripción General

Este sistema permite la gestión integral de una empresa, incluyendo:
- **Gestión de Empleados**: Crear, buscar, editar y asignar empleados a departamentos/proyectos
- **Gestión de Departamentos**: CRUD completo con asignación de gerentes
- **Gestión de Proyectos**: Crear proyectos y asignar equipos de trabajo
- **Registro de Horas**: Los empleados pueden registrar sus horas trabajadas por proyecto
- **Panel de Administración**: Acceso seguro con autenticación y contraseñas hasheadas (bcrypt)
- **Indicadores Económicos**: Consulta en tiempo real de UF, Dólar, Euro y más desde la API de Mindicador.cl
- **Gestión de Administradores**: Crear nuevos admins, cambiar contraseñas y listar administradores
- **Admin por Defecto**: Creación automática de un administrador inicial al ejecutar por primera vez

---

## ✨ Características

- 🔐 **Autenticación segura** con bcrypt para hash de contraseñas
- 🖥️ **Interfaz gráfica** intuitiva con Tkinter
- 🗄️ **Base de datos Oracle** con conexión mediante oracledb
- 🔒 **Variables de entorno** para credenciales (.env)
- 👥 **Dos roles de usuario**: Administrador y Empleado
- 📊 **Indicadores económicos** en tiempo real (UF, Dólar, Euro, IPC, UTM, etc.)
- 🔄 **Historial de indicadores** consultados y guardados
- 👤 **Admin por defecto** creado automáticamente en el primer inicio
- 🔑 **Cambio de contraseña** para administradores
- 📋 **Listado de administradores** del sistema

---

## 📋 Requisitos Previos

### Software Necesario
- **Python 3.8+**
- **Oracle Database** (o Oracle XE)
- **Oracle SQL Developer** (opcional, para administrar la BD)

### Dependencias de Python
```
oracledb
bcrypt
python-dotenv
requests
```

---

## 🚀 Instalación

### Paso 1: Clonar el Repositorio
```bash
git clone https://github.com/Luisillo377/GestionEmpresa.git
cd GestionEmpresa
```

### Paso 2: Instalar Dependencias
```bash
pip install oracledb bcrypt python-dotenv requests
```

### Paso 3: Configurar la Base de Datos

1. Abre Oracle SQL Developer o tu herramienta de administración Oracle
2. Conéctate a tu base de datos
3. Ejecuta el archivo `ADMIN CONEXION BASE.sql` **completo**
   - ✅ El script está ordenado para evitar errores de dependencias circulares
   - ✅ Simplemente ejecuta todo el archivo de una vez

> **Nota:** El script maneja automáticamente las dependencias circulares entre las tablas `empleados` y `departamentos` usando `ALTER TABLE`.

### Paso 4: Crear el Archivo de Configuración `.env`
Crea un archivo `.env` en la raíz del proyecto:
```env
DB_USER=tu_usuario_oracle
DB_PASSWORD=tu_contraseña
DB_DSN=localhost:1521/XE
```

### Paso 5: Ejecutar la Aplicación
```bash
python APP.py
```

> **🎉 ¡Nuevo!** Al ejecutar por primera vez, el sistema creará automáticamente un administrador por defecto:
> - **Usuario:** `admin`
> - **Contraseña:** `admin123`
> 
> ⚠️ **IMPORTANTE:** Cambie la contraseña después del primer inicio de sesión.

---

## ⚙️ Configuración

### Variables de Entorno (.env)

| Variable | Descripción | Ejemplo |
|----------|-------------|---------|
| `DB_USER` | Usuario de Oracle | `SYSTEM` |
| `DB_PASSWORD` | Contraseña de Oracle | `miPassword123` |
| `DB_DSN` | Data Source Name | `localhost:1521/XE` |

### Personalización de la Interfaz

En `APP.py` puedes modificar las constantes de estilo:

```python
# Fuentes
FONT_TITULO = ("Segoe UI", 18, "bold")
FONT_SUBTITULO = ("Segoe UI", 12, "bold", "underline")
FONT_TEXTO = ("Segoe UI", 10)
FONT_BOTON = ("Segoe UI", 10, "bold")

# Colores
COLOR_FONDO = "#f0f0f0"
COLOR_BOTON = "#e1e1e1"
COLOR_BOTON_ACTIVO = "#d4d4d4"
COLOR_TEXTO_ERROR = "#d9534f"   # Rojo
COLOR_TEXTO_EXITO = "#5cb85c"   # Verde

# Dimensiones
ANCHO_BOTON = 35
ANCHO_ENTRY = 40
PADDING_ESTANDAR = 10
```

---

## 💻 Uso de la Aplicación

### Pantalla de Inicio
Al iniciar, se muestran dos opciones:
- **Entrar como Administrador**: Requiere usuario y contraseña
- **Entrar como Empleado**: Requiere solo el RUT

### Panel de Administrador

#### Gestión de Departamentos
| Acción | Descripción |
|--------|-------------|
| Crear | Nuevo departamento con ID, nombre y gerente |
| Buscar | Ver info del depto y lista de empleados |
| Editar | Modificar nombre y gerente |
| Eliminar | Borra el depto (empleados quedan sin asignar) |
| Asignar Empleado | Agregar empleado al departamento |
| Quitar Empleado | Remover empleado del departamento |

#### Gestión de Proyectos
| Acción | Descripción |
|--------|-------------|
| Crear | Nuevo proyecto con ID, nombre, fecha y descripción |
| Buscar | Ver info del proyecto y equipo asignado |
| Editar | Modificar datos del proyecto |
| Eliminar | Elimina proyecto y registros asociados |
| Asignar Empleado | Agregar empleado al equipo |
| Quitar Empleado | Remover del equipo |

#### Gestión de Empleados
| Acción | Descripción |
|--------|-------------|
| Crear | Nuevo empleado con todos sus datos |
| Buscar | Ver información por ID de ficha |
| Editar | Modificar datos (busca por RUT) |

#### Gestión de Administradores
| Acción | Descripción |
|--------|-------------|
| Crear Admin | Crear nuevo administrador asociado a un empleado |
| Cambiar Contraseña | Cambiar la contraseña del admin actual |
| Ver Lista | Ver todos los administradores del sistema |

#### Indicadores Económicos
| Acción | Descripción |
|--------|-------------|
| Consultar | Obtener indicadores actuales desde Mindicador.cl |
| Guardar | Guardar todos los indicadores en la base de datos |
| Ver Historial | Ver historial de indicadores guardados |

### Panel de Empleado
- Ingresa con RUT
- Registra horas trabajadas por proyecto
- La fecha se autocompleta con la fecha actual

---

## 🏗️ Arquitectura del Proyecto

```
GestionEmpresa/
│
├── APP.py                    # Aplicación principal (interfaz Tkinter)
├── database.py               # Capa de acceso a datos (Oracle)
├── api_indicador.py          # Consumo de API Mindicador.cl
├── .env                      # Variables de entorno (credenciales)
│
├── Clases de Modelo/
│   ├── usuario.py            # Clase base Usuario
│   ├── empleado.py           # Clase Empleado (hereda de Usuario)
│   ├── administrador.py      # Clase Administrador (hereda de Empleado)
│   ├── departamento.py       # Clase Departamento
│   ├── proyecto.py           # Clase Proyecto
│   └── registro.py           # Clase Registro (horas trabajadas)
│
├── ADMIN CONEXION BASE.sql   # Script DDL de la base de datos
├── GestionEmpresa.spec       # Especificación para crear ejecutable
└── README.md                 # Documentación del proyecto
```

### Patrón de Diseño
El proyecto sigue una arquitectura de **3 capas**:
1. **Presentación** (`APP.py`): Interfaz gráfica Tkinter
2. **Lógica de Negocio** (Clases): Usuario, Empleado, Administrador, etc.
3. **Acceso a Datos** (`database.py`): Conexión y queries a Oracle

---

## 🗄️ Modelo de Datos

### Diagrama Entidad-Relación

```
┌─────────────┐       ┌─────────────────┐       ┌──────────────┐
│  USUARIOS   │       │    EMPLEADOS    │       │ DEPARTAMENTOS│
├─────────────┤       ├─────────────────┤       ├──────────────┤
│ idUsuario PK│◄──────│ idUsuario FK    │   ┌──►│idDepartamento│
│ nombre      │       │ idEmpleado PK   │◄──┤   │ nombre       │
│ direccion   │       │ fechaInicio     │   │   │idGerenteFKº──┼──┐
│ telefono    │       │ salario         │   │   └──────────────┘  │
│ correo      │       │ idDepartamento FK├───┘                     │
└─────────────┘       └────────┬────────┘◄─────────────────────────┘
                               │
         ┌─────────────────────┼─────────────────────┐
         │                     │                     │
         ▼                     ▼                     ▼
┌─────────────────┐   ┌─────────────────┐   ┌─────────────────┐
│ ADMINISTRADORES │   │PROYECTO_EMPLEADO│   │    REGISTROS    │
├─────────────────┤   ├─────────────────┤   ├─────────────────┤
│ idAdmin PK      │   │ idEmpleado FK   │   │ idRegistro PK   │
│ usuario         │   │ idProyecto FK   │   │ fechaRegistro   │
│ clave (hash)    │   └────────┬────────┘   │ horasTrabajadas │
│ idEmpleado FK   │            │            │ descripcion     │
└─────────────────┘            │            │ idEmpleado FK   │
                               │            │ idProyecto FK   │
                    ┌──────────▼─────────┐  └─────────────────┘
                    │     PROYECTOS      │
                    ├────────────────────┤
                    │ idProyecto PK      │
                    │ nombre             │
                    │ fechaInicioProyecto│
                    │ descripcion        │
                    └────────────────────┘

┌────────────────────────────┐
│   INDICADORES_REGISTRADOS  │
├────────────────────────────┤
│ idIndicador PK             │
│ codigo                     │
│ nombre                     │
│ valor                      │
│ unidadMedida               │
│ fechaValor                 │
│ fechaConsulta              │
│ idAdmin FK                 │
└────────────────────────────┘
```

### Tablas

| Tabla | Descripción | Campos Clave |
|-------|-------------|--------------|
| `usuarios` | Datos personales base | idUsuario, nombre, correo, telefono, rut |
| `empleados` | Información laboral | idEmpleado, salario, fechaContrato |
| `departamentos` | Áreas de la empresa | idDepartamento, nombre, idGerente |
| `proyectos` | Proyectos activos | idProyecto, nombre, fechaInicio |
| `proyecto_empleados` | Relación N:M | idEmpleado, idProyecto |
| `registros` | Horas trabajadas | fecha, horas, descripción |
| `administradores` | Usuarios con acceso admin | usuario, clave (hash bcrypt) |
| `indicadores_registrados` | Indicadores económicos | código, nombre, valor, fecha |

---

## 📊 API de Indicadores Económicos

El sistema integra la API de [Mindicador.cl](https://mindicador.cl/) para obtener indicadores económicos chilenos en tiempo real.

### Clase `Mindicador`
```python
class Mindicador:
    """Representa un indicador económico de Chile."""
    
    def __init__(self, indicador_data):
        self.codigo = indicador_data.get("codigo")      # ej: "uf", "dolar"
        self.nombre = indicador_data.get("nombre")      # ej: "Unidad de fomento"
        self.unidad_medida = indicador_data.get("unidad_medida")  # ej: "Pesos"
        self.fecha = indicador_data.get("fecha")        # Fecha del valor
        self.valor = indicador_data.get("valor")        # Valor numérico
```

### Función `obtener_indicadores()`
```python
def obtener_indicadores() -> dict[str, Mindicador]:
    """
    Consulta la API de Mindicador.cl y retorna un diccionario
    con todos los indicadores económicos disponibles.
    
    Indicadores incluidos:
    - UF (Unidad de Fomento)
    - Dólar observado
    - Euro
    - IPC (Índice de Precios al Consumidor)
    - UTM (Unidad Tributaria Mensual)
    - IVP (Índice de Valor Promedio)
    - Imacec
    - TPM (Tasa de Política Monetaria)
    - Libra de Cobre
    - Tasa de Desempleo
    - Bitcoin
    """
```

### Funciones de BD para Indicadores
```python
db_registrar_indicador(indicador: Mindicador, id_admin: int) -> bool
    """Guarda un indicador en la base de datos."""

db_registrar_multiples_indicadores(indicadores: dict, id_admin: int) -> dict
    """Guarda múltiples indicadores. Retorna {exitosos: int, fallidos: int}"""

db_obtener_historial_indicadores(limite: int = 50) -> list[dict]
    """Obtiene el historial de indicadores guardados."""
```

---

## 📚 Documentación de Clases

### Clase `Usuario`
```python
class Usuario:
    """Clase base para representar un usuario del sistema."""
    
    def __init__(self, nombre, direccion, telefono, correo, rut=None):
        self.rut = rut           # Identificador único (RUT chileno)
        self.nombre = nombre     # Nombre completo
        self.direccion = direccion
        self.telefono = telefono
        self.correo = correo
```

### Clase `Empleado` (hereda de Usuario)
```python
class Empleado(Usuario):
    """Representa un empleado de la empresa."""
    
    def __init__(self, nombre, direccion, telefono, correo, 
                 idEmpleado, fechaInicioContrato, salario, 
                 departamento=None, rut=None):
        super().__init__(nombre, direccion, telefono, correo, rut)
        self.idEmpleado = idEmpleado           # ID interno de ficha
        self.fechaInicioContrato = fechaInicioContrato  # Fecha formato YYYY-MM-DD
        self.salario = salario                  # Salario mensual
        self.departamento = departamento        # Objeto Departamento o None
```

### Clase `Administrador` (hereda de Empleado)
```python
class Administrador(Empleado):
    """Empleado con privilegios de administración."""
    
    def __init__(self, ..., idAdmin, usuario, clave):
        super().__init__(...)
        self.idAdmin = idAdmin    # ID de administrador
        self.usuario = usuario    # Nombre de usuario para login
        self.clave_hash = clave   # Hash bcrypt de la contraseña
    
    # Métodos principales:
    def crearProyecto(idProyecto, nombre, fechaInicio, descripcion) -> Proyecto
    def crearDepartamento(idDepartamento, nombre, gerente, empleados) -> Departamento
    def crearEmpleado(nombre, direccion, ...) -> Empleado
    def hash_clave(clave: str) -> bytes  # Genera hash bcrypt
```

### Clase `Departamento`
```python
class Departamento:
    """Representa un departamento/área de la empresa."""
    
    def __init__(self, idDepartamento, nombre, gerente=None, empleados=[]):
        self.idDepartamento = idDepartamento
        self.nombre = nombre
        self.gerente = gerente      # Objeto Empleado (gerente responsable)
        self.empleados = empleados  # Lista de objetos Empleado
```

### Clase `Proyecto`
```python
class Proyecto:
    """Representa un proyecto de la empresa."""
    
    def __init__(self, idProyecto, nombre, fechaInicioProyecto, 
                 descripcion, empleados=[]):
        self.idProyecto = idProyecto
        self.nombre = nombre
        self.fechaInicioProyecto = fechaInicioProyecto  # Formato DD/MM/YYYY
        self.descripcion = descripcion
        self.empleados = empleados  # Lista de empleados asignados
```

### Clase `Registro`
```python
class Registro:
    """Representa un registro de horas trabajadas."""
    
    def __init__(self, empleado, proyecto, fechaRegistro, 
                 horasTrabajadas, descripcionTrabajo):
        self.empleado = empleado           # Objeto Empleado
        self.proyecto = proyecto           # Objeto Proyecto
        self.fechaRegistro = fechaRegistro # Fecha del trabajo
        self.horasTrabajadas = horasTrabajadas  # Cantidad de horas
        self.descripcionTrabajo = descripcionTrabajo  # Descripción de actividad
```

---

## 🔧 Documentación de Funciones de BD

### Conexión
```python
get_connection() -> oracledb.Connection | None
    """Establece conexión a Oracle usando variables de entorno."""
```

### Inicialización Automática
```python
inicializar_admin_por_defecto() -> bool
    """
    Verifica si existe al menos un administrador.
    Si no existe, crea automáticamente:
    - Usuario base (id=1)
    - Empleado base (id=1)
    - Administrador: usuario='admin', clave='admin123'
    """
```

### Autenticación y Gestión de Admins
```python
db_login_admin(usuario: str, clave_plana: str) -> int | None
    """Valida credenciales y retorna idEmpleado del admin si es válido."""

db_buscar_admin_completo(id_empleado_admin: int) -> Administrador | None
    """Retorna objeto Administrador completo con todos sus datos."""

db_crear_nuevo_admin(id_admin, usuario, clave_plana, id_empleado) -> bool | str
    """Crea un nuevo administrador con contraseña hasheada."""

db_cambiar_clave_admin(usuario, clave_actual, clave_nueva) -> bool | str
    """Cambia la contraseña de un administrador."""

db_obtener_siguiente_id_admin() -> int
    """Obtiene el siguiente ID disponible para un nuevo admin."""

db_listar_administradores() -> list[dict]
    """Lista todos los administradores del sistema."""

db_obtener_usuario_admin_por_id_empleado(id_empleado) -> str | None
    """Obtiene el nombre de usuario del admin por su ID de empleado."""

db_obtener_id_admin_por_id_empleado(id_empleado) -> int | None
    """Obtiene el ID del admin por su ID de empleado."""
```

### Operaciones CRUD - Empleados
```python
db_crear_empleado(id_usuario: str, empleado_obj, id_depto: int) -> bool
db_buscar_empleado_por_id(id_empleado: int) -> Empleado | None
db_buscar_id_empleado_por_rut(rut: str) -> Empleado | None
db_actualizar_empleado(id_empleado, nombre, direccion, telefono, 
                        correo, salario, rut) -> bool
```

### Operaciones CRUD - Departamentos
```python
db_crear_departamento(id_depto: int, departamento_obj) -> None
db_buscar_departamento_por_id(id_depto: int) -> Departamento | None
db_actualizar_departamento(id_depto: int, nombre: str, id_gerente: int) -> bool
db_eliminar_departamento(id_depto: int) -> bool
```

### Operaciones CRUD - Proyectos
```python
db_crear_proyecto(id_proyecto: int, proyecto_obj) -> None
db_buscar_proyecto_por_id(id_proyecto: int) -> Proyecto | None
db_actualizar_proyecto(id_proyecto, nombre, fecha_inicio, descripcion) -> bool
db_eliminar_proyecto(id_proyecto: int) -> bool
```

### Asignaciones
```python
db_asignar_proyecto_empleado(id_empleado: int, id_proyecto: int) -> bool | str
db_eliminar_proyecto_empleado(id_proyecto: int, id_empleado: int) -> bool | None
db_asignar_departamento_empleado(id_empleado: int, id_depto: int) -> bool
db_eliminar_departamento_empleado(id_empleado: int) -> bool | str
db_verificar_empleado_en_depto(id_empleado: int, id_depto: int) -> bool
```

### Registro de Horas
```python
db_registrar_horas(id_empleado, id_proyecto, fecha, horas, descripcion) -> bool | str
    """Registra horas trabajadas. Fecha formato YYYY-MM-DD."""
```

### Indicadores Económicos
```python
db_registrar_indicador(indicador: Mindicador, id_admin: int) -> bool
db_registrar_multiples_indicadores(indicadores: dict, id_admin: int) -> dict
db_obtener_historial_indicadores(limite: int = 50) -> list[dict]
```

---

## 🖼️ Interfaz Gráfica

### Flujo de Navegación

```
┌─────────────────────┐
│   PANTALLA INICIO   │
└──────────┬──────────┘
           │
    ┌──────┴──────┐
    ▼             ▼
┌────────┐   ┌────────────┐
│ LOGIN  │   │   LOGIN    │
│ ADMIN  │   │  EMPLEADO  │
└────┬───┘   └─────┬──────┘
     │             │
     ▼             ▼
┌─────────────────┐  ┌──────────────┐
│  PANEL ADMIN    │  │ REGISTRO     │
├─────────────────┤  │ DE HORAS     │
│ • Deptos        │  └──────────────┘
│ • Proyectos     │
│ • Empleados     │
│ • Admins        │ ◄── NUEVO
│ • Indicadores   │ ◄── NUEVO
│ • Cambiar Clave │ ◄── NUEVO
└─────────────────┘
```

### Componentes Principales

| Frame | Descripción |
|-------|-------------|
| `frame_inicio` | Pantalla inicial con opciones de acceso |
| `frame_login_admin` | Login para administradores |
| `frame_login_empleado` | Login para empleados (por RUT) |
| `frame_panel_admin` | Panel principal del administrador |
| `frame_gest_deptos` | Menú de gestión de departamentos |
| `frame_gest_proyectos` | Menú de gestión de proyectos |
| `frame_gest_empleados` | Menú de gestión de empleados |
| `frame_gest_admins` | Gestión de administradores |
| `frame_indicadores` | Consulta y guardado de indicadores |
| `frame_cambiar_clave` | Cambio de contraseña del admin |
| `frame_registrar_horas` | Formulario de registro de horas |

### Funciones de Utilidad UI

```python
limpiar_formulario(lista_widgets)
    """Limpia Entries y Labels de mensaje."""

cambiar_frame(frame_destino, frame_origen, funcion_limpieza)
    """Navega entre frames con limpieza opcional."""

crear_popup_lista(titulo, datos, encabezado)
    """Muestra ventana emergente con lista de datos."""

crear_titulo(padre, texto)
    """Crea un Label de título estilizado."""

crear_input(padre, etiqueta) -> Entry
    """Crea un Label + Entry y retorna el Entry."""

crear_boton(padre, texto, comando, color_texto="black") -> Button
    """Crea un botón estilizado."""

crear_label_mensaje(padre) -> Label
    """Retorna un label vacío para mostrar errores o éxitos."""
```

---

## ⚠️ Solución de Problemas

### Error al crear tablas
Si tienes problemas al ejecutar el SQL:
1. Ejecuta el script **completo** (no por partes)
2. Verifica que no existan tablas previas

**Para eliminar todas las tablas:**
```sql
DROP TABLE indicadores_registrados CASCADE CONSTRAINTS;
DROP TABLE administradores CASCADE CONSTRAINTS;
DROP TABLE registros CASCADE CONSTRAINTS;
DROP TABLE proyecto_empleados CASCADE CONSTRAINTS;
DROP TABLE proyectos CASCADE CONSTRAINTS;
DROP TABLE empleados CASCADE CONSTRAINTS;
DROP TABLE departamentos CASCADE CONSTRAINTS;
DROP TABLE usuarios CASCADE CONSTRAINTS;
```

### Error de conexión a Oracle
- Verifica que Oracle esté ejecutándose
- Revisa las credenciales en `.env`
- Prueba el DSN: `localhost:1521/XEPDB1` o tu configuración

### Error "módulo no encontrado"
```bash
pip install oracledb bcrypt python-dotenv requests
```

### Error de login como admin
- La aplicación crea automáticamente un admin por defecto
- Credenciales: `admin` / `admin123`
- Si persiste el error, verifica la conexión a la base de datos

### Error al consultar indicadores
- Verifica tu conexión a internet
- La API de Mindicador.cl debe estar disponible
- Revisa que `requests` esté instalado

---

## 👥 Autores

- **Luis Muñoz** - [@Luisillo377](https://github.com/Luisillo377)
- **Matías Cerda**
- **Matías Soto**

---

## 📄 Licencia

Este proyecto es de uso educativo.

---

*Última actualización: Diciembre 2025*

---
*Sistema de Gestión Empresarial - Python + Tkinter + Oracle*
