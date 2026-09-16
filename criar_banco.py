import sqlite3

nome_banco = "financas.db"

def criar_banco():
    conexao = sqlite3.connect(nome_banco)
    cursor = conexao.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS transacoes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            data TEXT NOT NULL,
            descricao TEXT NOT NULL,
            categoria TEXT NOT NULL,
            valor REAL NOT NULL,
            tipo TEXT NOT NULL CHECK (tipo IN ('entrada', 'saida'))
        )
    """)

    conexao.commit()
    conexao.close()
    print(f"Banco '{nome_banco}' criado com sucesso, com a tabela 'transações'.")


if __name__ == "__main__":
    criar_banco()