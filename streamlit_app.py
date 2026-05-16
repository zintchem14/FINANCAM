import streamlit as st
import plotly.graph_objects as go
import pandas as pd
import requests
from datetime import datetime
from utils.preprocessing import (
    load_data, get_kpis, get_diverging, get_dotplot, get_heatmap, 
    get_radar, get_scatter, get_agence_grouped, get_violin_data,
    get_diverging_ville, get_dotplot_comparatif, get_portfolio_health, get_market_risk
)

# ── CONFIG ──────────────────────────────────────────────────
st.set_page_config(
    page_title="FinCam Analytics",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ── TAUX DE CHANGE ───────────────────────────────────────────
@st.cache_data(ttl=3600)
def get_taux():
    try:
        r1 = requests.get("https://api.exchangerate-api.com/v4/latest/USD", timeout=5)
        r2 = requests.get("https://api.exchangerate-api.com/v4/latest/EUR", timeout=5)
        return {
            'usd': round(r1.json()['rates']['XAF'], 0),
            'eur': round(r2.json()['rates']['XAF'], 0)
        }
    except:
        return {'usd': 610, 'eur': 655}

taux = get_taux()

# ── CSS ─────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Montserrat:wght@600;700;800;900&family=Inter:wght@300;400;500;600&family=JetBrains+Mono:wght@400;600&display=swap');

* { font-family: 'Inter', sans-serif; }
h1, h2, h3 { font-family: 'Montserrat', sans-serif; }

.stApp { background-color: #0F1923; }

section[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #060E17 0%, #0A1520 100%);
    border-right: 1px solid rgba(46,204,154,0.2);
}
section[data-testid="stSidebar"]::after {
    content: '';
    position: absolute;
    top: 0; right: 0;
    width: 1px; height: 100%;
    background: linear-gradient(to bottom, #2ECC9A, transparent);
}

.logo-container {
    text-align: center;
    padding: 1.5rem 0 2rem 0;
    border-bottom: 1px solid rgba(46,204,154,0.1);
    margin-bottom: 1.5rem;
}
.logo-icon { font-size: 2.2rem; margin-bottom: 0.3rem; }
.logo-image {
    width: 80px;
    height: 80px;
    border-radius: 50%;
    background: linear-gradient(135deg, #2ECC9A, #17A89E);
    display: flex;
    align-items: center;
    justify-content: center;
    margin: 0 auto 1rem auto;
    border: 3px solid rgba(46,204,154,0.3);
    box-shadow: 0 4px 20px rgba(46,204,154,0.2);
}
.logo-image-inner {
    font-size: 2.5rem;
}
.logo-title {
    font-family: 'Montserrat', sans-serif;
    font-size: 1.4rem;
    font-weight: 800;
    background: linear-gradient(135deg, #2ECC9A, #17A89E);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
}
.logo-sub { color: #3A5568; font-size: 0.65rem; letter-spacing: 0.15em; text-transform: uppercase; }

.live-badge {
    display: inline-flex;
    align-items: center;
    gap: 0.4rem;
    background: rgba(46,204,154,0.08);
    border: 1px solid rgba(46,204,154,0.25);
    border-radius: 20px;
    padding: 0.3rem 0.8rem;
    font-size: 0.65rem;
    color: #2ECC9A;
    font-weight: 600;
    letter-spacing: 0.05em;
}
.live-dot {
    width: 6px; height: 6px;
    background: #2ECC9A;
    border-radius: 50%;
    animation: pulse 2s infinite;
}
@keyframes pulse {
    0%, 100% { opacity: 1; }
    50% { opacity: 0.3; }
}

.filter-label {
    color: #3A5568;
    font-size: 0.65rem;
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: 0.1em;
    margin-bottom: 0.3rem;
}

.taux-card {
    background: linear-gradient(135deg, rgba(46,204,154,0.08), rgba(23,168,158,0.05));
    border: 1px solid rgba(46,204,154,0.2);
    border-radius: 10px;
    padding: 1rem;
    margin-top: 1rem;
}
.taux-title {
    color: #3A5568;
    font-size: 0.6rem;
    text-transform: uppercase;
    letter-spacing: 0.1em;
    margin-bottom: 0.8rem;
    font-weight: 600;
}
.taux-row {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 0.5rem;
}
.taux-currency { color: #7A8B94; font-size: 0.75rem; }
.taux-value {
    font-family: 'JetBrains Mono', monospace;
    color: #2ECC9A;
    font-size: 0.85rem;
    font-weight: 600;
}
.taux-unit { color: #3A5568; font-size: 0.65rem; }

.time-display {
    text-align: center;
    padding: 1rem 0;
}
.time-value {
    font-family: 'JetBrains Mono', monospace;
    color: #2ECC9A;
    font-size: 1.8rem;
    font-weight: 600;
    letter-spacing: 0.1em;
}
.time-date { color: #3A5568; font-size: 0.7rem; margin-top: 0.2rem; }

.kpi-green {
    background: linear-gradient(135deg, rgba(46,204,154,0.15), rgba(46,204,154,0.05));
    border: 1px solid rgba(46,204,154,0.3);
    border-radius: 14px;
    padding: 1.3rem 1.5rem;
    height: 100%;
}
.kpi-teal {
    background: linear-gradient(135deg, rgba(23,168,158,0.15), rgba(23,168,158,0.05));
    border: 1px solid rgba(23,168,158,0.3);
    border-radius: 14px;
    padding: 1.3rem 1.5rem;
    height: 100%;
}
.kpi-orange {
    background: linear-gradient(135deg, rgba(243,156,18,0.15), rgba(243,156,18,0.05));
    border: 1px solid rgba(243,156,18,0.3);
    border-radius: 14px;
    padding: 1.3rem 1.5rem;
    height: 100%;
}
.kpi-blue {
    background: linear-gradient(135deg, rgba(52,152,219,0.15), rgba(52,152,219,0.05));
    border: 1px solid rgba(52,152,219,0.3);
    border-radius: 14px;
    padding: 1.3rem 1.5rem;
    height: 100%;
}
.kpi-label {
    color: #7A8B94;
    font-size: 0.65rem;
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: 0.1em;
}
.kpi-value {
    font-family: 'JetBrains Mono', monospace;
    font-size: 1.6rem;
    font-weight: 600;
    margin: 0.4rem 0 0.1rem 0;
}
.kpi-unit { font-size: 0.75rem; color: #7A8B94; }
.kpi-green .kpi-value  { color: #2ECC9A; }
.kpi-teal .kpi-value   { color: #17A89E; }
.kpi-orange .kpi-value { color: #F39C12; }
.kpi-blue .kpi-value   { color: #3498DB; }

.glass {
    background: rgba(10,18,28,0.6);
    border: 1px solid rgba(46,204,154,0.1);
    border-radius: 14px;
    padding: 1.5rem;
    margin-bottom: 1rem;
}
.section-title {
    font-family: 'Syne', sans-serif;
    color: #E8E8E8;
    font-size: 1rem;
    font-weight: 700;
    margin-bottom: 0.2rem;
}
.section-sub { color: #3A5568; font-size: 0.72rem; margin-bottom: 0.5rem; }

.divider {
    height: 1px;
    background: linear-gradient(to right, rgba(46,204,154,0.3), transparent);
    margin: 2rem 0;
}

.alert-red {
    background: rgba(231,76,60,0.08);
    border: 1px solid rgba(231,76,60,0.25);
    border-radius: 8px; padding: 0.75rem; margin: 0.4rem 0;
}
.alert-green {
    background: rgba(46,204,154,0.08);
    border: 1px solid rgba(46,204,154,0.25);
    border-radius: 8px; padding: 0.75rem; margin: 0.4rem 0;
}
.insight-card {
    background: linear-gradient(135deg, rgba(243,156,18,0.08), rgba(243,156,18,0.03));
    border: 1px solid rgba(243,156,18,0.25);
    border-radius: 14px;
    padding: 1.5rem;
    margin-top: 1rem;
}
.footer {
    text-align: center;
    color: #1F3A4A;
    font-size: 0.7rem;
    padding: 2rem 0 1rem 0;
    border-top: 1px solid #111E2A;
    margin-top: 3rem;
    letter-spacing: 0.05em;
}

/* Scrollbars personnalisées */
::-webkit-scrollbar {
    width: 12px;
    height: 12px;
}
::-webkit-scrollbar-track {
    background: #0A1520;
    border-radius: 10px;
}
::-webkit-scrollbar-thumb {
    background: linear-gradient(180deg, #2ECC9A, #17A89E);
    border-radius: 10px;
    border: 2px solid #0A1520;
}
::-webkit-scrollbar-thumb:hover {
    background: linear-gradient(180deg, #3ED9A8, #2ECC9A);
}
::-webkit-scrollbar-corner {
    background: #0A1520;
}

/* En-têtes du dataframe */
[data-testid="stDataFrame"] thead th {
    background: linear-gradient(135deg, #00897B 0%, #50C878 100%) !important;
    color: #FFFFFF !important;
    font-weight: 700 !important;
    font-size: 0.85rem !important;
    text-transform: uppercase;
    letter-spacing: 0.05em;
    border-bottom: 2px solid #0A1520 !important;
}
[data-testid="stDataFrame"] thead tr:hover th {
    background: linear-gradient(135deg, #009688 0%, #66BB6A 100%) !important;
}
</style>
""", unsafe_allow_html=True)

# ── DATA ─────────────────────────────────────────────────────
@st.cache_data
def load():
    return load_data('dataset_financier.csv')

df_full = load()

# ── SIDEBAR ──────────────────────────────────────────────────
with st.sidebar:
    # Logo
    st.markdown("""
    <div class="logo-container">
        <div class="logo-image">
            <div class="logo-image-inner">📊</div>
        </div>
        <div class="logo-title">FinCam Analytics</div>
        <div class="logo-sub">Banking Intelligence Platform</div>
        <div style="margin-top:1rem;">
            <span class="live-badge">
                <span class="live-dot"></span>
                LIVE DATA
            </span>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # Filtres
    st.markdown('<div class="filter-label">Filtres</div>', unsafe_allow_html=True)

    villes  = ['Toutes'] + sorted(df_full['lieu'].unique().tolist())
    banques = ['Toutes'] + sorted(df_full['banque'].unique().tolist())
    agences = ['Toutes'] + sorted(df_full['agence'].unique().tolist())

    ville_sel  = st.selectbox('📍 Ville',  villes)
    banque_sel = st.selectbox('🏛️ Banque', banques)
    agence_sel = st.selectbox('🏢 Agence', agences)

    df = df_full.copy()
    if ville_sel  != 'Toutes': df = df[df['lieu']   == ville_sel]
    if banque_sel != 'Toutes': df = df[df['banque'] == banque_sel]
    if agence_sel != 'Toutes': df = df[df['agence'] == agence_sel]

    st.markdown("<hr style='border-color:#0D1F2D; margin:1.5rem 0;'>", unsafe_allow_html=True)

    # Heure
    now = datetime.now()
    st.markdown(f"""
    <div class="time-display">
        <div class="time-value">{now.strftime('%H:%M:%S')}</div>
        <div class="time-date">{now.strftime('%d %B %Y')}</div>
    </div>
    """, unsafe_allow_html=True)

    # Taux de change
    st.markdown(f"""
    <div class="taux-card">
        <div class="taux-title">💱 Taux de Change</div>
        <div class="taux-row">
            <span class="taux-currency">🇺🇸 USD</span>
            <span>
                <span class="taux-value">{taux['usd']:,.0f}</span>
                <span class="taux-unit"> XAF</span>
            </span>
        </div>
        <div class="taux-row">
            <span class="taux-currency">🇪🇺 EUR</span>
            <span>
                <span class="taux-value">{taux['eur']:,.0f}</span>
                <span class="taux-unit"> XAF</span>
            </span>
        </div>
        <div style="margin-top:0.8rem; padding-top:0.8rem; border-top:1px solid rgba(46,204,154,0.1);">
            <div class="taux-row">
                <span class="taux-currency">🏦 BEAC</span>
                <span>
                    <span class="taux-value">5.00</span>
                    <span class="taux-unit"> %</span>
                </span>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown(f"""
    <div style='text-align:center; margin-top:1.5rem;'>
        <span style='background:rgba(46,204,154,0.08); border:1px solid rgba(46,204,154,0.2);
        border-radius:20px; padding:0.3rem 0.8rem; color:#2ECC9A; font-size:0.65rem; font-weight:600;'>
            {len(df)} enregistrements actifs
        </span>
    </div>
    """, unsafe_allow_html=True)

# ── HEADER ───────────────────────────────────────────────────
st.markdown(f"""
<div style='padding-bottom:1.5rem; margin-bottom:2rem;
border-bottom:1px solid #111E2A;'>
    <div style='display:flex; justify-content:space-between; align-items:flex-end;'>
        <div>
            <div style='color:#3A5568; font-size:0.65rem; text-transform:uppercase;
            letter-spacing:0.15em; margin-bottom:0.4rem;'>CAMEROON BANKING INTELLIGENCE</div>
            <h1 style='font-family:Syne,sans-serif; color:#E8E8E8; font-size:2.2rem;
            font-weight:800; margin:0; line-height:1;'>Vue Générale
            <span style='background:linear-gradient(135deg,#2ECC9A,#17A89E);
            -webkit-background-clip:text; -webkit-text-fill-color:transparent;'> •</span>
            </h1>
            <div style='height:2px; width:60px;
            background:linear-gradient(to right,#2ECC9A,transparent);
            margin-top:0.8rem; border-radius:2px;'></div>
        </div>
        <div style='text-align:right;'>
            <div style='color:#3A5568; font-size:0.65rem;'>Filtre actif</div>
            <div style='color:#2ECC9A; font-size:0.8rem; font-weight:600;'>
                {ville_sel} • {banque_sel} • {agence_sel}
            </div>
        </div>
    </div>
</div>
""", unsafe_allow_html=True)

# ── KPIs ─────────────────────────────────────────────────────
kpis = get_kpis(df)
c1, c2, c3, c4 = st.columns(4)

kpi_configs = [
    (c1, 'kpi-green',  '💰', 'Revenu Total',        f"{kpis['revenu_total']/1e6:.1f}", 'Mrds FCFA'),
    (c2, 'kpi-teal',   '🏦', 'Capital Moyen',       f"{kpis['capital_moyen']/1000:.1f}",'Mrds FCFA'),
    (c3, 'kpi-orange', '📈', 'Flux Trésorerie Moy', f"{kpis['flux_moyen']:.0f}",        'FCFA'),
    (c4, 'kpi-blue',   '📉', 'Taux Intérêt Moyen',  f"{kpis['taux_moyen']:.2f}",        '%'),
]

for col, css, icon, label, value, unit in kpi_configs:
    with col:
        st.markdown(f"""
        <div class="{css}">
            <div style='display:flex; justify-content:space-between; align-items:flex-start;'>
                <div class="kpi-label">{label}</div>
                <div style='font-size:1.2rem;'>{icon}</div>
            </div>
            <div class="kpi-value">{value}</div>
            <div class="kpi-unit">{unit}</div>
        </div>
        """, unsafe_allow_html=True)

st.markdown("<div style='margin-top:1.5rem;'></div>", unsafe_allow_html=True)

# ── KPI DYNAMIQUES AVEC BARRES DE PROGRESSION ─────────────────────
portfolio_health = get_portfolio_health(df)
market_risk = get_market_risk(df)

st.markdown('<div class="glass">', unsafe_allow_html=True)
st.markdown('<div class="section-title">Indicateurs de Santé du Portefeuille</div>', unsafe_allow_html=True)

col_kpi1, col_kpi2 = st.columns(2)

with col_kpi1:
    health_color = '#2ECC9A' if portfolio_health > 70 else '#F39C12' if portfolio_health > 40 else '#E74C3C'
    st.markdown(f"""
    <div style='margin-bottom:1rem;'>
        <div style='display:flex; justify-content:space-between; margin-bottom:0.5rem;'>
            <span style='color:#7A8B94; font-size:0.75rem; font-weight:600;'>Portfolio Health</span>
            <span style='color:{health_color}; font-size:0.85rem; font-weight:700;'>{portfolio_health:.0f}%</span>
        </div>
        <div style='background:#111E2A; border-radius:10px; height:12px; overflow:hidden;'>
            <div style='width:{portfolio_health}%; background:{health_color}; height:100%; border-radius:10px;'></div>
        </div>
    </div>
    """, unsafe_allow_html=True)

with col_kpi2:
    risk_color = '#2ECC9A' if market_risk < 30 else '#F39C12' if market_risk < 60 else '#E74C3C'
    st.markdown(f"""
    <div style='margin-bottom:1rem;'>
        <div style='display:flex; justify-content:space-between; margin-bottom:0.5rem;'>
            <span style='color:#7A8B94; font-size:0.75rem; font-weight:600;'>Market Risk</span>
            <span style='color:{risk_color}; font-size:0.85rem; font-weight:700;'>{market_risk:.0f}%</span>
        </div>
        <div style='background:#111E2A; border-radius:10px; height:12px; overflow:hidden;'>
            <div style='width:{market_risk}%; background:{risk_color}; height:100%; border-radius:10px;'></div>
        </div>
    </div>
    """, unsafe_allow_html=True)

st.markdown('</div>', unsafe_allow_html=True)
st.markdown('<div class="divider"></div>', unsafe_allow_html=True)

# ── GRAPHIQUES PRINCIPAUX ─────────────────────────────────────
BG   = 'rgba(0,0,0,0)'
GRID = '#111E2A'
FONT = '#E8E8E8'

col_left, col_right = st.columns([3, 2])

with col_left:
    st.markdown('<div class="glass">', unsafe_allow_html=True)
    st.markdown('<div class="section-title">Benchmark Sectoriel</div>', unsafe_allow_html=True)
    st.markdown('<div class="section-sub">Écart au revenu moyen par Banque (FCFA)</div>', unsafe_allow_html=True)

    ecarts   = get_diverging(df)
    couleurs = ['#E74C3C' if v < 0 else '#2ECC9A' for v in ecarts.values]

    fig1 = go.Figure(go.Bar(
        y=ecarts.index, x=ecarts.values, orientation='h',
        marker_color=couleurs,
        text=[f"{v:+,.0f}" for v in ecarts.values],
        textposition='outside',
        textfont=dict(color=FONT, size=11),
        hovertemplate='<b>%{y}</b><br>Écart: %{x:,.0f} FCFA<extra></extra>'
    ))
    fig1.add_vline(x=0, line_color='rgba(255,255,255,0.15)', line_dash='dash')
    fig1.update_layout(
        height=300, plot_bgcolor=BG, paper_bgcolor=BG,
        font=dict(color=FONT, family='Inter'),
        xaxis=dict(gridcolor=GRID, color='#3A5568', zeroline=False),
        yaxis=dict(gridcolor=GRID, color=FONT),
        margin=dict(l=10, r=90, t=10, b=30),
        showlegend=False
    )
    st.plotly_chart(fig1, use_container_width=True)

    a1, a2 = st.columns(2)
    worst = ecarts.idxmin()
    best  = ecarts.idxmax()
    with a1:
        st.markdown(f"""<div class="alert-red">
            <span style='color:#E74C3C; font-weight:700; font-size:0.8rem;'>⚠ Sous-performance</span><br>
            <span style='color:#7A8B94; font-size:0.75rem; font-family:JetBrains Mono,monospace;'>
            {worst} : {ecarts[worst]:+,.0f}</span>
        </div>""", unsafe_allow_html=True)
    with a2:
        st.markdown(f"""<div class="alert-green">
            <span style='color:#2ECC9A; font-weight:700; font-size:0.8rem;'>✓ Leader</span><br>
            <span style='color:#7A8B94; font-size:0.75rem; font-family:JetBrains Mono,monospace;'>
            {best} : {ecarts[best]:+,.0f}</span>
        </div>""", unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

with col_right:
    st.markdown('<div class="glass">', unsafe_allow_html=True)
    st.markdown('<div class="section-title">Performance à Bafoussam</div>', unsafe_allow_html=True)
    st.markdown('<div class="section-sub">Revenu total par Banque — ville leader</div>', unsafe_allow_html=True)

    dot = get_dotplot(df_full)
    couleurs_dot = {'UBA':'#2ECC9A','BGFI':'#17A89E','Ecobank':'#F39C12','SG':'#E74C3C'}

    fig2 = go.Figure()
    for banque, val in dot.items():
        c = couleurs_dot.get(banque, '#7A8B94')
        fig2.add_trace(go.Scatter(
            x=[val], y=[banque], mode='markers+text',
            marker=dict(size=18, color=c,
                        line=dict(color='rgba(255,255,255,0.1)', width=2)),
            text=[f"{val/1000:.0f}k"],
            textposition='middle right',
            textfont=dict(color=c, size=11, family='JetBrains Mono'),
            name=banque
        ))
    fig2.update_layout(
        height=300, plot_bgcolor=BG, paper_bgcolor=BG,
        font=dict(color=FONT, family='Inter'),
        xaxis=dict(gridcolor=GRID, color='#3A5568'),
        yaxis=dict(gridcolor=GRID, color=FONT),
        margin=dict(l=10, r=70, t=10, b=30),
        showlegend=False
    )
    st.plotly_chart(fig2, use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)

st.markdown('<div class="divider"></div>', unsafe_allow_html=True)

# ── HEATMAP ───────────────────────────────────────────────────
st.markdown('<div class="glass">', unsafe_allow_html=True)
st.markdown('<div class="section-title">Heatmap — Performance par Banque & Ville</div>', unsafe_allow_html=True)
st.markdown('<div class="section-sub">Écart à la moyenne globale (FCFA)</div>', unsafe_allow_html=True)

hmap = get_heatmap(df)
fig3 = go.Figure(go.Heatmap(
    z=hmap.values, x=hmap.columns, y=hmap.index,
    colorscale='RdYlGn', zmid=0,
    text=hmap.round(0).values,
    texttemplate="%{text:,.0f}",
    textfont=dict(size=10, color='white'),
    hovertemplate='<b>%{y}</b> — %{x}<br>Écart: %{z:,.0f} FCFA<extra></extra>'
))
fig3.update_layout(
    height=300, plot_bgcolor=BG, paper_bgcolor=BG,
    font=dict(color=FONT, family='Inter'),
    xaxis=dict(color='#7A8B94'),
    yaxis=dict(color=FONT),
    margin=dict(l=60, r=20, t=10, b=40)
)
st.plotly_chart(fig3, use_container_width=True)
st.markdown('</div>', unsafe_allow_html=True)

st.markdown('<div class="divider"></div>', unsafe_allow_html=True)

# ── LIGNE 2: RADAR, SCATTER, BARPLOT GROUPÉ ─────────────────────
col_radar, col_scatter, col_bar = st.columns(3)

with col_radar:
    st.markdown('<div class="glass">', unsafe_allow_html=True)
    st.markdown('<div class="section-title">Radar — Profil Financier</div>', unsafe_allow_html=True)
    st.markdown('<div class="section-sub">5 ratios par Banque</div>', unsafe_allow_html=True)
    
    radar_data = get_radar(df)
    categories = ['Rentabilité', 'Marge Nette', 'Liquidité', 'Levier', 'Efficacité']
    
    fig_radar = go.Figure()
    couleurs_banques = {'UBA':'#2ECC9A','BGFI':'#17A89E','Ecobank':'#F39C12','SG':'#E74C3C'}
    
    for banque in radar_data.index:
        values = radar_data.loc[banque].values
        values = list(values) + [values[0]]  # Fermer le radar
        fig_radar.add_trace(go.Scatterpolar(
            r=values,
            theta=categories + [categories[0]],
            fill='toself',
            name=banque,
            line_color=couleurs_banques.get(banque, '#7A8B94'),
            opacity=0.7
        ))
    
    fig_radar.update_layout(
        height=350,
        polar=dict(
            radialaxis=dict(
                visible=True,
                gridcolor=GRID,
                color='#7A8B94'
            ),
            angularaxis=dict(
                gridcolor=GRID,
                color=FONT
            )
        ),
        plot_bgcolor=BG,
        paper_bgcolor=BG,
        font=dict(color=FONT, family='Inter'),
        margin=dict(l=20, r=20, t=30, b=20),
        legend=dict(
            orientation='h',
            yanchor='bottom',
            y=1.02,
            xanchor='right',
            x=1,
            font=dict(size=9)
        )
    )
    st.plotly_chart(fig_radar, use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)

with col_scatter:
    st.markdown('<div class="glass">', unsafe_allow_html=True)
    st.markdown('<div class="section-title">Scatter — Revenu vs Dépenses</div>', unsafe_allow_html=True)
    st.markdown('<div class="section-sub">Analyse de rentabilité par Banque</div>', unsafe_allow_html=True)
    
    scatter_data = get_scatter(df)
    
    fig_scatter = go.Figure()
    for banque in scatter_data['banque'].unique():
        data_banque = scatter_data[scatter_data['banque'] == banque]
        fig_scatter.add_trace(go.Scatter(
            x=data_banque['revenu'],
            y=data_banque['depenses'],
            mode='markers',
            name=banque,
            marker=dict(
                size=10,
                color=couleurs_banques.get(banque, '#7A8B94'),
                line=dict(color='rgba(255,255,255,0.2)', width=1)
            ),
            hovertemplate='<b>%{text}</b><br>Revenu: %{x:,.0f} FCFA<br>Dépenses: %{y:,.0f} FCFA<extra></extra>',
            text=[banque] * len(data_banque)
        ))
    
    fig_scatter.update_layout(
        height=350,
        plot_bgcolor=BG,
        paper_bgcolor=BG,
        font=dict(color=FONT, family='Inter'),
        xaxis=dict(
            title='Revenu (FCFA)',
            gridcolor=GRID,
            color='#7A8B94',
            title_font=dict(size=10)
        ),
        yaxis=dict(
            title='Dépenses (FCFA)',
            gridcolor=GRID,
            color='#7A8B94',
            title_font=dict(size=10)
        ),
        margin=dict(l=10, r=10, t=30, b=40),
        legend=dict(
            orientation='h',
            yanchor='bottom',
            y=1.02,
            xanchor='right',
            x=1,
            font=dict(size=9)
        )
    )
    st.plotly_chart(fig_scatter, use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)

with col_bar:
    st.markdown('<div class="glass">', unsafe_allow_html=True)
    st.markdown('<div class="section-title">Barplot — Revenus par Agence</div>', unsafe_allow_html=True)
    st.markdown('<div class="section-sub">Groupé par Banque</div>', unsafe_allow_html=True)
    
    agence_data = get_agence_grouped(df)
    
    fig_bar = go.Figure()
    for banque in agence_data.index:
        fig_bar.add_trace(go.Bar(
            x=agence_data.columns,
            y=agence_data.loc[banque],
            name=banque,
            marker_color=couleurs_banques.get(banque, '#7A8B94'),
            hovertemplate='<b>%{text}</b><br>Agence: %{x}<br>Revenu: %{y:,.0f} FCFA<extra></extra>',
            text=[banque] * len(agence_data.columns)
        ))
    
    fig_bar.update_layout(
        height=350,
        plot_bgcolor=BG,
        paper_bgcolor=BG,
        font=dict(color=FONT, family='Inter'),
        xaxis=dict(
            title='Agence',
            gridcolor=GRID,
            color='#7A8B94',
            title_font=dict(size=10)
        ),
        yaxis=dict(
            title='Revenu (FCFA)',
            gridcolor=GRID,
            color='#7A8B94',
            title_font=dict(size=10)
        ),
        margin=dict(l=10, r=10, t=30, b=40),
        barmode='group',
        legend=dict(
            orientation='h',
            yanchor='bottom',
            y=1.02,
            xanchor='right',
            x=1,
            font=dict(size=9)
        )
    )
    st.plotly_chart(fig_bar, use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)

st.markdown('<div class="divider"></div>', unsafe_allow_html=True)

# ── LIGNE 3: VIOLIN, DIVERGING VILLE ─────────────────────────────
col_violin, col_div_ville = st.columns(2)

with col_violin:
    st.markdown('<div class="glass">', unsafe_allow_html=True)
    st.markdown('<div class="section-title">Violin — Taux d\'Intérêt</div>', unsafe_allow_html=True)
    st.markdown('<div class="section-sub">Distribution par Banque</div>', unsafe_allow_html=True)
    
    violin_data = get_violin_data(df)
    
    fig_violin = go.Figure()
    for banque in violin_data['banque'].unique():
        data_banque = violin_data[violin_data['banque'] == banque]['taux_interet']
        fig_violin.add_trace(go.Violin(
            y=data_banque,
            name=banque,
            box_visible=True,
            meanline_visible=True,
            fillcolor=couleurs_banques.get(banque, '#7A8B94'),
            opacity=0.6,
            line_color=couleurs_banques.get(banque, '#7A8B94')
        ))
    
    fig_violin.update_layout(
        height=350,
        plot_bgcolor=BG,
        paper_bgcolor=BG,
        font=dict(color=FONT, family='Inter'),
        xaxis=dict(
            title='Banque',
            gridcolor=GRID,
            color='#7A8B94',
            title_font=dict(size=10)
        ),
        yaxis=dict(
            title='Taux d\'Intérêt (%)',
            gridcolor=GRID,
            color='#7A8B94',
            title_font=dict(size=10)
        ),
        margin=dict(l=10, r=10, t=30, b=40),
        showlegend=False
    )
    st.plotly_chart(fig_violin, use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)

with col_div_ville:
    st.markdown('<div class="glass">', unsafe_allow_html=True)
    st.markdown('<div class="section-title">Diverging — Performance par Ville</div>', unsafe_allow_html=True)
    st.markdown('<div class="section-sub">Écart à la moyenne (FCFA)</div>', unsafe_allow_html=True)
    
    ecarts_ville = get_diverging_ville(df)
    couleurs_ville = ['#E74C3C' if v < 0 else '#2ECC9A' for v in ecarts_ville.values]
    
    fig_div_ville = go.Figure(go.Bar(
        y=ecarts_ville.index,
        x=ecarts_ville.values,
        orientation='h',
        marker_color=couleurs_ville,
        text=[f"{v:+,.0f}" for v in ecarts_ville.values],
        textposition='outside',
        textfont=dict(color=FONT, size=11),
        hovertemplate='<b>%{y}</b><br>Écart: %{x:,.0f} FCFA<extra></extra>'
    ))
    fig_div_ville.add_vline(x=0, line_color='rgba(255,255,255,0.15)', line_dash='dash')
    fig_div_ville.update_layout(
        height=350,
        plot_bgcolor=BG,
        paper_bgcolor=BG,
        font=dict(color=FONT, family='Inter'),
        xaxis=dict(
            gridcolor=GRID,
            color='#3A5568',
            zeroline=False,
            title_font=dict(size=10)
        ),
        yaxis=dict(
            gridcolor=GRID,
            color=FONT,
            title_font=dict(size=10)
        ),
        margin=dict(l=10, r=90, t=10, b=30),
        showlegend=False
    )
    st.plotly_chart(fig_div_ville, use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)

st.markdown('<div class="divider"></div>', unsafe_allow_html=True)

# ── DOT PLOT COMPARATIF ───────────────────────────────────────────
st.markdown('<div class="glass">', unsafe_allow_html=True)
st.markdown('<div class="section-title">Dot Plot Comparatif — 4 Villes</div>', unsafe_allow_html=True)
st.markdown('<div class="section-sub">Revenu par Banque dans les villes principales</div>', unsafe_allow_html=True)

dot_comparatif = get_dotplot_comparatif(df)
villes = list(dot_comparatif.keys())

fig_dot_comp = go.Figure()
for ville in villes:
    for banque in dot_comparatif[ville].index:
        valeur = dot_comparatif[ville][banque]
        fig_dot_comp.add_trace(go.Scatter(
            x=[villes.index(ville)],
            y=[banque],
            mode='markers',
            marker=dict(
                size=valeur / dot_comparatif[ville].max() * 30 + 10,
                color=couleurs_banques.get(banque, '#7A8B94'),
                line=dict(color='rgba(255,255,255,0.3)', width=2)
            ),
            name=f"{banque} - {ville}",
            hovertemplate=f'<b>{banque}</b><br>Ville: {ville}<br>Revenu: {valeur:,.0f} FCFA<extra></extra>',
            showlegend=False
        ))

fig_dot_comp.update_layout(
    height=300,
    plot_bgcolor=BG,
    paper_bgcolor=BG,
    font=dict(color=FONT, family='Inter'),
    xaxis=dict(
        title='Ville',
        gridcolor=GRID,
        color='#7A8B94',
        tickmode='array',
        tickvals=list(range(len(villes))),
        ticktext=villes,
        title_font=dict(size=10)
    ),
    yaxis=dict(
        title='Banque',
        gridcolor=GRID,
        color=FONT,
        title_font=dict(size=10)
    ),
    margin=dict(l=10, r=10, t=30, b=40),
    showlegend=False
)
st.plotly_chart(fig_dot_comp, use_container_width=True)
st.markdown('</div>', unsafe_allow_html=True)

st.markdown('<div class="divider"></div>', unsafe_allow_html=True)

# ── DATAFRAME AVEC COULEURS DE CHALEUR ───────────────────────────
st.markdown('<div class="glass">', unsafe_allow_html=True)
st.markdown('<div class="section-title">Données Détaillées</div>', unsafe_allow_html=True)
st.markdown('<div class="section-sub">Tableau avec dégradé de couleurs</div>', unsafe_allow_html=True)

# Afficher le DataFrame original avec les colonnes du CSV
df_display = df[['bilan_financier', 'actifs', 'revenu', 'depenses', 
                 'taux_interet', 'flux_tresorerie', 'capital', 
                 'agence', 'banque', 'lieu']].copy()

# Renommer les colonnes pour l'affichage
df_display.columns = ['Bilan Financier', 'Actifs', 'Revenu', 'Dépenses', 
                      'Taux Intérêt', 'Flux Trésorerie', 'Capital', 
                      'Agence', 'Banque', 'Ville']

# Appliquer un dégradé de couleurs sur les colonnes numériques (une seule couleur)
styled_df = df_display.style.background_gradient(cmap='GnBu', subset=['Revenu', 'Dépenses', 'Capital', 'Actifs', 'Bilan Financier', 'Flux Trésorerie'])
styled_df = styled_df.background_gradient(cmap='GnBu', subset=['Taux Intérêt'])

st.dataframe(styled_df, use_container_width=True, hide_index=True)
st.markdown('</div>', unsafe_allow_html=True)

st.markdown('<div class="divider"></div>', unsafe_allow_html=True)

# ── INSIGHT ───────────────────────────────────────────────────
st.markdown(f"""
<div class="insight-card">
    <div style='display:flex; gap:1rem; align-items:flex-start;'>
        <div style='font-size:1.8rem;'>💡</div>
        <div>
            <div style='font-family:Syne,sans-serif; color:#F39C12;
            font-weight:700; font-size:1rem; margin-bottom:0.5rem;'>
                Insight Stratégique
            </div>
            <p style='color:#7A8B94; font-size:0.8rem; line-height:1.8; margin:0;'>
                <span style='color:#E8E8E8; font-weight:600;'>SG</span>
                affiche une sous-performance par rapport à la moyenne sectorielle,
                mais domine l'<span style='color:#2ECC9A; font-weight:600;'>
                Agence Nord de Bafoussam</span> là où
                <span style='color:#E8E8E8; font-weight:600;'>UBA</span>
                enregistre sa plus grande faiblesse territoriale.
                Recommandation : consolidation régionale ciblée sur les zones de force.
            </p>
        </div>
    </div>
    <div style='height:1px; background:linear-gradient(to right,#F39C12,transparent);
    margin-top:1.2rem; border-radius:2px;'></div>
</div>
""", unsafe_allow_html=True)

# ── FOOTER ────────────────────────────────────────────────────
st.markdown("""
<div class="footer">
    FinCam Analytics © 2026 &nbsp;|&nbsp; Cameroon Banking Intelligence Platform
    &nbsp;|&nbsp; Powered by Python & Streamlit
</div>
""", unsafe_allow_html=True)