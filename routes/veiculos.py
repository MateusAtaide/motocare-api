from flask import Blueprint, jsonify, request
import sqlite3
from flasgger import swag_from

from database import conectar_banco


veiculos_bp = Blueprint(
    "veiculos",
    __name__
)


def converter_veiculo(registro):
    return {
        "id": registro["id"],
        "tipo": registro["tipo"],
        "marca": registro["marca"],
        "modelo": registro["modelo"],
        "ano": registro["ano"],
        "placa": registro["placa"],
        "quilometragem": registro["quilometragem"]
    }


@veiculos_bp.route(
    "/veiculos",
    methods=["GET"]
)
@swag_from({
    "tags": ["Veículos"],
    "summary": "Lista todos os veículos",
    "description": "Retorna todos os veículos cadastrados no MotoCare.",
    "responses": {
        200: {
            "description": "Lista de veículos retornada com sucesso.",
            "schema": {
                "type": "array",
                "items": {
                    "$ref": "#/definitions/Veiculo"
                }
            }
        }
    }
})
def listar_veiculos():
    conexao = conectar_banco()

    try:
        registros = conexao.execute(
            """
            SELECT
                id,
                tipo,
                marca,
                modelo,
                ano,
                placa,
                quilometragem
            FROM veiculos
            ORDER BY id DESC
            """
        ).fetchall()

        veiculos = [
            converter_veiculo(registro)
            for registro in registros
        ]

        return jsonify(veiculos), 200

    finally:
        conexao.close()


@veiculos_bp.route(
    "/veiculos/<int:veiculo_id>",
    methods=["GET"]
)
@swag_from({
    "tags": ["Veículos"],
    "summary": "Busca um veículo pelo ID",
    "parameters": [
        {
            "name": "veiculo_id",
            "in": "path",
            "type": "integer",
            "required": True,
            "description": "ID do veículo"
        }
    ],
    "responses": {
        200: {
            "description": "Veículo encontrado.",
            "schema": {
                "$ref": "#/definitions/Veiculo"
            }
        },
        404: {
            "description": "Veículo não encontrado."
        }
    }
})
def buscar_veiculo(veiculo_id):
    conexao = conectar_banco()

    try:
        registro = conexao.execute(
            """
            SELECT
                id,
                tipo,
                marca,
                modelo,
                ano,
                placa,
                quilometragem
            FROM veiculos
            WHERE id = ?
            """,
            (veiculo_id,)
        ).fetchone()

        if registro is None:
            return jsonify({
                "erro": "Veículo não encontrado."
            }), 404

        return jsonify(
            converter_veiculo(registro)
        ), 200

    finally:
        conexao.close()


@veiculos_bp.route(
    "/veiculos",
    methods=["POST"]
)
@swag_from({
    "tags": ["Veículos"],
    "summary": "Cadastra um novo veículo",
    "parameters": [
        {
            "name": "body",
            "in": "body",
            "required": True,
            "schema": {
                "$ref": "#/definitions/VeiculoEntrada"
            }
        }
    ],
    "responses": {
        201: {
            "description": "Veículo cadastrado com sucesso.",
            "schema": {
                "$ref": "#/definitions/Veiculo"
            }
        },
        400: {
            "description": "Dados inválidos."
        },
        409: {
            "description": "Já existe um veículo com a placa informada."
        }
    }
})
def cadastrar_veiculo():
    dados = request.get_json(silent=True)

    if not dados:
        return jsonify({
            "erro": "Dados do veículo não informados."
        }), 400

    campos_obrigatorios = [
        "tipo",
        "marca",
        "modelo",
        "ano",
        "placa",
        "quilometragem"
    ]

    for campo in campos_obrigatorios:
        if campo not in dados:
            return jsonify({
                "erro": f"Campo obrigatório não informado: {campo}."
            }), 400

    tipo = str(dados["tipo"]).strip()
    marca = str(dados["marca"]).strip()
    modelo = str(dados["modelo"]).strip()
    placa = str(dados["placa"]).strip().upper()

    if not tipo or not marca or not modelo or not placa:
        return jsonify({
            "erro": "Os campos obrigatórios não podem estar vazios."
        }), 400

    try:
        ano = int(dados["ano"])
        quilometragem = int(
            dados["quilometragem"]
        )
    except (TypeError, ValueError):
        return jsonify({
            "erro": "Ano e quilometragem devem ser valores numéricos."
        }), 400

    if ano < 1900:
        return jsonify({
            "erro": "Informe um ano válido."
        }), 400

    if quilometragem < 0:
        return jsonify({
            "erro": "A quilometragem não pode ser negativa."
        }), 400

    conexao = conectar_banco()

    try:
        cursor = conexao.execute(
            """
            INSERT INTO veiculos (
                tipo,
                marca,
                modelo,
                ano,
                placa,
                quilometragem
            )
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (
                tipo,
                marca,
                modelo,
                ano,
                placa,
                quilometragem
            )
        )

        conexao.commit()

        registro = conexao.execute(
            """
            SELECT
                id,
                tipo,
                marca,
                modelo,
                ano,
                placa,
                quilometragem
            FROM veiculos
            WHERE id = ?
            """,
            (cursor.lastrowid,)
        ).fetchone()

        return jsonify(
            converter_veiculo(registro)
        ), 201

    except sqlite3.IntegrityError:
        return jsonify({
            "erro": "Já existe um veículo cadastrado com esta placa."
        }), 409

    finally:
        conexao.close()


@veiculos_bp.route(
    "/veiculos/<int:veiculo_id>",
    methods=["PUT"]
)
@swag_from({
    "tags": ["Veículos"],
    "summary": "Atualiza um veículo",
    "parameters": [
        {
            "name": "veiculo_id",
            "in": "path",
            "type": "integer",
            "required": True,
            "description": "ID do veículo"
        },
        {
            "name": "body",
            "in": "body",
            "required": True,
            "schema": {
                "$ref": "#/definitions/VeiculoEntrada"
            }
        }
    ],
    "responses": {
        200: {
            "description": "Veículo atualizado com sucesso.",
            "schema": {
                "$ref": "#/definitions/Veiculo"
            }
        },
        400: {
            "description": "Dados inválidos."
        },
        404: {
            "description": "Veículo não encontrado."
        },
        409: {
            "description": "Já existe um veículo com a placa informada."
        }
    }
})
def atualizar_veiculo(veiculo_id):
    dados = request.get_json(silent=True)

    if not dados:
        return jsonify({
            "erro": "Dados do veículo não informados."
        }), 400

    campos_obrigatorios = [
        "tipo",
        "marca",
        "modelo",
        "ano",
        "placa",
        "quilometragem"
    ]

    for campo in campos_obrigatorios:
        if campo not in dados:
            return jsonify({
                "erro": f"Campo obrigatório não informado: {campo}."
            }), 400

    tipo = str(dados["tipo"]).strip()
    marca = str(dados["marca"]).strip()
    modelo = str(dados["modelo"]).strip()
    placa = str(dados["placa"]).strip().upper()

    if not tipo or not marca or not modelo or not placa:
        return jsonify({
            "erro": "Os campos obrigatórios não podem estar vazios."
        }), 400

    try:
        ano = int(dados["ano"])
        quilometragem = int(
            dados["quilometragem"]
        )
    except (TypeError, ValueError):
        return jsonify({
            "erro": "Ano e quilometragem devem ser valores numéricos."
        }), 400

    if ano < 1900:
        return jsonify({
            "erro": "Informe um ano válido."
        }), 400

    if quilometragem < 0:
        return jsonify({
            "erro": "A quilometragem não pode ser negativa."
        }), 400

    conexao = conectar_banco()

    try:
        veiculo_existente = conexao.execute(
            """
            SELECT id
            FROM veiculos
            WHERE id = ?
            """,
            (veiculo_id,)
        ).fetchone()

        if veiculo_existente is None:
            return jsonify({
                "erro": "Veículo não encontrado."
            }), 404

        conexao.execute(
            """
            UPDATE veiculos
            SET
                tipo = ?,
                marca = ?,
                modelo = ?,
                ano = ?,
                placa = ?,
                quilometragem = ?
            WHERE id = ?
            """,
            (
                tipo,
                marca,
                modelo,
                ano,
                placa,
                quilometragem,
                veiculo_id
            )
        )

        conexao.commit()

        registro = conexao.execute(
            """
            SELECT
                id,
                tipo,
                marca,
                modelo,
                ano,
                placa,
                quilometragem
            FROM veiculos
            WHERE id = ?
            """,
            (veiculo_id,)
        ).fetchone()

        return jsonify(
            converter_veiculo(registro)
        ), 200

    except sqlite3.IntegrityError:
        return jsonify({
            "erro": "Já existe um veículo cadastrado com esta placa."
        }), 409

    finally:
        conexao.close()


@veiculos_bp.route(
    "/veiculos/<int:veiculo_id>",
    methods=["DELETE"]
)
@swag_from({
    "tags": ["Veículos"],
    "summary": "Exclui um veículo",
    "description": (
        "Exclui o veículo e suas manutenções "
        "associadas."
    ),
    "parameters": [
        {
            "name": "veiculo_id",
            "in": "path",
            "type": "integer",
            "required": True,
            "description": "ID do veículo"
        }
    ],
    "responses": {
        200: {
            "description": "Veículo excluído com sucesso."
        },
        404: {
            "description": "Veículo não encontrado."
        }
    }
})
def excluir_veiculo(veiculo_id):
    conexao = conectar_banco()

    try:
        veiculo = conexao.execute(
            """
            SELECT id
            FROM veiculos
            WHERE id = ?
            """,
            (veiculo_id,)
        ).fetchone()

        if veiculo is None:
            return jsonify({
                "erro": "Veículo não encontrado."
            }), 404

        conexao.execute(
            """
            DELETE FROM veiculos
            WHERE id = ?
            """,
            (veiculo_id,)
        )

        conexao.commit()

        return jsonify({
            "mensagem": "Veículo excluído com sucesso."
        }), 200

    finally:
        conexao.close()