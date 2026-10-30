"""Esternalità delle fonti energetiche – app Streamlit.

Avvio: streamlit run app.py
"""

import streamlit as st

st.set_page_config(
    page_title="Esternalità delle fonti energetiche",
    page_icon="⚡",
    layout="wide",
)

pagine = st.navigation(
    {
        "Confronto": [
            st.Page("pages/panoramica.py", title="Panoramica", icon=":material/dashboard:", default=True),
            st.Page("pages/confronto.py", title="Confronto per indicatore", icon=":material/bar_chart:"),
            st.Page("pages/scheda.py", title="Scheda per fonte", icon=":material/description:"),
            st.Page("pages/matrice.py", title="Impatti qualitativi", icon=":material/grid_view:"),
        ],
        "Accettazione sociale": [
            st.Page("pages/conflitti.py", title="Conflitti in FVG", icon=":material/location_on:"),
        ],
        "Metodo": [
            st.Page("pages/fonti.py", title="Fonti e metodo", icon=":material/menu_book:"),
        ],
    }
)
pagine.run()
