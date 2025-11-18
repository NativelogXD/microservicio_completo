from flask import Flask, jsonify
from flasgger import Swagger
from simulation.MantenimientoController import mantenimiento_bp
from marshmallow import ValidationError

def create_app():
    app = Flask(__name__)

    # Configurar Swagger
    app.config['SWAGGER'] = {
        'title': 'API de Mantenimientos',
        'uiversion': 3
    }
    Swagger(app)

    # Registrar Blueprint
    app.register_blueprint(mantenimiento_bp, url_prefix="/api")
    from database.session import Base, engine
    from persistence.entity.MantenimientoEntity import MantenimientoEntity
    Base.metadata.create_all(bind=engine)

    # Manejo global de errores de validación (Marshmallow)
    @app.errorhandler(ValidationError)
    def handle_validation_error(err: ValidationError):
        details = []
        if isinstance(err.messages, dict):
            for field, msgs in err.messages.items():
                for m in msgs:
                    details.append(f"{field}: {m}")
        else:
            details = [str(err)]
        return jsonify({
            "status": 400,
            "code": "VALIDATION_ERROR",
            "message": "Error de validación en la solicitud",
            "details": details,
        }), 400

    @app.route("/")
    def home():
        return "Microservicio de Mantenimientos corriendo"

    @app.route("/health")
    def health():
        return {"status": "healthy", "service": "mantenimiento"}

    return app


if __name__ == "__main__":
    app = create_app()
    app.run(debug=True, host="0.0.0.0", port=5000)
