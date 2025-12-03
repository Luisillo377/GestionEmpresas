from empleado import Empleado

class Proyecto:
    def __init__(self,idProyecto:int,nombre:str,fechaInicioProyecto:str,descripcion:str,empleados:list[Empleado] = []):
        self.idProyecto = idProyecto
        self.nombre = nombre
        self.fechaInicioProyecto = fechaInicioProyecto
        self.descripcion = descripcion
        self.empleados = empleados