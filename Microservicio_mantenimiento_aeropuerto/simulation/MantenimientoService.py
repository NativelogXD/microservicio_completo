from simulation.MantenimientoRepository import MantenimientoRepository
from simulation.Mantenimiento import Mantenimiento

class MantenimientoService:
    def __init__(self):
        self.repository = MantenimientoRepository()
        self.init_sample_data()

    def init_sample_data(self):
        m1 = Mantenimiento("AV123", "Revisión rutinaria", "Chequeo general", "2025-09-10", "Carlos López", 500)
        m2 = Mantenimiento("AV456", "Cambio de motor", "Reemplazo de motor", "2025-09-15", "Ana Torres", 15000)
        self.save(m1)
        self.save(m2)

    def save(self, mantenimiento: Mantenimiento):
        return self.repository.save(mantenimiento)

    def find_all(self):
        return self.repository.find_all()

    def find_by_id(self, id: str):
        return self.repository.find_by_id(id)

    def update(self, id: str, data: dict):
        return self.repository.update(id, data)

    def delete(self, id: str):
        return self.repository.delete(id)

    def find_by_avion(self, id_avion: str):
        return self.repository.find_by_avion(id_avion)

    def find_by_estado(self, estado: str):
        return self.repository.find_by_estado(estado)