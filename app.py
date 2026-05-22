import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import pandas as pd

# ── PAGE CONFIG ───────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="CORE/CG · Dashboard Regulação",
    page_icon="🏥",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── THEME COLORS ──────────────────────────────────────────────────────────────
NAVY   = "#1e2d45"
BLUE   = "#2563eb"
AMBER  = "#f59e0b"
GREEN  = "#10b981"
RED    = "#ef4444"
GRAY   = "#64748b"

# ── CUSTOM CSS ────────────────────────────────────────────────────────────────
st.markdown("""
<style>
/* Sidebar */
[data-testid="stSidebar"] {
    background-color: #1e2d45;
}
[data-testid="stSidebar"] * {
    color: #e2e8f0 !important;
}
[data-testid="stSidebar"] .stSelectbox label,
[data-testid="stSidebar"] .stMultiSelect label,
[data-testid="stSidebar"] h1, h2, h3 {
    color: #93c5fd !important;
    font-weight: 600;
}
/* KPI cards */
.kpi-card {
    background: white;
    border-radius: 10px;
    padding: 18px 22px;
    border-left: 5px solid #2563eb;
    box-shadow: 0 1px 4px rgba(0,0,0,0.08);
    margin-bottom: 4px;
}
.kpi-label  { font-size: 12px; color: #64748b; font-weight: 600; text-transform: uppercase; letter-spacing: .5px; margin-bottom: 4px; }
.kpi-value  { font-size: 28px; font-weight: 700; color: #1e2d45; line-height: 1.1; }
.kpi-delta  { font-size: 12px; margin-top: 4px; font-weight: 600; }
.kpi-up     { color: #10b981; }
.kpi-down   { color: #ef4444; }
.kpi-neutral{ color: #f59e0b; }
.section-header {
    font-size: 15px; font-weight: 700; color: #1e2d45;
    padding: 6px 12px; background: #dbeafe;
    border-radius: 6px; margin: 18px 0 10px 0;
    border-left: 4px solid #2563eb;
}
div[data-testid="stMetricValue"] { font-size: 28px !important; }
</style>
""", unsafe_allow_html=True)

# ════════════════════════════════════════════════════════════════════════════
# DATA
# ════════════════════════════════════════════════════════════════════════════
@st.cache_data
def load_data():
    # ── Mensal ────────────────────────────────────────────────────────────
    mensal = pd.DataFrame([
        {"Ano":2025,"Mes":"Janeiro",  "Num":1,"Encaminhamentos":3700,"Tempo_Med_Min":651},
        {"Ano":2025,"Mes":"Fevereiro","Num":2,"Encaminhamentos":3441,"Tempo_Med_Min":688},
        {"Ano":2025,"Mes":"Março",    "Num":3,"Encaminhamentos":3700,"Tempo_Med_Min":771},
        {"Ano":2025,"Mes":"Abril",    "Num":4,"Encaminhamentos":3549,"Tempo_Med_Min":983},
        {"Ano":2025,"Mes":"Maio*",    "Num":5,"Encaminhamentos":2299,"Tempo_Med_Min":962},
        {"Ano":2026,"Mes":"Janeiro",  "Num":1,"Encaminhamentos":4535,"Tempo_Med_Min":719},
        {"Ano":2026,"Mes":"Fevereiro","Num":2,"Encaminhamentos":4120,"Tempo_Med_Min":685},
        {"Ano":2026,"Mes":"Março",    "Num":3,"Encaminhamentos":4718,"Tempo_Med_Min":698},
        {"Ano":2026,"Mes":"Abril",    "Num":4,"Encaminhamentos":4834,"Tempo_Med_Min":785},
        {"Ano":2026,"Mes":"Maio*",    "Num":5,"Encaminhamentos":3002,"Tempo_Med_Min":683},
    ])
    mensal["Tempo_Med_Horas"] = mensal["Tempo_Med_Min"] / 60

    # ── Faixa etária ──────────────────────────────────────────────────────
    faixa = pd.DataFrame([
        {"Faixa":"0–11 anos","Grupo":"Criança",     "Ano":2025,"Qtd":2043},
        {"Faixa":"12–17 anos","Grupo":"Adolescente","Ano":2025,"Qtd":716},
        {"Faixa":"18–59 anos","Grupo":"Adulto",     "Ano":2025,"Qtd":8924},
        {"Faixa":"60+ anos",  "Grupo":"Idoso",      "Ano":2025,"Qtd":5006},
        {"Faixa":"0–11 anos", "Grupo":"Criança",    "Ano":2026,"Qtd":2480},
        {"Faixa":"12–17 anos","Grupo":"Adolescente","Ano":2026,"Qtd":1138},
        {"Faixa":"18–59 anos","Grupo":"Adulto",     "Ano":2026,"Qtd":11463},
        {"Faixa":"60+ anos",  "Grupo":"Idoso",      "Ano":2026,"Qtd":5749},
    ])

    # ── Tempo de permanência ──────────────────────────────────────────────
    tempo = pd.DataFrame([
        {"Faixa":"< 1h",    "Horas_Max":1,  "Ano":2025,"Qtd":3639,"Classif":"Rápido"},
        {"Faixa":"1–2h",    "Horas_Max":2,  "Ano":2025,"Qtd":2504,"Classif":"Rápido"},
        {"Faixa":"2–4h",    "Horas_Max":4,  "Ano":2025,"Qtd":2122,"Classif":"Adequado"},
        {"Faixa":"4–8h",    "Horas_Max":8,  "Ano":2025,"Qtd":2047,"Classif":"Moderado"},
        {"Faixa":"8–24h",   "Horas_Max":24, "Ano":2025,"Qtd":4001,"Classif":"Prolongado"},
        {"Faixa":"> 24h",   "Horas_Max":999,"Ano":2025,"Qtd":2000,"Classif":"Crítico"},
        {"Faixa":"< 1h",    "Horas_Max":1,  "Ano":2026,"Qtd":4465,"Classif":"Rápido"},
        {"Faixa":"1–2h",    "Horas_Max":2,  "Ano":2026,"Qtd":3531,"Classif":"Rápido"},
        {"Faixa":"2–4h",    "Horas_Max":4,  "Ano":2026,"Qtd":3159,"Classif":"Adequado"},
        {"Faixa":"4–8h",    "Horas_Max":8,  "Ano":2026,"Qtd":2693,"Classif":"Moderado"},
        {"Faixa":"8–24h",   "Horas_Max":24, "Ano":2026,"Qtd":4854,"Classif":"Prolongado"},
        {"Faixa":"> 24h",   "Horas_Max":999,"Ano":2026,"Qtd":2230,"Classif":"Crítico"},
    ])

    # ── CIDs ──────────────────────────────────────────────────────────────
    cids = pd.DataFrame([
        {"CID":"R100","Diagnostico":"Abdome agudo",            "Especialidade":"Cirurgia Geral","Ano":2025,"Qtd":387},
        {"CID":"J189","Diagnostico":"Pneumonia",               "Especialidade":"Clínica Médica","Ano":2025,"Qtd":524},
        {"CID":"I64", "Diagnostico":"AVC",                    "Especialidade":"Neurologia",     "Ano":2025,"Qtd":379},
        {"CID":"I219","Diagnostico":"IAM",                    "Especialidade":"Cardiologia",    "Ano":2025,"Qtd":412},
        {"CID":"K359","Diagnostico":"Apendicite aguda",        "Especialidade":"Cirurgia Geral","Ano":2025,"Qtd":334},
        {"CID":"S099","Diagnostico":"Traumatismo da cabeça",   "Especialidade":"Neurocirurgia", "Ano":2025,"Qtd":341},
        {"CID":"S525","Diagnostico":"Fratura rádio distal",    "Especialidade":"Ortopedia",     "Ano":2025,"Qtd":279},
        {"CID":"S626","Diagnostico":"Fratura de dedos",        "Especialidade":"Ortopedia",     "Ano":2025,"Qtd":147},
        {"CID":"S069","Diagnostico":"Traum. intracraniano",    "Especialidade":"Neurocirurgia", "Ano":2025,"Qtd":235},
        {"CID":"R074","Diagnostico":"Dor torácica",            "Especialidade":"Cardiologia",   "Ano":2025,"Qtd":84},
        {"CID":"T150","Diagnostico":"Corp. estr. córnea",      "Especialidade":"Oftalmologia",  "Ano":2025,"Qtd":207},
        {"CID":"S430","Diagnostico":"Luxação ombro",           "Especialidade":"Ortopedia",     "Ano":2025,"Qtd":163},
        {"CID":"N390","Diagnostico":"ITU",                    "Especialidade":"Clínica Médica","Ano":2025,"Qtd":175},
        {"CID":"J180","Diagnostico":"Broncopneumonia",         "Especialidade":"Clínica Médica","Ano":2025,"Qtd":152},
        {"CID":"F192","Diagnostico":"Transt. por drogas",      "Especialidade":"Psiquiatria",   "Ano":2025,"Qtd":174},
        {"CID":"A419","Diagnostico":"Septicemia",              "Especialidade":"Clínica Médica","Ano":2025,"Qtd":143},
        {"CID":"S420","Diagnostico":"Fratura clavícula",       "Especialidade":"Ortopedia",     "Ano":2025,"Qtd":98},
        {"CID":"T159","Diagnostico":"Corp. estr. olho",        "Especialidade":"Oftalmologia",  "Ano":2025,"Qtd":168},
        {"CID":"I200","Diagnostico":"Angina instável",         "Especialidade":"Cardiologia",   "Ano":2025,"Qtd":128},
        {"CID":"S925","Diagnostico":"Fratura artelho",         "Especialidade":"Ortopedia",     "Ano":2025,"Qtd":50},
        {"CID":"R100","Diagnostico":"Abdome agudo",            "Especialidade":"Cirurgia Geral","Ano":2026,"Qtd":462},
        {"CID":"J189","Diagnostico":"Pneumonia",               "Especialidade":"Clínica Médica","Ano":2026,"Qtd":311},
        {"CID":"I64", "Diagnostico":"AVC",                    "Especialidade":"Neurologia",     "Ano":2026,"Qtd":416},
        {"CID":"I219","Diagnostico":"IAM",                    "Especialidade":"Cardiologia",    "Ano":2026,"Qtd":299},
        {"CID":"K359","Diagnostico":"Apendicite aguda",        "Especialidade":"Cirurgia Geral","Ano":2026,"Qtd":361},
        {"CID":"S099","Diagnostico":"Traumatismo da cabeça",   "Especialidade":"Neurocirurgia", "Ano":2026,"Qtd":270},
        {"CID":"S525","Diagnostico":"Fratura rádio distal",    "Especialidade":"Ortopedia",     "Ano":2026,"Qtd":323},
        {"CID":"S626","Diagnostico":"Fratura de dedos",        "Especialidade":"Ortopedia",     "Ano":2026,"Qtd":379},
        {"CID":"S069","Diagnostico":"Traum. intracraniano",    "Especialidade":"Neurocirurgia", "Ano":2026,"Qtd":258},
        {"CID":"R074","Diagnostico":"Dor torácica",            "Especialidade":"Cardiologia",   "Ano":2026,"Qtd":368},
        {"CID":"T150","Diagnostico":"Corp. estr. córnea",      "Especialidade":"Oftalmologia",  "Ano":2026,"Qtd":237},
        {"CID":"S430","Diagnostico":"Luxação ombro",           "Especialidade":"Ortopedia",     "Ano":2026,"Qtd":226},
        {"CID":"N390","Diagnostico":"ITU",                    "Especialidade":"Clínica Médica","Ano":2026,"Qtd":189},
        {"CID":"J180","Diagnostico":"Broncopneumonia",         "Especialidade":"Clínica Médica","Ano":2026,"Qtd":187},
        {"CID":"F192","Diagnostico":"Transt. por drogas",      "Especialidade":"Psiquiatria",   "Ano":2026,"Qtd":164},
        {"CID":"A419","Diagnostico":"Septicemia",              "Especialidade":"Clínica Médica","Ano":2026,"Qtd":170},
        {"CID":"S420","Diagnostico":"Fratura clavícula",       "Especialidade":"Ortopedia",     "Ano":2026,"Qtd":213},
        {"CID":"T159","Diagnostico":"Corp. estr. olho",        "Especialidade":"Oftalmologia",  "Ano":2026,"Qtd":133},
        {"CID":"I200","Diagnostico":"Angina instável",         "Especialidade":"Cardiologia",   "Ano":2026,"Qtd":168},
        {"CID":"S925","Diagnostico":"Fratura artelho",         "Especialidade":"Ortopedia",     "Ano":2026,"Qtd":243},
    ])

    return mensal, faixa, tempo, cids

mensal_df, faixa_df, tempo_df, cids_df = load_data()

# ════════════════════════════════════════════════════════════════════════════
# SIDEBAR — FILTROS
# ════════════════════════════════════════════════════════════════════════════
with st.sidebar:
    st.markdown("## 🏥 CORE/CG")
    st.markdown("**Rede de Urgência e Emergência**  \nCampo Grande · MS")
    st.markdown("---")

    st.markdown("### Filtros")

    anos = st.multiselect(
        "Ano",
        options=[2025, 2026],
        default=[2025, 2026],
    )

    meses_disp = ["Janeiro","Fevereiro","Março","Abril","Maio*"]
    meses_sel = st.multiselect(
        "Mês",
        options=meses_disp,
        default=meses_disp,
    )

    especialidades_disp = sorted(cids_df["Especialidade"].unique().tolist())
    esp_sel = st.multiselect(
        "Especialidade (CIDs)",
        options=especialidades_disp,
        default=especialidades_disp,
    )

    top_n = st.slider("Top N diagnósticos", min_value=5, max_value=20, value=10, step=1)

    st.markdown("---")
    st.markdown("### Comparativo rápido")
    metrica = st.radio(
        "Métrica principal",
        ["Encaminhamentos", "Tempo médio (min)"],
        index=0,
    )

    st.markdown("---")
    st.caption("*Maio/2026: dados parciais até 20/05/2026")
    st.caption("Fonte: CORE/CG · Sistema de Regulação")

# ── aplicar filtros ───────────────────────────────────────────────────────────
if not anos:
    anos = [2025, 2026]

mensal_f = mensal_df[
    mensal_df["Ano"].isin(anos) &
    mensal_df["Mes"].isin(meses_sel)
]
faixa_f = faixa_df[faixa_df["Ano"].isin(anos)]
tempo_f  = tempo_df[tempo_df["Ano"].isin(anos)]
cids_f   = cids_df[
    cids_df["Ano"].isin(anos) &
    cids_df["Especialidade"].isin(esp_sel)
]

# ════════════════════════════════════════════════════════════════════════════
# HEADER
# ════════════════════════════════════════════════════════════════════════════
col_logo, col_title = st.columns([1, 9])
with col_title:
    st.markdown(
        "<h1 style='margin:0;color:#1e2d45;font-size:24px;font-weight:700'>"
        "CORE/CG — Painel de Encaminhamentos · Jan–Mai 2025 vs 2026</h1>",
        unsafe_allow_html=True,
    )
    st.markdown(
        "<p style='color:#64748b;font-size:13px;margin-top:2px'>"
        "Central de Regulação de Ofertas de Serviços de Saúde · Campo Grande/MS</p>",
        unsafe_allow_html=True,
    )

st.divider()

# ════════════════════════════════════════════════════════════════════════════
# KPI CARDS
# ════════════════════════════════════════════════════════════════════════════
anos_selecionados = sorted(anos)

def safe_total(df, ano_val, col):
    sub = df[df["Ano"] == ano_val]
    return sub[col].sum() if len(sub) > 0 else 0

def kpi_card(label, value, delta_text, delta_type="up", color=BLUE):
    delta_class = {"up": "kpi-up", "down": "kpi-down", "neutral": "kpi-neutral"}[delta_type]
    return f"""
    <div class="kpi-card" style="border-left-color:{color}">
        <div class="kpi-label">{label}</div>
        <div class="kpi-value">{value}</div>
        <div class="kpi-delta {delta_class}">{delta_text}</div>
    </div>
    """

k1, k2, k3, k4, k5 = st.columns(5)

with k1:
    t25 = safe_total(mensal_f, 2025, "Encaminhamentos")
    t26 = safe_total(mensal_f, 2026, "Encaminhamentos")
    if 2025 in anos and 2026 in anos and t25 > 0:
        pct = (t26 - t25) / t25 * 100
        delta = f"▲ {pct:.1f}% vs 2025"
        dt = "up"
    else:
        delta = "—"
        dt = "neutral"
    total_show = f"{t26:,}".replace(",",".") if 2026 in anos else f"{t25:,}".replace(",",".")
    st.markdown(kpi_card("Total encaminhamentos", total_show, delta, dt, BLUE),
                unsafe_allow_html=True)

with k2:
    m26 = mensal_df[mensal_df["Ano"]==2026]["Tempo_Med_Min"].mean() if 2026 in anos else None
    m25 = mensal_df[mensal_df["Ano"]==2025]["Tempo_Med_Min"].mean() if 2025 in anos else None
    val = m26 if m26 else m25
    h, mn = int(val)//60, int(val)%60
    if m25 and m26:
        pct = (m26 - m25) / m25 * 100
        delta = f"{'▼' if pct<0 else '▲'} {abs(pct):.1f}% vs 2025"
        dt = "up" if pct < 0 else "down"
    else:
        delta = "—"
        dt = "neutral"
    st.markdown(kpi_card("Tempo médio de espera", f"{h}h {mn:02d}min", delta, dt, AMBER),
                unsafe_allow_html=True)

with k3:
    acima_25 = 2000
    acima_26 = 2230
    pct_25 = 12.3
    pct_26 = 10.7
    if 2026 in anos:
        st.markdown(kpi_card("Acima de 24h (2026)", f"{acima_26:,}".replace(",","."),
                              f"▼ {pct_25-pct_26:.1f} p.p. · era {pct_25}%", "up", GREEN),
                    unsafe_allow_html=True)
    else:
        st.markdown(kpi_card("Acima de 24h (2025)", f"{acima_25:,}".replace(",","."),
                              f"{pct_25}% do total", "neutral", GRAY),
                    unsafe_allow_html=True)

with k4:
    best_mes = mensal_df[mensal_df["Ano"].isin(anos)].groupby("Mes")["Encaminhamentos"].sum().idxmax() if not mensal_f.empty else "—"
    best_val = mensal_df[mensal_df["Ano"].isin(anos)].groupby("Mes")["Encaminhamentos"].sum().max() if not mensal_f.empty else 0
    st.markdown(kpi_card("Mês com maior volume",
                          best_mes.replace("*",""),
                          f"{best_val:,} encaminhamentos".replace(",","."),
                          "neutral", "#8b5cf6"),
                unsafe_allow_html=True)

with k5:
    top_cid = cids_f.groupby(["CID","Diagnostico"])["Qtd"].sum().reset_index().sort_values("Qtd", ascending=False)
    if not top_cid.empty:
        tc = top_cid.iloc[0]
        st.markdown(kpi_card("CID mais frequente", tc["CID"],
                              f"{tc['Diagnostico']} · {int(tc['Qtd']):,} casos".replace(",","."),
                              "neutral", RED),
                    unsafe_allow_html=True)

st.markdown("<div style='margin-top:12px'></div>", unsafe_allow_html=True)

# ════════════════════════════════════════════════════════════════════════════
# LINHA 1 — Evolução mensal + Tempo médio
# ════════════════════════════════════════════════════════════════════════════
st.markdown("<div class='section-header'>📅 Evolução Mensal</div>", unsafe_allow_html=True)
c1, c2 = st.columns(2)

with c1:
    color_map = {2025: GRAY, 2026: BLUE}
    fig_bar = go.Figure()
    ordem_meses = ["Janeiro","Fevereiro","Março","Abril","Maio*"]
    mensal_sorted = mensal_f.copy()
    mensal_sorted["Mes_Ord"] = mensal_sorted["Mes"].apply(
        lambda x: ordem_meses.index(x) if x in ordem_meses else 99)
    mensal_sorted = mensal_sorted.sort_values("Mes_Ord")

    for ano in sorted(anos):
        d = mensal_sorted[mensal_sorted["Ano"]==ano]
        fig_bar.add_trace(go.Bar(
            x=d["Mes"].str.replace("*","", regex=False),
            y=d["Encaminhamentos"],
            name=str(ano),
            marker_color=color_map.get(ano, GRAY),
            text=d["Encaminhamentos"].apply(lambda v: f"{v:,}".replace(",",".")),
            textposition="outside",
            textfont=dict(size=10),
        ))
    fig_bar.update_layout(
        title="Encaminhamentos por mês",
        barmode="group",
        plot_bgcolor="white",
        paper_bgcolor="white",
        legend=dict(orientation="h", y=1.12, x=0),
        margin=dict(t=60, b=30, l=10, r=10),
        yaxis=dict(gridcolor="#f0f2f5", title=""),
        xaxis=dict(title=""),
        font=dict(family="Arial", size=12),
        height=320,
    )
    st.plotly_chart(fig_bar, use_container_width=True)

with c2:
    fig_line = go.Figure()
    for ano in sorted(anos):
        d = mensal_f[mensal_f["Ano"]==ano].copy()
        d["Mes_Ord"] = d["Mes"].apply(lambda x: ordem_meses.index(x) if x in ordem_meses else 99)
        d = d.sort_values("Mes_Ord")
        horas = (d["Tempo_Med_Min"] / 60).round(2)
        labels = d["Tempo_Med_Min"].apply(
            lambda v: f"{int(v)//60}h {int(v)%60:02d}min")
        fig_line.add_trace(go.Scatter(
            x=d["Mes"].str.replace("*","", regex=False),
            y=horas,
            mode="lines+markers+text",
            name=str(ano),
            line=dict(color=color_map.get(ano, GRAY), width=2.5),
            marker=dict(size=8),
            text=labels,
            textposition="top center",
            textfont=dict(size=9),
        ))
    fig_line.update_layout(
        title="Tempo médio de espera por mês",
        plot_bgcolor="white",
        paper_bgcolor="white",
        legend=dict(orientation="h", y=1.12, x=0),
        margin=dict(t=60, b=30, l=10, r=10),
        yaxis=dict(gridcolor="#f0f2f5", title="horas"),
        xaxis=dict(title=""),
        font=dict(family="Arial", size=12),
        height=320,
    )
    st.plotly_chart(fig_line, use_container_width=True)

# ════════════════════════════════════════════════════════════════════════════
# LINHA 2 — Top CIDs + Especialidades
# ════════════════════════════════════════════════════════════════════════════
st.markdown("<div class='section-header'>🏥 Diagnósticos (CIDs)</div>", unsafe_allow_html=True)
c3, c4 = st.columns([3, 2])

with c3:
    cid_agg = cids_f.groupby(["CID","Diagnostico"])["Qtd"].sum().reset_index()
    cid_agg = cid_agg.sort_values("Qtd", ascending=True).tail(top_n)

    fig_cid = go.Figure(go.Bar(
        x=cid_agg["Qtd"],
        y=cid_agg["CID"] + " · " + cid_agg["Diagnostico"],
        orientation="h",
        marker=dict(
            color=cid_agg["Qtd"],
            colorscale=[[0, "#dbeafe"], [1, BLUE]],
        ),
        text=cid_agg["Qtd"].apply(lambda v: f"{v:,}".replace(",",".")),
        textposition="outside",
    ))
    fig_cid.update_layout(
        title=f"Top {top_n} CIDs — volume combinado",
        plot_bgcolor="white",
        paper_bgcolor="white",
        margin=dict(t=50, b=20, l=10, r=60),
        xaxis=dict(gridcolor="#f0f2f5", title=""),
        yaxis=dict(title="", tickfont=dict(size=11)),
        font=dict(family="Arial", size=11),
        height=max(320, top_n * 34),
    )
    st.plotly_chart(fig_cid, use_container_width=True)

with c4:
    esp_agg = cids_f.groupby("Especialidade")["Qtd"].sum().reset_index().sort_values("Qtd", ascending=False)
    palette = [BLUE, AMBER, GREEN, RED, "#8b5cf6", "#ec4899", "#14b8a6", GRAY]
    colors  = (palette * 4)[:len(esp_agg)]

    fig_pizza = go.Figure(go.Pie(
        labels=esp_agg["Especialidade"],
        values=esp_agg["Qtd"],
        hole=0.45,
        marker=dict(colors=colors),
        textinfo="label+percent",
        textfont=dict(size=11),
        hovertemplate="%{label}<br>%{value:,} casos<br>%{percent}<extra></extra>",
    ))
    fig_pizza.update_layout(
        title="Volume por especialidade",
        plot_bgcolor="white",
        paper_bgcolor="white",
        margin=dict(t=50, b=20, l=10, r=10),
        legend=dict(orientation="v", font=dict(size=10)),
        font=dict(family="Arial"),
        height=max(320, top_n * 34),
        annotations=[dict(text="CIDs", x=0.5, y=0.5,
                          font=dict(size=14, color=NAVY), showarrow=False)],
    )
    st.plotly_chart(fig_pizza, use_container_width=True)

# ════════════════════════════════════════════════════════════════════════════
# LINHA 3 — Faixa etária + Tempo de permanência
# ════════════════════════════════════════════════════════════════════════════
st.markdown("<div class='section-header'>👥 Perfil dos Pacientes</div>", unsafe_allow_html=True)
c5, c6 = st.columns(2)

with c5:
    faixa_piv = faixa_f.pivot_table(index="Faixa", columns="Ano", values="Qtd", aggfunc="sum").reset_index()
    faixa_order = ["0–11 anos","12–17 anos","18–59 anos","60+ anos"]
    faixa_piv["_ord"] = faixa_piv["Faixa"].apply(lambda x: faixa_order.index(x) if x in faixa_order else 99)
    faixa_piv = faixa_piv.sort_values("_ord")

    fig_fx = go.Figure()
    for ano in sorted(anos):
        if ano in faixa_piv.columns:
            fig_fx.add_trace(go.Bar(
                name=str(ano),
                x=faixa_piv["Faixa"],
                y=faixa_piv[ano],
                marker_color=color_map.get(ano, GRAY),
                text=faixa_piv[ano].apply(lambda v: f"{int(v):,}".replace(",",".")),
                textposition="outside",
                textfont=dict(size=10),
            ))
    fig_fx.update_layout(
        title="Encaminhamentos por faixa etária",
        barmode="group",
        plot_bgcolor="white",
        paper_bgcolor="white",
        legend=dict(orientation="h", y=1.12, x=0),
        margin=dict(t=60, b=30, l=10, r=10),
        yaxis=dict(gridcolor="#f0f2f5", title=""),
        font=dict(family="Arial", size=12),
        height=320,
    )
    st.plotly_chart(fig_fx, use_container_width=True)

with c6:
    tempo_order = ["< 1h","1–2h","2–4h","4–8h","8–24h","> 24h"]
    tempo_f2 = tempo_f.copy()
    tempo_f2["_ord"] = tempo_f2["Faixa"].apply(lambda x: tempo_order.index(x) if x in tempo_order else 99)
    tempo_f2 = tempo_f2.sort_values("_ord")

    classif_colors = {
        "Rápido":     GREEN,
        "Adequado":   BLUE,
        "Moderado":   AMBER,
        "Prolongado": "#f97316",
        "Crítico":    RED,
    }

    fig_tempo = go.Figure()
    for ano in sorted(anos):
        d = tempo_f2[tempo_f2["Ano"]==ano]
        fig_tempo.add_trace(go.Bar(
            name=str(ano),
            x=d["Faixa"],
            y=d["Qtd"],
            marker_color=color_map.get(ano, GRAY),
            text=d["Qtd"].apply(lambda v: f"{v:,}".replace(",",".")),
            textposition="outside",
            textfont=dict(size=10),
        ))
    fig_tempo.update_layout(
        title="Distribuição do tempo de permanência",
        barmode="group",
        plot_bgcolor="white",
        paper_bgcolor="white",
        legend=dict(orientation="h", y=1.12, x=0),
        margin=dict(t=60, b=30, l=10, r=10),
        yaxis=dict(gridcolor="#f0f2f5", title=""),
        font=dict(family="Arial", size=12),
        height=320,
    )
    st.plotly_chart(fig_tempo, use_container_width=True)

# ════════════════════════════════════════════════════════════════════════════
# LINHA 4 — Variação CIDs (scatter / waterfall)
# ════════════════════════════════════════════════════════════════════════════
st.markdown("<div class='section-header'>📊 Análise de Variação 2025 → 2026</div>",
            unsafe_allow_html=True)

if 2025 in anos and 2026 in anos:
    cid_25 = cids_df[cids_df["Ano"]==2025][["CID","Diagnostico","Especialidade","Qtd"]].rename(columns={"Qtd":"Qtd_2025"})
    cid_26 = cids_df[cids_df["Ano"]==2026][["CID","Diagnostico","Especialidade","Qtd"]].rename(columns={"Qtd":"Qtd_2026"})
    cid_merge = cid_25.merge(cid_26, on=["CID","Diagnostico","Especialidade"])
    cid_merge = cid_merge[cid_merge["Especialidade"].isin(esp_sel)]
    cid_merge["Variacao"] = cid_merge["Qtd_2026"] - cid_merge["Qtd_2025"]
    cid_merge["Var_Pct"]  = ((cid_merge["Qtd_2026"] - cid_merge["Qtd_2025"]) / cid_merge["Qtd_2025"] * 100).round(1)
    cid_merge["Total"]    = cid_merge["Qtd_2025"] + cid_merge["Qtd_2026"]
    cid_merge = cid_merge.sort_values("Variacao")

    cv1, cv2 = st.columns(2)

    with cv1:
        fig_var = go.Figure(go.Bar(
            x=cid_merge["CID"],
            y=cid_merge["Variacao"],
            marker_color=[GREEN if v >= 0 else RED for v in cid_merge["Variacao"]],
            text=cid_merge["Variacao"].apply(lambda v: f"+{v}" if v >= 0 else str(v)),
            textposition="outside",
            textfont=dict(size=9),
            hovertemplate="<b>%{x}</b><br>%{customdata}<br>Variação: %{y:+d}<extra></extra>",
            customdata=cid_merge["Diagnostico"],
        ))
        fig_var.add_hline(y=0, line_dash="dash", line_color=GRAY, line_width=1)
        fig_var.update_layout(
            title="Variação absoluta por CID (2025 → 2026)",
            plot_bgcolor="white",
            paper_bgcolor="white",
            margin=dict(t=50, b=40, l=10, r=10),
            yaxis=dict(gridcolor="#f0f2f5", title="Δ casos"),
            xaxis=dict(title="", tickangle=-45),
            font=dict(family="Arial", size=11),
            height=340,
        )
        st.plotly_chart(fig_var, use_container_width=True)

    with cv2:
        fig_sc = px.scatter(
            cid_merge,
            x="Qtd_2025", y="Qtd_2026",
            size="Total",
            color="Especialidade",
            hover_name="Diagnostico",
            hover_data={"Var_Pct": True, "Total": False},
            color_discrete_sequence=px.colors.qualitative.Bold,
            labels={"Qtd_2025":"Volume 2025","Qtd_2026":"Volume 2026"},
            title="Volume 2025 vs 2026 por CID",
        )
        max_val = max(cid_merge["Qtd_2025"].max(), cid_merge["Qtd_2026"].max()) * 1.1
        fig_sc.add_shape(type="line",
                         x0=0, y0=0, x1=max_val, y1=max_val,
                         line=dict(dash="dash", color=GRAY, width=1))
        fig_sc.update_layout(
            plot_bgcolor="white",
            paper_bgcolor="white",
            margin=dict(t=50, b=30, l=10, r=10),
            font=dict(family="Arial", size=11),
            legend=dict(font=dict(size=10)),
            height=340,
        )
        st.plotly_chart(fig_sc, use_container_width=True)

    st.caption("Na linha de referência diagonal: crescimento igual ao de 2025. Acima da linha = aceleração. Abaixo = redução.")

else:
    st.info("Selecione ambos os anos na sidebar para ver a análise de variação.", icon="ℹ️")

# ════════════════════════════════════════════════════════════════════════════
# TABELA DETALHADA
# ════════════════════════════════════════════════════════════════════════════
with st.expander("📋 Ver tabela de dados completa"):
    tab_sel = st.radio("Tabela", ["Mensal","CIDs","Faixa Etária","Tempo de Espera"],
                       horizontal=True)
    if tab_sel == "Mensal":
        df_show = mensal_f[["Ano","Mes","Encaminhamentos","Tempo_Med_Min"]].copy()
        df_show.columns = ["Ano","Mês","Encaminhamentos","Tempo Médio (min)"]
        st.dataframe(df_show, use_container_width=True, hide_index=True)
    elif tab_sel == "CIDs":
        df_show = cids_f.groupby(["CID","Diagnostico","Especialidade","Ano"])["Qtd"].sum().reset_index()
        df_show.columns = ["CID","Diagnóstico","Especialidade","Ano","Qtd"]
        st.dataframe(df_show.sort_values(["Ano","Qtd"], ascending=[True,False]),
                     use_container_width=True, hide_index=True)
    elif tab_sel == "Faixa Etária":
        st.dataframe(faixa_f, use_container_width=True, hide_index=True)
    else:
        st.dataframe(tempo_f, use_container_width=True, hide_index=True)

st.divider()
st.caption("CORE/CG · Central de Regulação de Ofertas de Serviços de Saúde · Campo Grande/MS  |  "
           "Dados: Jan–Mai 2025 (16.689 encam.) e Jan–Mai 2026 (21.209 encam.)  |  "
           "*Maio/2026 parcial até 20/05/2026")
