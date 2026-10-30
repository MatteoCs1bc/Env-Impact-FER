import plotly.graph_objects as go
import streamlit as st

from src import data as D
from src import ui

d = ui.dati()
mat, prof = d["matrice"], d["profili"]

st.title("Impatti qualitativi")
st.markdown(
    "Impatti difficili da misurare in numeri: biodiversità, paesaggio, disturbo locale, filiere lontane. "
    "I livelli sono una **stima preliminare del gruppo** (0–3), motivata e con certezza dichiarata. "
    "Non vanno sommati in un punteggio unico."
)

griglia = mat.pivot(index="fonte", columns="dimensione", values="livello").reindex(index=D.ORDINE_FONTI, columns=D.ORDINE_DIMENSIONI)
cert = mat.pivot(index="fonte", columns="dimensione", values="certezza").reindex(index=D.ORDINE_FONTI, columns=D.ORDINE_DIMENSIONI)
mot = mat.pivot(index="fonte", columns="dimensione", values="motivazione").reindex(index=D.ORDINE_FONTI, columns=D.ORDINE_DIMENSIONI)
testo = griglia.apply(lambda col: col.map(lambda v: D.LIVELLI[v]))
testo = testo + cert.apply(lambda col: col.map(lambda c: " ?" if c == "bassa" else ""))

fig = go.Figure(go.Heatmap(
    z=griglia.values, x=griglia.columns, y=griglia.index,
    text=testo.values, texttemplate="%{text}", zmin=0, zmax=3,
    colorscale=[[0, "#f1f0ec"], [0.33, "#b7d3f6"], [0.66, "#5598e7"], [1, "#1c5cab"]],
    colorbar=dict(tickvals=[0, 1, 2, 3], ticktext=list(D.LIVELLI.values()), title="Livello"),
    customdata=[[f"{cert.iloc[i, j]}<br>{mot.iloc[i, j]}" for j in range(griglia.shape[1])] for i in range(griglia.shape[0])],
    hovertemplate="<b>%{y}</b> · %{x}<br>Certezza %{customdata}<extra></extra>",
    xgap=2, ygap=2,
))
fig.update_layout(
    height=560, margin=dict(l=10, r=10, t=10, b=10),
    yaxis=dict(autorange="reversed"), xaxis=dict(side="top", tickangle=-20),
    plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)", font=dict(size=12),
)
st.plotly_chart(fig, width="stretch")
st.caption("« ? » indica certezza bassa. Passa sopra una cella per la motivazione.")

st.subheader("L'asimmetria spaziale degli impatti")
st.markdown(
    "Le rinnovabili portano gran parte degli impatti **vicino a chi vede l'impianto**; fossili e filiere estrattive "
    "li spostano **lontano** (miniere all'estero, clima globale). Questa asimmetria è uno dei motori dell'opposizione locale: "
    "a parità o anche a fronte di impatti complessivi minori, il carico percepito sul territorio è più alto."
)
ui.legenda_famiglie()
fig2 = go.Figure()
for fam, col in D.FAMIGLIE.items():
    s = prof[prof["famiglia"] == fam]
    # Fonti nella stessa posizione: un solo punto con le etichette impilate.
    gruppi = s.groupby(["quota_impatti_locali", "visibilita_locale"])
    # Spostamento orizzontale per famiglia, così famiglie diverse nella stessa cella non si coprono.
    dx = (list(D.FAMIGLIE).index(fam) - 1.5) * 0.12
    fig2.add_trace(go.Scatter(
        x=[k[0] + dx for k, _ in gruppi], y=[k[1] for k, _ in gruppi], mode="markers+text",
        text=["<br>".join(g["fonte"]) for _, g in gruppi], textposition="bottom center", name=fam,
        marker=dict(size=16, color=col, line=dict(width=2, color="white")),
        customdata=["<br>".join(f"<b>{f}</b>: {t}" for f, t in zip(g["fonte"], g["dove_ricade"])) for _, g in gruppi],
        hovertemplate="%{customdata}<extra></extra>",
        showlegend=False, textfont=dict(size=11),
    ))
fig2.update_layout(
    height=520, margin=dict(l=10, r=10, t=10, b=10),
    xaxis=dict(title="Quanta parte degli impatti ricade vicino all'impianto", range=[0.5, 3.5],
               tickvals=[1, 2, 3], ticktext=["Soprattutto lontano", "Misto", "Soprattutto vicino"], gridcolor=ui.GRIGLIA),
    yaxis=dict(title="Visibilità per chi vive vicino", range=[0.5, 3.6],
               tickvals=[1, 2, 3], ticktext=["Bassa", "Media", "Alta"], gridcolor=ui.GRIGLIA),
    plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)", font=dict(size=12),
)
st.plotly_chart(fig2, width="stretch")
st.caption("Posizioni: stima preliminare del gruppo su scala 1–3; alcune fonti condividono lo stesso punto.")

with st.expander("Tabella completa"):
    st.dataframe(mat.rename(columns=str.capitalize), hide_index=True, width="stretch")

ui.piede()
