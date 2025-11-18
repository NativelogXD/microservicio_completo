import uuid
from datetime import datetime

class Mantenimiento:
    def __init__(self, id_avion, tipo, descripcion, fecha, responsable, costo, estado="Pendiente", id=None):
        self.id = id if id else str(uuid.uuid4())   # Genera un UUID si no se pasa
        self.id_avion = id_avion                   # Relación con un avión
        self.tipo = tipo                           # Tipo de mantenimiento (rutinario, correctivo, etc.)
        self.descripcion = descripcion             # Detalles del mantenimiento
        self.fecha = fecha if isinstance(fecha, str) else fecha.strftime("%Y-%m-%d")
        self.responsable = responsable             # Persona encargada
        self.costo = costo                         # Costo estimado
        self.estado = estado                       # Estado: Pendiente, En Proceso, Completado

    def __repr__(self):
        return f"<Mantenimiento {self.id} - {self.tipo} - {self.estado}>"