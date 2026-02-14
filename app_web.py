import streamlit as st
import pandas as pd
from datetime import datetime
import os

# 1. CONFIGURAÇÃO E ESTILO
st.set_page_config(page_title="Motorista Pro Dashboard", page_icon="🏎️", layout="wide")



# CSS 
st.markdown("""
    <style>
    /* 1. Fundo da Barra Lateral */
    [data-testid="stSidebar"] { 
        background-color: #111827 !important; 
    }
    
    /* 2. NOMES DOS CAMPOS (Labels) - Forçar Branco Puro */
    [data-testid="stSidebar"] label p, 
    [data-testid="stSidebar"] .stMarkdown p,
    [data-testid="stSidebar"] h2, 
    [data-testid="stSidebar"] h3 {
        color: #FFFFFF !important;
        opacity: 1 !important;
        font-weight: 800 !important;
        font-size: 1.1rem !important;
        text-shadow: 1px 1px 2px rgba(0,0,0,0.8); /* Sombra para destacar no fundo escuro */
    }

    /* 3. NÚMEROS DENTRO DAS CAIXAS - Forçar Preto no fundo Branco */
    [data-testid="stSidebar"] input {
        color: #000000 !important; /* Cor do número */
        background-color: #FFFFFF !important; /* Cor do fundo da caixa */
        -webkit-text-fill-color: #000000 !important; /* Garante que o número apareça em alguns navegadores */
    }

    /* 4. Estilo do Card Principal */
    .main-card {
        background: linear-gradient(135deg, #1e293b 0%, #0f172a 100%);
        color: white; padding: 25px; border-radius: 15px;
        border-left: 10px solid #3b82f6;
        margin-bottom: 20px;
    }

    /* 5. Texto da Meta Colorido e Limpo */
    .meta-texto {
        font-size: 1.2rem;
        font-weight: bold;
        color: #1e293b;
        margin-bottom: 10px;
    }
    </style>
    """, unsafe_allow_html=True)

NOME_FICHEIRO = "historico_ganhos.csv"

def data_por_extenso_limpa(dt):
    meses = {1: "janeiro", 2: "fevereiro", 3: "março", 4: "abril", 5: "maio", 6: "junho", 
             7: "julho", 8: "agosto", 9: "setembro", 10: "outubro", 11: "novembro", 12: "dezembro"}
    dias_semana = {0: "Segunda-feira", 1: "Terça-feira", 2: "Quarta-feira", 3: "Quinta-feira", 
                   4: "Sexta-feira", 5: "Sábado", 6: "Domingo"}
    return f"{dias_semana[dt.weekday()]}, {dt.day} de {meses[dt.month]} de {dt.year}"

# --- BARRA LATERAL ---
with st.sidebar:
    st.image("https://cdn-icons-png.flaticon.com/512/235/235861.png", width=100)
    st.markdown("## 📝 Novo Registro")
    
    data_sel = st.date_input("Data da Atividade", datetime.now(), format="DD/MM/YYYY")
    faturamento = st.number_input("Ganhos Brutos (R$)", min_value=0.0)
    combustivel = st.number_input("Combustível (R$)", min_value=0.0)
    manutencao = st.number_input("Manutenção/Outros (R$)", min_value=0.0)
    horas = st.number_input("Horas Online", min_value=0.1)
    
    if st.button("🚀 Salvar Lançamento", use_container_width=True):
        despesas = combustivel + manutencao
        lucro = faturamento - despesas
        novo_registo = {
            "Data_Simples": data_sel.strftime("%Y-%m-%d"),
            "Data_Extenso": data_por_extenso_limpa(data_sel),
            "Faturamento": faturamento, "Despesas": despesas,
            "Lucro": lucro, "Horas": horas
        }
        df = pd.DataFrame([novo_registo])
        df.to_csv(NOME_FICHEIRO, mode='a', index=False, header=not os.path.isfile(NOME_FICHEIRO))
        st.balloons()
        st.rerun()

    st.markdown("---")
    st.markdown("### 🎯 Meta do Mês")
    meta_valor = st.number_input("Definir Meta (R$)", min_value=1.0, value=3000.0)

# --- ÁREA PRINCIPAL ---
st.title("🏎️ Motorista de Aplicativo Pro")

if os.path.isfile(NOME_FICHEIRO):
    df_hist = pd.read_csv(NOME_FICHEIRO)
    if not df_hist.empty:
        # CÁLCULO DA META 
        total_acumulado = df_hist["Lucro"].sum()
        progresso = min(total_acumulado / meta_valor, 1.0)
        
        
        # EXIBIÇÃO DA META NA ÁREA PRINCIPAL
        st.markdown(f"""
            <div class="meta-texto">
                Progresso: <span style='color: #10b981;'>R$ {total_acumulado:.2f}</span> 
                de <span style='color: #3b82f6;'>R$ {meta_valor:.2f}</span>
            </div>
        """, unsafe_allow_html=True)
        st.progress(progresso)
        
     
        
        ultimo = df_hist.iloc[-1]
        lucro_val = float(ultimo['Lucro'])
        cor_lucro = "#10b981" if lucro_val > 0 else "#ef4444"

        # CARD DE DESTAQUE
        st.markdown(f"""
            <div class="main-card">
                <p style="color: #9ca3af; margin-bottom: 5px;">Último Fechamento: {ultimo['Data_Extenso']}</p>
                <h2 style="margin: 0; color: white;">Lucro Líquido do Dia</h2>
                <h1 style="color: {cor_lucro}; font-size: 3.5em; margin: 0;">R$ {lucro_val:.2f}</h1>
            </div>
        """, unsafe_allow_html=True)

        # MÉTRICAS COM MOLDURA
        m1, m2, m3, m4 = st.columns(4)
        with m1:
            with st.container(border=True):
                st.metric("💰 Ganhos Brutos", f"R$ {ultimo['Faturamento']:.2f}")
        with m2:
            with st.container(border=True):
                st.metric("⛽ Total Gastos", f"R$ {ultimo['Despesas']:.2f}", delta=f"-R$ {ultimo['Despesas']:.2f}", delta_color="inverse")
        with m3:
            with st.container(border=True):
                st.metric("⏱️ Lucro/Hora", f"R$ {ultimo['Lucro']/ultimo['Horas']:.2f}")
        with m4:
            with st.container(border=True):
                eficiencia = (ultimo['Lucro']/ultimo['Faturamento'])*100 if ultimo['Faturamento'] > 0 else 0
                st.metric("📈 Margem", f"{eficiencia:.0f}%")

        # GRÁFICOS EM ABAS
        st.markdown("### 📊 Evolução do Desempenho")
        tab1, tab2 = st.tabs(["Lucro Líquido", "Ganhos Brutos"])
        with tab1:
            st.area_chart(df_hist.set_index("Data_Extenso")["Lucro"], color="#10b981")
        with tab2:
            st.area_chart(df_hist.set_index("Data_Extenso")["Faturamento"], color="#3b82f6")

# --- TABELA HISTÓRICO ---
st.subheader("📁 Histórico de Atividades")
if os.path.isfile(NOME_FICHEIRO):
    st.dataframe(
        df_hist[["Data_Extenso", "Faturamento", "Despesas", "Lucro", "Horas"]].iloc[::-1],
        use_container_width=True, hide_index=True,
        column_config={
            "Data_Extenso": "Data",
            "Faturamento": st.column_config.NumberColumn("Ganhos", format="R$ %.2f"),
            "Despesas": st.column_config.NumberColumn("Gastos", format="R$ %.2f"),
            "Lucro": st.column_config.NumberColumn("Lucro", format="R$ %.2f"),
            "Horas": st.column_config.NumberColumn("Tempo", format="%.1f horas")
        }
    )