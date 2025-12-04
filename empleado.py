# Arreglo recursivo de importacion
from __future__ import annotations
from typing import TYPE_CHECKING
from usuario import Usuario

if TYPE_CHECKING:
    from departamento import Departamento
# Arreglo recursivo de importacion
class Empleado(Usuario):
    def __init__(self, nombre:str, direccion:str, telefono:str, correo:str, idEmpleado:int, fechaInicioContrato:str, salario:float, departamento:'Departamento|None' = None, rut = None):
        super().__init__(nombre, direccion, telefono, correo, rut=rut)

        self.idEmpleado = idEmpleado
        self.fechaInicioContrato = fechaInicioContrato
        self.salario = salario
        self.departamento = departamento