import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots

# Configuração de Segurança e Interface
st.set_page_config(page_title="02 ANUPL Terminal", layout="wide")

st.markdown("""
<style>
    .main { background-color: #0F0F0F; } 
    div[data-testid='stMetric'] { 
        background-color: #161616; 
        padding: 20px; 
        border-radius: 5px; 
        border: 1px solid #333; 
    }
</style>
""", unsafe_allow_html=True)

@st.cache_data(ttl=60) # Atualização rápida para evitar erros de cache
def fetch_anupl_fixed():
    try:
        # 1. Download do Histórico
        ticker_sym = "BTC-USD"
        data_raw = yf.download(ticker_sym, period="max", interval="1d", progress=False)
        
        if data_raw.empty: return pd.DataFrame()

        # Limpeza de Colunas (Tratando MultiIndex se necessário)
        if isinstance(data_raw.columns, pd.MultiIndex):
            df = pd.DataFrame(data_raw['Close'].iloc[:, 0])
        else:
            df = pd.DataFrame(data_raw['Close'])
            
        df.columns = ['close']
        
        # 2. Injeção de Preço Atual (Fallback Seguro)
        # Se o download falhar no último candle, usamos o último preço disponível
        current_price = df['close'].iloc[-1]
        
        # 3. Cálculo de Proxy Realized (Média Móvel 365d)
        df['realized_proxy'] = df['close'].rolling(window=365).mean()
        
        # 4. Transformação Logarítmica
        df['raw_ratio'] = np.log(df['realized_proxy'] / df['close'])
        
        # 5. Normalização Z-Score (Janela 350d)
        window = 350
        df['mean'] = df['raw_ratio'].rolling(window=window).mean()
        df['std'] = df['raw_ratio'].rolling(window=window).std()
        
        # Cálculo Final e Clipping
        df['anupl_z'] = ((df['raw_ratio'] - df['mean']) / df['std']).clip(-3.8, 3.8)
        
        return df.dropna()
    except Exception as e:
        st.error(f"Erro Crítico no Motor de Dados: {e}")
        return pd.DataFrame()

# Execução
data = fetch_anupl_fixed()

if not data.empty:
    last_z = data['anupl_z'].iloc[-1]
    current_price = data['close'].iloc[-1]
    
    st.markdown("<h1 style='text-align: center; color: #3D5AFE; font-family: serif;'>✦ 𝓐𝓵𝓹𝓱𝓪 𝓝𝓮𝓽 𝓤𝓷𝓻𝓮𝓪𝓵𝓲𝔃𝓮𝓭 𝓟𝓻𝓸𝓯𝓲𝓽/𝓛𝓸𝓼𝓼 ✦</h1>", unsafe_allow_html=True)

    # Matriz de Sentimento
    status, s_color = "NEUTRAL", "#FFFFFF"
    if last_z >= 2.0: status, s_color = "💎 EXTREME CAPITULATION", "#00FBFF"
    elif 1.0 <= last_z < 2.0: status, s_color = "🔹 CAPITULATION / FEAR", "rgba(0, 251, 255, 0.6)"
    elif last_z <= -2.0: status, s_color = "🔴 EXTREME EUPHORIA", "#3D5AFE"
    elif -1.0 >= last_z > -2.0: status, s_color = "🔸 OPTIMISM / ANXIETY", "rgba(61, 90, 254, 0.6)"

    # Dashboard Metrics
    c1, c2, c3 = st.columns([1, 1, 1.2])
    c1.metric("BITCOIN PRICE", f"${current_price:,.2f}")
    c2.metric("SENTIMENT (SD)", f"{last_z:.2f} SD")
    c3.markdown(f"<h1 style='text-align: right; color: {s_color}; font-size: 28px;'>{status}</h1>", unsafe_allow_html=True)

    # Gráfico
    fig = make_subplots(rows=2, cols=1, shared_xaxes=True, vertical_spacing=0.03, row_heights=[0.65, 0.35])
    
    fig.add_trace(go.Scatter(x=data.index, y=data['close'], name="Price", line=dict(color='white', width=2)), row=1, col=1)
    fig.add_trace(go.Scatter(x=data.index, y=data['anupl_z'], name="Sentiment SD", line=dict(color='#888', width=1.5)), row=2, col=1)

    # Escala Institucional
    for val, color, dash in [(-3, "#3D5AFE", "dot"), (-2, "#3D5AFE", "dash"), (3, "#00FBFF", "dot"), (2, "#00FBFF", "dash")]:
        fig.add_hline(y=val, line=dict(color=color, width=1.5, dash=dash), row=2, col=1)
    
    fig.add_hline(y=0, line=dict(color="rgba(255,255,255,0.2)", width=1), row=2, col=1)

    # Fills
    fig.add_trace(go.Scatter(x=data.index, y=[-2.0]*len(data), line=dict(width=0), showlegend=False), row=2, col=1)
    fig.add_trace(go.Scatter(x=data.index, y=np.where(data['anupl_z'] <= -2.0, data['anupl_z'], -2.0), fill='tonexty', fillcolor='rgba(61, 90, 254, 0.5)', line=dict(width=0), showlegend=False), row=2, col=1)
    fig.add_trace(go.Scatter(x=data.index, y=[2.0]*len(data), line=dict(width=0), showlegend=False), row=2, col=1)
    fig.add_trace(go.Scatter(x=data.index, y=np.where(data['anupl_z'] >= 2.0, data['anupl_z'], 2.0), fill='tonexty', fillcolor='rgba(0, 251, 255, 0.5)', line=dict(width=0), showlegend=False), row=2, col=1)

    fig.update_layout(template="plotly_dark", paper_bgcolor="#0F0F0F", plot_bgcolor="#0F0F0F", height=900, margin=dict(l=60, r=60, t=50, b=60), showlegend=False)
    fig.update_yaxes(type="log", row=1, col=1, gridcolor="#222")
    fig.update_yaxes(row=2, col=1, gridcolor="#222", autorange='reversed', range=[-3.8, 3.8], tickvals=[-3, -2, -1, 0, 1, 2, 3])
    
    st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})
else:
    st.warning("Aguardando resposta da API financeira... Recarregue em instantes.")
    
    st.markdown(f"<p style='text-align: center; color: #444;'>Engine: Alpha Sentiment V6 (Real-Time Price Injection Active)</p>", unsafe_allow_html=True)
else:
    st.error("Erro na obtenção de dados do Alpha Sentiment.")False})
