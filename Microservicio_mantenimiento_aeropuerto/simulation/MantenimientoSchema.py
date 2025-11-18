from marshmallow import Schema, fields, validate


class MantenimientoCreateSchema(Schema):
    id_avion = fields.Str(required=True, validate=validate.Length(min=1))
    tipo = fields.Str(required=True, validate=validate.Length(min=2, max=100))
    descripcion = fields.Str(required=True, validate=validate.Length(min=2, max=255))
    fecha = fields.Date(required=True, format="%Y-%m-%d")
    responsable = fields.Str(required=True, validate=validate.Length(min=2, max=100))
    costo = fields.Float(required=True, validate=validate.Range(min=0))
    estado = fields.Str(required=False, validate=validate.OneOf(["Pendiente", "En Proceso", "Completado"]))


class MantenimientoUpdateSchema(Schema):
    # Todos opcionales, se validan formatos si se envían
    id_avion = fields.Str(validate=validate.Length(min=1))
    tipo = fields.Str(validate=validate.Length(min=2, max=100))
    descripcion = fields.Str(validate=validate.Length(min=2, max=255))
    fecha = fields.Date(format="%Y-%m-%d")
    responsable = fields.Str(validate=validate.Length(min=2, max=100))
    costo = fields.Float(validate=validate.Range(min=0))
    estado = fields.Str(validate=validate.OneOf(["Pendiente", "En Proceso", "Completado"]))