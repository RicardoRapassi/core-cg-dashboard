import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd

st.set_page_config(
    page_title="CORE/CG · Dashboard Regulação",
    page_icon="🏥",
    layout="wide",
    initial_sidebar_state="expanded",
)

NAVY  = "#1e2d45"
BLUE  = "#2563eb"
AMBER = "#f59e0b"
GREEN = "#10b981"
RED   = "#ef4444"
GRAY  = "#64748b"

st.markdown("""
<style>
[data-testid="stSidebar"] { background-color: #1e2d45; }
[data-testid="stSidebar"] * { color: #e2e8f0 !important; }
[data-testid="stSidebar"] .stMultiSelect span { color: #1e2d45 !important; }
.kpi-card {
    background: white; border-radius: 10px; padding: 16px 20px;
    border-left: 5px solid #2563eb; margin-bottom: 4px;
}
.kpi-label { font-size: 11px; color: #64748b; font-weight: 600;
             text-transform: uppercase; letter-spacing: .5px; margin-bottom: 4px; }
.kpi-value { font-size: 26px; font-weight: 700; color: #1e2d45; line-height: 1.1; }
.kpi-delta { font-size: 12px; margin-top: 4px; font-weight: 600; }
.kpi-up    { color: #10b981; }
.kpi-down  { color: #ef4444; }
.kpi-neu   { color: #f59e0b; }
.sec { font-size: 14px; font-weight: 700; color: #1e2d45; padding: 6px 12px;
       background: #dbeafe; border-radius: 6px; margin: 16px 0 10px 0;
       border-left: 4px solid #2563eb; }
</style>
""", unsafe_allow_html=True)

# ── DADOS ────────────────────────────────────────────────────────────────────
@st.cache_data
def load():
    df = pd.read_csv("dados.csv")
    return df

df_raw = load()

# ── SIDEBAR ──────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("## 🏥 CORE/CG")
    st.markdown("**Rede de Urgência e Emergência**  \nCampo Grande · MS")
    st.markdown("---")
    st.markdown("### Filtros")

    anos_op = sorted(df_raw["Ano"].unique().tolist())
    anos = st.multiselect("Ano", anos_op, default=anos_op)

    meses_op = ["Janeiro","Fevereiro","Março","Abril","Maio*"]
    meses = st.multiselect("Mês", meses_op, default=meses_op)

    unidades_op = sorted(df_raw["Unidade"].dropna().unique().tolist())
    unidades = st.multiselect("Unidade de origem", unidades_op, default=unidades_op)

    top_n = st.slider("Top N diagnósticos (CIDs)", 5, 20, 10)

    st.markdown("---")
    st.caption("*Maio/2026: parcial até 20/05/2026")
    st.caption("Fonte: CORE/CG · Sistema de Regulação")

# ── FILTRO PRINCIPAL ──────────────────────────────────────────────────────────
if not anos:    anos    = anos_op
if not meses:   meses   = meses_op
if not unidades: unidades = unidades_op

df = df_raw[
    df_raw["Ano"].isin(anos) &
    df_raw["Mes"].isin(meses) &
    df_raw["Unidade"].isin(unidades)
].copy()

color_map = {2025: GRAY, 2026: BLUE}
mes_order = ["Janeiro","Fevereiro","Março","Abril","Maio*"]

# ── HEADER ────────────────────────────────────────────────────────────────────
st.markdown(
    "<h1 style='margin:0;color:#1e2d45;font-size:22px;font-weight:700'>"
    "CORE/CG — Painel de Encaminhamentos · Jan–Mai 2025 vs 2026</h1>",
    unsafe_allow_html=True)
st.markdown(
    "<p style='color:#64748b;font-size:13px;margin-top:2px'>"
    "Central de Regulação de Ofertas de Serviços de Saúde · Campo Grande/MS</p>",
    unsafe_allow_html=True)
st.divider()

# ── KPIs ──────────────────────────────────────────────────────────────────────
def kpi(label, value, delta, dtype="neu", color=BLUE):
    cls = {"up":"kpi-up","down":"kpi-down","neu":"kpi-neu"}[dtype]
    return f"""<div class="kpi-card" style="border-left-color:{color}">
        <div class="kpi-label">{label}</div>
        <div class="kpi-value">{value}</div>
        <div class="kpi-delta {cls}">{delta}</div></div>"""

k1,k2,k3,k4,k5 = st.columns(5)

# total encaminhamentos
t25 = len(df[df["Ano"]==2025])
t26 = len(df[df["Ano"]==2026])
with k1:
    if t25>0 and t26>0:
        pct = (t26-t25)/t25*100
        delta = f"{'▲' if pct>=0 else '▼'} {abs(pct):.1f}% vs 2025"
        dt = "up" if pct>=0 else "down"
    else:
        delta = "—"; dt = "neu"
    total = t26 if 2026 in anos else t25
    st.markdown(kpi("Total encaminhamentos", f"{total:,}".replace(",","."), delta, dt, BLUE),
                unsafe_allow_html=True)

# tempo médio
with k2:
    m25 = df[df["Ano"]==2025]["Tempo_Min"].mean()
    m26 = df[df["Ano"]==2026]["Tempo_Min"].mean()
    ref = m26 if not pd.isna(m26) else m25
    h,mn = int(ref)//60, int(ref)%60
    if not pd.isna(m25) and not pd.isna(m26):
        pct = (m26-m25)/m25*100
        delta = f"{'▼' if pct<0 else '▲'} {abs(pct):.1f}% vs 2025"
        dt = "up" if pct<0 else "down"
    else:
        delta = "—"; dt = "neu"
    st.markdown(kpi("Tempo médio de espera", f"{h}h {mn:02d}min", delta, dt, AMBER),
                unsafe_allow_html=True)

# acima 24h
with k3:
    ac26 = len(df[(df["Ano"]==2026)&(df["Faixa_Tempo"]=="> 24h")])
    tot26 = len(df[df["Ano"]==2026])
    ac25 = len(df[(df["Ano"]==2025)&(df["Faixa_Tempo"]=="> 24h")])
    tot25 = len(df[df["Ano"]==2025])
    pct26 = ac26/tot26*100 if tot26>0 else 0
    pct25 = ac25/tot25*100 if tot25>0 else 0
    ref_n = ac26 if 2026 in anos else ac25
    ref_p = pct26 if 2026 in anos else pct25
    if tot25>0 and tot26>0:
        chg = pct26-pct25
        delta = f"{'▲' if chg>0 else '▼'} {abs(chg):.1f} p.p. vs 2025"
        dt = "down" if chg>0 else "up"
    else:
        delta = f"{ref_p:.1f}% do total"; dt = "neu"
    st.markdown(kpi("Acima de 24h", f"{ref_n:,}".replace(",","."), delta, dt, RED),
                unsafe_allow_html=True)

# mês com maior volume
with k4:
    if not df.empty:
        mes_vol = df.groupby("Mes").size()
        best_mes = mes_vol.idxmax()
        best_val = mes_vol.max()
        st.markdown(kpi("Mês com maior volume", best_mes.replace("*",""),
                         f"{best_val:,} encaminhamentos".replace(",","."), "neu", "#8b5cf6"),
                    unsafe_allow_html=True)
    else:
        st.markdown(kpi("Mês com maior volume","—","—"), unsafe_allow_html=True)

# unidade mais ativa
with k5:
    if not df.empty:
        top_u = df["Unidade"].value_counts().idxmax()
        top_u_n = df["Unidade"].value_counts().max()
        st.markdown(kpi("Unidade mais ativa", top_u.split()[-1],
                         f"{top_u_n:,} encaminhamentos".replace(",","."), "neu", GREEN),
                    unsafe_allow_html=True)
    else:
        st.markdown(kpi("Unidade mais ativa","—","—"), unsafe_allow_html=True)

st.markdown("<div style='margin-top:10px'></div>", unsafe_allow_html=True)

# ── EVOLUÇÃO MENSAL ────────────────────────────────────────────────────────────
st.markdown("<div class='sec'>📅 Evolução Mensal</div>", unsafe_allow_html=True)
c1,c2 = st.columns(2)

mensal_enc = (df.groupby(["Ano","Mes","Mes_Num"])
              .size().reset_index(name="Encaminhamentos"))
mensal_enc = mensal_enc.sort_values("Mes_Num")

mensal_tmp = (df.groupby(["Ano","Mes","Mes_Num"])["Tempo_Min"]
              .mean().reset_index())
mensal_tmp = mensal_tmp.sort_values("Mes_Num")
mensal_tmp["Horas"] = mensal_tmp["Tempo_Min"]/60

with c1:
    fig = go.Figure()
    for ano in sorted(anos):
        d = mensal_enc[mensal_enc["Ano"]==ano]
        fig.add_trace(go.Bar(
            x=d["Mes"].str.replace("*","",regex=False),
            y=d["Encaminhamentos"],
            name=str(ano),
            marker_color=color_map.get(ano,GRAY),
            text=d["Encaminhamentos"].apply(lambda v: f"{int(v):,}".replace(",",".")),
            textposition="outside", textfont=dict(size=10),
        ))
    fig.update_layout(title="Encaminhamentos por mês", barmode="group",
        plot_bgcolor="white", paper_bgcolor="white", height=320,
        legend=dict(orientation="h",y=1.12,x=0),
        margin=dict(t=55,b=25,l=10,r=10),
        yaxis=dict(gridcolor="#f0f2f5"), font=dict(family="Arial",size=11))
    st.plotly_chart(fig, use_container_width=True)

with c2:
    fig2 = go.Figure()
    for ano in sorted(anos):
        d = mansal_tmp = mensal_tmp[mensal_tmp["Ano"]==ano]
        labels = d["Tempo_Min"].apply(lambda v: f"{int(v)//60}h {int(v)%60:02d}min" if not pd.isna(v) else "")
        fig2.add_trace(go.Scatter(
            x=d["Mes"].str.replace("*","",regex=False),
            y=d["Horas"], mode="lines+markers+text",
            name=str(ano),
            line=dict(color=color_map.get(ano,GRAY),width=2.5),
            marker=dict(size=8), text=labels,
            textposition="top center", textfont=dict(size=9),
        ))
    fig2.update_layout(title="Tempo médio de espera por mês",
        plot_bgcolor="white", paper_bgcolor="white", height=320,
        legend=dict(orientation="h",y=1.12,x=0),
        margin=dict(t=55,b=25,l=10,r=10),
        yaxis=dict(gridcolor="#f0f2f5",title="horas"),
        font=dict(family="Arial",size=11))
    st.plotly_chart(fig2, use_container_width=True)

# ── UNIDADES ───────────────────────────────────────────────────────────────────
st.markdown("<div class='sec'>🏨 Volume por Unidade de Origem</div>", unsafe_allow_html=True)
cu1, cu2 = st.columns(2)

unid_agg = df.groupby(["Unidade","Ano"]).size().reset_index(name="Qtd")

with cu1:
    unid_tot = unid_agg.groupby("Unidade")["Qtd"].sum().reset_index()
    unid_tot = unid_tot.sort_values("Qtd", ascending=True)
    fig_u = go.Figure(go.Bar(
        x=unid_tot["Qtd"], y=unid_tot["Unidade"], orientation="h",
        marker=dict(color=unid_tot["Qtd"],
                    colorscale=[[0,"#dbeafe"],[1,BLUE]]),
        text=unid_tot["Qtd"].apply(lambda v: f"{v:,}".replace(",",".")),
        textposition="outside",
    ))
    fig_u.update_layout(title="Total por unidade (período selecionado)",
        plot_bgcolor="white", paper_bgcolor="white", height=380,
        margin=dict(t=50,b=20,l=10,r=60),
        xaxis=dict(gridcolor="#f0f2f5"),
        font=dict(family="Arial",size=11))
    st.plotly_chart(fig_u, use_container_width=True)

with cu2:
    if len(anos) == 2:
        unid_piv = unid_agg.pivot_table(index="Unidade", columns="Ano",
                                         values="Qtd", aggfunc="sum", fill_value=0).reset_index()
        if 2025 in unid_piv.columns and 2026 in unid_piv.columns:
            unid_piv["Var"] = unid_piv[2026] - unid_piv[2025]
            unid_piv = unid_piv.sort_values("Var")
            fig_uv = go.Figure(go.Bar(
                x=unid_piv["Var"],
                y=unid_piv["Unidade"],
                orientation="h",
                marker_color=[GREEN if v>=0 else RED for v in unid_piv["Var"]],
                text=unid_piv["Var"].apply(lambda v: f"+{v:,}".replace(",",".") if v>=0 else f"{v:,}".replace(",",".")),
                textposition="outside",
            ))
            fig_uv.add_vline(x=0, line_dash="dash", line_color=GRAY, line_width=1)
            fig_uv.update_layout(title="Variação por unidade (2025 → 2026)",
                plot_bgcolor="white", paper_bgcolor="white", height=380,
                margin=dict(t=50,b=20,l=10,r=60),
                xaxis=dict(gridcolor="#f0f2f5",title="Δ casos"),
                font=dict(family="Arial",size=11))
            st.plotly_chart(fig_uv, use_container_width=True)
    else:
        unid_ano = unid_agg[unid_agg["Ano"].isin(anos)].sort_values("Qtd",ascending=True)
        fig_u2 = px.bar(unid_ano, x="Qtd", y="Unidade", color="Ano",
                         orientation="h", barmode="group",
                         color_discrete_map={2025:GRAY,2026:BLUE},
                         title="Volume por unidade e ano")
        fig_u2.update_layout(plot_bgcolor="white",paper_bgcolor="white",
                              height=380, font=dict(family="Arial",size=11),
                              margin=dict(t=50,b=20,l=10,r=40))
        st.plotly_chart(fig_u2, use_container_width=True)

# ── DIAGNÓSTICOS ───────────────────────────────────────────────────────────────
st.markdown("<div class='sec'>🏥 Diagnósticos (CIDs)</div>", unsafe_allow_html=True)
cd1, cd2 = st.columns([3,2])

cid_agg = (df.dropna(subset=["CID"])
           .groupby(["CID","Diagnostico"]).size()
           .reset_index(name="Qtd")
           .sort_values("Qtd",ascending=True).tail(top_n))

with cd1:
    fig_c = go.Figure(go.Bar(
        x=cid_agg["Qtd"],
        y=cid_agg["CID"] + " · " + cid_agg["Diagnostico"].str[:25],
        orientation="h",
        marker=dict(color=cid_agg["Qtd"],colorscale=[[0,"#dbeafe"],[1,BLUE]]),
        text=cid_agg["Qtd"].apply(lambda v: f"{v:,}".replace(",",".")),
        textposition="outside",
    ))
    fig_c.update_layout(
        title=f"Top {top_n} CIDs", plot_bgcolor="white", paper_bgcolor="white",
        margin=dict(t=50,b=20,l=10,r=60),
        xaxis=dict(gridcolor="#f0f2f5"),
        yaxis=dict(tickfont=dict(size=10)),
        font=dict(family="Arial",size=11),
        height=max(320, top_n*34))
    st.plotly_chart(fig_c, use_container_width=True)

with cd2:
    unid_pizza = df["Unidade"].value_counts().reset_index()
    unid_pizza.columns = ["Unidade","Qtd"]
    palette = [BLUE,AMBER,GREEN,RED,"#8b5cf6","#ec4899","#14b8a6",GRAY,"#f97316","#06b6d4","#a855f7","#84cc16"]
    fig_p = go.Figure(go.Pie(
        labels=unid_pizza["Unidade"],
        values=unid_pizza["Qtd"],
        hole=0.45,
        marker=dict(colors=palette[:len(unid_pizza)]),
        textinfo="percent",
        textfont=dict(size=10),
        hovertemplate="%{label}<br>%{value:,} encaminhamentos<br>%{percent}<extra></extra>",
    ))
    fig_p.update_layout(
        title="Participação por unidade",
        plot_bgcolor="white", paper_bgcolor="white",
        margin=dict(t=50,b=20,l=10,r=10),
        legend=dict(font=dict(size=9), orientation="v"),
        font=dict(family="Arial"),
        height=max(320, top_n*34),
        annotations=[dict(text="Unidades",x=0.5,y=0.5,
                          font=dict(size=13,color=NAVY),showarrow=False)],
    )
    st.plotly_chart(fig_p, use_container_width=True)

# ── PERFIL DOS PACIENTES ────────────────────────────────────────────────────────
st.markdown("<div class='sec'>👥 Perfil dos Pacientes</div>", unsafe_allow_html=True)
cp1, cp2 = st.columns(2)

faixa_agg = df.groupby(["Faixa_Etaria","Ano"]).size().reset_index(name="Qtd")
faixa_order = ["0–11 anos","12–17 anos","18–59 anos","60+ anos"]
faixa_agg["_ord"] = faixa_agg["Faixa_Etaria"].apply(
    lambda x: faixa_order.index(x) if x in faixa_order else 99)
faixa_agg = faixa_agg.sort_values("_ord")

tempo_agg = df.groupby(["Faixa_Tempo","Ano"]).size().reset_index(name="Qtd")
tempo_order = ["< 1h","1–2h","2–4h","4–8h","8–24h","> 24h"]
tempo_agg["_ord"] = tempo_agg["Faixa_Tempo"].apply(
    lambda x: tempo_order.index(x) if x in tempo_order else 99)
tempo_agg = tempo_agg.sort_values("_ord")

with cp1:
    fig_fx = go.Figure()
    for ano in sorted(anos):
        d = faixa_agg[faixa_agg["Ano"]==ano]
        fig_fx.add_trace(go.Bar(
            name=str(ano), x=d["Faixa_Etaria"], y=d["Qtd"],
            marker_color=color_map.get(ano,GRAY),
            text=d["Qtd"].apply(lambda v: f"{int(v):,}".replace(",",".")),
            textposition="outside", textfont=dict(size=10),
        ))
    fig_fx.update_layout(title="Encaminhamentos por faixa etária",
        barmode="group", plot_bgcolor="white", paper_bgcolor="white", height=320,
        legend=dict(orientation="h",y=1.12,x=0),
        margin=dict(t=55,b=25,l=10,r=10),
        yaxis=dict(gridcolor="#f0f2f5"), font=dict(family="Arial",size=11))
    st.plotly_chart(fig_fx, use_container_width=True)

with cp2:
    fig_tp = go.Figure()
    for ano in sorted(anos):
        d = tempo_agg[tempo_agg["Ano"]==ano]
        fig_tp.add_trace(go.Bar(
            name=str(ano), x=d["Faixa_Tempo"], y=d["Qtd"],
            marker_color=color_map.get(ano,GRAY),
            text=d["Qtd"].apply(lambda v: f"{int(v):,}".replace(",",".")),
            textposition="outside", textfont=dict(size=10),
        ))
    fig_tp.update_layout(title="Distribuição do tempo de permanência",
        barmode="group", plot_bgcolor="white", paper_bgcolor="white", height=320,
        legend=dict(orientation="h",y=1.12,x=0),
        margin=dict(t=55,b=25,l=10,r=10),
        yaxis=dict(gridcolor="#f0f2f5"), font=dict(family="Arial",size=11))
    st.plotly_chart(fig_tp, use_container_width=True)

# ── VARIAÇÃO CIDs ──────────────────────────────────────────────────────────────
if len(anos) == 2 and 2025 in anos and 2026 in anos:
    st.markdown("<div class='sec'>📊 Variação 2025 → 2026</div>", unsafe_allow_html=True)
    cid25 = df[df["Ano"]==2025].groupby(["CID","Diagnostico"]).size().reset_index(name="Q25")
    cid26 = df[df["Ano"]==2026].groupby(["CID","Diagnostico"]).size().reset_index(name="Q26")
    cid_var = cid25.merge(cid26, on=["CID","Diagnostico"], how="outer").fillna(0)
    cid_var["Var"] = cid_var["Q26"] - cid_var["Q25"]
    cid_var["Var_Pct"] = ((cid_var["Q26"]-cid_var["Q25"])/cid_var["Q25"].replace(0,1)*100).round(1)
    cid_var["Total"] = cid_var["Q25"] + cid_var["Q26"]
    cid_var = cid_var.sort_values("Total", ascending=False).head(top_n)
    cid_var_sorted = cid_var.sort_values("Var")

    vv1, vv2 = st.columns(2)
    with vv1:
        fig_v = go.Figure(go.Bar(
            x=cid_var_sorted["CID"],
            y=cid_var_sorted["Var"],
            marker_color=[GREEN if v>=0 else RED for v in cid_var_sorted["Var"]],
            text=cid_var_sorted["Var"].apply(lambda v: f"+{int(v)}" if v>=0 else str(int(v))),
            textposition="outside", textfont=dict(size=9),
            hovertemplate="<b>%{x}</b><br>%{customdata}<br>Δ: %{y:+d}<extra></extra>",
            customdata=cid_var_sorted["Diagnostico"],
        ))
        fig_v.add_hline(y=0, line_dash="dash", line_color=GRAY, line_width=1)
        fig_v.update_layout(title=f"Variação por CID (top {top_n})",
            plot_bgcolor="white", paper_bgcolor="white", height=340,
            margin=dict(t=50,b=40,l=10,r=10),
            yaxis=dict(gridcolor="#f0f2f5",title="Δ casos"),
            xaxis=dict(tickangle=-45), font=dict(family="Arial",size=11))
        st.plotly_chart(fig_v, use_container_width=True)

    with vv2:
        fig_sc = px.scatter(cid_var, x="Q25", y="Q26",
            size="Total", hover_name="Diagnostico",
            hover_data={"Var_Pct":True,"Total":False,"Q25":False,"Q26":False},
            labels={"Q25":"Volume 2025","Q26":"Volume 2026"},
            title=f"Volume 2025 vs 2026 (top {top_n} CIDs)",
            color_discrete_sequence=[BLUE])
        mx = max(cid_var["Q25"].max(), cid_var["Q26"].max())*1.1
        fig_sc.add_shape(type="line",x0=0,y0=0,x1=mx,y1=mx,
                         line=dict(dash="dash",color=GRAY,width=1))
        fig_sc.update_layout(plot_bgcolor="white",paper_bgcolor="white",
            height=340,margin=dict(t=50,b=30,l=10,r=10),
            font=dict(family="Arial",size=11))
        st.plotly_chart(fig_sc, use_container_width=True)

# ── TABELA ────────────────────────────────────────────────────────────────────
with st.expander("📋 Ver dados filtrados"):
    tab = st.radio("Visualizar", ["Resumo mensal","Por unidade","CIDs","Faixa etária"],
                   horizontal=True)
    if tab == "Resumo mensal":
        t = df.groupby(["Ano","Mes","Mes_Num"]).agg(
            Encaminhamentos=("CID","count"),
            Tempo_Med_Min=("Tempo_Min","mean")
        ).reset_index().sort_values(["Ano","Mes_Num"])
        t["Tempo_Med_Min"] = t["Tempo_Med_Min"].round(0).astype("Int64")
        t = t.drop(columns="Mes_Num")
        st.dataframe(t, use_container_width=True, hide_index=True)
    elif tab == "Por unidade":
        t = df.groupby(["Unidade","Ano"]).agg(
            Encaminhamentos=("CID","count"),
            Tempo_Med_Min=("Tempo_Min","mean")
        ).reset_index()
        t["Tempo_Med_Min"] = t["Tempo_Med_Min"].round(0).astype("Int64")
        st.dataframe(t.sort_values(["Ano","Encaminhamentos"],ascending=[True,False]),
                     use_container_width=True, hide_index=True)
    elif tab == "CIDs":
        t = df.dropna(subset=["CID"]).groupby(["CID","Diagnostico","Ano"]).size().reset_index(name="Qtd")
        st.dataframe(t.sort_values(["Ano","Qtd"],ascending=[True,False]),
                     use_container_width=True, hide_index=True)
    else:
        t = df.groupby(["Faixa_Etaria","Ano"]).size().reset_index(name="Qtd")
        st.dataframe(t, use_container_width=True, hide_index=True)

st.divider()
st.caption(f"Exibindo {len(df):,} de {len(df_raw):,} registros com os filtros selecionados  |  "
           "CORE/CG · *Maio/2026 parcial até 20/05/2026".replace(",","."))
