class Usuario:
    def __init__(self, nombre:str, direccion:str, telefono:str, correo:str, rut = None):
        self.rut = rut
        self.nombre = nombre
        self.direccion = direccion
        self.telefono = telefono
        self.correo = correo