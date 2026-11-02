"""Componenti grafici condivisi tra le pagine."""

from __future__ import annotations

import math

import pandas as pd
import plotly.graph_objects as go
import streamlit as st

from src import data as D

TESTO_SECONDARIO = "#52514e"
GRIGLIA = "rgba(120,120,120,0.18)"
GRIGIO_ALTRE = "#c9c8c2"


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
        "sintesi": D.carica_sintesi(),
    }


def _ordina_per_valore(df: pd.DataFrame) -> pd.DataFrame:
    """Ordina dal valore più alto al più basso (centrale, o centro dell'intervallo)."""
    centro = df["punto"].fillna((df["lo"] + df["hi"]) / 2)
    return df.assign(_c=centro).sort_values("_c", ascending=False)


def posizione(rif: pd.DataFrame, fonte: str) -> str:
    """Frase sulla posizione della fonte tra quelle con un valore di riferimento."""
    if fonte not in set(rif["fonte"]) or len(rif) < 2:
        return ""
    ordinate = _ordina_per_valore(rif)["fonte"].tolist()
    i = ordinate.index(fonte) + 1
    n = len(ordinate)
    if i == 1:
        return f"Valore più alto tra le {n} fonti con dati."
    if i == n:
        return f"Valore più basso tra le {n} fonti con dati."
    return f"{i}ª su {n} fonti con dati, dal valore più alto."


def grafico_riferimento(rif: pd.DataFrame, profili: pd.DataFrame, bib: pd.DataFrame, unita: str,
                        log: bool, evidenzia: str | None = None, compatto: bool = False) -> go.Figure:
    """Una riga per fonte (valore di riferimento), ordinate dal valore più alto, con etichette dirette.

    Barra = intervallo min–max; pallino = valore centrale o valore singolo.
    Con `evidenzia`, le altre fonti diventano grigie.
    """
    rif = _ordina_per_valore(rif).iloc[::-1]  # plotly disegna dal basso
    cit = bib.set_index("fonte_id")["citazione_breve"]
    valori = pd.concat([rif["lo"], rif["hi"]]).dropna()
    usa_log = log and len(valori) > 0 and (valori > 0).all()
    fig = go.Figure()
    etichette = []
    for _, r in rif.iterrows():
        attiva = evidenzia is None or r["fonte"] == evidenzia
        col = colore_fonte(r["fonte"], profili) if attiva else GRIGIO_ALTRE
        nome = f"<b>{r['fonte']}</b>" if (evidenzia is None or r["fonte"] == evidenzia) else r["fonte"]
        tec = r["tecnologia"] if len(r["tecnologia"]) <= 34 else r["tecnologia"][:32] + "…"
        y = nome if compatto else f"{nome}<br><span style='font-size:11px'>{tec}</span>"
        etichette.append(y)
        hover = (
            f"<b>{r['fonte']}</b> · {r['tecnologia']}<br>"
            f"{descrivi_valore(r)} {unita}<br>"
            f"{r['tipo_valore']} · {r['regione']} · {r['anno_dato']}<br>"
            f"Fonte: {cit.get(r['fonte_id'], r['fonte_id'])}<extra></extra>"
        )
        intervallo = not pd.isna(r["min"]) and not pd.isna(r["max"]) and r["min"] != r["max"]
        if intervallo:
            fig.add_trace(go.Scatter(
                x=[r["lo"], r["hi"]], y=[y, y], mode="lines",
                line=dict(color=col, width=12), hovertemplate=hover, showlegend=False,
            ))
        x_punto = r["punto"] if not pd.isna(r["punto"]) else (None if intervallo else r["lo"])
        if x_punto is not None and not pd.isna(x_punto):
            fig.add_trace(go.Scatter(
                x=[x_punto], y=[y], mode="markers",
                marker=dict(size=13, color=col if not intervallo else "white", line=dict(width=3, color=col)),
                hovertemplate=hover, showlegend=False,
            ))
        # Etichetta diretta del valore, a destra dell'estremo superiore, staccata dal segno.
        testo = (f"{fmt(r['min'])}–{fmt(r['max'])}" if intervallo else fmt(x_punto))
        if not pd.isna(r["hi"]):
            # Sugli assi logaritmici plotly vuole la coordinata delle annotazioni in log10.
            x_testo = math.log10(r["hi"]) if usa_log else r["hi"]
            fig.add_annotation(
                x=x_testo, y=y, text=testo, showarrow=False, xanchor="left", xshift=18,
                font=dict(size=12, color="#0b0b0b" if attiva else TESTO_SECONDARIO),
            )

    massimo = valori.max() if len(valori) else 1
    if usa_log:
        rng = [math.log10(valori.min()) - 0.3, math.log10(massimo) + 0.9]
    else:
        rng = [0, massimo * 1.28 if massimo > 0 else 1]
    riga = 30 if compatto else 46
    fig.update_layout(
        height=max(150, riga * len(rif) + 70),
        margin=dict(l=10, r=10, t=8, b=36),
        xaxis=dict(title=dict(text=unita, font=dict(size=12)), type="log" if usa_log else "linear",
                   range=rng, gridcolor=GRIGLIA, zeroline=False),
        yaxis=dict(categoryorder="array", categoryarray=etichette, automargin=True, gridcolor="rgba(0,0,0,0)",
                   tickfont=dict(color="#0b0b0b")),
        plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)",
        hoverlabel=dict(align="left"), font=dict(size=13 if not compatto else 12),
    )
    return fig


def serve_log(df: pd.DataFrame) -> bool:
    valori = pd.concat([df["lo"], df["hi"]]).dropna()
    if valori.empty or (valori <= 0).any():
        return False
    return valori.max() / valori.min() > 50


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
        "Ogni numero riporta fonte, anno e perimetro: passa sopra un valore nel grafico o apri la tabella."
    )
