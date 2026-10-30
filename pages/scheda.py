import pandas as pd
import plotly.graph_objects as go
import streamlit as st

from src import data as D
from src import ui

d = ui.dati()
ind, prof, bib, mat, conf = d["indicatori"], d["profili"], d["bibliografia"], d["matrice"], d["conflitti"]

st.title("Scheda per fonte")
fonte = st.selectbox("Fonte energetica", D.ORDINE_FONTI)
p = prof.set_index("fonte").loc[fonte]
colore = D.FAMIGLIE[p["famiglia"]]

st.markdown(
    f"<span style='display:inline-block;padding:2px 10px;border-radius:12px;background:{colore};color:white;font-size:0.85rem'>"
    f"{p['famiglia']}</span>&nbsp; Copertura dei dati: **{p['copertura_dati']}**",
    unsafe_allow_html=True,
)

c1, c2 = st.columns(2)
with c1:
    st.markdown("**Dove ricadono gli impatti**")
    st.write(p["dove_ricade"])
    st.markdown("**Chi li subisce e chi ne beneficia**")
    st.write(p["chi_subisce_chi_beneficia"])
with c2:
    st.markdown("**Aree di impatto PPE**")
    st.write(p["aree_ppe"])
    st.markdown("**Scala**")
    st.write(p["scala_ppe"])

st.subheader("1. Ciclo di vita: indicatori quantitativi")
sotto = ind[ind["fonte"] == fonte]
if sotto.empty:
    st.info("Nessun dato quantitativo per questa fonte nella base attuale.")
else:
    fasi = {
        "Front end (estrazione, manifattura, costruzione)": sotto["fase"].str.contains("front end"),
        "Esercizio": sotto["fase"].str.contains("esercizio"),
        "Back end (smantellamento, rifiuti)": sotto["fase"].str.contains("back end"),
        "Intero ciclo di vita": sotto["fase"] == "ciclo di vita",
    }
    schede = st.tabs([f"{k} ({int(v.sum())})" for k, v in fasi.items()])
    for scheda, maschera in zip(schede, fasi.values()):
        with scheda:
            if maschera.sum() == 0:
                st.caption("Nessun valore per questa fase.")
            else:
                ui.tabella_valori(sotto[maschera].sort_values(["categoria", "indicatore"]), bib)

st.subheader("2. Impatti qualitativi")
st.caption("Stima preliminare del gruppo (0 = trascurabile, 3 = alto), con livello di certezza. Da validare.")
m = mat[mat["fonte"] == fonte].set_index("dimensione").reindex(D.ORDINE_DIMENSIONI)
opacita = {"alta": 1.0, "media": 0.7, "bassa": 0.4}
fig = go.Figure(go.Bar(
    x=m["livello"], y=m.index, orientation="h",
    marker=dict(color=colore, opacity=[opacita[c] for c in m["certezza"]], cornerradius=4),
    text=[f"{D.LIVELLI[v]} · certezza {c}" for v, c in zip(m["livello"], m["certezza"])],
    textposition="outside", cliponaxis=False,
    customdata=m["motivazione"],
    hovertemplate="<b>%{y}</b><br>%{customdata}<extra></extra>",
))
fig.update_layout(
    height=360, margin=dict(l=10, r=140, t=10, b=30),
    xaxis=dict(range=[0, 3], tickvals=[0, 1, 2, 3], ticktext=list(D.LIVELLI.values()), gridcolor=ui.GRIGLIA),
    yaxis=dict(autorange="reversed"), plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)", font=dict(size=13),
)
st.plotly_chart(fig, width="stretch")
with st.expander("Motivazioni"):
    st.dataframe(
        m.reset_index()[["dimensione", "livello", "certezza", "motivazione", "riferimenti"]].rename(columns=str.capitalize),
        hide_index=True, width="stretch",
    )

st.subheader("3. Conflitti collegati in FVG")
c = conf[conf["fonte_app"] == fonte]
if c.empty:
    st.caption("Nessun conflitto registrato per questa fonte in Local opposition.xlsx.")
else:
    st.dataframe(
        c[["luogo", "tipologia", "anno", "motivazioni", "esito"]].rename(columns=str.capitalize),
        hide_index=True, width="stretch",
    )

ui.piede()
