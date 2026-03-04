import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots

# Configuração de Interface Institucional
st.set_page_config(page_title="Alpha Macro Terminal", layout="wide")

# Estética Customizada (Métricas em caixas pretas como na imagem)
st.markdown("""
    <style>
    .main { background-color: #0F0F0F; }
    div[data-testid="stMetric"] { 
        background-color: #161616; 
        padding: 20px; 
        border-radius: 5px; 
        border: 1px solid #333; 
    }
    </style>
    """, unsafe_allow_html=True)

@st.cache_data(ttl=3600)
def fetch_alpha_data():
    # Download dos dados máximos
    df = yf.download("BTC-USD", period="max", interval="1d", progress=False)
    if isinstance(df.columns, pd.MultiIndex):
        df = df['Close']
    else:
        df = df[['Close']]
    df.columns = ['close']
    
    # Matemática de Ciclo (Hedge Fund Standard)
    df['log_price'] = np.log(df['close'])
    window = 350
    df['mean'] = df['log_price'].rolling(window=window).mean()
    df['std'] = df['log_price'].rolling(window=window).std()
    
    # Lógica Invertida: Preço < Média = Positivo (Aqua) | Preço > Média = Negativo (Blue)
    df['z_score'] = (df['mean'] - df['log_price']) / df['std']
    return df.dropna()

try:
    data = fetch_alpha_data()
    last_z = data['z_score'].iloc[-1]
    
    # --- HEADER DE MÉTRICAS (Estilo image_bbc95f.png) ---
    c1, c2, c3 = st.columns([1, 1, 1.2])
    with c1: st.metric("BITCOIN PRICE", f"${data['close'].iloc[-1]:,.2f}")
    with c2: st.metric("Z-SCORE LEVEL", f"{last_z:.2f}")
    
    with c3:
        status = "NEUTRAL"
        s_color = "white"
        if last_z >= 2.0: 
            status = "💎 BUY (BOTTOM)"
            s_color = "#00FBFF"
        elif last_z <= -2.0: 
            status = "🔴 SELL (TOP)"
            s_color = "#3D5AFE"
        st.markdown(f"<h1 style='text-align: right; color: {s_color}; margin-top: 10px; font-family: sans-serif;'>{status}</h1>", unsafe_allow_html=True)

    # --- CONSTRUÇÃO DO PLOT (REPLICA EXATA image_bc5b88.png) ---
    fig = make_subplots(
        rows=2, cols=1, 
        shared_xaxes=True, 
        vertical_spacing=0.08,
        row_heights=[0.5, 0.5]
    )

    # 1. PAINEL SUPERIOR: BTC PRICE (LOG CHART)
    fig.add_trace(
        go.Scatter(
            x=data.index, 
            y=data['close'], 
            name="Price", 
            line=dict(color='white', width=1.8)
        ),
        row=1, col=1
    )

    # 2. PAINEL INFERIOR: INDICADOR ALPHA
    fig.add_trace(
        go.Scatter(
            x=data.index, 
            y=data['z_score'], 
            name="Z-Score", 
            line=dict(color='#888', width=1.3)
        ),
        row=2, col=1
    )

    # LINHAS TRACEJADAS PROFISSIONAIS (Trigger em 2 e -2 SD)
    # Top Side (Blue Zone / Overbought)
    fig.add_hline(y=-2.0, line=dict(color="#3D5AFE", width=1.5, dash="dash"), row=2, col=1)
    # Down Side (Aqua Zone / Oversold)
    fig.add_hline(y=2.0, line=dict(color="#00FBFF", width=1.5, dash="dash"), row=2, col=1)
    
    fig.add_hline(y=0, line=dict(color="rgba(255,255,255,0.2)", width=1), row=2, col=1)

    # PREENCHIMENTO DE COR (Exatamente como na imagem)
    # Blue Fill (Top / Negative SD)
    fig.add_trace(go.Scatter(x=data.index, y=[-2.0]*len(data), line=dict(width=0), showlegend=False), row=2, col=1)
    fig.add_trace(go.Scatter(
        x=data.index, 
        y=np.where(data['z_score'] <= -2.0, data['z_score'], -2.0),
        fill='tonexty',
        fillcolor='rgba(61, 90, 254, 0.7)',
        line=dict(width=0),
        showlegend=False
    ), row=2, col=1)

    # Aqua Fill (Bottom / Positive SD)
    fig.add_trace(go.Scatter(x=data.index, y=[2.0]*len(data), line=dict(width=0), showlegend=False), row=2, col=1)
    fig.add_trace(go.Scatter(
        x=data.index, 
        y=np.where(data['z_score'] >= 2.0, data['z_score'], 2.0),
        fill='tonexty',
        fillcolor='rgba(0, 251, 255, 0.7)',
        line=dict(width=0),
        showlegend=False
    ), row=2, col=1)

    # CONFIGURAÇÃO DE LAYOUT GLOBAL
    fig.update_layout(
        title=dict(text="ALPHA MACRO HISTORY", x=0.5, font=dict(color="#3D5AFE", size=20)),
        template="plotly_dark",
        paper_bgcolor="#0F0F0F",
        plot_bgcolor="#0F0F0F",
        height=900,
        margin=dict(l=50, r=50, t=80, b=50),
        showlegend=False,
        dragmode="pan"
    )

    # AJUSTES DE EIXO (Log Scale e Eixo Invertido)
    fig.update_yaxes(
        type="log", # LOG CHART ATIVADO
        row=1, col=1, 
        gridcolor="#222", 
        title="Price (Log)",
        showline=True, linecolor="#444",
        exponentformat="none",
        tickvals=[100, 1000, 10000, 100000]
    )
    
    fig.update_yaxes(
        row=2, col=1, 
        gridcolor="#222", 
        title="Cycle Stress (SD)", 
        autorange='reversed', # EIXO INVERTIDO (Negativos no topo, Positivos no fundo)
        range=[-4, 4],
        showline=True, linecolor="#444"
    )
    
    fig.update_xaxes(
        gridcolor="#222", 
        range=[data.index[-2000], data.index[-1] + pd.Timedelta(days=60)],
        showline=True, linecolor="#444"
    )

    st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False, 'scrollZoom': True})

except Exception as e:
    st.error(f"Erro no Terminal: {e}")

