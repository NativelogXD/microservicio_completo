from typing import List, Optional
from persistence.repositorylmpl.MantenimientoRepositoryDb import MantenimientoRepositoryDb
from persistence.entity.MantenimientoEntity import MantenimientoEntity
from database.session import DBSessionContext

class MantenimientoServiceDb:
    def __init__(self):
        pass

    def _normalize(self, data: dict) -> dict:
        from datetime import datetime, date
        normalized = dict(data)
        if 'fecha' in normalized and isinstance(normalized['fecha'], str):
            try:
                normalized['fecha'] = datetime.fromisoformat(normalized['fecha']).date()
            except ValueError:
                normalized['fecha'] = datetime.strptime(normalized['fecha'], "%Y-%m-%d").date()
        if 'costo' in normalized and isinstance(normalized['costo'], str):
            try:
                normalized['costo'] = float(normalized['costo'])
            except ValueError:
                pass
        return normalized

    def save(self, data: dict) -> MantenimientoEntity:
        with DBSessionContext() as db:
            repo = MantenimientoRepositoryDb(db)
            m = MantenimientoEntity(**self._normalize(data))
            return repo.save(m)

    def find_all(self) -> List[MantenimientoEntity]:
        with DBSessionContext() as db:
            repo = MantenimientoRepositoryDb(db)
            return repo.find_all()

    def find_by_id(self, id: str) -> Optional[MantenimientoEntity]:
        with DBSessionContext() as db:
            repo = MantenimientoRepositoryDb(db)
            return repo.find_by_id(id)

    def update(self, id: str, data: dict) -> Optional[MantenimientoEntity]:
        with DBSessionContext() as db:
            repo = MantenimientoRepositoryDb(db)
            return repo.update(id, self._normalize(data))

    def delete(self, id: str) -> bool:
        with DBSessionContext() as db:
            repo = MantenimientoRepositoryDb(db)
            return repo.delete(id)

    def find_by_avion(self, id_avion: str) -> List[MantenimientoEntity]:
        with DBSessionContext() as db:
            repo = MantenimientoRepositoryDb(db)
            return repo.find_by_avion(id_avion)

    def find_by_estado(self, estado: str) -> List[MantenimientoEntity]:
        with DBSessionContext() as db:
            repo = MantenimientoRepositoryDb(db)
            return repo.find_by_estado(estado)