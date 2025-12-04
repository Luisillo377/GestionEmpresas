# Arreglo recursivo de importacion
from __future__ import annotations
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from empleado import Empleado
# Arreglo recursivo de importacion
class Departamento:
    def __init__(self, idDepartamento:int, nombre:str, gerente:'Empleado|None' = None, empleados:'list[Empleado]' = []):
        self.idDepartamento = idDepartamento
        self.nombre = nombre
        self.gerente = gerente
        self.empleados = empleados