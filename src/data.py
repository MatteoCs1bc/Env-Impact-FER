"""Caricamento e validazione dei dataset dell'app Esternalità."""

from __future__ import annotations

from pathlib import Path

import pandas as pd

DATA_DIR = Path(__file__).resolve().parent.parent / "data"

# Ordine fisso delle fonti in tutte le viste.
ORDINE_FONTI = [
    "Carbone",
    "Petrolio",
    "Gas naturale",
    "Nucleare",
    "Idroelettrico",
    "Bioenergie",
    "Fotovoltaico",
    "Eolico onshore",
    "Eolico offshore fisso",
    "Eolico offshore galleggiante",
    "Accumuli (BESS)",
    "Reti ed elettrodotti",
]

# Colori per famiglia (palette di riferimento validata, slot 2-1-3-7).
FAMIGLIE = {
    "Fossili": "#eb6834",
    "Programmabili a basse emissioni": "#2a78d6",
    "Rinnovabili variabili": "#1baf7a",
    "Sistema (accumuli e reti)": "#6250d6",
}

ORDINE_DIMENSIONI = [
    "Biodiversità e habitat",
    "Paesaggio e visibilità",
    "Rumore, odori, traffico",
    "Suolo agricolo",
    "Impatti delocalizzati della filiera",
    "Inquinamento e salute",
    "Rischio di incidenti gravi",
    "Irreversibilità e passività di lungo periodo",
]

ORDINE_CATEGORIE = [
    "Emissioni",
    "Materiali ed estrazione",
    "Efficienza",
    "Suolo e acqua",
    "Fauna, flora, biodiversità",
    "Salute e sicurezza",
]

LIVELLI = {0: "Trascurabile", 1: "Basso", 2: "Medio", 3: "Alto"}


def _csv(nome: str) -> pd.DataFrame:
    return pd.read_csv(DATA_DIR / nome, dtype=str, keep_default_na=False)


def carica_indicatori() -> pd.DataFrame:
    df = _csv("indicatori.csv")
    for col in ("min", "centrale", "max"):
        df[col] = pd.to_numeric(df[col].replace("", None), errors="coerce")
    df["anno_dato"] = pd.to_numeric(df["anno_dato"], errors="coerce").astype("Int64")
    # Valori per i grafici: estremi dell'intervallo e punto da mostrare.
    df["lo"] = df["min"].fillna(df["centrale"])
    df["hi"] = df["max"].fillna(df["centrale"])
    df["punto"] = df["centrale"]
    df["etichetta"] = df["fonte"] + " – " + df["tecnologia"]
    df["is_rif"] = df["riferimento"] == "sì"
    return df


def carica_sintesi() -> pd.DataFrame:
    return _csv("sintesi_fonti.csv")


# Indicatore mostrato per primo in ogni categoria.
INDICATORE_PREDEFINITO = {
    "Emissioni": "Gas serra nel ciclo di vita",
    "Materiali ed estrazione": "Minerali critici (totale)",
    "Efficienza": "Capacity factor",
    "Suolo e acqua": "Uso di suolo",
    "Fauna, flora, biodiversità": "Mortalità avifauna",
    "Salute e sicurezza": "Mortalità per TWh",
}


def unita_principale(df: pd.DataFrame, indicatore: str) -> str:
    """Unità usata dai valori di riferimento di un indicatore (la più frequente)."""
    s = df[(df["indicatore"] == indicatore) & df["is_rif"]]["unita"]
    if s.empty:
        s = df[df["indicatore"] == indicatore]["unita"]
    return s.value_counts().index[0]


def carica_bibliografia() -> pd.DataFrame:
    return _csv("fonti_bibliografiche.csv")


def carica_matrice() -> pd.DataFrame:
    df = _csv("matrice_qualitativa.csv")
    df["livello"] = pd.to_numeric(df["livello"]).astype(int)
    return df


def carica_profili() -> pd.DataFrame:
    df = _csv("profilo_fonti.csv")
    for col in ("quota_impatti_locali", "visibilita_locale"):
        df[col] = pd.to_numeric(df[col]).astype(int)
    return df


def carica_conflitti() -> pd.DataFrame:
    df = _csv("conflitti_fvg.csv")
    df["anno"] = pd.to_numeric(df["anno"], errors="coerce").astype("Int64")
    df["lista_temi"] = df["temi"].str.split(";")
    return df


def carica_temi() -> pd.DataFrame:
    return _csv("temi_conflitto.csv")


def carica_consumo_suolo() -> pd.DataFrame:
    df = _csv("consumo_suolo_cause.csv")
    df["ettari"] = pd.to_numeric(df["ettari"])
    return df


def carica_costi_esterni() -> pd.DataFrame:
    df = _csv("costi_esterni.csv")
    for col in ("min", "max"):
        df[col] = pd.to_numeric(df[col])
    return df


def carica_termoelettrico() -> pd.DataFrame:
    df = _csv("termoelettrico_italia.csv")
    for col in ("v2005", "v2024", "emissioni_2024_kt"):
        df[col] = pd.to_numeric(df[col])
    return df


def valida() -> list[str]:
    """Restituisce la lista dei problemi trovati nei dati (vuota se tutto è in ordine)."""
    problemi: list[str] = []
    ind = carica_indicatori()
    bib = carica_bibliografia()
    mat = carica_matrice()
    prof = carica_profili()
    conf = carica_conflitti()
    temi = carica_temi()

    id_fonti = set(bib["fonte_id"])
    fonti_note = set(ORDINE_FONTI)

    if ind["id"].duplicated().any():
        problemi.append(f"ID duplicati in indicatori: {ind.loc[ind['id'].duplicated(), 'id'].tolist()}")

    for _, r in ind.iterrows():
        rif = f"indicatori {r['id']}"
        if r["fonte_id"] not in id_fonti:
            problemi.append(f"{rif}: fonte_id '{r['fonte_id']}' assente dalla bibliografia")
        if r["fonte"] not in fonti_note:
            problemi.append(f"{rif}: fonte energetica '{r['fonte']}' non prevista")
        if r["categoria"] not in ORDINE_CATEGORIE:
            problemi.append(f"{rif}: categoria '{r['categoria']}' non prevista")
        if pd.isna(r["anno_dato"]):
            problemi.append(f"{rif}: anno mancante")
        for campo in ("unita", "regione", "fase", "tipo_dato", "tipo_valore"):
            if not r[campo]:
                problemi.append(f"{rif}: campo '{campo}' vuoto")
        if pd.isna(r["min"]) and pd.isna(r["centrale"]) and pd.isna(r["max"]):
            problemi.append(f"{rif}: nessun valore numerico")
        valori = [v for v in (r["min"], r["centrale"], r["max"]) if not pd.isna(v)]
        if valori != sorted(valori):
            problemi.append(f"{rif}: valori non ordinati (min ≤ centrale ≤ max)")
        if r["tipo_dato"] not in {"letteratura", "misurato", "stima nostra"}:
            problemi.append(f"{rif}: tipo_dato '{r['tipo_dato']}' non valido")
        if r["riferimento"] not in {"sì", ""}:
            problemi.append(f"{rif}: riferimento deve essere 'sì' o vuoto")

    n_rif = ind[ind["is_rif"]].groupby(["fonte", "indicatore", "unita"]).size()
    for chiave in n_rif[n_rif > 1].index:
        problemi.append(f"indicatori: più di un valore di riferimento per {chiave}")

    sint = carica_sintesi()
    for _, r in sint.iterrows():
        if r["fonte"] not in fonti_note:
            problemi.append(f"sintesi: fonte '{r['fonte']}' non prevista")
        if r["categoria"] not in ORDINE_CATEGORIE:
            problemi.append(f"sintesi: categoria '{r['categoria']}' non prevista")
    if sint.duplicated(["fonte", "categoria"]).any():
        problemi.append("sintesi: coppie fonte/categoria duplicate")
    for cat, ind_pred in INDICATORE_PREDEFINITO.items():
        if not ((ind["categoria"] == cat) & (ind["indicatore"] == ind_pred)).any():
            problemi.append(f"indicatore predefinito '{ind_pred}' assente nella categoria {cat}")

    for _, r in mat.iterrows():
        if r["fonte"] not in fonti_note:
            problemi.append(f"matrice: fonte '{r['fonte']}' non prevista")
        if r["dimensione"] not in ORDINE_DIMENSIONI:
            problemi.append(f"matrice: dimensione '{r['dimensione']}' non prevista")
        if r["livello"] not in LIVELLI:
            problemi.append(f"matrice: livello {r['livello']} fuori scala per {r['fonte']}")
        if r["certezza"] not in {"alta", "media", "bassa"}:
            problemi.append(f"matrice: certezza '{r['certezza']}' non valida per {r['fonte']}")
    coppie = mat.groupby(["fonte", "dimensione"]).size()
    if (coppie > 1).any():
        problemi.append(f"matrice: coppie duplicate {coppie[coppie > 1].index.tolist()}")
    attese = len(ORDINE_FONTI) * len(ORDINE_DIMENSIONI)
    if len(coppie) != attese:
        problemi.append(f"matrice: {len(coppie)} celle invece di {attese}")

    if set(prof["fonte"]) != fonti_note:
        problemi.append("profilo_fonti: l'elenco delle fonti non coincide con ORDINE_FONTI")
    if not set(prof["famiglia"]) <= set(FAMIGLIE):
        problemi.append("profilo_fonti: famiglia non prevista")

    temi_noti = set(temi["tema"])
    for _, r in conf.iterrows():
        if r["fonte_app"] not in fonti_note:
            problemi.append(f"conflitti {r['id']}: fonte '{r['fonte_app']}' non prevista")
        for t in r["lista_temi"]:
            if t not in temi_noti:
                problemi.append(f"conflitti {r['id']}: tema '{t}' non definito in temi_conflitto")

    for nome, df in (("consumo_suolo_cause", carica_consumo_suolo()), ("costi_esterni", carica_costi_esterni()),
                     ("termoelettrico_italia", carica_termoelettrico())):
        for fid in set(df["fonte_id"]) - id_fonti:
            problemi.append(f"{nome}: fonte_id '{fid}' assente dalla bibliografia")
    ce = carica_costi_esterni()
    if (ce["min"] > ce["max"]).any():
        problemi.append("costi_esterni: min maggiore di max")
    if not set(ce["famiglia"]) <= set(FAMIGLIE):
        problemi.append("costi_esterni: famiglia non prevista")

    return problemi
