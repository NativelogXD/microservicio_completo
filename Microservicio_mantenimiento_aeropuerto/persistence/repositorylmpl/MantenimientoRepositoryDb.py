from sqlalchemy.orm import Session
from typing import List, Optional
from persistence.entity.MantenimientoEntity import MantenimientoEntity

class MantenimientoRepositoryDb:
    def __init__(self, db: Session):
        self.db = db

    def save(self, mantenimiento: MantenimientoEntity) -> MantenimientoEntity:
        self.db.add(mantenimiento)
        self.db.commit()
        self.db.refresh(mantenimiento)
        return mantenimiento

    def find_all(self) -> List[MantenimientoEntity]:
        return self.db.query(MantenimientoEntity).all()

    def find_by_id(self, id: str) -> Optional[MantenimientoEntity]:
        return self.db.query(MantenimientoEntity).filter(MantenimientoEntity.id == id).first()

    def update(self, id: str, data: dict) -> Optional[MantenimientoEntity]:
        m = self.find_by_id(id)
        if not m:
            return None
        for k, v in data.items():
            if hasattr(m, k):
                setattr(m, k, v)
        self.db.commit()
        self.db.refresh(m)
        return m

    def delete(self, id: str) -> bool:
        m = self.find_by_id(id)
        if not m:
            return False
        self.db.delete(m)
        self.db.commit()
        return True

    def find_by_avion(self, id_avion: str) -> List[MantenimientoEntity]:
        return self.db.query(MantenimientoEntity).filter(MantenimientoEntity.id_avion == id_avion).all()

    def find_by_estado(self, estado: str) -> List[MantenimientoEntity]:
        return self.db.query(MantenimientoEntity).filter(MantenimientoEntity.estado == estado).all()