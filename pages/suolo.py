import plotly.graph_objects as go
import streamlit as st

from src import data as D
from src import ui

d = ui.dati()
suolo, ind, prof, bib = d["suolo"], d["indicatori"], d["profili"], d["bibliografia"]
t = ui.tema()

st.title("Consumo di suolo")
st.markdown(
    "Il consumo di suolo agricolo è il primo motivo di protesta contro il fotovoltaico in FVG. "
    "Qui lo guardiamo da tre lati: **quanto suolo si consuma ogni anno in Italia e per cosa** (ISPRA), "
    "**quanto suolo serve per ogni MWh** a ciascuna fonte, compresa la parte che sta all'estero (LCA), "
    "e **cosa succede in FVG**."
)

# --- 1. Il quadro nazionale -------------------------------------------------------------
st.subheader("Italia, 2025: quanto suolo si consuma e per cosa")
m1, m2, m3, m4 = st.columns(4)
m1.metric("Nuovo consumo lordo 2025", "10.200 ha", "+22% sul 2024", delta_color="inverse")
m2.metric("Consumo netto (dopo i ripristini)", "≈ 9.500 ha", "746 ha ripristinati", delta_color="off", delta_arrow="off")
m3.metric("Suolo consumato in totale", "7,19%", "21.644 km² del territorio", delta_color="off", delta_arrow="off")
m4.metric("Fotovoltaico a terra nel 2025", "2.798 ha", "≈ 27% del nuovo consumo", delta_color="off", delta_arrow="off")
st.caption("Fonte: ISPRA-SNPA, Rapporto consumo di suolo 2026 (dati 2025), comunicato stampa e slide di presentazione.")

s = suolo.sort_values("ettari")
colori = [
    ui.colore_famiglia("Rinnovabili variabili") if g == "Energia" else t["altre"] for g in s["gruppo"]
]
fig = go.Figure(go.Bar(
    y=s["causa"], x=s["ettari"], orientation="h", marker=dict(color=colori),
    text=[ui.fmt(v) + " ha" for v in s["ettari"]], textposition="outside", cliponaxis=False,
    textfont=dict(color=t["testo"]), customdata=s["note"],
    hovertemplate="<b>%{y}</b><br>%{x:,.0f} ha nel 2025<br>%{customdata}<extra></extra>",
))
ui.stile(fig, height=380, margin=dict(l=12, r=14, t=14, b=44), font=dict(size=13), showlegend=False)
fig.update_xaxes(title=dict(text="ettari di nuovo consumo nel 2025"), range=[0, s["ettari"].max() * 1.18])
fig.update_yaxes(showgrid=False)
st.plotly_chart(fig, width="stretch", key="suolo_cause")
st.caption(
    "In verde le voci legate alla produzione di energia. Le voci vengono da tavole diverse del rapporto e non si "
    "sommano esattamente al totale: per esempio, parte dei cantieri diventerà edifici, strade o logistica."
)

with st.container(border=True):
    st.markdown("**Cosa dicono questi numeri, senza sconti a nessuno**")
    st.markdown(
        "- **Il fotovoltaico a terra pesa davvero.** Con circa 2.800 ettari è la seconda voce del 2025 e "
        "quasi 40 volte il valore del 2021. La preoccupazione per il suolo agricolo è quindi un **impatto misurato**, "
        "non un'esagerazione.\n"
        "- **Ma è consumo reversibile.** ISPRA lo classifica così: a fine vita i moduli si smontano e il suolo, "
        "se non è stato impermeabilizzato, torna coltivabile. Edifici, piazzali e strade restano per decenni.\n"
        "- **L'eolico conta poco in superficie** (118 ha), anche se pesa di più sul paesaggio e, in quota, sugli habitat.\n"
        "- **Esiste un'alternativa senza consumo di suolo.** ISPRA stima 1.116 km² di tetti utilizzabili per il "
        "fotovoltaico: circa 40 volte la superficie occupata dal FV a terra nel 2025. Agrivoltaico e aree idonee "
        "(cave dismesse, aree industriali) riducono il conflitto con l'agricoltura.\n"
        "- **Il fossile non compare quasi mai in questi conti.** Raffinerie, depositi, centrali e oleodotti sono stati "
        "costruiti decenni fa e stanno nello stock storico, non nel flusso annuale. Le miniere di carbone e i giacimenti "
        "sono all'estero. Il loro suolo c'è, ma non lo vediamo qui: per vederlo serve il confronto per MWh, sotto."
    )

# --- 2. Per MWh ----------------------------------------------------------------------------
st.subheader("Quanto suolo serve per produrre un MWh")
st.markdown(
    "Il confronto per MWh conta tutto il ciclo di vita, comprese miniere e giacimenti, ovunque si trovino. "
    "È il modo per mettere sulla stessa scala impatti visibili (un campo FV qui) e invisibili (una miniera in Colombia)."
)
indicatore = "Uso di suolo"
unita = D.unita_principale(ind, indicatore)
rif = ind[(ind["indicatore"] == indicatore) & ind["is_rif"] & (ind["unita"] == unita)]
log = st.toggle("Scala logaritmica", value=ui.serve_log(rif), key="suolo_log")
st.plotly_chart(ui.grafico_riferimento(rif, prof, bib, unita, log), width="stretch", key="suolo_mwh")
ui.legenda_famiglie()
st.caption(
    "Fonte: Lovering et al. 2022, mediane tra studi su impianti reali. Passa sopra una riga per tecnologia e perimetro."
)
st.markdown(
    "Il risultato va detto chiaramente: **per MWh il fotovoltaico a terra occupa più suolo del carbone** "
    "(20 contro 10 m²·anno/MWh) e del gas (4,1). Le biomasse dedicate sono di gran lunga le più esigenti (580). "
    "Cambia però la *qualità* del suolo occupato: per il carbone più di metà dell'impronta sta in miniere a cielo aperto, "
    "spesso all'estero e con ripristini lenti o assenti; per il gas oltre il 90% sta nei giacimenti. L'impronta del "
    "fotovoltaico è quasi tutta nel campo, quindi **vicina e visibile**, ma reversibile e in parte condivisibile "
    "(agrivoltaico, pascolo, prati sotto i moduli). Per l'eolico l'impronta diretta è minima (1,3); l'area del parco "
    "con la spaziatura tra le torri (120) resta in gran parte coltivabile."
)

# --- 3. FVG ---------------------------------------------------------------------------------
st.subheader("Friuli Venezia Giulia")
f1, f2, f3 = st.columns(3)
f1.metric("Suolo consumato", "63.603 ha", "8,05% del territorio", delta_color="off", delta_arrow="off")
f2.metric("Nuovo consumo netto 2024", "+169 ha", "+0,27% (Italia +0,37%)", delta_color="off", delta_arrow="off")
f3.metric("Consumo pro capite di elettricità", "7.957 kWh/ab", "il più alto d'Italia (media 4.966)", delta_color="off", delta_arrow="off")
st.caption(
    "Fonti: ARPA FVG, Terra rara 2025 (dati 2024); ISPRA r430/2026 per i consumi elettrici. "
    "Il FVG ha una quota di suolo consumato superiore alla media nazionale ma una crescita annua più lenta. "
    "Il consumo elettrico pro capite molto alto, legato all'industria, è il contesto in cui leggere la domanda di nuovi impianti."
)
st.info(
    "Manca ancora la ripartizione regionale per causa (quanto del consumo FVG è dovuto al fotovoltaico a terra). "
    "Il rapporto ISPRA completo è nel Drive ma il PDF supera i limiti di lettura: se carichi il capitolo su FV ed energia "
    "o le tabelle regionali, si possono aggiungere."
)

ui.piede()
