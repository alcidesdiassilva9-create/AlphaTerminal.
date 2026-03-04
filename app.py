import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots

# Institutional Page Configuration
st.set_page_config(page_title="Alpha Macro Terminal", layout="wide")

st.markdown("""
    <style>
    .main { background-color: #0F0F0F; }
    div[data-testid="stMetric"] { background-color: #161616; padding: 15px; border-radius: 5px; border: 1px solid #333; }
    </style>
    """, unsafe_allow_html=True)

@st.cache_data(ttl=3600)
def fetch_alpha_data():
    df = yf.download("BTC-USD", period="max", interval="1d", progress=False)
    if isinstance(df.columns, pd.MultiIndex):
        df = df['Close']
    else:
        df = df[['Close']]
    df.columns = ['close']
    
    # ALPHA CYCLE MATHEMATICS
    df['log_price'] = np.log(df['close'])
    window = 350
    df['mean'] = df['log_price'].rolling(window=window).mean()
    df['std'] = df['log_price'].rolling(window=window).std()
    
    # Custom Logic: Price < Mean -> Positive Z (Bottom/Aqua) | Price > Mean -> Negative Z (Top/Blue)
    df['z_score'] = (df['mean'] - df['log_price']) / df['std']
    return df.dropna()

try:
    data = fetch_alpha_data()
    last_z = data['z_score'].iloc[-1]
    
    # Signal Metrics Header
    c1, c2, c3 = st.columns(3)
    c1.metric("BITCOIN PRICE", f"${data['close'].iloc[-1]:,.2f}")
    c2.metric("CURRENT SD", f"{last_z:.2f}")
    
    # Visual Verdict
    status = "NEUTRAL"
    s_color = "white"
    if last_z >= 1.0: 
        status = "💎 OVERSOLD (AQUA ZONE)"
        s_color = "#00FBFF"
    elif last_z <= -1.0: 
        status = "🔴 OVERBOUGHT (BLUE ZONE)"
        s_color = "#3D5AFE"
    c3.markdown(f"<h2 style='text-align: center; color: {s_color}; margin: 0;'>{status}</h2>", unsafe_allow_html=True)

    # DUAL-PANEL TERMINAL (LOG CHART + Z-SCORE)
    fig = make_subplots(
        rows=2, cols=1, 
        shared_xaxes=True, 
        vertical_spacing=0.06,
        row_heights=[0.5, 0.5]
    )

    # 1. LOGARITHMIC PRICE CHART (TOP PANEL)
    fig.add_trace(
        go.Scatter(
            x=data.index, 
            y=data['close'], 
            name="Price", 
            line=dict(color='white', width=1.5)
        ),
        row=1, col=1
    )

    # 2. CYCLE INDICATOR (BOTTOM PANEL)
    fig.add_trace(
        go.Scatter(
            x=data.index, 
            y=data['z_score'], 
            name="Alpha Z-Score", 
            line=dict(color='#888', width=1.3)
        ),
        row=2, col=1
    )

    # PROFESSIONAL SD LIMITS (DASHED LINES)
    # Top Side (Blue Zone: -1 to -3 SD)
    fig.add_hline(y=-1.0, line=dict(color="#3D5AFE", width=1.5, dash="dash"), row=2, col=1)
    fig.add_hline(y=-3.0, line=dict(color="#3D5AFE", width=1.5, dash="dash"), row=2, col=1)
    
    # Bottom Side (Aqua Zone: 1 to 3 SD)
    fig.add_hline(y=1.0, line=dict(color="#00FBFF", width=1.5, dash="dash"), row=2, col=1)
    fig.add_hline(y=3.0, line=dict(color="#00FBFF", width=1.5, dash="dash"), row=2, col=1)

    # DYNAMIC DENSITY FILLING
    # Blue Zone Fill (Overbought)
    fig.add_trace(go.Scatter(x=data.index, y=[-1.0]*len(data), line=dict(width=0), showlegend=False), row=2, col=1)
    fig.add_trace(go.Scatter(
        x=data.index, 
        y=np.where(data['z_score'] <= -1.0, data['z_score'], -1.0),
        fill='tonexty',
        fillcolor='rgba(61, 90, 254, 0.6)',
        line=dict(width=0),
        showlegend=False
    ), row=2, col=1)

    # Aqua Zone Fill (Oversold)
    fig.add_trace(go.Scatter(x=data.index, y=[1.0]*len(data), line=dict(width=0), showlegend=False), row=2, col=1)
    fig.add_trace(go.Scatter(
        x=data.index, 
        y=np.where(data['z_score'] >= 1.0, data['z_score'], 1.0),
        fill='tonexty',
        fillcolor='rgba(0, 251, 255, 0.6)',
        line=dict(width=0),
        showlegend=False
    ), row=2, col=1)

    # GLOBAL LAYOUT CONFIGURATION
    fig.update_layout(
        title=dict(text="ALPHA MACRO HISTORY", x=0.5, font=dict(color="#3D5AFE", size=22)),
        template="plotly_dark",
        paper_bgcolor="#0F0F0F",
        plot_bgcolor="#0F0F0F",
        height=900,
        margin=dict(l=50, r=50, t=100, b=50),
        showlegend=False,
        dragmode="pan"
    )

    # AXIS ADJUSTMENTS: LOG PRICE
    fig.update_yaxes(
        type="log", # LOG SCALE ENABLED
        row=1, col=1, 
        gridcolor="#222", 
        title="BTC Price (Log Scale)",
        showline=True,
        linecolor="#444",
        dtick=1 # Shows powers of 10 for professional log look
    )
    
    # REVERSED AXIS FOR MACRO SYMMETRY
    fig.update_yaxes(
        row=2, col=1, 
        gridcolor="#222", 
        title="Cycle Stress (SD)", 
        autorange='reversed',
        range=[-4, 4],
        showline=True,
        linecolor="#444"
    )
    
    fig.update_xaxes(
        gridcolor="#222", 
        range=[data.index[-2000], data.index[-1] + pd.Timedelta(days=60)],
        showline=True,
        linecolor="#444"
    )

    st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False, 'scrollZoom': True})

except Exception as e:
    st.error(f"Terminal Error: {e}")
