-- ============================================
-- SCRIPT DE CREACIÓN DE BASE DE DATOS
-- Sistema de Gestión de Empresa
-- ============================================
-- NOTA: Este script está ordenado para evitar
-- problemas de dependencias circulares.
-- Simplemente ejecuta todo el archivo en orden.
-- ============================================

-- =====================
-- PASO 1: CREAR TABLAS
-- (sin foreign keys circulares)
-- =====================

-- Tabla de usuarios (base, sin dependencias)
CREATE TABLE usuarios
(
    idUsuario INT PRIMARY KEY,
    nombre VARCHAR2(50),
    direccion VARCHAR2(50),
    telefono VARCHAR2(50) UNIQUE,  
    correo VARCHAR2(50) UNIQUE
);

-- Tabla de departamentos (sin FK a empleados por ahora)
CREATE TABLE departamentos
(
    idDepartamento INT PRIMARY KEY,
    nombre VARCHAR2(100),
    idGerenteResponsable INT  -- Se agregará la FK después
);

-- Tabla de empleados (sin FK a departamentos por ahora)
CREATE TABLE empleados
(
    idEmpleado INT PRIMARY KEY,
    fechaInicioContrato DATE,
    salario FLOAT,
    idUsuario INT,
    idDepartamento INT,
    CONSTRAINT USUARIO_EMPLEADO FOREIGN KEY (idUsuario) REFERENCES usuarios(idUsuario)
    -- La FK a departamentos se agregará después
);

-- Tabla de proyectos
CREATE TABLE proyectos
(
    idProyecto INT PRIMARY KEY,
    nombre VARCHAR2(50),
    fechaInicioProyecto DATE,
    descripcion VARCHAR2(50)
);

-- Tabla intermedia proyecto_empleados
CREATE TABLE proyecto_empleados
(
    idEmpleado INT,
    idProyecto INT,
    CONSTRAINT PK_PROYECTO_EMPLEADO PRIMARY KEY (idEmpleado, idProyecto),
    CONSTRAINT FK_PROYECTO_EMPLEADO_EMP FOREIGN KEY (idEmpleado) REFERENCES empleados(idEmpleado),
    CONSTRAINT FK_PROYECTO_EMPLEADO_PROY FOREIGN KEY (idProyecto) REFERENCES proyectos(idProyecto)
);

-- Tabla de registros
CREATE TABLE registros
(
    idRegistro INT GENERATED AS IDENTITY PRIMARY KEY,
    fechaRegistro DATE NOT NULL,
    horasTrabajadas FLOAT NOT NULL,
    descripcionTrabajo VARCHAR2(200) NOT NULL,
    idEmpleado INT,
    idProyecto INT,
    CONSTRAINT FK_EMPLEADO_REGISTRO FOREIGN KEY (idEmpleado) REFERENCES empleados(idEmpleado),
    CONSTRAINT FK_PROYECTO_REGISTRO FOREIGN KEY (idProyecto) REFERENCES proyectos(idProyecto)
);

-- Tabla de administradores
CREATE TABLE administradores
(
    idAdmin INT PRIMARY KEY,
    usuario VARCHAR2(50) UNIQUE, 
    clave VARCHAR2(255),
    idEmpleado INT,
    CONSTRAINT FK_EMPLEADO_ADMINISTRADO FOREIGN KEY (idEmpleado) REFERENCES empleados(idEmpleado)
);

-- Tabla de indicadores registrados
CREATE TABLE indicadores_registrados
(
    idIndicadorRegistro INT PRIMARY KEY,
    nombre_indicador VARCHAR2(50) NOT NULL,  -- (Ej: "UF", "Dólar Observado")
    valor_indicador FLOAT,                   -- (El valor en sí, ej: 37000.50)
    fecha_valor DATE,                        -- (La fecha del valor, ej: 10-11-2025)
    fecha_consulta DATE,                     -- (El día que se guardó, ej: 12-11-2025)
    sitio_proveedor VARCHAR2(100),           -- (Ej: "mindicador.cl")
    id_admin_consulta INT,                   -- El usuario/admin que hizo la consulta
    CONSTRAINT FK_ADMIN_CONSULTA FOREIGN KEY (id_admin_consulta) REFERENCES administradores(idAdmin)
);

-- =====================
-- PASO 2: AGREGAR FOREIGN KEYS CIRCULARES
-- (ahora que ambas tablas existen)
-- =====================

-- FK de empleados -> departamentos
ALTER TABLE empleados
ADD CONSTRAINT FK_EMPLEADO_DEPARTAMENTO 
FOREIGN KEY (idDepartamento) REFERENCES departamentos(idDepartamento);

-- FK de departamentos -> empleados (gerente responsable)
ALTER TABLE departamentos
ADD CONSTRAINT FK_GERENTE_RESPONSABLE 
FOREIGN KEY (idGerenteResponsable) REFERENCES empleados(idEmpleado);

-- =====================
-- FIN DEL SCRIPT
-- =====================

COMMIT;
