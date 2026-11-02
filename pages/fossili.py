import streamlit as st

from src import ui
from src.sezioni import compagnie, quadro_fossili, shale

st.title("Le esternalità che non vediamo: il fossile")
st.markdown(
    "Il dibattito locale si concentra sugli impatti delle rinnovabili, perché sono **vicini e visibili**: il campo "
    "fotovoltaico accanto a casa, la pala sul crinale. Gli impatti dei combustibili fossili sono spesso più grandi, ma "
    "ricadono **lontano** (miniere e giacimenti all'estero), sono **diffusi** (inquinamento dell'aria, clima) o sono "
    "**già sedimentati** nel paesaggio da decenni. Questa pagina mette gli stessi occhiali su entrambi."
)

quadro, scisti, aziende = st.tabs(["Quadro generale", "Shale gas e olio di scisto", "Le compagnie: danni e responsabilità"])
with quadro:
    quadro_fossili.mostra()
with scisti:
    shale.mostra()
with aziende:
    compagnie.mostra()

ui.piede()
