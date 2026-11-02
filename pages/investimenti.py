import plotly.graph_objects as go
import streamlit as st

from src import ui

d = ui.dati()
inv = d["investimenti"]
t = ui.tema()
FOSSILE = ui.colore_famiglia("Fossili")
VERDE = ui.colore_famiglia("Rinnovabili variabili")

st.title("Investimenti e profitti")
st.markdown(
    "Le esternalità dicono chi paga i danni. Questa pagina guarda l'altra faccia: **dove vanno gli investimenti**, "
    "**quanto costano** le diverse fonti e **chi ha guadagnato** dalla crisi energetica del 2022. Le cifre sono in "
    "dollari o euro correnti, con fonte e anno."
)

# --- 1. Investimenti mondiali ---------------------------------------------------------------
st.subheader("Dove vanno gli investimenti nel mondo (2026)")
m1, m2, m3 = st.columns(3)
m1.metric("Investimenti energetici totali", "3.400 mld $", "+5% sul 2025", delta_color="off", delta_arrow="off")
m2.metric("Energia pulita", "≈ 2.200 mld $", "rinnovabili, nucleare, reti, accumuli, efficienza…",
          delta_color="off", delta_arrow="off")
m3.metric("Petrolio, gas e carbone", "≈ 1.200 mld $", "carbone ai massimi dal 2012", delta_color="off", delta_arrow="off")

s = inv.sort_values("miliardi_usd")
fig = go.Figure(go.Bar(
    y=s["voce"], x=s["miliardi_usd"], orientation="h",
    marker=dict(color=[ui.colore_famiglia(f) for f in s["famiglia"]]),
    text=[f"{ui.fmt(v)} mld $" for v in s["miliardi_usd"]], textposition="outside", cliponaxis=False,
    textfont=dict(color=t["testo"]), customdata=s["note"],
    hovertemplate="<b>%{y}</b><br>%{x} miliardi di dollari<br>%{customdata}<extra></extra>",
))
ui.stile(fig, height=380, margin=dict(l=12, r=14, t=14, b=44), font=dict(size=13), showlegend=False)
fig.update_xaxes(title=dict(text="miliardi di dollari, stima IEA per il 2026"), range=[0, 600])
fig.update_yaxes(showgrid=False)
st.plotly_chart(fig, width="stretch", key="inv_voci")
ui.legenda_famiglie()
st.caption(
    "Fonte: IEA, World Energy Investment 2026, dalle sintesi giornalistiche del rapporto (da verificare sul testo IEA). "
    "Sono le voci principali e non sommano ai totali: mancano, per esempio, reti elettriche, veicoli elettrici, "
    "raffinazione e centrali fossili. Il petrolio scende per il terzo anno, il gas sale ai massimi da dieci anni "
    "trainato dal GNL statunitense."
)

# --- 2. Costi ------------------------------------------------------------------------------
st.subheader("Quanto costano le fonti")
c1, c2, c3 = st.columns(3)
c1.metric("Fotovoltaico, nuovi impianti 2024", "0,043 $/kWh", "−41% rispetto al fossile più economico",
          delta_color="off", delta_arrow="off")
c2.metric("Eolico onshore, nuovi impianti 2024", "0,034 $/kWh", "−53% rispetto al fossile più economico",
          delta_color="off", delta_arrow="off")
c3.metric("Nuovi progetti rinnovabili più economici del fossile", "91%", "nel 2024", delta_color="off",
          delta_arrow="off")
st.caption(
    "Fonte: IRENA, Renewable Power Generation Costs in 2024 (luglio 2025). Sono costi livellati medi mondiali: "
    "non includono il costo di sistema dell'intermittenza (accumuli, reti, riserva), che va aggiunto per un confronto "
    "completo, né i costi esterni, che invece pesano molto di più sul fossile (vedi *Le esternalità del fossile*)."
)

# --- 3. Extraprofitti -----------------------------------------------------------------------
st.subheader("Gli extraprofitti del fossile")
st.markdown(
    "Con l'aumento dei prezzi dopo l'invasione russa dell'Ucraina, l'industria del petrolio e del gas ha avuto i "
    "guadagni più alti della sua storia. Quei soldi sono arrivati in buona parte dalle bollette e dai carburanti "
    "pagati da famiglie e imprese, e sono andati soprattutto agli azionisti."
)
e1, e2, e3 = st.columns(3)
e1.metric("Reddito dell'industria di petrolio e gas, 2022", "≈ 4.000 mld $", "IEA", delta_color="off",
          delta_arrow="off")
e2.metric("Restituiti agli azionisti 2020–2022", "1.500 mld $", "dividendi e riacquisto di azioni",
          delta_color="off", delta_arrow="off")
e3.metric("Investimenti upstream fuori dal fossile, 2022", "≈ 4%", "per oltre metà bioenergie",
          delta_color="off", delta_arrow="off")
st.caption("Fonti: Fatih Birol (IEA), febbraio 2023; IEA, The Oil and Gas Industry in Net Zero Transitions (2023).")

g1, g2 = st.columns([3, 2])
with g1:
    fig = go.Figure()
    for nome, v, col in (("Profitti", 467, FOSSILE), ("Dividendi e riacquisti di azioni", 444, t["altre"])):
        fig.add_trace(go.Bar(
            x=[v], y=[nome], orientation="h", marker=dict(color=col), text=[f"{v} mld $"], textposition="outside",
            cliponaxis=False, textfont=dict(color=t["testo"]), hovertemplate=f"{nome}: {v} miliardi di dollari<extra></extra>",
            showlegend=False,
        ))
    ui.stile(fig, height=200, margin=dict(l=12, r=14, t=14, b=44), font=dict(size=13))
    fig.update_xaxes(title=dict(text="miliardi di dollari, febbraio 2022 – gennaio 2026"), range=[0, 560])
    fig.update_yaxes(showgrid=False, autorange="reversed")
    st.plotly_chart(fig, width="stretch", key="profitti_major")
    st.caption(
        "Shell, BP, Chevron, ExxonMobil e TotalEnergies dall'inizio della guerra in Ucraina. Fonte: analisi di Global "
        "Witness sui bilanci (The Independent, febbraio 2026). Nel solo 2022 le cinque hanno superato i 200 miliardi "
        "di dollari di profitti (Visual Capitalist 2023)."
    )
with g2:
    with st.container(border=True):
        st.markdown("**Eni, 2022**")
        st.markdown(
            "- Utile netto: **13,8 miliardi di euro**, circa 9 in più del 2021\n"
            "- Agli azionisti: dividendo +7% e **riacquisto di azioni per 2,2 miliardi**\n"
            "- Piano 2023–2026: **37 miliardi** di investimenti, con 6–6,5 miliardi l'anno nell'upstream; "
            "per le rinnovabili (Plenitude) obiettivo di oltre 7 GW al 2026"
        )
        st.caption("Fonte: FIRSTonline, febbraio 2023, sui conti e sul piano Eni.")

with st.container(border=True):
    st.markdown("**La tassa italiana sugli extraprofitti**")
    st.markdown(
        "- **2022, contributo straordinario** (governo Draghi): 25% sull'aumento del saldo IVA tra ottobre 2021 e "
        "aprile 2022. Gettito atteso: **oltre 10 miliardi**. A fine agosto 2022 ne era arrivato **circa uno**: molte "
        "aziende non hanno pagato e una ventina ha fatto ricorso al TAR.\n"
        "- **2023, contributo di solidarietà** (legge di bilancio): 50% sugli utili oltre il 10% della media dei "
        "quattro anni precedenti. Gettito stimato: **circa 2,5 miliardi**.\n\n"
        "Il gettito effettivamente incassato a fine contenzioso è da verificare (Corte dei conti, MEF)."
    )
    st.caption("Fonti: La Notizia, 30 agosto 2022; L'Adige, 29 novembre 2022.")

# --- 4. Sussidi e finanza --------------------------------------------------------------------
st.subheader("Sussidi e banche")
f1, f2, f3 = st.columns(3)
f1.metric("Sussidi al consumo di fossili nel mondo, 2022", "> 1.000 mld $", "primo superamento", delta_color="off",
          delta_arrow="off")
f2.metric("Sussidi ambientalmente dannosi in Italia, 2025", "22,4 mld €", "di cui 11,6 sui prodotti energetici",
          delta_color="off", delta_arrow="off")
f3.metric("Finanziamenti delle banche alle fossili, 2024", "869 mld $", "65 banche; 7.900 mld dal 2016",
          delta_color="off", delta_arrow="off")
st.markdown(
    "Tra le banche italiane, nel 2024 **UniCredit** ha finanziato aziende fossili per **6,2 miliardi di dollari** "
    "(71,8 dal 2016) e **Intesa Sanpaolo** per **5 miliardi** (51,7 dal 2016)."
)
st.caption(
    "Fonti: IEA 2023 sui sussidi al consumo; MASE, Catalogo SAD 2026; Banking on Climate Chaos 2025, sintesi di Valori.it."
)

# --- 5. Lock-in ----------------------------------------------------------------------------
st.subheader("Contratti che durano decenni")
st.markdown(
    "Il 16 luglio 2025 Eni ha firmato un **accordo ventennale** con Venture Global per l'acquisto di GNL statunitense "
    "(ANSA). Contratti e infrastrutture di questa durata legano il sistema al gas, e quindi allo shale gas americano "
    "e alle sue perdite di metano, ben oltre il 2040."
)

with st.container(border=True):
    st.markdown(
        "**Come leggere questa pagina.** Una parte degli investimenti nel petrolio e nel gas serve a compensare il "
        "declino dei giacimenti esistenti finché la domanda non cala, e le rinnovabili richiedono investimenti in reti "
        "e accumuli che il costo livellato non mostra. Ma il quadro è chiaro: il fossile genera profitti molto alti, li "
        "distribuisce soprattutto agli azionisti e lascia alla collettività i costi esterni e i sussidi. Le rinnovabili "
        "costano meno per kWh ma portano gli impatti vicino a chi le vede: è questa la differenza che va spiegata nel "
        "dibattito locale."
    )

ui.piede()
