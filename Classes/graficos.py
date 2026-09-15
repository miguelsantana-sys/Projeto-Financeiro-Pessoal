import sqlite3
import matplotlib.pyplot as plt
from consultas import gastos_por_categoria, gastos_por_mes
 
PASTA_SAIDA = "graficos_saida"
 
 
def gerar_grafico_pizza():
    dados = gastos_por_categoria()
    if not dados:
        print("Sem dados de gastos para gerar o gráfico de pizza.")
        return
 
    categorias = [linha[0] for linha in dados]
    valores = [linha[1] for linha in dados]
 
    plt.figure(figsize=(6, 6))
    plt.pie(valores, labels=categorias, autopct="%1.1f%%", startangle=90)
    plt.title("Gastos por categoria")
    plt.tight_layout()
    caminho = f"{PASTA_SAIDA}/gastos_por_categoria.png"
    plt.savefig(caminho, dpi=150)
    plt.close()
    print(f"Gráfico salvo em: {caminho}")
 
 
def gerar_grafico_linha():
    dados = gastos_por_mes()
    if not dados:
        print("Sem dados de gastos para gerar o gráfico de linha.")
        return
 
    meses = [linha[0] for linha in dados]
    valores = [linha[1] for linha in dados]
 
    plt.figure(figsize=(8, 5))
    plt.plot(meses, valores, marker="o", linewidth=2)
    plt.title("Evolução dos gastos por mês")
    plt.xlabel("Mês")
    plt.ylabel("Total gasto (R$)")
    plt.grid(True, linestyle="--", alpha=0.5)
    plt.tight_layout()
    caminho = f"{PASTA_SAIDA}/gastos_por_mes.png"
    plt.savefig(caminho, dpi=150)
    plt.close()
    print(f"Gráfico salvo em: {caminho}")
 
 
if __name__ == "__main__":
    import os
    os.makedirs(PASTA_SAIDA, exist_ok=True)
    gerar_grafico_pizza()
    gerar_grafico_linha()
