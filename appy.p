import streamlit as st

# Configuração Central (Aba do Navegador)
st.set_page_config(page_title="Alpha Macro Terminal", layout="wide")

# Estética Hedge Fund - Sidebar Branca Consistente
st.markdown("""
<style>
    .main { background-color: #0F0F0F; }
    /* Força a cor branca em todos os itens da barra lateral */
    [data-testid="stSidebarNav"] span { 
        color: #FFFFFF !important; 
        font-weight: 500; 
        font-size: 16px;
    }
    section[data-testid="stSidebar"] {
        background-color: #111111;
    }
</style>
""", unsafe_allow_html=True)

st.markdown("<h1 style='text-align: center; color: #3D5AFE; font-family: serif; font-size: 50px;'>✦ 𝓐𝓵𝓹𝓱𝓪 𝓜𝓪𝓬𝓻𝓸 𝓣𝓮𝓻𝓶𝓲𝓷𝓪𝓵 ✦</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center; color: #888; font-size: 20px;'>Institutional Intelligence & Cycle Analytics</p>", unsafe_allow_html=True)

st.divider()

c1, c2 = st.columns(2)
with c1:
    st.info("### 🟢 System I: ACD\nMacro Cycle Deviation based on Price Volatility.")
with c2:
    st.info("### 🔵 System II: NUPL\nNetwork Sentiment & Unrealized Profit/Loss Engine.")

st.markdown("---")
st.write("Selecione um sistema na barra lateral para iniciar o streaming de dados em tempo real.")




