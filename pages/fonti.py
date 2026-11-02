import streamlit as st

from src import ui

d = ui.dati()
bib, ind = d["bibliografia"], d["indicatori"]

st.title("Fonti e metodo")

st.subheader("Regole")
st.markdown(
    """
- **Unità funzionale:** 1 MWh (o kWh) di elettricità immesso in rete. Capacity factor e vita utile assunti sono indicati nella categoria *Efficienza*.
- **Confini:** front end (estrazione, manifattura, costruzione), esercizio, back end (smantellamento, rifiuti, ripristino). Accumuli e rete sono esclusi dagli LCA di base: il costo di sistema dell'intermittenza è mostrato a parte.
- **Ogni numero** ha fonte, anno, regione e perimetro. Il *tipo di dato* distingue letteratura, dato misurato e stima nostra.
- **Intervalli, non solo medie.** Le differenze dipendono soprattutto da irraggiamento e vento, mix elettrico della manifattura, efficienza delle centrali e fughe di metano.
- **Fonti divergenti** sono mostrate entrambe, con una nota. Esempio: per il carbone IPCC AR5 (820 g) contro UNECE 2022 (751–1095 g).
- **Un valore di riferimento per fonte.** Nei grafici di confronto ogni fonte ha un solo valore (colonna `riferimento` in `indicatori.csv`); gli altri (tecnologie diverse, fonti bibliografiche alternative) restano visibili in *Tutti i valori*.
- **Nessun punteggio aggregato.** Ogni indicatore si legge da solo.
"""
)

st.subheader("Cautele di lettura")
st.markdown(
    """
- I capacity factor del Breakthrough Institute (FV 24%, eolico onshore 35%, offshore 55%) sono più alti delle medie europee usate da UNECE (12%, 23%, 36%). I valori per MWh in Italia sarebbero più alti di quelli BTI.
- La "roccia movimentata" di carbone e gas nel dataset BTI è la massa del combustibile, non gli sterili: il carbone è sottostimato.
- Gli LCA non coprono rumore, paesaggio, mortalità della fauna né incidenti gravi: questi impatti sono descritti a parole nell'*Analisi per fonte* (valutazione preliminare del gruppo).
- I tassi di mortalità per TWh sono valori arrotondati da Our World in Data e vanno aggiornati con il dataset ufficiale.
"""
)

st.subheader("Bibliografia")
uso = ind.groupby("fonte_id").size()
tab = bib.assign(valori=bib["fonte_id"].map(uso).fillna(0).astype(int))
st.dataframe(
    tab[["citazione_breve", "titolo", "autori_ente", "anno", "tipo", "perimetro", "valori", "link", "drive_id", "note"]].rename(
        columns={"citazione_breve": "Fonte", "titolo": "Titolo", "autori_ente": "Autori/ente", "anno": "Anno", "tipo": "Tipo",
                 "perimetro": "Perimetro", "valori": "Valori nella base", "link": "Link", "drive_id": "ID Drive", "note": "Note"}
    ),
    hide_index=True, width="stretch",
    column_config={"Link": st.column_config.LinkColumn("Link")},
)

st.subheader("Lacune da colmare")
st.markdown(
    """
1. LCA petrolio greggio → elettricità (es. Masnadi et al. 2018, Jing et al. 2020).
2. LCA eolico offshore galleggiante.
3. EROI e energy payback time con metodo dichiarato.
4. Uso di suolo in m²·anno/MWh dal corrigendum UNECE 2022, per avere tutte le fonti con lo stesso metodo.
5. Mortalità e costi esterni monetizzati (EEA, ExternE).
6. Evidenza specifica per il FVG: campi elettromagnetici (ARPA FVG), odori del biometano, consumo di suolo dei parchi FV.
"""
)

st.subheader("Aggiornare i dati")
st.markdown(
    "I dati sono file CSV nella cartella `data/` del repository. Dopo ogni modifica esegui "
    "`python scripts/valida_dati.py`: controlla che ogni valore abbia fonte, anno, unità e perimetro."
)

ui.piede()
