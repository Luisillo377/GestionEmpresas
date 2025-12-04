from proyecto import Proyecto
from departamento import Departamento
from empleado import Empleado
import database as dbFunciones
import bcrypt


class Administrador(Empleado):
    def __init__(self, nombre:str, direccion:str, telefono:str, correo:str, idEmpleado:int, fechaInicioContrato:str, salario:float, idAdmin:int,usuario:str,clave:str):
        super().__init__(nombre, direccion, telefono, correo, idEmpleado, fechaInicioContrato, salario)

        self.idAdmin = idAdmin
        self.usuario = usuario
        self.clave_hash = clave
    #crear hash
    
    
    def hash_clave(self,clave: str) -> bytes:
        salt = bcrypt.gensalt()
        return bcrypt.hashpw(clave.encode('utf-8'), salt)


    # Metodos Proyecto
    def crearProyecto(self, idProyecto:int, nombre:str, fechaInicioProyecto:str, descripcion:str):
        temp = Proyecto(idProyecto, nombre, fechaInicioProyecto, descripcion)
        
        
        try:
            dbFunciones.db_crear_proyecto(temp.idProyecto, temp)
            return temp
        except Exception as e:
            print(f"No se puedo crear el proyecto en la BD :{e}")
            return None
    
    # Metodo Departamento
    def crearDepartamento(self, idDepartamento:int, nombre:str, gerente:'Empleado|None' = None, empleados:list[Empleado] = []):
        temp = Departamento(idDepartamento, nombre, gerente, empleados)

        try:
            dbFunciones.db_crear_departamento(temp.idDepartamento, temp)
            return temp
        except Exception as e:
            print(f"No se puedo crear el departamento en la BD :{e}")
            return None
        
    # Metodo Empleado
    def crearEmpleado(self, nombre:str, direccion:str, telefono:str, correo:str, idEmpleado:int, fechaInicioContrato:str, salario:float):
        temp = Empleado(nombre, direccion, telefono, correo, idEmpleado, fechaInicioContrato, salario)
        return temp
    

