# Esternalità delle fonti energetiche

App Streamlit che mette a confronto gli impatti e le esternalità delle fonti di elettricità lungo tutto il ciclo di vita (front end, esercizio, back end) e li collega ai conflitti locali in Friuli Venezia Giulia.

Fa parte del progetto **ESTERNALITÀ**, filone Social Acceptance / POWERUP.

## Cosa contiene

| Pagina | Cosa mostra |
|---|---|
| Panoramica | Quanti dati ci sono per fonte e categoria, e dove mancano |
| Confronto per indicatore | Un indicatore alla volta (gas serra, uso di suolo, materiali, mortalità…), intervalli min–max, fonte di ogni numero |
| Scheda per fonte | Indicatori divisi per fase del ciclo di vita, dove ricadono gli impatti, classificazione PPE, conflitti collegati |
| Impatti qualitativi | Matrice fonti × impatti non misurabili (biodiversità, paesaggio, odori…) e grafico dell'asimmetria spaziale |
| Conflitti in FVG | I 21 casi di *Local opposition.xlsx*, motivo per motivo, con l'evidenza disponibile |
| Fonti e metodo | Bibliografia, regole, cautele, lacune |

Fonti energetiche: carbone, petrolio, gas naturale, nucleare, idroelettrico, bioenergie, fotovoltaico, eolico onshore, eolico offshore fisso e galleggiante, accumuli (BESS), reti ed elettrodotti.

## Avvio in locale

```bash
python -m venv .venv
source .venv/bin/activate        # su Windows: .venv\Scripts\activate
pip install -r requirements.txt
streamlit run app.py
```

L'app si apre su http://localhost:8501.

## Pubblicazione su Streamlit Community Cloud

1. Carica il repository su GitHub.
2. Vai su https://share.streamlit.io, collega l'account GitHub e scegli **New app**.
3. Seleziona il repository, il ramo `main` e il file `app.py`.

## Struttura

```
app.py                       navigazione tra le pagine
pages/                       una pagina per file
src/data.py                  caricamento e validazione dei dati
src/ui.py                    grafici e tabelle condivisi
data/                        tutti i dati, in CSV
scripts/valida_dati.py       controllo dei dati
tests/                       test dei dati e delle pagine
```

## I dati

Tutti i dati sono file CSV in `data/`, modificabili anche con Excel o Google Sheets (salvando in CSV UTF-8).

| File | Contenuto |
|---|---|
| `indicatori.csv` | Valori quantitativi: una riga per valore, con min / centrale / max, unità, regione, anno, fase, fonte bibliografica e tipo di dato |
| `fonti_bibliografiche.csv` | Bibliografia, con link e ID del file sul Drive |
| `matrice_qualitativa.csv` | Livelli 0–3 per gli impatti non misurabili, con certezza e motivazione |
| `profilo_fonti.csv` | Famiglia, dove ricadono gli impatti, chi li subisce, aree PPE |
| `conflitti_fvg.csv` | I 21 conflitti in FVG, con i motivi codificati |
| `temi_conflitto.csv` | Per ogni motivo di protesta: natura, evidenza, stato (misurato / plausibile / non supportato) |

### Regole

- Ogni numero ha fonte, anno, regione e perimetro. Il campo `tipo_dato` vale `letteratura`, `misurato` o `stima nostra`.
- Si riportano intervalli, non solo medie. Se due fonti divergono si tengono entrambe e si scrive perché nella colonna `note` (iniziando con `FONTI DIVERGENTI:` la nota viene evidenziata nell'app).
- La matrice qualitativa e le posizioni nel grafico dell'asimmetria sono **stime preliminari del gruppo**, da validare.
- Nessun punteggio unico aggregato.

### Aggiungere o correggere un dato

1. Modifica il CSV in `data/`.
2. Esegui il controllo:

   ```bash
   python scripts/valida_dati.py
   ```

   Segnala fonti bibliografiche mancanti, unità o anni vuoti, valori non ordinati, fonti o categorie non previste.
3. Esegui i test: `python -m pytest`.

## Fonti principali

- UNECE (2022), *Carbon Neutrality in the UNECE Region: Integrated Life-cycle Assessment of Electricity Sources*.
- Breakthrough Institute (2024), *Updated Mining Footprints and Raw Material Needs for Clean Energy*.
- Lovering et al. (2022), *Land-use intensity of electricity production and tomorrow's energy landscape*, PLOS ONE.
- Turconi et al. (2013), *Life cycle assessment of electricity generation technologies*, RSER.
- Markandya & Wilkinson (2007); Sovacool et al. (2016), via Our World in Data.
- *Local opposition.xlsx* (progetto POWERUP).

## Lacune note

- Nessun LCA del petrolio greggio → elettricità e dell'eolico offshore galleggiante.
- Nessun dato su EROI e costi esterni monetizzati.
- Uso di suolo non ancora dal corrigendum UNECE 2022 (stesso metodo per tutte le fonti).
- Evidenza specifica per il FVG su campi elettromagnetici, odori del biometano e consumo di suolo.
