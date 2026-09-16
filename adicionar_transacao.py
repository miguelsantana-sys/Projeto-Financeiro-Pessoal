


import sqlite3
from datetime import date

nome_banco = "financas.db"

def adicionar_transacao(data, descricao, categoria, valor, tipo):
    conexao = sqlite3.connect(nome_banco)
    cursor = conexao.cursor()

    cursor.execute("""
        INSERT INTO transacoes (data, descricao, categoria, valor, tipo)
        VALUES (?, ?, ?, ?, ?)
    """, (data, descricao, categoria, valor, tipo))

    conexao.commit()
    conexao.close()
    print("Transação adicionada com sucesso!")

def perguntar_no_terminal():
    print("=== Nova Transação ===")

    data_input = input(f"Data (AAAA-MM-DD) [Enter = hoje, {date.today()}]: ").strip()
    data_transacao = data_input if data_input else str(date.today())

    descricao = input("Descrição (ex: Mercado, Sálario): ").strip()
    categoria = input("Categoria (ex: Alimentação, Transporte, Renda): ").strip()

    while True:
        valor_input = input("Valor (ex: 150.50): ").strip().replace(",", ".")
        try:
            valor = float(valor_input)
            break
        except ValueError:
            print("Valor inválido, tente novamente.")


    while True:
        tipo = input("Tipo (entrada/saída): ").strip().lower()
        if tipo in ("entrada", "saida"):
            break
        print("Digite 'entrada' ou 'saída'.")

    adicionar_transacao(data_transacao, descricao, categoria, valor, tipo)

if __name__ == "__main__":
    perguntar_no_terminal()