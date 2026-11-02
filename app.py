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
    [
        st.Page("pages/scheda.py", title="Analisi per fonte", icon=":material/description:", default=True),
        st.Page("pages/confronto.py", title="Confronto per indicatore", icon=":material/bar_chart:"),
        st.Page("pages/suolo.py", title="Consumo di suolo", icon=":material/landscape:"),
        st.Page("pages/fossili.py", title="Le esternalità del fossile", icon=":material/factory:"),
        st.Page("pages/conflitti.py", title="Conflitti in FVG", icon=":material/location_on:"),
        st.Page("pages/fonti.py", title="Fonti e metodo", icon=":material/menu_book:"),
    ]
)
pagine.run()
