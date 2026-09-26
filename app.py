from flask import Flask, jsonify
from flask_cors import CORS
from flasgger import Swagger

from database import inicializar_banco
from routes.veiculos import veiculos_bp
from routes.manutencoes import manutencoes_bp
from routes.fipe import fipe_bp


def criar_app():
    app = Flask(__name__)

    CORS(app)

    app.config["SWAGGER"] = {
        "title": "MotoCare API",
        "uiversion": 3
    }

    Swagger(
    app,
    template={
        "swagger": "2.0",
        "info": {
            "title": "MotoCare API",
            "description": (
                "API REST para gerenciamento de veículos "
                "e manutenções do sistema MotoCare."
            ),
            "version": "1.0.0"
        },
        "basePath": "/",
        "schemes": [
            "http"
        ],
        "definitions": {
            "VeiculoEntrada": {
                "type": "object",
                "required": [
                    "tipo",
                    "marca",
                    "modelo",
                    "ano",
                    "placa",
                    "quilometragem"
                ],
                "properties": {
                    "tipo": {
                        "type": "string",
                        "example": "Moto"
                    },
                    "marca": {
                        "type": "string",
                        "example": "Honda"
                    },
                    "modelo": {
                        "type": "string",
                        "example": "CBX 250"
                    },
                    "ano": {
                        "type": "integer",
                        "example": 2008
                    },
                    "placa": {
                        "type": "string",
                        "example": "ABC1D23"
                    },
                    "quilometragem": {
                        "type": "integer",
                        "example": 49000
                    }
                }
            },
            "Veiculo": {
                "allOf": [
                    {
                        "$ref": "#/definitions/VeiculoEntrada"
                    },
                    {
                        "type": "object",
                        "properties": {
                            "id": {
                                "type": "integer",
                                "example": 1
                            }
                        }
                    }
                ]
            }
        }
    }
)

    app.register_blueprint(veiculos_bp)
    app.register_blueprint(manutencoes_bp)
    app.register_blueprint(fipe_bp)

    @app.route("/", methods=["GET"])
    def inicio():
        return jsonify({
            "nome": "MotoCare API",
            "versao": "1.0.0",
            "status": "online",
            "swagger": "/apidocs/"
        }), 200

    @app.errorhandler(404)
    def rota_nao_encontrada(erro):
        return jsonify({
            "erro": "Rota não encontrada."
        }), 404

    @app.errorhandler(405)
    def metodo_nao_permitido(erro):
        return jsonify({
            "erro": "Método HTTP não permitido para esta rota."
        }), 405

    inicializar_banco()

    return app


app = criar_app()


if __name__ == "__main__":
    app.run(
        host="0.0.0.0",
        port=5000,
        debug=True
    )