import streamlit as st

from src import data as D
from src import ui

d = ui.dati()
ind, prof, bib = d["indicatori"], d["profili"], d["bibliografia"]

st.title("Confronto per indicatore")

f1, f2, f3 = st.columns([1, 1.4, 1])
categorie = [c for c in D.ORDINE_CATEGORIE if c in set(ind["categoria"])]
categoria = f1.selectbox("Categoria", categorie)
sotto = ind[ind["categoria"] == categoria]
nomi = sorted(sotto["indicatore"].unique())
predefinito = "Gas serra nel ciclo di vita"
indicatore = f2.selectbox("Indicatore", nomi, index=nomi.index(predefinito) if predefinito in nomi else 0)
sotto = sotto[sotto["indicatore"] == indicatore]

unita_disponibili = sotto["unita"].unique().tolist()
if len(unita_disponibili) > 1:
    unita = f3.selectbox("Unità", unita_disponibili, help="Valori in unità diverse non vanno sullo stesso asse.")
    sotto = sotto[sotto["unita"] == unita]
else:
    unita = unita_disponibili[0]
    f3.text_input("Unità", unita, disabled=True)

fonti_presenti = [f for f in D.ORDINE_FONTI if f in set(sotto["fonte"])]
scelte = st.multiselect("Fonti energetiche", fonti_presenti, default=fonti_presenti)
sotto = sotto[sotto["fonte"].isin(scelte)]

c1, c2 = st.columns([1, 3])
log = c1.toggle("Scala logaritmica", value=sotto["hi"].max() / max(sotto["lo"][sotto["lo"] > 0].min(), 1e-9) > 50 if len(sotto) else False)
tipi = c2.multiselect("Tipo di dato", sorted(ind["tipo_dato"].unique()), default=sorted(ind["tipo_dato"].unique()))
sotto = sotto[sotto["tipo_dato"].isin(tipi)]

mancanti = [f for f in D.ORDINE_FONTI if f not in fonti_presenti]
if mancanti:
    st.caption("Nessun dato per: " + ", ".join(mancanti) + ".")

if sotto.empty:
    st.info("Nessun valore con questi filtri.")
else:
    ui.legenda_famiglie()
    st.caption("Barra = intervallo min–max · punto = valore centrale (mediana, media o valore singolo). Passa sopra una barra per fonte, anno e perimetro.")
    st.plotly_chart(ui.grafico_intervalli(sotto, prof, bib, unita, log), width="stretch")

    divergenti = sotto.groupby("fonte")["fonte_id"].nunique()
    divergenti = divergenti[divergenti > 1].index.tolist()
    if divergenti:
        st.info(
            "Più fonti bibliografiche per: " + ", ".join(divergenti) + ". "
            "Controlla le note in tabella: perimetri e ipotesi diverse spiegano gran parte delle differenze."
        )
    avvisi = sotto[sotto["note"].str.contains("ATTENZIONE|FONTI DIVERGENTI", regex=True)]
    for _, r in avvisi.iterrows():
        st.warning(f"**{r['fonte']} – {r['tecnologia']}**: {r['note']}")

    with st.expander("Tabella dei valori", expanded=False):
        ui.tabella_valori(sotto, bib)
        st.download_button(
            "Scarica CSV", sotto.drop(columns=["lo", "hi", "punto", "etichetta"]).to_csv(index=False).encode("utf-8"),
            file_name=f"esternalita_{indicatore}.csv".replace(" ", "_"), mime="text/csv",
        )

ui.piede()
