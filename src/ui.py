"""Componenti grafici condivisi tra le pagine."""

from __future__ import annotations

import math

import pandas as pd
import plotly.graph_objects as go
import streamlit as st

from src import data as D

TESTO_SECONDARIO = "#52514e"
GRIGLIA = "rgba(120,120,120,0.18)"


@st.cache_data
def dati():
    """Carica tutti i dataset una sola volta."""
    return {
        "indicatori": D.carica_indicatori(),
        "bibliografia": D.carica_bibliografia(),
        "matrice": D.carica_matrice(),
        "profili": D.carica_profili(),
        "conflitti": D.carica_conflitti(),
        "temi": D.carica_temi(),
    }


def colore_fonte(fonte: str, profili: pd.DataFrame) -> str:
    fam = profili.set_index("fonte").loc[fonte, "famiglia"]
    return D.FAMIGLIE[fam]


def fmt(v) -> str:
    """Formatta un numero all'italiana, con cifre significative ragionevoli."""
    if v is None or (isinstance(v, float) and math.isnan(v)) or pd.isna(v):
        return "–"
    v = float(v)
    if v == 0:
        return "0"
    if abs(v) >= 100:
        s = f"{v:,.0f}"
    elif abs(v) >= 10:
        s = f"{v:,.1f}"
    elif abs(v) >= 1:
        s = f"{v:,.2f}"
    else:
        s = f"{v:.3g}"
    s = s.replace(",", "§").replace(".", ",").replace("§", ".")
    if "," in s:
        s = s.rstrip("0").rstrip(",")
    return s


def descrivi_valore(r) -> str:
    if not pd.isna(r["min"]) and not pd.isna(r["max"]):
        base = f"{fmt(r['min'])} – {fmt(r['max'])}"
        if not pd.isna(r["centrale"]):
            base += f" (centrale {fmt(r['centrale'])})"
        return base
    return fmt(r["centrale"] if not pd.isna(r["centrale"]) else (r["min"] if not pd.isna(r["min"]) else r["max"]))


def legenda_famiglie():
    pezzi = [
        f"<span style='display:inline-flex;align-items:center;gap:6px;margin-right:18px'>"
        f"<span style='width:12px;height:12px;border-radius:3px;background:{c};display:inline-block'></span>"
        f"<span>{f}</span></span>"
        for f, c in D.FAMIGLIE.items()
    ]
    st.markdown("<div style='font-size:0.9rem'>" + "".join(pezzi) + "</div>", unsafe_allow_html=True)


def grafico_intervalli(df: pd.DataFrame, profili: pd.DataFrame, bib: pd.DataFrame, unita: str, log: bool) -> go.Figure:
    """Barre di intervallo (min–max) con punto centrale, una riga per valore."""
    ordine = {f: i for i, f in enumerate(D.ORDINE_FONTI)}
    df = df.assign(_o=df["fonte"].map(ordine)).sort_values(["_o", "id"], ascending=[False, False])
    cit = bib.set_index("fonte_id")["citazione_breve"]

    fig = go.Figure()
    for _, r in df.iterrows():
        col = colore_fonte(r["fonte"], profili)
        etichetta = f"{r['fonte']} · {r['tecnologia']}"
        hover = (
            f"<b>{r['fonte']}</b><br>{r['tecnologia']}<br>"
            f"Valore: {descrivi_valore(r)} {unita}<br>"
            f"{r['tipo_valore']} · {r['regione']} · {r['anno_dato']}<br>"
            f"Fonte: {cit.get(r['fonte_id'], r['fonte_id'])}<extra></extra>"
        )
        intervallo = not pd.isna(r["min"]) and not pd.isna(r["max"]) and r["min"] != r["max"]
        if intervallo:
            fig.add_trace(go.Scatter(
                x=[r["lo"], r["hi"]], y=[etichetta, etichetta], mode="lines+markers",
                line=dict(color=col, width=8), marker=dict(size=10, color=col, symbol="line-ns-open", line=dict(width=2, color=col)),
                hovertemplate=hover, showlegend=False,
            ))
        if not pd.isna(r["punto"]):
            fig.add_trace(go.Scatter(
                x=[r["punto"]], y=[etichetta], mode="markers",
                marker=dict(size=12, color=col, line=dict(width=2, color="white")),
                hovertemplate=hover, showlegend=False,
            ))
        elif not intervallo:
            fig.add_trace(go.Scatter(
                x=[r["lo"]], y=[etichetta], mode="markers",
                marker=dict(size=12, color=col, line=dict(width=2, color="white")),
                hovertemplate=hover, showlegend=False,
            ))

    positivi = pd.concat([df["lo"], df["hi"]]).dropna()
    usa_log = log and (positivi > 0).all()
    fig.update_layout(
        height=max(260, 42 * len(df) + 90),
        margin=dict(l=10, r=20, t=10, b=40),
        xaxis=dict(title=unita, type="log" if usa_log else "linear", gridcolor=GRIGLIA, zeroline=False),
        yaxis=dict(gridcolor="rgba(0,0,0,0)", automargin=True),
        plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)",
        hoverlabel=dict(align="left"),
        font=dict(size=13),
    )
    return fig


def tabella_valori(df: pd.DataFrame, bib: pd.DataFrame):
    cit = bib.set_index("fonte_id")["citazione_breve"]
    out = pd.DataFrame({
        "Fonte energetica": df["fonte"],
        "Indicatore": df["indicatore"],
        "Tecnologia": df["tecnologia"],
        "Valore": df.apply(descrivi_valore, axis=1),
        "Unità": df["unita"],
        "Tipo di valore": df["tipo_valore"],
        "Regione": df["regione"],
        "Anno": df["anno_dato"],
        "Fase": df["fase"],
        "Fonte": df["fonte_id"].map(cit),
        "Tipo di dato": df["tipo_dato"],
        "Note": df["note"],
    })
    st.dataframe(out, hide_index=True, width="stretch")


def piede():
    st.divider()
    st.caption(
        "Progetto ESTERNALITÀ · filone Social Acceptance / POWERUP. "
        "Ogni numero riporta fonte, anno e perimetro; la matrice qualitativa è una stima preliminare del gruppo, da validare."
    )
