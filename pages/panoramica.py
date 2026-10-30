import pandas as pd
import plotly.graph_objects as go
import streamlit as st

from src import data as D
from src import ui

d = ui.dati()
ind, prof = d["indicatori"], d["profili"]

st.title("Esternalità delle fonti energetiche")
st.markdown(
    "Confronto degli impatti lungo tutto il ciclo di vita (front end, esercizio, back end) "
    "per le principali fonti di elettricità, con un collegamento ai conflitti locali in Friuli Venezia Giulia."
)

c1, c2, c3, c4 = st.columns(4)
c1.metric("Valori quantitativi", len(ind))
c2.metric("Fonti energetiche con dati", ind["fonte"].nunique(), help=f"Su {len(D.ORDINE_FONTI)} considerate")
c3.metric("Fonti bibliografiche", ind["fonte_id"].nunique())
c4.metric("Conflitti in FVG", len(d["conflitti"]))

st.subheader("Come leggere l'app")
st.markdown(
    """
- **Confronto per indicatore**: un indicatore alla volta (gas serra, uso di suolo, materiali…), tutte le fonti a confronto, con intervalli min–max e fonte di ogni numero.
- **Scheda per fonte**: tutto ciò che sappiamo su una fonte, diviso per fase del ciclo di vita, più dove ricadono gli impatti e i conflitti collegati.
- **Impatti qualitativi**: biodiversità, paesaggio, odori e gli altri impatti che non si misurano bene in numeri. È una **stima preliminare del gruppo**, con livello di certezza dichiarato.
- **Conflitti in FVG**: i 21 casi di opposizione locale, con le motivazioni confrontate con l'evidenza disponibile.
"""
)

st.subheader("Dove i dati mancano")
st.caption(
    "Numero di valori disponibili per fonte e categoria. Le celle vuote sono lacune da colmare, "
    "non impatti assenti."
)
conteggi = (
    ind.groupby(["fonte", "categoria"]).size().unstack(fill_value=0)
    .reindex(index=D.ORDINE_FONTI, columns=D.ORDINE_CATEGORIE, fill_value=0)
)
testo = conteggi.astype(str).where(conteggi > 0, "–")
fig = go.Figure(go.Heatmap(
    z=conteggi.values, x=conteggi.columns, y=conteggi.index,
    text=testo.values, texttemplate="%{text}",
    colorscale=[[0, "#f1f0ec"], [0.001, "#cde2fb"], [0.5, "#5598e7"], [1, "#1c5cab"]],
    showscale=False, xgap=2, ygap=2,
    hovertemplate="%{y} · %{x}: %{z} valori<extra></extra>",
))
fig.update_layout(
    height=480, margin=dict(l=10, r=10, t=10, b=10),
    yaxis=dict(autorange="reversed"), xaxis=dict(side="top"),
    plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)", font=dict(size=13),
)
st.plotly_chart(fig, width="stretch")

scarse = prof.loc[prof["copertura_dati"] == "scarsa", "fonte"].tolist()
st.warning(
    "Copertura scarsa per: " + ", ".join(scarse) + ". "
    "Mancano in particolare un LCA del petrolio greggio → elettricità, un LCA dell'eolico galleggiante, "
    "dati sull'EROI e stime monetarie dei costi esterni."
)

ui.piede()
