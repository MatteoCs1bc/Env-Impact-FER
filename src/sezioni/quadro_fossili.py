import pandas as pd
import plotly.graph_objects as go
import streamlit as st

from src import data as D
from src import ui


def mostra():
    """Quadro generale delle esternalità fossili."""
    d = ui.dati()
    ind, prof, bib, conf = d["indicatori"], d["profili"], d["bibliografia"], d["conflitti"]
    costi, termo = d["costi_esterni"], d["termoelettrico"]
    t = ui.tema()

    # --- 1. Asimmetria --------------------------------------------------------------------------
    st.subheader("Dove ricadono gli impatti")
    righe = []
    for f in D.ORDINE_FONTI:
        p = prof.set_index("fonte").loc[f]
        righe.append({"Fonte": f, "Famiglia": p["famiglia"], "Dove ricadono gli impatti": p["dove_ricade"],
                      "Chi li subisce e chi ne beneficia": p["chi_subisce_chi_beneficia"]})
    tab = pd.DataFrame(righe)
    st.dataframe(tab[tab["Famiglia"].isin(["Fossili", "Rinnovabili variabili"])], hide_index=True, width="stretch")
    n_fossili = int((conf["fonte_app"].map(prof.set_index("fonte")["famiglia"]) == "Fossili").sum())
    st.warning(
        f"**Nei 21 conflitti FVG di Local opposition.xlsx i casi contro impianti fossili sono {n_fossili}.** "
        "Eppure la regione ospita il terminal petrolifero SIOT di Trieste e l'oleodotto TAL (circa 40 milioni di tonnellate "
        "di greggio all'anno verso Austria, Germania e Repubblica Ceca), la centrale di Monfalcone in conversione da carbone "
        "a gas e altre centrali termoelettriche. L'assenza può dipendere da come è stato costruito l'elenco, ma riflette anche "
        "l'asimmetria di percezione: un'infrastruttura esistente fa meno notizia di un impianto nuovo.",
        icon=":material/balance:",
    )

    # --- 2. Emissioni italiane ------------------------------------------------------------------
    st.subheader("Quanto emette il termoelettrico italiano")
    c1, c2 = st.columns(2)
    with c1:
        st.markdown("**CO2 dalla combustione, per kWh prodotto (Italia, 2024)**")
        fattori = pd.DataFrame({
            "combustibile": ["Lignite", "Carbone", "Altre fonti non rinnovabili", "Prodotti petroliferi", "Gas naturale"],
            "g": [1012.5, 862.4, 684.8, 476.6, 370.6],
        }).sort_values("g")
        fig = go.Figure(go.Bar(
            y=fattori["combustibile"], x=fattori["g"], orientation="h",
            marker=dict(color=ui.colore_famiglia("Fossili")),
            text=[ui.fmt(v) for v in fattori["g"]], textposition="outside", cliponaxis=False,
            textfont=dict(color=t["testo"]), hovertemplate="<b>%{y}</b><br>%{x:.1f} gCO2/kWh<extra></extra>",
        ))
        ui.stile(fig, height=300, margin=dict(l=12, r=14, t=14, b=44), showlegend=False, font=dict(size=13))
        fig.update_xaxes(title=dict(text="gCO2/kWh (produzione lorda)"), range=[0, 1250])
        fig.update_yaxes(showgrid=False)
        st.plotly_chart(fig, width="stretch", key="fattori_co2")
        st.caption(
            "Fonte: ISPRA r430/2026, Tab. 1.10. Solo combustione in centrale: estrazione, trasporto e fughe di metano sono "
            "esclusi (con il ciclo di vita il carbone sale a 751–1.095 g, vedi *Confronto per indicatore*). "
            "Nel FVG il termoelettrico fossile emette 411,3 gCO2/kWh; le emissioni regionali del settore sono scese da "
            "2,87 Mt di CO2 nel 2022 a 1,19 Mt nel 2024."
        )
    with c2:
        st.markdown("**Inquinanti per kWh termoelettrico: 2005 e 2024**")
        fig = go.Figure()
        for anno, col, nome in (("v2005", t["altre"], "2005"), ("v2024", ui.colore_famiglia("Fossili"), "2024")):
            fig.add_trace(go.Bar(
                y=termo["inquinante"], x=termo[anno], orientation="h", name=nome, marker=dict(color=col),
                text=[ui.fmt(v) for v in termo[anno]], textposition="outside", cliponaxis=False,
                textfont=dict(color=t["testo"]), hovertemplate=f"<b>%{{y}}</b><br>{nome}: %{{x:.2f}} mg/kWh<extra></extra>",
            ))
        ui.stile(fig, barmode="group", height=300, margin=dict(l=12, r=14, t=14, b=44), font=dict(size=13))
        fig.update_layout(legend=dict(orientation="h", y=1.12, x=0))
        fig.update_xaxes(title=dict(text="mg/kWh"), range=[0, 640])
        fig.update_yaxes(showgrid=False, autorange="reversed")
        st.plotly_chart(fig, width="stretch", key="inquinanti")
        st.caption(
            "Fonte: ISPRA r430/2026, Tab. 1.19–1.20. Il calo è reale (ossidi di zolfo −94%, PM10 −89%), grazie a filtri, "
            "uscita dall'olio combustibile e passaggio al gas. Ma nel 2024 il termoelettrico ha ancora emesso 55,6 kt di NOx, "
            "10 kt di SOx e 0,6 kt di PM10 diretto, che ricadono soprattutto vicino alle centrali e si sommano al particolato "
            "secondario."
        )

    # --- 3. Costi esterni ----------------------------------------------------------------------
    st.subheader("Quanto costano alla società: i costi esterni per MWh")
    st.markdown(
        "I costi esterni traducono in euro i danni non pagati da chi produce: clima, salute, ecosistemi, materiali. "
        "Sono stime con molte ipotesi, ma il **divario tra fonti è di un ordine di grandezza** ed è robusto ai metodi."
    )
    cs = costi.iloc[::-1]
    fig = go.Figure()
    for _, r in cs.iterrows():
        col = ui.colore_famiglia(r["famiglia"])
        fig.add_trace(go.Scatter(
            x=[r["min"], r["max"]], y=[r["tecnologia"]] * 2, mode="lines", line=dict(color=col, width=14),
            hovertemplate=f"<b>{r['tecnologia']}</b><br>{r['min']:.0f}–{r['max']:.0f} €/MWh<br>{r['note']}<extra></extra>",
            showlegend=False,
        ))
        fig.add_annotation(x=r["max"], y=r["tecnologia"], text=f"{r['min']:.0f}–{r['max']:.0f} €", showarrow=False,
                           xanchor="left", xshift=12, font=dict(color=t["testo"], size=12))
    ui.stile(fig, height=320, margin=dict(l=12, r=14, t=14, b=44), font=dict(size=13))
    fig.update_xaxes(title=dict(text="€2018 per MWh (UE27, 2018)"), range=[0, 205])
    fig.update_yaxes(showgrid=False, automargin=True)
    st.plotly_chart(fig, width="stretch", key="costi_esterni")
    st.caption(
        "Fonte: Trinomics et al. 2020 per la Commissione europea, metodo Environmental Prices, CO2 a 102 €/t. "
        "Per i fossili il clima pesa per oltre il 65%; il particolato è quasi nullo per rinnovabili e nucleare. "
        "In Italia i costi esterni dell'elettricità sono stimati in 17,5 miliardi di euro all'anno. Sono valori medi europei: "
        "non includono il costo di sistema dell'intermittenza (accumuli, reti, riserva), che per le rinnovabili variabili va aggiunto."
    )

    # --- 4. Sussidi ----------------------------------------------------------------------------
    st.subheader("Chi paga: i sussidi ambientalmente dannosi")
    s1, s2, s3 = st.columns(3)
    s1.metric("Sussidi ambientalmente dannosi, 2025", "22,4 mld €", "-1,3 mld sul 2024", delta_color="inverse")
    s2.metric("di cui sui prodotti energetici", "11,6 mld €", delta_color="off", delta_arrow="off")
    s3.metric("che abbassano il costo dei fossili", "20,6 mld €", "dei sussidi analizzati", delta_color="off", delta_arrow="off")
    st.caption(
        "Fonte: MASE, Catalogo dei sussidi ambientalmente dannosi, VIII edizione (luglio 2026), sintesi di Renewable Matter. "
        "Comprende, tra gli altri, le esenzioni sul cherosene per l'aviazione (1,6 mld) e sul trasporto marittimo (612 mln). "
        "Sono costi pagati dalla collettività che il prezzo dell'energia fossile non mostra, come i costi esterni."
    )

    # --- 5. Filiera ----------------------------------------------------------------------------
    st.subheader("La filiera lontana")
    st.markdown(
        "- **Carbone:** per ogni TWh si estraggono circa 1,2 milioni di tonnellate di carbone, più sterili e terreno di "
        "copertura. L'Italia lo importa: miniere, polveri e drenaggi acidi restano nei paesi produttori.\n"
        "- **Gas:** le fughe di metano lungo pozzi e gasdotti possono avvicinare il gas al carbone in termini climatici "
        "se superano qualche punto percentuale. Si verificano lontano, in giacimenti e lungo i gasdotti di importazione.\n"
        "- **Petrolio:** sversamenti, gas flaring e piattaforme hanno impatti gravi sugli ecosistemi marini e costieri, ma "
        "nella base dati mancano ancora numeri armonizzati (è una lacuna dichiarata del progetto).\n"
        "- **Minerali per le rinnovabili:** anche le rinnovabili hanno una filiera lontana (rame, litio, terre rare, silicio). "
        "La differenza è che la loro estrazione avviene **una volta**, per la costruzione, e i materiali sono in gran parte "
        "riciclabili; il combustibile fossile si estrae e si brucia **ogni giorno** per tutta la vita dell'impianto."
    )
    st.caption("Valori e fonti nella pagina *Analisi per fonte* (schede Carbone, Gas naturale, Petrolio) e in *Fonti e metodo*.")
