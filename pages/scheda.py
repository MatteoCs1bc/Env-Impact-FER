import streamlit as st

from src import data as D
from src import ui

d = ui.dati()
ind, prof, bib, mat, conf, sint = (
    d["indicatori"], d["profili"], d["bibliografia"], d["matrice"], d["conflitti"], d["sintesi"],
)
sint_idx = sint.set_index(["fonte", "categoria"])["testo"]
prof_idx = prof.set_index("fonte")

st.title("Analisi per fonte")
st.markdown(
    "Una scheda per ogni fonte, con gli stessi impatti del *Confronto per indicatore*. "
    "Nei grafici la fonte è evidenziata e le altre sono in grigio, per vedere subito dove si colloca."
)


def scheda(fonte: str):
    p = prof_idx.loc[fonte]
    colore = D.FAMIGLIE[p["famiglia"]]
    st.markdown(
        f"<span style='display:inline-block;padding:2px 10px;border-radius:12px;background:{colore};"
        f"color:white;font-size:0.85rem'>{p['famiglia']}</span>&nbsp; Copertura dei dati: **{p['copertura_dati']}**",
        unsafe_allow_html=True,
    )

    with st.container(border=True):
        c1, c2 = st.columns(2)
        c1.markdown(f"**Dove ricadono gli impatti**  \n{p['dove_ricade']}")
        c1.markdown(f"**Chi li subisce e chi ne beneficia**  \n{p['chi_subisce_chi_beneficia']}")
        c2.markdown(f"**Aree di impatto PPE**  \n{p['aree_ppe']}")
        c2.markdown(f"**Scala**  \n{p['scala_ppe']}")

    dati_fonte = ind[ind["fonte"] == fonte]
    mancanti = []
    for categoria in D.ORDINE_CATEGORIE:
        testo = sint_idx.get((fonte, categoria))
        dc = dati_fonte[dati_fonte["categoria"] == categoria]
        if testo is None and dc.empty:
            mancanti.append(categoria)
            continue
        st.markdown(f"#### {categoria}")
        if testo:
            st.markdown(testo)
        pred = D.INDICATORE_PREDEFINITO.get(categoria)
        indicatori = sorted(dc["indicatore"].unique(), key=lambda i: (i != pred, i))
        if indicatori:
            colonne = st.columns(2)
            for k, indicatore in enumerate(indicatori):
                unita = D.unita_principale(ind, indicatore)
                rif = ind[(ind["indicatore"] == indicatore) & ind["is_rif"] & (ind["unita"] == unita)]
                with colonne[k % 2]:
                    st.markdown(f"**{indicatore}**")
                    if fonte in set(rif["fonte"]):
                        st.plotly_chart(
                            ui.grafico_riferimento(rif, prof, bib, unita, ui.serve_log(rif), evidenzia=fonte, compatto=True),
                            width="stretch", key=f"{fonte}_{indicatore}",
                        )
                        r = rif[rif["fonte"] == fonte].iloc[0]
                        cit = bib.set_index("fonte_id").loc[r["fonte_id"], "citazione_breve"]
                        st.caption(
                            f"{fonte}: **{ui.descrivi_valore(r)} {unita}** · {r['tecnologia']} · {cit}, dato al {r['anno_dato']}. "
                            + ui.posizione(rif, fonte)
                        )
                    else:
                        r = dc[dc["indicatore"] == indicatore].iloc[0]
                        st.caption(
                            f"{ui.descrivi_valore(r)} {r['unita']} ({r['tecnologia']}). "
                            "Non confrontabile con le altre fonti: vedi la nota in tabella."
                        )
            with st.expander(f"Tutti i valori di {fonte} – {categoria.lower()} ({len(dc)})"):
                ui.tabella_valori(dc.sort_values("indicatore"), bib)

    if mancanti:
        st.caption("Nessun dato né sintesi per: " + ", ".join(m.lower() for m in mancanti) + ".")

    st.markdown("#### Biodiversità, paesaggio e territorio")
    st.caption("Impatti che gli LCA non misurano. Valutazione preliminare del gruppo, da completare con fonti specifiche.")
    m = mat[mat["fonte"] == fonte].set_index("dimensione").reindex(D.ORDINE_DIMENSIONI)
    # Non ripetere la biodiversità se è già spiegata nella sezione Fauna, flora, biodiversità.
    if (fonte, "Fauna, flora, biodiversità") in sint_idx.index:
        m = m.drop(index="Biodiversità e habitat")
    st.markdown("\n".join(
        f"- **{dim}**: {r['motivazione']}" for dim, r in m.iterrows() if r["motivazione"]
    ))

    st.markdown("#### Conflitti in FVG")
    c = conf[conf["fonte_app"] == fonte]
    if c.empty:
        st.caption("Nessun conflitto registrato per questa fonte in Local opposition.xlsx.")
    else:
        st.dataframe(
            c[["luogo", "tipologia", "anno", "motivazioni", "esito"]].rename(columns=str.capitalize),
            hide_index=True, width="stretch",
        )
        st.caption("Per l'analisi motivo per motivo vedi la pagina *Conflitti in FVG*.")


schede = st.tabs(D.ORDINE_FONTI)
for tab, fonte in zip(schede, D.ORDINE_FONTI):
    with tab:
        scheda(fonte)

ui.piede()
