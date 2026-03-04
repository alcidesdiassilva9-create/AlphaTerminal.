import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
import plotly.graph_objects as go

# Configuração de Identidade Visual
st.set_page_config(page_title="Alpha Macro Terminal", layout="wide")

# Estilo CSS para remover margens desnecessárias e melhorar o fundo
st.markdown("""
    <style>
    .main { background-color: #0F0F0F; }
    .stMetric { background-color: #1A1A1A; padding: 15px; border-radius: 10px; border: 1px solid #333; }
    </style>
    """, unsafe_allow_html=True)

st.markdown("<h1 style='text-align: center; color: #00FBFF; font-family: sans-serif;'>✦ 𝓐𝓵𝓹𝓱𝓪 𝓜𝓪𝓬𝓻𝓸: 𝓒𝔂𝓬𝓵𝓮 𝓜𝓪𝓼𝓽𝓮𝓻 ✦</h1>", unsafe_allow_html=True)

@st.cache_data(ttl=3600) # Atualiza a cada hora para bater com o Python
def get_data():
    df = yf.download("BTC-USD", period="max", interval="1d", progress=False)
    if isinstance(df.columns, pd.MultiIndex):
        df = df['Close']
    else:
        df = df[['Close']]
    df.columns = ['close']
    
    # Cálculo de Ciclo (Log Z-Score 350 dias) - Precisão Matemática
    df['log_price'] = np.log(df['close'])
    window = 350
    df['mean'] = df['log_price'].rolling(window=window).mean()
    df['std'] = df['log_price'].rolling(window=window).std()
    df['z_score'] = (df['log_price'] - df['mean']) / df['std']
    return df.dropna()

try:
    data = get_data()
    current_z = data['z_score'].iloc[-1]
    current_p = data['close'].iloc[-1]

    # --- MÉTRICAS DE TOPO ---
    c1, c2, c3 = st.columns(3)
    with c1: st.metric("PREÇO ATUAL", f"${current_p:,.2f}")
    with c2: st.metric("Z-SCORE", f"{current_z:.2f}")
    with c3:
        status = "NEUTRO"
        color = "#FFFFFF"
        if current_z <= -1.5:
            status = "💎 BUY ZONE"
            color = "#00FBFF" # Aqua/AlphaBlue
        elif current_z >= 1.8:
            status = "🔴 SELL ZONE"
            color = "#3D5AFE" # Blue/AlphaRed
        st.markdown(f"<h3 style='text-align:center; color:{color}; margin-top:10px;'>{status}</h3>", unsafe_allow_html=True)

    # --- GRÁFICO ESTILO PYTHON/MATPLOTLIB ---
    fig = go.Figure()

    # Zonas de Stress (Fundo colorido sólido como no Matplotlib)
    fig.add_hrect(y0=-3, y1=-1.5, fillcolor="#00FBFF", opacity=0.15, line_width=0)
    fig.add_hrect(y0=1.8, y1=5, fillcolor="#3D5AFE", opacity=0.15, line_width=0)

    # Linhas de Fronteira (Estilo PineScript)
    fig.add_hline(y=1.8, line=dict(color="#3D5AFE", width=1, dash="dash"))
    fig.add_hline(y=-1.5, line=dict(color="#00FBFF", width=1, dash="dash"))
    fig.add_hline(y=0, line=dict(color="gray", width=0.5))

    # Linha Principal do Z-Score (Mais grossa para parecer o Matplotlib)
    fig.add_trace(go.Scatter(
        x=data.index, 
        y=data['z_score'], 
        name="Z-Score", 
        line=dict(color='white', width=2.5) # Linha sólida e forte
    ))

    # Ajuste de Layout "Clean & Professional"
    fig.update_layout(
        template="plotly_dark",
        height=700,
        margin=dict(l=20, r=20, t=20, b=20),
        paper_bgcolor="#0F0F0F",
        plot_bgcolor="#0F0F0F",
        yaxis=dict(
            gridcolor="#222", 
            zeroline=False, 
            title="Stress Level (Z-Score)",
            tickfont=dict(color="gray")
        ),
        xaxis=dict(
            gridcolor="#222", 
            title="",
            tickfont=dict(color="gray"),
            range=[data.index[-1000], data.index[-1] + pd.Timedelta(days=60)] # Foco nos últimos 3 anos + margem à direita
        ),
        showlegend=False,
        dragmode="pan"
    )

    # Configuração de Interatividade
    st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False, 'scrollZoom': True})

except Exception as e:
    st.error(f"Erro na renderização: {e}")
    
