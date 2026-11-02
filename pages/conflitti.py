import pandas as pd
import plotly.graph_objects as go
import streamlit as st

from src import data as D
from src import ui

d = ui.dati()
conf, temi, ind, bib, prof = d["conflitti"], d["temi"], d["indicatori"], d["bibliografia"], d["profili"]
temi_idx = temi.set_index("tema")

st.title("Conflitti locali in Friuli Venezia Giulia")
st.markdown(
    "I 21 casi di opposizione registrati in *Local opposition.xlsx*. Per ogni motivazione di protesta "
    "l'app mostra cosa dice l'evidenza disponibile, distinguendo tra **impatto misurato**, "
    "**impatto plausibile ma incerto** e **preoccupazione non supportata dall'evidenza**. "
    "Tutte le preoccupazioni sono legittime e vanno ascoltate: la classificazione serve a capire "
    "quali risposte servono (dati, mitigazioni, compensazioni, processo)."
)

esploso = conf.explode("lista_temi").rename(columns={"lista_temi": "tema"})
esploso["etichetta"] = esploso["tema"].map(temi_idx["etichetta"])
esploso["natura"] = esploso["tema"].map(temi_idx["natura"])

st.subheader("Motivi di protesta più frequenti")
esploso["famiglia"] = esploso["fonte_app"].map(prof.set_index("fonte")["famiglia"])
conteggio = (
    esploso.groupby(["etichetta", "famiglia"])
    .agg(n=("id", "size"), fonti=("fonte_app", lambda s: ", ".join(sorted(set(s)))))
    .reset_index()
)
ordine_temi = esploso["etichetta"].value_counts().index.tolist()
fig = go.Figure()
for fam, col in D.FAMIGLIE.items():
    s = conteggio[conteggio["famiglia"] == fam]
    if s.empty:
        continue
    fig.add_trace(go.Bar(
        y=s["etichetta"], x=s["n"], orientation="h", name=fam,
        marker=dict(color=ui.colore_famiglia(fam), line=dict(color=ui.tema()["pannello"], width=2)),
        customdata=s["fonti"],
        hovertemplate=f"<b>{fam}</b> (%{{customdata}})<br>%{{y}}: %{{x}} casi<extra></extra>",
    ))
ui.stile(fig, barmode="stack", height=500, margin=dict(l=12, r=14, t=14, b=30), font=dict(size=13))
fig.update_layout(legend=dict(orientation="h", y=-0.17))
fig.update_yaxes(categoryorder="array", categoryarray=ordine_temi[::-1], showgrid=False)
fig.update_xaxes(title=dict(text="Numero di conflitti in cui il motivo compare"), dtick=1)
st.plotly_chart(fig, width="stretch")
st.caption("Colori per famiglia di fonte; passa sopra una barra per vedere le fonti. Un conflitto può avere più motivi.")

st.subheader("Motivo per motivo: cosa dice l'evidenza")
st.caption("Classificazione preliminare del gruppo, da completare con fonti specifiche per il FVG.")
for tema in ordine_temi:
    chiave = temi[temi["etichetta"] == tema]["tema"].iloc[0]
    t = temi_idx.loc[chiave]
    casi = esploso[esploso["tema"] == chiave]
    with st.expander(f"{tema} · {len(casi)} casi · {t['stato_evidenza']}"):
        st.markdown(f"**Natura:** {t['natura']}")
        st.markdown(f"**Evidenza:** {t['sintesi_evidenza']}")
        if t["indicatori_collegati"]:
            nomi = [x.strip() for x in t["indicatori_collegati"].split(";")]
            fonti_casi = casi["fonte_app"].unique()
            rel = ind[ind["indicatore"].isin(nomi) & ind["fonte"].isin(fonti_casi)]
            if not rel.empty:
                st.markdown("**Dati collegati nella base:**")
                ui.tabella_valori(rel, bib)
        st.markdown("**Casi:** " + "; ".join(f"{r.luogo} ({r.tipologia}, {r.anno})" for r in casi.itertuples()))

st.subheader("Elenco dei conflitti")
f1, f2 = st.columns(2)
fonti_sel = f1.multiselect("Fonte", [f for f in D.ORDINE_FONTI if f in set(conf["fonte_app"])])
temi_sel = f2.multiselect("Motivo", ordine_temi)
vista = conf.copy()
if fonti_sel:
    vista = vista[vista["fonte_app"].isin(fonti_sel)]
if temi_sel:
    chiavi = set(temi[temi["etichetta"].isin(temi_sel)]["tema"])
    vista = vista[vista["lista_temi"].apply(lambda l: bool(chiavi & set(l)))]
vista = vista.assign(motivi=vista["lista_temi"].apply(lambda l: ", ".join(temi_idx.loc[x, "etichetta"] for x in l)))
st.dataframe(
    vista[["luogo", "tipologia", "anno", "comitato", "motivazioni", "motivi", "attori", "esito"]].rename(columns=str.capitalize),
    hide_index=True, width="stretch",
)
st.caption("Fonte: Local opposition.xlsx (Drive, Materiale POWERUP). Pavia di Udine è il caso studio POWERUP.")

ui.piede()
