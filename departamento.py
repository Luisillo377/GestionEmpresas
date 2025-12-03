class Departamento:
    def __init__(self, idDepartamento:int, nombre:str, gerente:'Empleado|None' = None, empleados:'list[Empleado]' = []):
        self.idDepartamento = idDepartamento
        self.nombre = nombre
        self.gerente = gerente
        self.empleados = empleados