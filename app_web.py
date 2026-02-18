import streamlit as st
import pandas as pd
from sqlalchemy import create_engine, text
from datetime import datetime
import os

# --- CONEXÃO COM O SQL (SUPABASE) ---
# Use a sua URI real aqui
DB_URI = "postgresql://postgres:$8&9eiGcXmxBT?T@db.fefyazgiwvttygzfgclk.supabase.co:5432/postgres"
engine = create_engine(DB_URI)

# --- FUNÇÕES DE BANCO DE DADOS ---

def salvar_no_sql(usuario, data_simples, data_extenso, faturamento, despesas, lucro, horas):
    dados = {
        'usuario': [usuario],
        'data': [data_simples],
        'data_extenso': [data_extenso],
        'valor_ganho': [faturamento],
        'combustivel': [despesas], # Aqui podes separar se quiseres, usei despesas como combustível
        'lucro': [lucro],
        'horas': [horas]
    }
    df = pd.DataFrame(dados)
    # Salva na tabela que criamos
    df.to_sql('historico_ganhos', engine, if_exists='append', index=False)

def ler_historico_sql(usuario):
    query = f"SELECT * FROM historico_ganhos WHERE usuario = '{usuario}' ORDER BY data ASC"
    return pd.read_sql(query, engine)

def apagar_registro_sql(id_registro):
    with engine.connect() as conn:
        conn.execute(text(f"DELETE FROM historico_ganhos WHERE id = {id_registro}"))
        conn.commit()

# --- 1. CONFIGURAÇÃO E ESTILO ---
st.set_page_config(page_title="Motorista Pro Dashboard", page_icon="🏎️", layout="wide")

# (Mantém o teu dicionário USUARIOS e a função login() igual...)
# ... [CÓDIGO DE LOGIN IGUAL AO TEU] ...

# --- SISTEMA MULTI-UTILIZADOR ---
USUARIOS = {
    "teste": "teste",
    "gustavo": "123456",
    "joao": "motorista77"
}

def login():
    if "autenticado" not in st.session_state:
        st.session_state.autenticado = False
        st.session_state.usuario_atual = None

    if not st.session_state.autenticado:
        st.markdown("<h1 style='text-align: center;'>🔐 Login Driver Pro</h1>", unsafe_allow_html=True)
        col1, col2, col3 = st.columns([1, 1.5, 1])
        with col2:
            with st.form("form_login"):
                user_input = st.text_input("Utilizador").lower().strip()
                senha_input = st.text_input("Senha", type="password")
                botao_entrar = st.form_submit_button("Entrar", use_container_width=True)
                if botao_entrar:
                    if user_input in USUARIOS and USUARIOS[user_input] == senha_input:
                        st.session_state.autenticado = True
                        st.session_state.usuario_atual = user_input
                        st.rerun()
                    else:
                        st.error("Utilizador ou senha incorretos")
        return False
    return True

if not login():
    st.stop()

usuario_logado = st.session_state.usuario_atual

# (Mantém o teu CSS de Estilo igual...)
# ... [TEU CSS AQUI] ...

def data_por_extenso_limpa(dt):
    meses = {1: "janeiro", 2: "fevereiro", 3: "março", 4: "abril", 5: "maio", 6: "junho", 
             7: "julho", 8: "agosto", 9: "setembro", 10: "outubro", 11: "novembro", 12: "dezembro"}
    dias_semana = {0: "Segunda-feira", 1: "Terça-feira", 2: "Quarta-feira", 3: "Quinta-feira", 
                    4: "Sexta-feira", 5: "Sábado", 6: "Domingo"}
    return f"{dias_semana[dt.weekday()]}, {dt.day} de {meses[dt.month]} de {dt.year}"

# --- BARRA LATERAL ---
with st.sidebar:
    st.image("https://cdn-icons-png.flaticon.com/512/235/235861.png", width=100)
    st.markdown(f"### Olá, {usuario_logado.capitalize()}!")
    
    st.markdown("<h2 style='color: white;'>📝 Novo Registro</h2>", unsafe_allow_html=True)
    data_sel = st.date_input("Data da Atividade", datetime.now(), format="DD/MM/YYYY")
    faturamento = st.number_input("Ganhos Brutos (R$)", min_value=0.0)
    combustivel = st.number_input("Combustível (R$)", min_value=0.0)
    manutencao = st.number_input("Manutenção/Outros (R$)", min_value=0.0)
    horas = st.number_input("Horas Online", min_value=0.1)
    
    if st.button("🚀 Salvar Lançamento", use_container_width=True):
        despesas = combustivel + manutencao
        lucro = faturamento - despesas
        
        # SALVANDO NO SQL 
        salvar_no_sql(usuario_logado, data_sel, data_por_extenso_limpa(data_sel), faturamento, despesas, lucro, horas)
        
        st.balloons()
        st.rerun()

    st.markdown("---")
    st.markdown("<h3 style='color: white;'>🗑️ Gerenciar Histórico</h3>", unsafe_allow_html=True)
    
    df_hist = ler_historico_sql(usuario_logado)
    if not df_hist.empty:
        # Criar uma lista para o selectbox com o ID para podermos apagar
        opcoes_apagar = {f"{row['data_extenso']} (ID: {row['id']})": row['id'] for _, row in df_hist.iterrows()}
        selecionado = st.selectbox("Apagar registro:", list(opcoes_apagar.keys()))
        
        if st.button("Confirmar Exclusão", type="secondary", use_container_width=True):
            apagar_registro_sql(opcoes_apagar[selecionado])
            st.warning("Registro removido!")
            st.rerun()

# --- ÁREA PRINCIPAL ---
st.title(f"🏎️ Painel de {usuario_logado.capitalize()}")

# Verificamos se o DataFrame que veio do SQL não está vazio
if not df_hist.empty:
    # 1. CÁLCULO DE METAS
    # Usamos nomes em minúsculas pois o SQL/Pandas costuma retornar assim
    total_acumulado = float(df_hist["lucro"].sum())
    progresso = min(total_acumulado / meta_valor, 1.0)
    
    st.markdown(f"""
        <div class="meta-texto">
            Progresso: <span style='color: #10b981;'>R$ {total_acumulado:.2f}</span> 
            de <span style='color: #3b82f6;'>R$ {meta_valor:.2f}</span>
        </div>
    """, unsafe_allow_html=True)
    st.progress(progresso)
    
    # 2. CARD DE ÚLTIMO FECHAMENTO
    ultimo = df_hist.iloc[-1]
    lucro_val = float(ultimo['lucro'])
    cor_lucro = "#10b981" if lucro_val > 0 else "#ef4444"

    st.markdown(f"""
        <div class="main-card">
            <p style="color: #9ca3af; margin-bottom: 5px;">Último Fechamento: {ultimo['data_extenso']}</p>
            <h2 style="margin: 0; color: white;">Lucro Líquido do Dia</h2>
            <h1 style="color: {cor_lucro}; font-size: 3.5em; margin: 0;">R$ {lucro_val:.2f}</h1>
        </div>
    """, unsafe_allow_html=True)

    # 3. MÉTRICAS EM COLUNAS
    m1, m2, m3, m4 = st.columns(4)
    with m1:
        with st.container(border=True):
            st.metric("💰 Ganhos Brutos", f"R$ {ultimo['valor_ganho']:.2f}")
    with m2:
        with st.container(border=True):
            # No nosso SQL, 'combustivel' guarda o total de despesas que enviamos
            st.metric("⛽ Total Gastos", f"R$ {ultimo['combustivel']:.2f}", 
                      delta=f"-R$ {ultimo['combustivel']:.2f}", delta_color="inverse")
    with m3:
        with st.container(border=True):
            lucro_hora = ultimo['lucro']/ultimo['horas'] if ultimo['horas'] > 0 else 0
            st.metric("⏱️ Lucro/Hora", f"R$ {lucro_hora:.2f}")
    with m4:
        with st.container(border=True):
            eficiencia = (ultimo['lucro']/ultimo['valor_ganho'])*100 if ultimo['valor_ganho'] > 0 else 0
            st.metric("📈 Margem", f"{eficiencia:.0f}%")

    # 4. GRÁFICOS
    st.markdown("### 📊 Evolução do Desempenho")
    tab1, tab2 = st.tabs(["Lucro Líquido", "Ganhos Brutos"])
    
    # Preparamos o DF para o gráfico (ordenado por data)
    df_grafico = df_hist.copy()
    df_grafico = df_grafico.set_index("data_extenso")
    
    with tab1:
        st.area_chart(df_grafico["lucro"], color="#10b981")
    with tab2:
        st.area_chart(df_grafico["valor_ganho"], color="#3b82f6")

    # 5. TABELA DE HISTÓRICO
    st.subheader("📁 Histórico de Atividades (SQL)")
    st.dataframe(
        df_hist[["data_extenso", "valor_ganho", "combustivel", "lucro", "horas"]].iloc[::-1],
        use_container_width=True, hide_index=True,
        column_config={
            "data_extenso": "Data",
            "valor_ganho": st.column_config.NumberColumn("Ganhos", format="R$ %.2f"),
            "combustivel": st.column_config.NumberColumn("Gastos", format="R$ %.2f"),
            "lucro": st.column_config.NumberColumn("Lucro", format="R$ %.2f"),
            "horas": st.column_config.NumberColumn("Tempo", format="%.1f horas")
        }
    )
else:
    st.info("Bem-vindo! Comece adicionando o seu primeiro registro na barra lateral. Os dados serão salvos no Supabase.")