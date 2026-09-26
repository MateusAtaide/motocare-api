import os
import sqlite3


BASE_DIR = os.path.dirname(
    os.path.abspath(__file__)
)

DATABASE_DIR = os.path.join(
    BASE_DIR,
    "database"
)

DATABASE_PATH = os.path.join(
    DATABASE_DIR,
    "motocare.db"
)


def conectar_banco():
    conexao = sqlite3.connect(DATABASE_PATH)

    conexao.row_factory = sqlite3.Row

    conexao.execute(
        "PRAGMA foreign_keys = ON"
    )

    return conexao


def inicializar_banco():
    os.makedirs(
        DATABASE_DIR,
        exist_ok=True
    )

    conexao = conectar_banco()

    try:
        cursor = conexao.cursor()

        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS veiculos (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                tipo TEXT NOT NULL,
                marca TEXT NOT NULL,
                modelo TEXT NOT NULL,
                ano INTEGER NOT NULL,
                placa TEXT NOT NULL UNIQUE,
                quilometragem INTEGER NOT NULL DEFAULT 0
            )
            """
        )

        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS manutencoes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                veiculo_id INTEGER NOT NULL,
                tipo TEXT NOT NULL,
                data TEXT NOT NULL,
                quilometragem INTEGER NOT NULL,
                valor REAL NOT NULL,
                proxima_quilometragem INTEGER,
                observacoes TEXT,
                FOREIGN KEY (veiculo_id)
                    REFERENCES veiculos(id)
                    ON DELETE CASCADE
            )
            """
        )

        conexao.commit()

    finally:
        conexao.close()