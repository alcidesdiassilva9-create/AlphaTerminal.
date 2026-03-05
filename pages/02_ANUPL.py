import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots

# Configuração Institucional ANUPL Evolution
st.set_page_config(page_title="02 ANUPL Terminal", layout="wide")

# Estilização do Terminal
st.markdown("<style>.main { background-color: #0F0F0F; } div[data-testid='stMetric'] { background-color: #161616; padding: 20px; border-radius: 5px; border: 1px solid #333; }</style>", unsafe_allow_html=True)

@st.cache_data(ttl=3600)
def fetch_anupl_evolution():
    try:
        df = yf.download("BTC-USD", period="max", interval="1d", progress=False)
        if df.empty: return pd.DataFrame()
        df = df[['Close']] if not isinstance(df.columns, pd.MultiIndex) else df['Close']
        df.columns = ['close']
        
        # MATEMÁTICA ANUPL (Proxy Realized Price via SMA 365)
        df['realized_proxy'] = df['close'].rolling(window=365).mean()
        # Lógica: Realized > Market = Valor Positivo (Capitulação/Aqua)
        df['anupl'] = (df['realized_proxy'] - df['close']) / df['close']
        
        # Níveis de Convicção (Bandas Fixas baseadas em SD Histórico)
        df['upper_extreme'] = -2.5
        df['upper_slight'] = -1.5
        df['lower_slight'] = 1.5
        df['lower_extreme'] = 2.5
        
        return df.dropna()
    except:
        return pd.DataFrame()

data = fetch_anupl_evolution()

if not data.empty:
    last_v = data['anupl'].iloc[-1]
    
    # Título Centralizado "Italiano" em Azul (#3D5AFE)
    st.markdown("<h1 style='text-align: center; color: #3D5AFE; font-family: serif;'>✦ 𝓐𝓵𝓹𝓱𝓪 𝓝𝓮𝓽 𝓤𝓷𝓻𝓮𝓪𝓵𝓲𝔃𝓮𝓭 𝓟𝓻𝓸𝓯𝓲𝓽/𝓛𝓸𝓼𝓼 ✦</h1>", unsafe_allow_html=True)

    # MATRIZ DE SENTIMENTO DE 5 NÍVEIS
    status, s_color = "NEUTRAL", "#FFFFFF"
    if last_v >= 2.5: status, s_color = "💎 EXTREME CAPITULATION", "#00FBFF"
    elif 1.5 <= last_v < 2.5: status, s_color = "🔹 CAPITULATION / FEAR", "rgba(0, 251, 255, 0.6)"
    elif last_v <= -2.5: status, s_color = "🔴 EXTREME EUPHORIA", "#3D5AFE"
    elif -1.5 >= last_v > -2.5: status, s_color = "🔸 OPTIMISM / ANXIETY", "rgba(61, 90, 254, 0.6)"

    # Header de Métricas
    c1, c2, c3 = st.columns([1, 1, 1.2])
    with c1: st.metric("BITCOIN PRICE", f"${data['close'].iloc[-1]:,.2f}")
    with c2: st.metric("SENTIMENT (SD)", f"{last_v:.2f}")
    with c3: st.markdown(f"<h1 style='text-align: right; color: {s_color}; font-family: sans-serif;'>{status}</h1>", unsafe_allow_html=True)

    # CONSTRUÇÃO DO PLOT EVOLUTION
    fig = make_subplots(
        rows=2, cols=1, 
        shared_xaxes=True, 
        vertical_spacing=0.03, 
        row_heights=[0.65, 0.35]
    )
    
    # 1. Painel de Preço (Escala Logarítmica)
    fig.add_trace(go.Scatter(x=data.index, y=data['close'], name="Price", line=dict(color='white', width=2)), row=1, col=1)

    # 2. Painel de Sentimento ANUPL
    fig.add_trace(go.Scatter(x=data.index, y=data['anupl'], name="ANUPL", line=dict(color='#888', width=1.5)), row=2, col=1)

    # ADIÇÃO DAS BANDAS DE CONVICÇÃO (±1.5 e ±2.5)
    fig.add_hline(y=-1.5, line=dict(color="#3D5AFE", width=1, dash="dot"), row=2, col=1)
    fig.add_hline(y=-2.5, line=dict(color="#3D5AFE", width=1.5, dash="dash"), row=2, col=1)
    fig.add_hline(y=1.5, line=dict(color="#00FBFF", width=1, dash="dot"), row=2, col=1)
    fig.add_hline(y=2.5, line=dict(color="#00FBFF", width=1.5, dash="dash"), row=2, col=1)
    fig.add_hline(y=0, line=dict(color="rgba(255,255,255,0.1)", width=1), row=2, col=1)

    # PREENCHIMENTO DINÂMICO DE DUAS CAMADAS
    # Zona Blue (Euforia / Topo)
    fig.add_trace(go.Scatter(x=data.index, y=[-1.5]*len(data), line=dict(width=0), showlegend=False), row=2, col=1)
    fig.add_trace(go.Scatter(x=data.index, y=np.where(data['anupl'] <= -1.5, data['anupl'], -1.5), fill='tonexty', fillcolor='rgba(61, 90, 254, 0.3)', line=dict(width=0), showlegend=False), row=2, col=1)
    fig.add_trace(go.Scatter(x=data.index, y=[-2.5]*len(data), line=dict(width=0), showlegend=False), row=2, col=1)
    fig.add_trace(go.Scatter(x=data.index, y=np.where(data['anupl'] <= -2.5, data['anupl'], -2.5), fill='tonexty', fillcolor='rgba(61, 90, 254, 0.7)', line=dict(width=0), showlegend=False), row=2, col=1)

    # Zona Aqua (Capitulação / Fundo)
    fig.add_trace(go.Scatter(x=data.index, y=[1.5]*len(data), line=dict(width=0), showlegend=False), row=2, col=1)
    fig.add_trace(go.Scatter(x=data.index, y=np.where(data['anupl'] >= 1.5, data['anupl'], 1.5), fill='tonexty', fillcolor='rgba(0, 251, 255, 0.3)', line=dict(width=0), showlegend=False), row=2, col=1)
    fig.add_trace(go.Scatter(x=data.index, y=[2.5]*len(data), line=dict(width=0), showlegend=False), row=2, col=1)
    fig.add_trace(go.Scatter(x=data.index, y=np.where(data['anupl'] >= 2.5, data['anupl'], 2.5), fill='tonexty', fillcolor='rgba(0, 251, 255, 0.7)', line=dict(width=0), showlegend=False), row=2, col=1)

    # Layout e Eixos
    fig.update_layout(
        template="plotly_dark", paper_bgcolor="#0F0F0F", plot_bgcolor="#0F0F0F", 
        height=1000, margin=dict(l=60, r=60, t=50, b=60), 
        showlegend=False, dragmode="pan"
    )
    
    fig.update_yaxes(type="log", row=1, col=1, gridcolor="#222", title="BTC Price (Log Scale)")
    fig.update_yaxes(row=2, col=1, gridcolor="#222", autorange='reversed', range=[-4, 4], title="Psychology Stress (SD)")
    fig.update_xaxes(gridcolor="#222", range=[data.index[-1800], data.index[-1] + pd.Timedelta(days=60)])

    st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False, 'scrollZoom': True})

else:
    st.error("⚠️ Falha ao carregar dados do Alpha Sentiment. Verifique a ligação com o Yahoo Finance.")
