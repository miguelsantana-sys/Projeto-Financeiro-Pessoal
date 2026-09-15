import sqlite3
from tabulate import tabulate

nome_banco = "financas.db"

def conectar():
    return sqlite3.connect(nome_banco)

def saldo_total():
    conexao = conectar()
    cursor = conexao.cursor()
    cursor.execute("""
        SELECT
            SUM(CASE WHEN tipo = 'entrada' THEN valor ELSE 0 END) AS total_entradas,
            SUM(CASE WHEN tipo = 'saida' THEN valor ELSE 0 END) AS total_saidas
        FROM transacoes
    """)
    entradas, saidas = cursor.fetchone()
    entradas = entradas or 0
    saidas = saidas or 0
    conexao.close()
    return entradas, saidas, entradas - saidas

def gastos_por_categoria():
    conexao = conectar()
    cursor = conexao.cursor()
    cursor.execute("""
        SELECT categoria, SUM(valor) AS total
        FROM transacoes
        WHERE tipo = 'saida'
        GROUP BY categoria
        ORDER BY total DESC
    """)
    resultado = cursor.fetchall()
    conexao.close()
    return resultado

def gastos_por_mes():
    conexao = conectar()
    cursor = conexao.cursor()
    cursor.execute("""
        SELECT strftime('%Y-%m', data) AS mes, SUM(valor) AS total
        FROM transacoes
        WHERE tipo = 'saida'
        GROUP BY mes
        ORDER BY mes
    """)
    resultado = cursor.fetchall()
    conexao.close()
    return resultado

def formatar_reais(valor):
    return f"R$  {valor:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")

def exibir_relatorio():
    entradas, saidas, saldo = saldo_total()

    print("\n" + "=" * 40)
    print(" RESUMO GERAL".center(40))
    print("=" * 40)
    resumo = [
        ["Total de entradas", formatar_reais(entradas)],
        ["Total de saídas", formatar_reais(saidas)],
        ["Saldo", formatar_reais(saldo)],
    ]

    print(tabulate(resumo, tablefmt="fancy_grid"))


    print("\n" + "=" * 40)
    print(" GASTOS POR CATEGORIA".center(40))
    print("=" * 40)
    dados_categoria = [[cat, formatar_reais(total)] for cat, total in gastos_por_categoria()]
    print(tabulate(dados_categoria, headers=["Categoria", "Total"], tablefmt="fancy_grid"))


    print("\n" + "=" * 40)
    print(" GASTOS POR MÊS".center(40))
    print("=" * 40)
    dados_mes = [[mes, formatar_reais(total)] for mes, total in gastos_por_mes()]
    print(tabulate(dados_mes, headers=["Mês", "Total"], tablefmt="fancy_grid"))
    print()


if __name__ == "__main__":
    exibir_relatorio()