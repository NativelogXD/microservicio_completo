from flask import Blueprint, request, jsonify
from flasgger import swag_from
from persistence.servicelmpl.MantenimientoServiceDb import MantenimientoServiceDb
from simulation.MantenimientoSchema import MantenimientoCreateSchema, MantenimientoUpdateSchema

mantenimiento_bp = Blueprint("mantenimiento", __name__)
service = MantenimientoServiceDb()

def _to_dict(m):
    return {
        "id": getattr(m, "id", None),
        "id_avion": getattr(m, "id_avion", None),
        "tipo": getattr(m, "tipo", None),
        "descripcion": getattr(m, "descripcion", None),
        "fecha": getattr(m, "fecha", None).isoformat() if getattr(m, "fecha", None) else None,
        "responsable": getattr(m, "responsable", None),
        "costo": getattr(m, "costo", None),
        "estado": getattr(m, "estado", None),
    }

# ---------------------------------------------------
# GET all
# ---------------------------------------------------
@swag_from({
    'tags': ['Mantenimiento'],
    'description': 'Obtener todos los mantenimientos',
    'responses': {
        200: {
            'description': 'Lista de mantenimientos',
            'examples': {
                'application/json': [
                    {
                        "id": "uuid",
                        "id_avion": "AV123",
                        "tipo": "Revisión rutinaria",
                        "descripcion": "Chequeo general",
                        "fecha": "2025-09-10",
                        "responsable": "Carlos López",
                        "costo": 500,
                        "estado": "Pendiente"
                    }
                ]
            }
        }
    }
})
@mantenimiento_bp.route("/mantenimientos", methods=["GET"])
def get_all():
    mantenimientos = [
        _to_dict(m) for m in service.find_all()
    ]
    return jsonify(mantenimientos), 200


# ---------------------------------------------------
# GET by id
# ---------------------------------------------------
@swag_from({
    'tags': ['Mantenimiento'],
    'description': 'Obtener un mantenimiento por ID',
    'parameters': [
        {
            'name': 'id',
            'in': 'path',
            'type': 'string',
            'required': True
        }
    ],
    'responses': {
        200: {'description': 'Mantenimiento encontrado'},
        404: {'description': 'No encontrado'}
    }
})
@mantenimiento_bp.route("/mantenimientos/<string:id>", methods=["GET"])
def get_by_id(id):
    mantenimiento = service.find_by_id(id)
    if mantenimiento:
        return jsonify(_to_dict(mantenimiento)), 200
    return jsonify({"message": "Mantenimiento no encontrado"}), 404


# ---------------------------------------------------
# POST create
# ---------------------------------------------------
@swag_from({
    'tags': ['Mantenimiento'],
    'description': 'Crear un nuevo mantenimiento',
    'parameters': [
        {
            'name': 'body',
            'in': 'body',
            'required': True,
            'schema': {
                'properties': {
                    'id_avion': {'type': 'string'},
                    'tipo': {'type': 'string'},
                    'descripcion': {'type': 'string'},
                    'fecha': {'type': 'string'},
                    'responsable': {'type': 'string'},
                    'costo': {'type': 'number'}
                }
            }
        }
    ],
    'responses': {
        201: {'description': 'Mantenimiento creado'}
    }
})
@mantenimiento_bp.route("/mantenimientos", methods=["POST"])
def create():
    data = request.json or {}
    payload = MantenimientoCreateSchema().load(data)
    creado = service.save(payload)
    return jsonify(_to_dict(creado)), 201


# ---------------------------------------------------
# PUT update
# ---------------------------------------------------
@swag_from({
    'tags': ['Mantenimiento'],
    'description': 'Actualizar un mantenimiento existente',
    'parameters': [
        {'name': 'id', 'in': 'path', 'type': 'string', 'required': True},
        {'name': 'body', 'in': 'body', 'required': True}
    ],
    'responses': {
        200: {'description': 'Mantenimiento actualizado'},
        404: {'description': 'No encontrado'}
    }
})
@mantenimiento_bp.route("/mantenimientos/<string:id>", methods=["PUT"])
def update(id):
    data = request.json or {}
    payload = MantenimientoUpdateSchema().load(data)
    actualizado = service.update(id, payload)
    if actualizado:
        return jsonify(_to_dict(actualizado)), 200
    return jsonify({"message": "Mantenimiento no encontrado"}), 404


# ---------------------------------------------------
# DELETE
# ---------------------------------------------------
@swag_from({
    'tags': ['Mantenimiento'],
    'description': 'Eliminar un mantenimiento por ID',
    'parameters': [{'name': 'id', 'in': 'path', 'type': 'string', 'required': True}],
    'responses': {
        204: {'description': 'Mantenimiento eliminado'},
        404: {'description': 'No encontrado'}
    }
})
@mantenimiento_bp.route("/mantenimientos/<string:id>", methods=["DELETE"])
def delete(id):
    mantenimiento = service.find_by_id(id)
    if not mantenimiento:
        return jsonify({"message": "Mantenimiento no encontrado"}), 404
    service.delete(id)
    return jsonify({"message": "Mantenimiento eliminado"}), 204


# ---------------------------------------------------
# GET by id_avion
# ---------------------------------------------------
@swag_from({
    'tags': ['Mantenimiento'],
    'description': 'Obtener mantenimientos de un avión específico',
    'parameters': [{'name': 'id_avion', 'in': 'path', 'type': 'string', 'required': True}],
    'responses': {
        200: {'description': 'Lista de mantenimientos filtrados'}
    }
})
@mantenimiento_bp.route("/mantenimientos/avion/<string:id_avion>", methods=["GET"])
def get_by_avion(id_avion):
    mantenimientos = [
        _to_dict(m) for m in service.find_by_avion(id_avion)
    ]
    return jsonify(mantenimientos), 200


# ---------------------------------------------------
# GET by estado
# ---------------------------------------------------
@swag_from({
    'tags': ['Mantenimiento'],
    'description': 'Obtener mantenimientos filtrados por estado',
    'parameters': [{'name': 'estado', 'in': 'path', 'type': 'string', 'required': True}],
    'responses': {
        200: {'description': 'Lista de mantenimientos filtrados'}
    }
})
@mantenimiento_bp.route("/mantenimientos/estado/<string:estado>", methods=["GET"])
def get_by_estado(estado):
    mantenimientos = [
        _to_dict(m) for m in service.find_by_estado(estado)
    ]
    return jsonify(mantenimientos), 200