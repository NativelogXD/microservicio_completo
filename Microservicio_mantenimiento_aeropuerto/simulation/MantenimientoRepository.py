from simulation.Mantenimiento import Mantenimiento

class MantenimientoRepository:
    def __init__(self):
        self.base_datos = []

    def save(self, mantenimiento: Mantenimiento):
        self.base_datos.append(mantenimiento)
        return mantenimiento

    def find_all(self):
        return self.base_datos

    def find_by_id(self, id: str):
        return next((m for m in self.base_datos if m.id == id), None)

    def update(self, id: str, data: dict):
        mantenimiento = self.find_by_id(id)
        if mantenimiento:
            for key, value in data.items():
                if hasattr(mantenimiento, key):
                    setattr(mantenimiento, key, value)
            return mantenimiento
        return None

    def delete(self, id: str):
        self.base_datos = [m for m in self.base_datos if m.id != id]

    def find_by_avion(self, id_avion: str):
        return [m for m in self.base_datos if m.id_avion == id_avion]

    def find_by_estado(self, estado: str):
        return [m for m in self.base_datos if m.estado == estado]