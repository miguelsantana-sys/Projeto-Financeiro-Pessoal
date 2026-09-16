
import io
import os
import sqlite3
from datetime import date
 
import pandas as pd
import plotly.express as px
import streamlit as st
 
NOME_BANCO = "financas.db"
 
CATEGORIAS_PADRAO = [
    "Alimentação", "Transporte", "Moradia", "Lazer",
    "Saúde", "Educação", "Renda", "Outros",
]
 
ICONES_CATEGORIA = {
    "Alimentação": "🍔",
    "Transporte": "🚗",
    "Moradia": "🏠",
    "Lazer": "🎮",
    "Saúde": "🏥",
    "Educação": "📚",
    "Renda": "💵",
    "Outros": "📦",
}
 
NOME_AUTOR = "Miguel Santana Florêncio"
LINK_GITHUB = "https://github.com/seu-usuario"

CAMINHO_LOGO = "logo.png"
 
st.set_page_config(
    page_title="Controle Financeiro",
    page_icon=CAMINHO_LOGO if CAMINHO_LOGO and os.path.exists(CAMINHO_LOGO) else "💰",
    layout="wide",
)
 
 
# ---------------------------------------------------------
# Carregar CSS externo (estilo.css)
# ---------------------------------------------------------
def carregar_css(caminho):
    with open(caminho, encoding="utf-8") as arquivo:
        st.markdown(f"<style>{arquivo.read()}</style>", unsafe_allow_html=True)
 
 
carregar_css("estilo.css")
 
 
# ---------------------------------------------------------
# Banco de dados
# ---------------------------------------------------------
def conectar():
    return sqlite3.connect(NOME_BANCO)
 
 
def garantir_banco():
    conexao = conectar()
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
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS metas (
            categoria TEXT PRIMARY KEY,
            limite REAL NOT NULL
        )
    """)
    conexao.commit()
    conexao.close()
 
 
def carregar_dados():
    conexao = conectar()
    df = pd.read_sql_query("SELECT * FROM transacoes", conexao)
    conexao.close()
    if not df.empty:
        df["data"] = pd.to_datetime(df["data"])
        df["mes"] = df["data"].dt.strftime("%Y-%m")
    return df
 
 
def carregar_metas():
    conexao = conectar()
    df = pd.read_sql_query("SELECT * FROM metas", conexao)
    conexao.close()
    return df
 
 
def salvar_meta(categoria, limite):
    conexao = conectar()
    cursor = conexao.cursor()
    cursor.execute(
        "INSERT INTO metas (categoria, limite) VALUES (?, ?) "
        "ON CONFLICT(categoria) DO UPDATE SET limite = excluded.limite",
        (categoria, limite),
    )
    conexao.commit()
    conexao.close()
 
 
def inserir_transacao(data_transacao, descricao, categoria, valor, tipo):
    conexao = conectar()
    cursor = conexao.cursor()
    cursor.execute(
        """
        INSERT INTO transacoes (data, descricao, categoria, valor, tipo)
        VALUES (?, ?, ?, ?, ?)
        """,
        (str(data_transacao), descricao, categoria, valor, tipo),
    )
    conexao.commit()
    conexao.close()
 
 
def atualizar_transacao(id_transacao, data_transacao, descricao, categoria, valor, tipo):
    conexao = conectar()
    cursor = conexao.cursor()
    cursor.execute(
        """
        UPDATE transacoes
        SET data = ?, descricao = ?, categoria = ?, valor = ?, tipo = ?
        WHERE id = ?
        """,
        (str(data_transacao), descricao, categoria, valor, tipo, id_transacao),
    )
    conexao.commit()
    conexao.close()
 
 
def excluir_transacao(id_transacao):
    conexao = conectar()
    cursor = conexao.cursor()
    cursor.execute("DELETE FROM transacoes WHERE id = ?", (id_transacao,))
    conexao.commit()
    conexao.close()
 
 
# ---------------------------------------------------------
# Formatação
# ---------------------------------------------------------
def formatar_reais(valor):
    texto = f"R$ {abs(valor):,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
    return f"-{texto}" if valor < 0 else texto
 
 
def cartao_metrica(label, valor_formatado, classe_extra="", subtitulo=None):
    sub_html = f'<div class="metric-sub">{subtitulo}</div>' if subtitulo else ""
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-label">{label}</div>
        <div class="metric-value {classe_extra}">{valor_formatado}</div>
        {sub_html}
    </div>
    """, unsafe_allow_html=True)
 
 
garantir_banco()
 
# ---------------------------------------------------------
# Barra lateral — navegação e assinatura (sem filtros aqui)
# ---------------------------------------------------------
with st.sidebar:
    if CAMINHO_LOGO and os.path.exists(CAMINHO_LOGO):
        st.image(CAMINHO_LOGO, width=64)
    else:
        st.markdown("### 💰")
 
    st.markdown("### Controle Financeiro")
 
    pagina = st.radio(
        "Navegação",
        options=["📊 Resumo", "🎯 Metas", "➕ Nova transação", "📋 Transações", "ℹ️ Sobre"],
        label_visibility="collapsed",
    )
 
    st.divider()
    st.caption(f"{NOME_AUTOR}\n\n[GitHub]({LINK_GITHUB})")
 
df = carregar_dados()
 
# ---------------------------------------------------------
# Cabeçalho
# ---------------------------------------------------------
col_logo, col_titulo = st.columns([1, 10])
with col_logo:
    if CAMINHO_LOGO and os.path.exists(CAMINHO_LOGO):
        st.image(CAMINHO_LOGO, width=56)
    else:
        st.markdown("<span style='font-size:2.5rem'>💰</span>", unsafe_allow_html=True)
with col_titulo:
    st.title("Controle Financeiro Pessoal")
st.caption("Acompanhe suas entradas, saídas e para onde seu dinheiro está indo.")
st.write("")
 
# ---------------------------------------------------------
# PÁGINA — RESUMO
# ---------------------------------------------------------
if pagina == "📊 Resumo":
    if df.empty:
        st.info("Nenhuma transação cadastrada ainda. Use a página 'Nova transação' para começar.")
    else:
        # --- Filtros dentro de um menu que abre/fecha ---
        with st.expander("🔍 Filtros", expanded=False):
            col_filtro1, col_filtro2 = st.columns(2)
            meses_disponiveis = sorted(df["mes"].unique(), reverse=True)
            meses_selecionados = col_filtro1.multiselect(
                "Mês", options=meses_disponiveis, default=meses_disponiveis
            )
            categorias_disponiveis = sorted(df["categoria"].unique())
            categorias_selecionadas = col_filtro2.multiselect(
                "Categoria", options=categorias_disponiveis, default=categorias_disponiveis
            )
 
        df_filtrado = df[
            df["mes"].isin(meses_selecionados) & df["categoria"].isin(categorias_selecionadas)
        ]
 
        st.write("")
 
        entradas = df_filtrado[df_filtrado["tipo"] == "entrada"]["valor"].sum()
        saidas = df_filtrado[df_filtrado["tipo"] == "saida"]["valor"].sum()
        saldo = entradas - saidas
 
        col1, col2, col3 = st.columns(3)
        with col1:
            cartao_metrica("Total de entradas", formatar_reais(entradas), "positivo")
        with col2:
            cartao_metrica("Total de saídas", formatar_reais(saidas), "negativo")
        with col3:
            cartao_metrica(
                "Saldo", formatar_reais(saldo), "positivo" if saldo >= 0 else "negativo"
            )
 
        st.write("")
 
        gastos_saida = df_filtrado[df_filtrado["tipo"] == "saida"]
        col4, col5, col6 = st.columns(3)
 
        with col4:
            if not gastos_saida.empty:
                media_categoria = gastos_saida.groupby("categoria")["valor"].sum().mean()
                cartao_metrica("Média de gasto por categoria", formatar_reais(media_categoria))
            else:
                cartao_metrica("Média de gasto por categoria", "R$ 0,00")
 
        with col5:
            if not gastos_saida.empty:
                maior = gastos_saida.loc[gastos_saida["valor"].idxmax()]
                cartao_metrica(
                    "Maior gasto", formatar_reais(maior["valor"]),
                    subtitulo=f"{maior['descricao']} ({maior['categoria']})",
                )
            else:
                cartao_metrica("Maior gasto", "R$ 0,00")
 
        with col6:
            saidas_por_mes_total = (
                df[df["tipo"] == "saida"].groupby("mes")["valor"].sum().sort_index()
            )
            if len(saidas_por_mes_total) >= 2:
                atual = saidas_por_mes_total.iloc[-1]
                anterior = saidas_por_mes_total.iloc[-2]
                variacao = ((atual - anterior) / anterior * 100) if anterior else 0
                sinal = "+" if variacao >= 0 else ""
                cartao_metrica(
                    "Variação vs mês anterior",
                    f"{sinal}{variacao:.1f}%",
                    "negativo" if variacao > 0 else "positivo",
                    subtitulo=f"{saidas_por_mes_total.index[-2]} → {saidas_por_mes_total.index[-1]}",
                )
            else:
                cartao_metrica("Variação vs mês anterior", "—", subtitulo="Poucos meses para comparar")
 
        st.write("")
        col_esquerda, col_direita = st.columns(2)
 
        with col_esquerda:
            st.markdown('<div class="chart-card"><h4>Gastos por categoria</h4>', unsafe_allow_html=True)
            gastos_categoria = (
                gastos_saida.groupby("categoria")["valor"]
                .sum()
                .reset_index()
                .sort_values("valor", ascending=False)
            )
            if not gastos_categoria.empty:
                gastos_categoria["categoria_icone"] = gastos_categoria["categoria"].apply(
                    lambda c: f"{ICONES_CATEGORIA.get(c, '💰')} {c}"
                )
                fig_pizza = px.pie(
                    gastos_categoria,
                    values="valor",
                    names="categoria_icone",
                    hole=0.55,
                    color_discrete_sequence=px.colors.sequential.Purples_r,
                )
                fig_pizza.update_traces(
                    textposition="inside",
                    textinfo="percent+label",
                    hovertemplate="%{label}<br>R$ %{value:,.2f}<extra></extra>",
                )
                fig_pizza.update_layout(
                    showlegend=False,
                    margin=dict(t=10, b=10, l=10, r=10),
                    height=340,
                    paper_bgcolor="rgba(0,0,0,0)",
                    font_color="#1F2937",
                )
                st.plotly_chart(fig_pizza, width="stretch", config={"displayModeBar": False})
            else:
                st.info("Sem gastos no filtro selecionado.")
            st.markdown('</div>', unsafe_allow_html=True)
 
        with col_direita:
            st.markdown('<div class="chart-card"><h4>Evolução dos gastos por mês</h4>', unsafe_allow_html=True)
            gastos_mes = (
                gastos_saida.groupby("mes")["valor"]
                .sum()
                .reset_index()
                .sort_values("mes")
            )
            if not gastos_mes.empty:
                fig_mes_barras = px.bar(
                    gastos_mes, x="mes", y="valor",
                    text="valor",
                    color_discrete_sequence=["#7C3AED"],
                )
                fig_mes_barras.update_traces(
                    texttemplate="R$ %{text:,.2f}",
                    textposition="outside",
                    hovertemplate="%{x}<br>R$ %{y:,.2f}<extra></extra>",
                )
                fig_mes_barras.update_layout(
                    xaxis_title=None, yaxis_title=None,
                    margin=dict(t=10, b=10, l=10, r=10),
                    height=340,
                    plot_bgcolor="rgba(0,0,0,0)",
                    paper_bgcolor="rgba(0,0,0,0)",
                    font_color="#1F2937",
                )
                fig_mes_barras.update_yaxes(gridcolor="#F1F3F4")
                st.plotly_chart(fig_mes_barras, width="stretch", config={"displayModeBar": False})
            else:
                st.info("Sem gastos no filtro selecionado.")
            st.markdown('</div>', unsafe_allow_html=True)
# ---------------------------------------------------------
# PÁGINA — NOVA TRANSAÇÃO
# ---------------------------------------------------------
elif pagina == "➕ Nova transação":
    st.subheader("Adicionar nova transação")
 
    with st.form("form_nova_transacao", clear_on_submit=True):
        col_a, col_b = st.columns(2)
        data_transacao = col_a.date_input("Data", value=date.today())
        tipo = col_b.selectbox(
            "Tipo", options=["saida", "entrada"],
            format_func=lambda t: "Saída" if t == "saida" else "Entrada",
        )
 
        descricao = st.text_input("Descrição (ex: Mercado, Salário)")
        categoria = st.selectbox(
            "Categoria", options=CATEGORIAS_PADRAO,
            format_func=lambda c: f"{ICONES_CATEGORIA.get(c, '💰')} {c}",
        )
        valor = st.number_input("Valor (R$)", min_value=0.0, step=10.0, format="%.2f")
 
        enviado = st.form_submit_button("Adicionar transação", width="stretch")
 
        if enviado:
            if not descricao.strip():
                st.error("Preencha a descrição antes de salvar.")
            elif valor <= 0:
                st.error("O valor precisa ser maior que zero.")
            else:
                inserir_transacao(data_transacao, descricao.strip(), categoria, valor, tipo)
                st.success(f"Transação '{descricao}' adicionada com sucesso!")
                st.rerun()
 
# ---------------------------------------------------------
# PÁGINA — TRANSAÇÕES (tabela + exportar + editar/excluir)
# ---------------------------------------------------------
elif pagina == "📋 Transações":
    st.subheader("Todas as transações")
    if df.empty:
        st.info("Nenhuma transação cadastrada ainda.")
    else:
        df_exibicao = df.sort_values("data", ascending=False)[
            ["data", "descricao", "categoria", "valor", "tipo"]
        ].copy()
        df_exibicao["data"] = df_exibicao["data"].dt.strftime("%d/%m/%Y")
        df_exibicao["valor_fmt"] = df_exibicao["valor"].apply(formatar_reais)
        df_exibicao["tipo_fmt"] = df_exibicao["tipo"].map({"entrada": "Entrada", "saida": "Saída"})
 
        st.dataframe(
            df_exibicao[["data", "descricao", "categoria", "valor_fmt", "tipo_fmt"]].rename(
                columns={"data": "Data", "descricao": "Descrição", "categoria": "Categoria",
                         "valor_fmt": "Valor", "tipo_fmt": "Tipo"}
            ),
            width="stretch", hide_index=True,
        )
 
        col_csv, col_xlsx = st.columns(2)
        csv_bytes = df.drop(columns=["mes"]).to_csv(index=False).encode("utf-8-sig")
        col_csv.download_button(
            "📥 Baixar CSV", data=csv_bytes,
            file_name="transacoes.csv", mime="text/csv",
            width="stretch",
        )
 
        buffer_excel = io.BytesIO()
        with pd.ExcelWriter(buffer_excel, engine="openpyxl") as writer:
            df.drop(columns=["mes"]).to_excel(writer, index=False, sheet_name="Transações")
        col_xlsx.download_button(
            "📥 Baixar Excel", data=buffer_excel.getvalue(),
            file_name="transacoes.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            width="stretch",
        )
 
        st.divider()
 
        st.subheader("Editar ou excluir uma transação")
        df_ordenado = df.sort_values("data", ascending=False).reset_index(drop=True)
        opcoes = {
            f"{row['data'].strftime('%d/%m/%Y')} — {row['descricao']} — {formatar_reais(row['valor'])}": row["id"]
            for _, row in df_ordenado.iterrows()
        }
        escolha = st.selectbox("Selecione a transação", options=list(opcoes.keys()))
 
        if escolha:
            id_selecionado = opcoes[escolha]
            linha_atual = df[df["id"] == id_selecionado].iloc[0]
 
            with st.form("form_editar_transacao"):
                col_a, col_b = st.columns(2)
                nova_data = col_a.date_input("Data", value=linha_atual["data"].date())
                novo_tipo = col_b.selectbox(
                    "Tipo", options=["saida", "entrada"],
                    index=0 if linha_atual["tipo"] == "saida" else 1,
                    format_func=lambda t: "Saída" if t == "saida" else "Entrada",
                )
                nova_descricao = st.text_input("Descrição", value=linha_atual["descricao"])
                indice_categoria = (
                    CATEGORIAS_PADRAO.index(linha_atual["categoria"])
                    if linha_atual["categoria"] in CATEGORIAS_PADRAO else 0
                )
                nova_categoria = st.selectbox(
                    "Categoria", options=CATEGORIAS_PADRAO, index=indice_categoria,
                    format_func=lambda c: f"{ICONES_CATEGORIA.get(c, '💰')} {c}",
                )
                novo_valor = st.number_input(
                    "Valor (R$)", min_value=0.0, step=10.0, format="%.2f",
                    value=float(linha_atual["valor"]),
                )
 
                col_salvar, col_excluir = st.columns(2)
                salvar_edicao = col_salvar.form_submit_button("💾 Salvar alterações", width="stretch")
                excluir = col_excluir.form_submit_button("🗑️ Excluir transação", width="stretch")
 
                if salvar_edicao:
                    atualizar_transacao(
                        id_selecionado, nova_data, nova_descricao.strip(), nova_categoria, novo_valor, novo_tipo
                    )
                    st.success("Transação atualizada com sucesso!")
                    st.rerun()
 
                if excluir:
                    excluir_transacao(id_selecionado)
                    st.success("Transação excluída com sucesso!")
                    st.rerun()
 
# ---------------------------------------------------------
# PÁGINA — SOBRE
# ---------------------------------------------------------
elif pagina == "ℹ️ Sobre":
    st.subheader("Sobre este projeto")
    texto_sobre = (
        "Este é um dashboard de **controle financeiro pessoal**, feito como "
        "projeto de portfólio para praticar Python, SQL e visualização de dados.\n\n"
        "**Funcionalidades:**\n"
        "- Cadastro de transações (entradas e saídas) direto pelo navegador\n"
        "- Relatórios e indicadores calculados com consultas SQL (SQLite)\n"
        "- Gráficos interativos de gastos por categoria e por mês (Plotly)\n"
        "- Metas de gastos por categoria com acompanhamento de progresso\n"
        "- Exportação dos dados em CSV e Excel\n"
        "- Edição e exclusão de transações já cadastradas\n\n"
        "**Tecnologias usadas:**\n"
        "- Python\n"
        "- SQLite (banco de dados)\n"
        "- Streamlit (interface web)\n"
        "- Pandas (manipulação de dados)\n"
        "- Plotly (gráficos interativos)\n\n"
        "---\n\n"
        f"Desenvolvido por **{NOME_AUTOR}** · [GitHub]({LINK_GITHUB})"
    )
    st.markdown(texto_sobre)
 