import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots

st.set_page_config(page_title="02 ANUPL Terminal", layout="wide")

st.markdown("<style>.main { background-color: #0F0F0F; } div[data-testid='stMetric'] { background-color: #161616; padding: 20px; border-radius: 5px; border: 1px solid #333; }</style>", unsafe_allow_html=True)

@st.cache_data(ttl=3600)
def fetch_anupl_calibrated():
    try:
        df = yf.download("BTC-USD", period="max", interval="1d", progress=False)
        if df.empty: return pd.DataFrame()
        df = df[['Close']] if not isinstance(df.columns, pd.MultiIndex) else df['Close']
        df.columns = ['close']
        
        # 1. Calculo do Rácio de Sentimento (Proxy Realized via SMA 365)
        df['realized_proxy'] = df['close'].rolling(window=365).mean()
        df['raw_ratio'] = (df['realized_proxy'] - df['close']) / df['close']
        
        # 2. Normalização Estatística (Z-Score do Rácio)
        # Isto transforma o rácio estático num oscilador de stress real (SD)
        window = 350
        df['anupl_mean'] = df['raw_ratio'].rolling(window=window).mean()
        df['anupl_std'] = df['raw_ratio'].rolling(window=window).std()
        df['anupl_z'] = (df['raw_ratio'] - df['anupl_mean']) / df['anupl_std']
        
        return df.dropna()
    except:
        return pd.DataFrame()

data = fetch_anupl_calibrated()

if not data.empty:
    last_z = data['anupl_z'].iloc[-1]
    
    st.markdown("<h1 style='text-align: center; color: #3D5AFE; font-family: serif;'>✦ 𝓐𝓵𝓹𝓱𝓪 𝓝𝓮𝓽 𝓤𝓷𝓻𝓮𝓪𝓵𝓲𝔃𝓮𝓭 𝓟𝓻𝓸𝓯𝓲𝓽/𝓛𝓸𝓼𝓼 ✦</h1>", unsafe_allow_html=True)

    # Matriz de Sentimento Normalizada (Baseada em Z-Score Real)
    status, s_color = "NEUTRAL", "#FFFFFF"
    if last_z >= 2.0: status, s_color = "💎 EXTREME CAPITULATION", "#00FBFF"
    elif 1.0 <= last_z < 2.0: status, s_color = "🔹 CAPITULATION / FEAR", "rgba(0, 251, 255, 0.6)"
    elif last_z <= -2.0: status, s_color = "🔴 EXTREME EUPHORIA", "#3D5AFE"
    elif -1.0 >= last_z > -2.0: status, s_color = "🔸 OPTIMISM / ANXIETY", "rgba(61, 90, 254, 0.6)"

    c1, c2, c3 = st.columns([1, 1, 1.2])
    c1.metric("BITCOIN PRICE", f"${data['close'].iloc[-1]:,.2f}")
    c2.metric("SENTIMENT (SD)", f"{last_z:.2f}")
    c3.markdown(f"<h1 style='text-align: right; color: {s_color}; font-family: sans-serif;'>{status}</h1>", unsafe_allow_html=True)

    fig = make_subplots(rows=2, cols=1, shared_xaxes=True, vertical_spacing=0.03, row_heights=[0.65, 0.35])
    
    # Painel 1: Preço Logarítmico
    fig.add_trace(go.Scatter(x=data.index, y=data['close'], name="Price", line=dict(color='white', width=2)), row=1, col=1)

    # Painel 2: ANUPL Z-Score (O Sentimento agora oscila corretamente)
    fig.add_trace(go.Scatter(x=data.index, y=data['anupl_z'], name="Sentiment SD", line=dict(color='#888', width=1.5)), row=2, col=1)

    # Bandas de Convicção Estatística
    fig.add_hline(y=-1.0, line=dict(color="#3D5AFE", width=1, dash="dot"), row=2, col=1)
    fig.add_hline(y=-2.0, line=dict(color="#3D5AFE", width=1.5, dash="dash"), row=2, col=1)
    fig.add_hline(y=1.0, line=dict(color="#00FBFF", width=1, dash="dot"), row=2, col=1)
    fig.add_hline(y=2.0, line=dict(color="#00FBFF", width=1.5, dash="dash"), row=2, col=1)
    fig.add_hline(y=0, line=dict(color="rgba(255,255,255,0.1)", width=1), row=2, col=1)

    # Preenchimentos de Dupla Intensidade
    # Lado Blue (Euforia)
    fig.add_trace(go.Scatter(x=data.index, y=[-1.0]*len(data), line=dict(width=0), showlegend=False), row=2, col=1)
    fig.add_trace(go.Scatter(x=data.index, y=np.where(data['anupl_z'] <= -1.0, data['anupl_z'], -1.0), fill='tonexty', fillcolor='rgba(61, 90, 254, 0.3)', line=dict(width=0), showlegend=False), row=2, col=1)
    fig.add_trace(go.Scatter(x=data.index, y=[-2.0]*len(data), line=dict(width=0), showlegend=False), row=2, col=1)
    fig.add_trace(go.Scatter(x=data.index, y=np.where(data['anupl_z'] <= -2.0, data['anupl_z'], -2.0), fill='tonexty', fillcolor='rgba(61, 90, 254, 0.7)', line=dict(width=0), showlegend=False), row=2, col=1)

    # Lado Aqua (Capitulação)
    fig.add_trace(go.Scatter(x=data.index, y=[1.0]*len(data), line=dict(width=0), showlegend=False), row=2, col=1)
    fig.add_trace(go.Scatter(x=data.index, y=np.where(data['anupl_z'] >= 1.0, data['anupl_z'], 1.0), fill='tonexty', fillcolor='rgba(0, 251, 255, 0.3)', line=dict(width=0), showlegend=False), row=2, col=1)
    fig.add_trace(go.Scatter(x=data.index, y=[2.0]*len(data), line=dict(width=0), showlegend=False), row=2, col=1)
    fig.add_trace(go.Scatter(x=data.index, y=np.where(data['anupl_z'] >= 2.0, data['anupl_z'], 2.0), fill='tonexty', fillcolor='rgba(0, 251, 255, 0.7)', line=dict(width=0), showlegend=False), row=2, col=1)

    fig.update_layout(template="plotly_dark", paper_bgcolor="#0F0F0F", plot_bgcolor="#0F0F0F", height=1000, margin=dict(l=60, r=60, t=50, b=60), showlegend=False)
    fig.update_yaxes(type="log", row=1, col=1, gridcolor="#222")
    fig.update_yaxes(row=2, col=1, gridcolor="#222", autorange='reversed', range=[-4, 4], title="Psychology Z-Score")
    
    st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})
else:
    st.error("Erro na obtenção de dados do Alpha Sentiment.")

else:
    st.error("⚠️ Falha ao carregar dados do Alpha Sentiment. Verifique a ligação com o Yahoo Finance.")
