from empleado import Empleado
from proyecto import Proyecto


class Registro:
    def __init__(self, empleado:Empleado, proyecto:Proyecto, fechaRegistro:str, horasTrabajadas:float, descripcionTrabajo:str):
        self.empleado = empleado
        self.proyecto = proyecto
        self.fechaRegistro = fechaRegistro
        self.horasTrabajadas = horasTrabajadas
        self.descripcionTrabajo = descripcionTrabajo

