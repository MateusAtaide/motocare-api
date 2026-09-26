from flask import Blueprint, jsonify, request
from flasgger import swag_from

from database import conectar_banco


manutencoes_bp = Blueprint(
    "manutencoes",
    __name__
)


def converter_manutencao(registro):
    return {
        "id": registro["id"],
        "veiculoId": registro["veiculo_id"],
        "tipo": registro["tipo"],
        "data": registro["data"],
        "quilometragem": registro["quilometragem"],
        "valor": registro["valor"],
        "proximaQuilometragem":
            registro["proxima_quilometragem"],
        "observacoes": registro["observacoes"] or ""
    }


# =========================================================
# GET /manutencoes
# =========================================================

@manutencoes_bp.route(
    "/manutencoes",
    methods=["GET"]
)
@swag_from({
    "tags": ["Manutenções"],
    "summary": "Lista todas as manutenções",
    "description": (
        "Retorna todas as manutenções cadastradas "
        "no MotoCare."
    ),
    "responses": {
        200: {
            "description":
                "Lista de manutenções retornada com sucesso.",
            "schema": {
                "type": "array",
                "items": {
                    "$ref": "#/definitions/Manutencao"
                }
            }
        }
    }
})
def listar_manutencoes():
    conexao = conectar_banco()

    try:
        registros = conexao.execute(
            """
            SELECT
                id,
                veiculo_id,
                tipo,
                data,
                quilometragem,
                valor,
                proxima_quilometragem,
                observacoes
            FROM manutencoes
            ORDER BY data DESC, id DESC
            """
        ).fetchall()

        manutencoes = [
            converter_manutencao(registro)
            for registro in registros
        ]

        return jsonify(manutencoes), 200

    finally:
        conexao.close()


# =========================================================
# GET /manutencoes/{id}
# =========================================================

@manutencoes_bp.route(
    "/manutencoes/<int:manutencao_id>",
    methods=["GET"]
)
@swag_from({
    "tags": ["Manutenções"],
    "summary": "Busca uma manutenção pelo ID",
    "parameters": [
        {
            "name": "manutencao_id",
            "in": "path",
            "type": "integer",
            "required": True,
            "description": "ID da manutenção"
        }
    ],
    "responses": {
        200: {
            "description": "Manutenção encontrada.",
            "schema": {
                "$ref": "#/definitions/Manutencao"
            }
        },
        404: {
            "description": "Manutenção não encontrada."
        }
    }
})
def buscar_manutencao(manutencao_id):
    conexao = conectar_banco()

    try:
        registro = conexao.execute(
            """
            SELECT
                id,
                veiculo_id,
                tipo,
                data,
                quilometragem,
                valor,
                proxima_quilometragem,
                observacoes
            FROM manutencoes
            WHERE id = ?
            """,
            (manutencao_id,)
        ).fetchone()

        if registro is None:
            return jsonify({
                "erro": "Manutenção não encontrada."
            }), 404

        return jsonify(
            converter_manutencao(registro)
        ), 200

    finally:
        conexao.close()


# =========================================================
# POST /manutencoes
# =========================================================

@manutencoes_bp.route(
    "/manutencoes",
    methods=["POST"]
)
@swag_from({
    "tags": ["Manutenções"],
    "summary": "Cadastra uma nova manutenção",
    "description": (
        "Cadastra uma manutenção vinculada "
        "a um veículo existente."
    ),
    "parameters": [
        {
            "name": "body",
            "in": "body",
            "required": True,
            "schema": {
                "$ref": "#/definitions/ManutencaoEntrada"
            }
        }
    ],
    "responses": {
        201: {
            "description":
                "Manutenção cadastrada com sucesso.",
            "schema": {
                "$ref": "#/definitions/Manutencao"
            }
        },
        400: {
            "description": "Dados inválidos."
        },
        404: {
            "description": "Veículo não encontrado."
        }
    }
})
def cadastrar_manutencao():
    dados = request.get_json(silent=True)

    if not dados:
        return jsonify({
            "erro": "Dados da manutenção não informados."
        }), 400

    campos_obrigatorios = [
        "veiculoId",
        "tipo",
        "data",
        "quilometragem",
        "valor"
    ]

    for campo in campos_obrigatorios:
        if campo not in dados:
            return jsonify({
                "erro":
                    f"Campo obrigatório não informado: {campo}."
            }), 400

    tipo = str(dados["tipo"]).strip()
    data = str(dados["data"]).strip()

    if not tipo or not data:
        return jsonify({
            "erro":
                "Os campos obrigatórios não podem estar vazios."
        }), 400

    try:
        veiculo_id = int(dados["veiculoId"])

        quilometragem = int(
            dados["quilometragem"]
        )

        valor = float(
            dados["valor"]
        )

        proxima_quilometragem = dados.get(
            "proximaQuilometragem"
        )

        if (
            proxima_quilometragem is not None
            and proxima_quilometragem != ""
        ):
            proxima_quilometragem = int(
                proxima_quilometragem
            )
        else:
            proxima_quilometragem = None

    except (TypeError, ValueError):
        return jsonify({
            "erro": (
                "Veículo, quilometragem e valor devem "
                "possuir valores válidos."
            )
        }), 400

    if quilometragem < 0 or valor < 0:
        return jsonify({
            "erro":
                "Quilometragem e valor não podem ser negativos."
        }), 400

    if (
        proxima_quilometragem is not None
        and proxima_quilometragem <= quilometragem
    ):
        return jsonify({
            "erro": (
                "A próxima quilometragem deve ser maior "
                "que a quilometragem atual."
            )
        }), 400

    observacoes = str(
        dados.get("observacoes", "")
    ).strip()

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

        cursor = conexao.execute(
            """
            INSERT INTO manutencoes (
                veiculo_id,
                tipo,
                data,
                quilometragem,
                valor,
                proxima_quilometragem,
                observacoes
            )
            VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            (
                veiculo_id,
                tipo,
                data,
                quilometragem,
                valor,
                proxima_quilometragem,
                observacoes
            )
        )

        conexao.commit()

        registro = conexao.execute(
            """
            SELECT
                id,
                veiculo_id,
                tipo,
                data,
                quilometragem,
                valor,
                proxima_quilometragem,
                observacoes
            FROM manutencoes
            WHERE id = ?
            """,
            (cursor.lastrowid,)
        ).fetchone()

        return jsonify(
            converter_manutencao(registro)
        ), 201

    finally:
        conexao.close()


# =========================================================
# PUT /manutencoes/{id}
# =========================================================

@manutencoes_bp.route(
    "/manutencoes/<int:manutencao_id>",
    methods=["PUT"]
)
@swag_from({
    "tags": ["Manutenções"],
    "summary": "Atualiza uma manutenção",
    "parameters": [
        {
            "name": "manutencao_id",
            "in": "path",
            "type": "integer",
            "required": True,
            "description": "ID da manutenção"
        },
        {
            "name": "body",
            "in": "body",
            "required": True,
            "schema": {
                "$ref": "#/definitions/ManutencaoEntrada"
            }
        }
    ],
    "responses": {
        200: {
            "description":
                "Manutenção atualizada com sucesso.",
            "schema": {
                "$ref": "#/definitions/Manutencao"
            }
        },
        400: {
            "description": "Dados inválidos."
        },
        404: {
            "description":
                "Manutenção ou veículo não encontrado."
        }
    }
})
def atualizar_manutencao(manutencao_id):
    dados = request.get_json(silent=True)

    if not dados:
        return jsonify({
            "erro": "Dados da manutenção não informados."
        }), 400

    campos_obrigatorios = [
        "veiculoId",
        "tipo",
        "data",
        "quilometragem",
        "valor"
    ]

    for campo in campos_obrigatorios:
        if campo not in dados:
            return jsonify({
                "erro":
                    f"Campo obrigatório não informado: {campo}."
            }), 400

    tipo = str(dados["tipo"]).strip()
    data = str(dados["data"]).strip()

    if not tipo or not data:
        return jsonify({
            "erro":
                "Os campos obrigatórios não podem estar vazios."
        }), 400

    try:
        veiculo_id = int(dados["veiculoId"])

        quilometragem = int(
            dados["quilometragem"]
        )

        valor = float(
            dados["valor"]
        )

        proxima_quilometragem = dados.get(
            "proximaQuilometragem"
        )

        if (
            proxima_quilometragem is not None
            and proxima_quilometragem != ""
        ):
            proxima_quilometragem = int(
                proxima_quilometragem
            )
        else:
            proxima_quilometragem = None

    except (TypeError, ValueError):
        return jsonify({
            "erro": (
                "Veículo, quilometragem e valor devem "
                "possuir valores válidos."
            )
        }), 400

    if quilometragem < 0 or valor < 0:
        return jsonify({
            "erro":
                "Quilometragem e valor não podem ser negativos."
        }), 400

    if (
        proxima_quilometragem is not None
        and proxima_quilometragem <= quilometragem
    ):
        return jsonify({
            "erro": (
                "A próxima quilometragem deve ser maior "
                "que a quilometragem atual."
            )
        }), 400

    observacoes = str(
        dados.get("observacoes", "")
    ).strip()

    conexao = conectar_banco()

    try:
        manutencao = conexao.execute(
            """
            SELECT id
            FROM manutencoes
            WHERE id = ?
            """,
            (manutencao_id,)
        ).fetchone()

        if manutencao is None:
            return jsonify({
                "erro": "Manutenção não encontrada."
            }), 404

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
            UPDATE manutencoes
            SET
                veiculo_id = ?,
                tipo = ?,
                data = ?,
                quilometragem = ?,
                valor = ?,
                proxima_quilometragem = ?,
                observacoes = ?
            WHERE id = ?
            """,
            (
                veiculo_id,
                tipo,
                data,
                quilometragem,
                valor,
                proxima_quilometragem,
                observacoes,
                manutencao_id
            )
        )

        conexao.commit()

        registro = conexao.execute(
            """
            SELECT
                id,
                veiculo_id,
                tipo,
                data,
                quilometragem,
                valor,
                proxima_quilometragem,
                observacoes
            FROM manutencoes
            WHERE id = ?
            """,
            (manutencao_id,)
        ).fetchone()

        return jsonify(
            converter_manutencao(registro)
        ), 200

    finally:
        conexao.close()


# =========================================================
# DELETE /manutencoes/{id}
# =========================================================

@manutencoes_bp.route(
    "/manutencoes/<int:manutencao_id>",
    methods=["DELETE"]
)
@swag_from({
    "tags": ["Manutenções"],
    "summary": "Exclui uma manutenção",
    "parameters": [
        {
            "name": "manutencao_id",
            "in": "path",
            "type": "integer",
            "required": True,
            "description": "ID da manutenção"
        }
    ],
    "responses": {
        200: {
            "description":
                "Manutenção excluída com sucesso."
        },
        404: {
            "description":
                "Manutenção não encontrada."
        }
    }
})
def excluir_manutencao(manutencao_id):
    conexao = conectar_banco()

    try:
        manutencao = conexao.execute(
            """
            SELECT id
            FROM manutencoes
            WHERE id = ?
            """,
            (manutencao_id,)
        ).fetchone()

        if manutencao is None:
            return jsonify({
                "erro": "Manutenção não encontrada."
            }), 404

        conexao.execute(
            """
            DELETE FROM manutencoes
            WHERE id = ?
            """,
            (manutencao_id,)
        )

        conexao.commit()

        return jsonify({
            "mensagem":
                "Manutenção excluída com sucesso."
        }), 200

    finally:
        conexao.close()