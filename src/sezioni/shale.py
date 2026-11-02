import numpy as np
import plotly.graph_objects as go
import streamlit as st

from src import ui


def mostra():
    """Sezione su shale gas, tight oil e scisti bituminosi."""
    d = ui.dati()
    imp = d["shale"]
    t = ui.tema()
    FOSSILE = ui.colore_famiglia("Fossili")

    st.markdown(
        "In Italia non si pratica la fratturazione idraulica (*fracking*), e in diversi paesi europei è vietata "
        "(in Francia dal 2011). Ma una parte del gas e del petrolio che consumiamo viene da lì: gli impatti "
        "restano negli Stati Uniti, vicino ai pozzi, e non entrano nel dibattito locale sugli impianti."
    )
    st.caption(
        "Due cose diverse con nomi simili. **Shale gas** e **tight oil** (o *shale oil*) sono gas e greggio intrappolati in "
        "rocce poco permeabili, estratti con pozzi orizzontali e fratturazione idraulica: è il caso degli Stati Uniti. "
        "Gli **scisti bituminosi** (*oil shale*) sono rocce che contengono cherogene: si estraggono in miniera e si bruciano "
        "o si scaldano per ricavarne olio, come in Estonia. In fondo alla pagina c'è una sezione su questi ultimi."
    )

    # --- 1. Quote importate --------------------------------------------------------------
    st.subheader("Quanto shale arriva in Italia")
    righe = []
    for _, r in imp.iterrows():
        lo = round(r["quota_usa_min"] * r["quota_shale_usa"] / 100, 1)
        hi = round(r["quota_usa_max"] * r["quota_shale_usa_max"] / 100, 1)
        righe.append((r, lo, hi))

    cols = st.columns(len(righe))
    for c, (r, lo, hi) in zip(cols, righe):
        with c:
            with st.container(border=True):
                st.markdown(f"**{r['combustibile']}**, {r['anno']}")
                st.metric("Quota stimata da fracking sulle importazioni", f"{ui.fmt(lo)}–{ui.fmt(hi)}%")
                st.markdown(
                    f"- Dagli Stati Uniti: **{ui.fmt(r['quota_usa_min'])}–{ui.fmt(r['quota_usa_max'])}%** delle importazioni\n"
                    f"- Quota shale/tight nella produzione USA: **{ui.fmt(r['quota_shale_usa'])}%**"
                    + (f" (fino al {ui.fmt(r['quota_shale_usa_max'])}% per il greggio esportato)"
                       if r["quota_shale_usa_max"] != r["quota_shale_usa"] else "")
                )
                st.caption(r["note"])

    fig = go.Figure()
    for r, lo, hi in righe[::-1]:
        usa_hi = r["quota_usa_max"]
        fig.add_trace(go.Bar(
            y=[r["combustibile"]], x=[usa_hi], orientation="h", marker=dict(color=t["altre"]),
            name="Dagli Stati Uniti", showlegend=r is righe[0][0],
            hovertemplate=f"Dagli USA: fino al {ui.fmt(usa_hi)}%<extra></extra>",
        ))
        fig.add_trace(go.Scatter(
            x=[lo, hi], y=[r["combustibile"]] * 2, mode="lines", line=dict(color=FOSSILE, width=16),
            name="Da fracking (stima)", showlegend=r is righe[0][0],
            hovertemplate=f"Da fracking: {ui.fmt(lo)}–{ui.fmt(hi)}%<extra></extra>",
        ))
        fig.add_annotation(x=usa_hi, y=r["combustibile"], text=f"da fracking {ui.fmt(lo)}–{ui.fmt(hi)}%",
                           showarrow=False, xanchor="left", xshift=10, font=dict(color=t["testo"], size=12))
    ui.stile(fig, height=210, margin=dict(l=12, r=14, t=14, b=44), font=dict(size=13), barmode="overlay")
    fig.update_layout(legend=dict(orientation="h", y=1.25, x=0))
    fig.update_xaxes(title=dict(text="% delle importazioni italiane"), range=[0, 30])
    fig.update_yaxes(showgrid=False)
    st.plotly_chart(fig, width="stretch", key="quote_shale")
    st.markdown(
        "In parole semplici: **tra un metro cubo di gas su nove e uno su otto** consumato in Italia nel 2025 viene da pozzi fratturati "
        "negli Stati Uniti, arrivato come GNL. Per il greggio la quota è più bassa, **tra uno su venti e uno su undici**. "
        "Sono **stime nostre**: moltiplicano la quota degli Stati Uniti nelle importazioni per la quota di shale nella "
        "produzione statunitense, perché le statistiche doganali non distinguono il gas o il greggio per tipo di giacimento. "
        "Il gas di Algeria, Azerbaigian, Qatar e Norvegia è convenzionale."
    )
    st.caption(
        "Fonti: ARERA, Relazione annuale 2026 (dati provvisori MASE, via luce-gas.it); Snam 2025 sui carichi di GNL; "
        "UNEM/MASE per il greggio; EIA per le quote di shale gas (79%, 2024) e tight oil (64%, 2023). I dati sulle "
        "importazioni sono ripresi da fonti secondarie: vanno verificati sui documenti originali prima di citarli."
    )

    # --- 2. Metano -------------------------------------------------------------------------
    st.subheader("Il nodo del metano: quanto pesa il gas di scisto sul clima")
    st.markdown(
        "Il metano che sfugge da pozzi, compressori e gasdotti è un gas serra molto più potente della CO2 nel breve periodo. "
        "Con campagne aeree su quasi un milione di siti, **Sherwin et al. (Nature, 2024)** hanno misurato perdite medie del "
        "**2,95% del gas prodotto** in sei regioni degli Stati Uniti, circa **tre volte** l'inventario ufficiale, con un "
        "intervallo **dallo 0,75% al 9,63%**. Le perdite più alte sono nelle regioni petrolifere in rapida espansione, "
        "dove il gas è un sottoprodotto del greggio di scisto e spesso viene sfiatato o bruciato in torcia."
    )
    st.markdown("**Calcola le emissioni di un kWh prodotto con gas importato (stima nostra)**")
    c1, c2, c3, c4 = st.columns(4)
    perdita = c1.slider("Perdite di metano (% del gas prodotto)", 0.0, 10.0, 2.95, 0.05)
    orizzonte = c2.radio("Orizzonte del metano", ["100 anni", "20 anni"], horizontal=True,
                         help="GWP del metano fossile secondo IPCC AR6: 29,8 a 100 anni, 82,5 a 20 anni.")
    rendimento = c3.slider("Rendimento della centrale (%)", 40, 62, 50, 1,
                           help="50% è il valore UNECE 2022 per un ciclo combinato.")
    gnl = c4.toggle("Arriva come GNL", value=True,
                    help="Aggiunge circa 8,7 gCO2eq per MJ di gas per liquefazione, trasporto via nave e rigassificazione.")

    GWP = {"100 anni": 29.8, "20 anni": 82.5}[orizzonte]
    COMB, CATENA_GNL, CH4_PER_MJ = 56.1, 8.7, 20.0  # gCO2/MJ, gCO2eq/MJ, g di CH4 per MJ


    def emissioni(f, gwp=GWP, eta=rendimento / 100, con_gnl=gnl):
        metano = f / (1 - f) * CH4_PER_MJ * gwp
        return (COMB + (CATENA_GNL if con_gnl else 0) + metano) / eta * 3.6, metano / eta * 3.6


    tot, quota_ch4 = emissioni(perdita / 100)
    m1, m2, m3 = st.columns(3)
    m1.metric("Emissioni per kWh", f"{ui.fmt(tot)} gCO2eq")
    m2.metric("di cui dal metano disperso", f"{ui.fmt(quota_ch4)} g", f"{ui.fmt(quota_ch4 / tot * 100)}% del totale",
              delta_color="off", delta_arrow="off")
    m3.metric("Carbone (UNECE, ciclo di vita)", "751–1.095 g", "a 100 anni", delta_color="off", delta_arrow="off")

    xs = np.linspace(0, 10, 101)
    fig = go.Figure()
    fig.add_hrect(y0=751, y1=1095, fillcolor=t["altre"], opacity=0.35, line_width=0)
    fig.add_annotation(x=0.2, y=1095, text="Carbone, ciclo di vita (UNECE, 100 anni)", showarrow=False,
                       xanchor="left", yanchor="bottom", font=dict(color=t["secondario"], size=12))
    for oriz, dash in (("100 anni", "solid"), ("20 anni", "dot")):
        ys = [emissioni(x / 100, gwp={"100 anni": 29.8, "20 anni": 82.5}[oriz])[0] for x in xs]
        fig.add_trace(go.Scatter(
            x=xs, y=ys, mode="lines", name=f"Gas, metano a {oriz}",
            line=dict(color=FOSSILE, width=3 if oriz == orizzonte else 2, dash=dash),
            hovertemplate="Perdite %{x:.1f}% → %{y:.0f} gCO2eq/kWh<extra></extra>",
        ))
    for x, testo in ((0.75, "0,75%"), (2.95, "media 2,95%"), (9.63, "9,63%")):
        fig.add_vline(x=x, line=dict(color=t["assi"], width=1, dash="dash"))
        fig.add_annotation(x=x, y=0, yref="paper", text=testo, showarrow=False, yanchor="bottom", xanchor="left",
                           xshift=4, font=dict(color=t["secondario"], size=11))
    fig.add_trace(go.Scatter(x=[perdita], y=[tot], mode="markers", marker=dict(size=13, color=FOSSILE,
                             line=dict(width=2, color=t["pannello"])), name="La tua scelta", hoverinfo="skip"))
    ui.stile(fig, height=380, margin=dict(l=12, r=14, t=14, b=44), font=dict(size=13))
    fig.update_layout(legend=dict(orientation="h", y=1.12, x=0))
    fig.update_xaxes(title=dict(text="perdite di metano lungo la filiera (% del gas prodotto)"), range=[0, 10])
    fig.update_yaxes(title=dict(text="gCO2eq/kWh"), rangemode="tozero")
    st.plotly_chart(fig, width="stretch", key="calc_metano")
    st.caption(
        "Stima nostra, semplificata. Combustione 56,1 gCO2/MJ (fattore IPCC per il gas naturale); metano 20 g per MJ; GWP "
        "IPCC AR6; catena del GNL 8,7 gCO2eq/MJ, cioè la metà dei 17,4 g/MJ dalla culla al cancello stimati da Tagliaferri "
        "et al. 2017 per il GNL importato nel Regno Unito (citati in Wójcik et al. 2022). Le linee tratteggiate sono le "
        "perdite misurate da Sherwin et al. 2024 nelle sei regioni. Il valore del carbone è a 100 anni: a 20 anni sale "
        "anche quello, per il metano delle miniere. La stima non include le perdite nei gasdotti di trasporto e "
        "distribuzione."
    )
    with st.container(border=True):
        st.markdown(
            "**Come leggerlo.** Con le perdite medie misurate, il gas di scisto importato come GNL resta sotto il carbone "
            "a 100 anni, ma il margine si riduce molto rispetto al gas convenzionale via tubo. Con l'orizzonte a 20 anni "
            "o nelle regioni con più perdite si avvicina al carbone o lo supera. Il dibattito scientifico è aperto: "
            "Howarth (2024) sostiene che il GNL statunitense sia peggiore del carbone a 20 anni; altri studi, con "
            "ipotesi diverse sulle perdite, trovano valori più bassi. Il punto robusto è che **il risultato dipende da "
            "perdite che avvengono lontano, che non vediamo e che gli inventari ufficiali sottostimano**."
        )

    # --- 3. Impatti locali ---------------------------------------------------------------
    st.subheader("Gli impatti vicino ai pozzi")
    st.caption("Impatti che ricadono sulle comunità americane, non su chi consuma il gas in Italia.")
    a, b = st.columns(2)
    with a:
        with st.container(border=True):
            st.markdown("**Acqua**")
            st.markdown(
                "Il fluido di fratturazione è al 99% acqua e sabbia, più additivi chimici. Tra il 2011 e il 2016 l'acqua "
                "usata **per pozzo** è aumentata **fino al 770%** e le acque di scarto del primo anno **fino al 1.440%**, "
                "perché i pozzi sono sempre più lunghi (Kondash et al. 2018, oltre 12.000 pozzi). Le acque di risalita "
                "sono salate, possono contenere metalli e radioattività naturale e vengono in gran parte reiniettate nel "
                "sottosuolo."
            )
        with st.container(border=True):
            st.markdown("**Salute**")
            st.markdown(
                "Su oltre 1,1 milioni di nascite in Pennsylvania (2004–2013), le madri che vivevano **entro 1 km** da un "
                "pozzo fratturato avevano una probabilità di **basso peso alla nascita più alta del 25%**; gli effetti si "
                "vedono fino a 3 km (Currie, Greenstone e Meckel 2017). È un impatto **misurato**, con un disegno di "
                "studio robusto."
            )
    with b:
        with st.container(border=True):
            st.markdown("**Terremoti indotti**")
            st.markdown(
                "In Oklahoma la reiniezione delle acque di scarto di petrolio e gas ha fatto passare i terremoti di "
                "magnitudo 3 o più da **circa uno all'anno** prima del 2009 a **due o più al giorno** nel 2015, fino al "
                "terremoto di magnitudo 5,8 di Pawnee nel 2016 (Stanford, studi di Walsh e Zoback). Dopo i limiti alla "
                "reiniezione i terremoti sono diminuiti."
            )
        with st.container(border=True):
            st.markdown("**Suolo, habitat, aria e traffico**")
            st.markdown(
                "Ogni piazzola richiede strade, vasche, condotte e migliaia di viaggi di camion; migliaia di pozzi "
                "frammentano habitat e paesaggi agricoli. Le torce e lo sfiato del gas associato al greggio emettono "
                "metano, composti organici volatili e ossidi di azoto. Nella base non abbiamo ancora numeri armonizzati "
                "per questi impatti: sono **plausibili e documentati**, ma non quantificati qui."
            )

    # --- 4. Scisti bituminosi ------------------------------------------------------------
    st.subheader("Gli scisti bituminosi (oil shale): il caso dell'Estonia")
    st.markdown(
        "L'Estonia, con meno dell'1% delle riserve mondiali, estrae circa metà dello scisto bituminoso del mondo e per decenni "
        "ne ha ricavato quasi tutta la sua elettricità. Secondo l'inventario di **Gavrilova et al. (2010)**, che è nel Drive:\n"
        "- le centrali di Narva emettevano **289–333 kg di CO2 per GJ di energia generata**, cioè circa **1.040–1.200 g "
        "per kWh**, più del carbone;\n"
        "- la produzione di olio per pirolisi recupera solo il **55–66%** dell'energia contenuta nella roccia;\n"
        "- ceneri e semi-coke finiscono in grandi discariche che, con le piogge, rilasciano inquinanti in acque e suoli.\n\n"
        "L'olio di scisto estone non risulta tra le importazioni italiane: lo riportiamo come caso limite della filiera fossile."
    )
    st.caption(
        "Il valore per kWh è una nostra conversione (1 GJ = 0,278 MWh) delle emissioni per GJ generato riportate dallo studio, "
        "che include anche il calore; dati 2002–2007."
    )
