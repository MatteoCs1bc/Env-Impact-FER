import streamlit as st

from src import ui

ORDINE_STATI = [
    "Accertato in giudizio",
    "Accertato in giudizio (ammissibilità)",
    "Accertato",
    "Ammesso dall'azienda; procedimenti in corso",
    "Documentato da un'agenzia ONU",
    "Documentato in letteratura scientifica",
    "Documentato da ONG su dati aziendali",
    "Contestazione legale di ONG, nessuna pronuncia",
    "Accusa respinta in giudizio",
]


def mostra():
    """Danni ambientali e responsabilità delle compagnie petrolifere."""
    d = ui.dati()
    casi, bib = d["compagnie"], d["bibliografia"].set_index("fonte_id")

    st.markdown(
        "Le esternalità del fossile hanno anche nomi e indirizzi. Qui raccogliamo alcuni casi documentati che "
        "riguardano le grandi compagnie, comprese quelle italiane. Per ogni caso indichiamo **quanto è solido** "
        "quello che si afferma: una sentenza, una valutazione ONU, uno studio scientifico, un'accusa di ONG non ancora "
        "giudicata o un'accusa respinta. È la stessa distinzione che usiamo per le proteste contro le rinnovabili."
    )
    c1, c2 = st.columns(2)
    compagnie = sorted(casi["compagnia"].unique())
    scelte = c1.multiselect("Compagnia", compagnie, placeholder="Tutte")
    tipi = c2.multiselect("Tipo di impatto", sorted(casi["tipo"].unique()), placeholder="Tutti")
    vista = casi
    if scelte:
        vista = vista[vista["compagnia"].isin(scelte)]
    if tipi:
        vista = vista[vista["tipo"].isin(tipi)]

    for _, r in vista.iterrows():
        with st.container(border=True):
            st.markdown(f"**{r['compagnia']}** · {r['luogo']} ({r['paese']}) · {r['periodo']}")
            st.markdown(
                f"<span style='display:inline-block;padding:1px 9px;border-radius:10px;border:1px solid "
                f"{ui.colore_famiglia('Fossili')};font-size:0.8rem'>{r['tipo']}</span>&nbsp; "
                f"<span style='font-size:0.85rem'>Solidità: <b>{r['stato']}</b></span>",
                unsafe_allow_html=True,
            )
            st.markdown(r["descrizione"])
            b = bib.loc[r["fonte_id"]]
            fonte = f"[{b['citazione_breve']}]({b['link']})" if b["link"] else b["citazione_breve"]
            st.caption(f"Fonte: {fonte}." + (f" {r['note']}" if r["note"] else ""))

    st.caption(
        "Elenco non esaustivo, da completare (per esempio con TotalEnergies, Chevron in Ecuador e le raffinerie italiane). "
        "Molti casi del Delta del Niger e della presentazione *Climate Change & Big Oils* (San Vito al Tagliamento, 2025) "
        "sono qui con le fonti originali."
    )
