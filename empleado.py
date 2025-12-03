from usuario import Usuario

class Empleado(Usuario):
    def __init__(self, nombre:str, direccion:str, telefono:str, correo:str, idEmpleado:int, fechaInicioContrato:str, salario:float, departamento:'Departamento|None' = None, rut = None):
        super().__init__(nombre, direccion, telefono, correo, rut=rut)

        self.idEmpleado = idEmpleado
        self.fechaInicioContrato = fechaInicioContrato
        self.salario = salario
        self.departamento = departamento