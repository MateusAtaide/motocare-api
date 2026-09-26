import requests

from flask import Blueprint, jsonify
from flasgger import swag_from


fipe_bp = Blueprint("fipe", __name__)

BRASIL_API_URL = "https://brasilapi.com.br/api/fipe"


@fipe_bp.route("/fipe/marcas/<tipo>", methods=["GET"])
@swag_from({
    "tags": ["FIPE"],
    "summary": "Lista marcas de veículos",
    "description": (
        "Consulta as marcas disponíveis na Tabela FIPE "
        "através da BrasilAPI."
    ),
    "parameters": [
        {
            "name": "tipo",
            "in": "path",
            "required": True,
            "type": "string",
            "enum": [
                "carros",
                "motos",
                "caminhoes"
            ],
            "description": "Tipo do veículo."
        }
    ],
    "responses": {
        200: {
            "description": "Lista de marcas encontrada com sucesso.",
            "schema": {
                "type": "array",
                "items": {
                    "type": "object",
                    "properties": {
                        "nome": {
                            "type": "string",
                            "example": "Honda"
                        },
                        "valor": {
                            "type": "string",
                            "example": "80"
                        }
                    }
                }
            }
        },
        400: {
            "description": "Tipo de veículo inválido."
        },
        502: {
            "description": "Erro ao consultar a BrasilAPI."
        }
    }
})
def listar_marcas(tipo):
    tipos_validos = [
        "carros",
        "motos",
        "caminhoes"
    ]

    tipo = tipo.lower().strip()

    if tipo not in tipos_validos:
        return jsonify({
            "erro": (
                "Tipo de veículo inválido. "
                "Utilize carros, motos ou caminhoes."
            )
        }), 400

    try:
        resposta = requests.get(
            f"{BRASIL_API_URL}/marcas/v1/{tipo}",
            timeout=10
        )

        resposta.raise_for_status()

        marcas = resposta.json()

        return jsonify(marcas), 200

    except requests.RequestException as erro:
        print(
            "Erro ao consultar BrasilAPI:",
            erro
        )

        return jsonify({
            "erro": (
                "Não foi possível consultar "
                "as marcas na BrasilAPI."
            )
        }), 502

@fipe_bp.route(
    "/fipe/modelos/<tipo>/<marca>",
    methods=["GET"]
)
@swag_from({
    "tags": ["FIPE"],
    "summary": "Lista modelos de uma marca",
    "description": (
        "Consulta os modelos disponíveis na Tabela FIPE "
        "para uma determinada marca através da BrasilAPI."
    ),
    "parameters": [
        {
            "name": "tipo",
            "in": "path",
            "required": True,
            "type": "string",
            "enum": [
                "carros",
                "motos",
                "caminhoes"
            ],
            "description": "Tipo do veículo."
        },
        {
            "name": "marca",
            "in": "path",
            "required": True,
            "type": "string",
            "description": "Código da marca na Tabela FIPE."
        }
    ],
    "responses": {
        200: {
            "description": "Lista de modelos encontrada com sucesso.",
            "schema": {
                "type": "array",
                "items": {
                    "type": "object",
                    "properties": {
                        "nome": {
                            "type": "string",
                            "example": "CBX 250 TWISTER"
                        },
                        "valor": {
                            "type": "string",
                            "example": "1234"
                        }
                    }
                }
            }
        },
        400: {
            "description": "Tipo de veículo inválido."
        },
        404: {
            "description": "Marca não encontrada."
        },
        502: {
            "description": "Erro ao consultar a BrasilAPI."
        }
    }
})
def listar_modelos(tipo, marca):
    tipos_validos = [
        "carros",
        "motos",
        "caminhoes"
    ]

    tipo = tipo.lower().strip()
    marca = marca.strip()

    if tipo not in tipos_validos:
        return jsonify({
            "erro": (
                "Tipo de veículo inválido. "
                "Utilize carros, motos ou caminhoes."
            )
        }), 400

    try:
        resposta = requests.get(
            f"{BRASIL_API_URL}/veiculos/v1/"
            f"{tipo}/{marca}",
            timeout=10
        )

        if resposta.status_code == 404:
            return jsonify({
                "erro": "Marca não encontrada na Tabela FIPE."
            }), 404

        resposta.raise_for_status()

        dados = resposta.json()

        if isinstance(dados, dict) and "modelos" in dados:
            modelos = dados["modelos"]
        else:
            modelos = dados

        return jsonify(modelos), 200

    except requests.RequestException as erro:
        print(
            "Erro ao consultar BrasilAPI:",
            erro
        )

        return jsonify({
            "erro": (
                "Não foi possível consultar "
                "os modelos na BrasilAPI."
            )
        }), 502
@fipe_bp.route(
    "/fipe/anos/<tipo>/<marca>/<modelo>",
    methods=["GET"]
)
@swag_from({
    "tags": ["FIPE"],
    "summary": "Lista anos de um modelo",
    "description": (
        "Consulta os anos disponíveis na Tabela FIPE "
        "para um determinado modelo através da BrasilAPI."
    ),
    "parameters": [
        {
            "name": "tipo",
            "in": "path",
            "required": True,
            "type": "string",
            "enum": [
                "carros",
                "motos",
                "caminhoes"
            ],
            "description": "Tipo do veículo."
        },
        {
            "name": "marca",
            "in": "path",
            "required": True,
            "type": "string",
            "description": "Código da marca na Tabela FIPE."
        },
        {
            "name": "modelo",
            "in": "path",
            "required": True,
            "type": "string",
            "description": "Código do modelo na Tabela FIPE."
        }
    ],
    "responses": {
        200: {
            "description": "Lista de anos encontrada com sucesso.",
            "schema": {
                "type": "array",
                "items": {
                    "type": "object",
                    "properties": {
                        "nome": {
                            "type": "string",
                            "example": "2008 Gasolina"
                        },
                        "valor": {
                            "type": "string",
                            "example": "2008-1"
                        }
                    }
                }
            }
        },
        400: {
            "description": "Tipo de veículo inválido."
        },
        404: {
            "description": "Modelo não encontrado."
        },
        502: {
            "description": "Erro ao consultar a BrasilAPI."
        }
    }
})
def listar_anos(tipo, marca, modelo):
    tipos_validos = [
        "carros",
        "motos",
        "caminhoes"
    ]

    tipo = tipo.lower().strip()
    marca = marca.strip()
    modelo = modelo.strip()

    if tipo not in tipos_validos:
        return jsonify({
            "erro": (
                "Tipo de veículo inválido. "
                "Utilize carros, motos ou caminhoes."
            )
        }), 400

    try:
        resposta = requests.get(
            f"{BRASIL_API_URL}/anos/v1/"
            f"{tipo}/{marca}/{modelo}",
            timeout=10
        )

        if resposta.status_code == 404:
            return jsonify({
                "erro": "Modelo não encontrado na Tabela FIPE."
            }), 404

        resposta.raise_for_status()

        anos = resposta.json()

        return jsonify(anos), 200

    except requests.RequestException as erro:
        print(
            "Erro ao consultar BrasilAPI:",
            erro
        )

        return jsonify({
            "erro": (
                "Não foi possível consultar "
                "os anos na BrasilAPI."
            )
        }), 502
@fipe_bp.route(
    "/fipe/detalhes/<tipo>/<marca>/<modelo>/<ano>",
    methods=["GET"]
)
@swag_from({
    "tags": ["FIPE"],
    "summary": "Consulta detalhes FIPE de um veículo",
    "description": (
        "Consulta os detalhes e o valor de referência "
        "de um veículo na Tabela FIPE através da BrasilAPI."
    ),
    "parameters": [
        {
            "name": "tipo",
            "in": "path",
            "required": True,
            "type": "string",
            "enum": [
                "carros",
                "motos",
                "caminhoes"
            ],
            "description": "Tipo do veículo."
        },
        {
            "name": "marca",
            "in": "path",
            "required": True,
            "type": "string",
            "description": "Código da marca na Tabela FIPE."
        },
        {
            "name": "modelo",
            "in": "path",
            "required": True,
            "type": "string",
            "description": "Código do modelo na Tabela FIPE."
        },
        {
            "name": "ano",
            "in": "path",
            "required": True,
            "type": "string",
            "description": (
                "Código do ano e combustível retornado "
                "pela consulta de anos."
            )
        }
    ],
    "responses": {
        200: {
            "description": "Detalhes FIPE encontrados com sucesso.",
            "schema": {
                "type": "object",
                "properties": {
                    "valor": {
                        "type": "string",
                        "example": "R$ 12.345,00"
                    },
                    "marca": {
                        "type": "string",
                        "example": "HONDA"
                    },
                    "modelo": {
                        "type": "string",
                        "example": "CBX 250 TWISTER"
                    },
                    "anoModelo": {
                        "type": "integer",
                        "example": 2008
                    },
                    "combustivel": {
                        "type": "string",
                        "example": "Gasolina"
                    },
                    "codigoFipe": {
                        "type": "string"
                    },
                    "mesReferencia": {
                        "type": "string"
                    }
                }
            }
        },
        400: {
            "description": "Tipo de veículo inválido."
        },
        404: {
            "description": "Veículo não encontrado na Tabela FIPE."
        },
        502: {
            "description": "Erro ao consultar a BrasilAPI."
        }
    }
})
def consultar_detalhes(tipo, marca, modelo, ano):
    tipos_validos = [
        "carros",
        "motos",
        "caminhoes"
    ]

    tipo = tipo.lower().strip()
    marca = marca.strip()
    modelo = modelo.strip()
    ano = ano.strip()

    if tipo not in tipos_validos:
        return jsonify({
            "erro": (
                "Tipo de veículo inválido. "
                "Utilize carros, motos ou caminhoes."
            )
        }), 400

    try:
        resposta = requests.get(
            f"{BRASIL_API_URL}/detalhes/v1/"
            f"{tipo}/{marca}/{modelo}/{ano}",
            timeout=10
        )

        if resposta.status_code == 404:
            return jsonify({
                "erro": (
                    "Veículo não encontrado "
                    "na Tabela FIPE."
                )
            }), 404

        resposta.raise_for_status()

        detalhes = resposta.json()

        return jsonify(detalhes), 200

    except requests.RequestException as erro:
        print(
            "Erro ao consultar BrasilAPI:",
            erro
        )

        return jsonify({
            "erro": (
                "Não foi possível consultar "
                "os detalhes na BrasilAPI."
            )
        }), 502