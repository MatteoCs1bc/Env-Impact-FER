import streamlit as st

from src import data as D
from src import ui

d = ui.dati()
ind, prof, bib = d["indicatori"], d["profili"], d["bibliografia"]

st.title("Confronto per indicatore")
st.markdown(
    "Per ogni categoria scegli un indicatore: il grafico mostra **un valore per fonte**, "
    "ordinato dal più alto al più basso. La **barra** è l'intervallo tra minimo e massimo, "
    "il **pallino** il valore centrale o il valore singolo. Passa sopra una riga per fonte, anno e perimetro."
)
ui.legenda_famiglie()

for categoria in D.ORDINE_CATEGORIE:
    sotto_cat = ind[ind["categoria"] == categoria]
    if sotto_cat.empty:
        continue
    with st.container(border=True):
        st.subheader(categoria)
        nomi = sorted(sotto_cat["indicatore"].unique())
        pred = D.INDICATORE_PREDEFINITO.get(categoria)
        c1, c2 = st.columns([3, 1])
        indicatore = c1.selectbox(
            "Indicatore", nomi, index=nomi.index(pred) if pred in nomi else 0, key=f"ind_{categoria}",
        )
        tutti = sotto_cat[sotto_cat["indicatore"] == indicatore]
        unita = D.unita_principale(ind, indicatore)
        rif = tutti[tutti["is_rif"] & (tutti["unita"] == unita)]
        positivi = not rif.empty and (rif["lo"] > 0).all() and (rif["hi"] > 0).all()
        log = c2.toggle(
            "Scala logaritmica", value=ui.serve_log(rif), key=f"log_{categoria}_{indicatore}",
            disabled=not positivi,
            help="Utile quando i valori differiscono di molti ordini di grandezza. Non disponibile se ci sono valori pari a zero.",
        )

        if rif.empty:
            st.info("Nessun valore di riferimento per questo indicatore: vedi tutti i valori qui sotto.")
        else:
            st.plotly_chart(ui.grafico_riferimento(rif, prof, bib, unita, log), width="stretch", key=f"g_{categoria}")

        senza = [f for f in D.ORDINE_FONTI if f not in set(tutti["fonte"])]
        fuori = sorted(set(tutti["fonte"]) - set(rif["fonte"]), key=D.ORDINE_FONTI.index)
        righe = []
        if senza:
            righe.append("Nessun dato per: " + ", ".join(senza) + ".")
        if fuori:
            righe.append(
                "Non in grafico (dato non confrontabile o in un'altra unità): " + ", ".join(fuori) + ". "
                "Lo trovi in *Tutti i valori*."
            )
        if righe:
            st.caption(" ".join(righe))

        for _, r in tutti[tutti["note"].str.contains("ATTENZIONE|FONTI DIVERGENTI|Valore di riferimento", regex=True)].iterrows():
            st.caption(f"⚠️ **{r['fonte']} – {r['tecnologia']}**: {r['note']}")

        altri = len(tutti) - len(rif)
        titolo = f"Tutti i valori ({len(tutti)})"
        if altri:
            titolo += f": anche {altri} alternativi (altre tecnologie o altre fonti bibliografiche)"
        with st.expander(titolo):
            for u in tutti["unita"].unique():
                gruppo = tutti[tutti["unita"] == u]
                st.plotly_chart(
                    ui.grafico_intervalli(gruppo, prof, bib, u, ui.serve_log(gruppo)),
                    width="stretch", key=f"tutti_{categoria}_{u}",
                )
            ui.tabella_valori(tutti, bib)
            st.download_button(
                "Scarica CSV",
                tutti.drop(columns=["lo", "hi", "punto", "etichetta", "is_rif"]).to_csv(index=False).encode("utf-8"),
                file_name=f"esternalita_{indicatore}.csv".replace(" ", "_"), mime="text/csv", key=f"dl_{categoria}",
            )

ui.piede()
