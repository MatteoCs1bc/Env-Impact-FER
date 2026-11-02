# Esternalità delle fonti energetiche

App Streamlit che mette a confronto gli impatti e le esternalità delle fonti di elettricità lungo tutto il ciclo di vita (front end, esercizio, back end) e li collega ai conflitti locali in Friuli Venezia Giulia.

Fa parte del progetto **ESTERNALITÀ**, filone Social Acceptance / POWERUP.

## Cosa contiene

| Pagina | Cosa mostra |
|---|---|
| Analisi per fonte | Una scheda per fonte: per ogni categoria una spiegazione e i grafici con la fonte evidenziata tra le altre; dove ricadono gli impatti, aree PPE, biodiversità e paesaggio, conflitti collegati |
| Confronto per indicatore | Tutte le categorie (emissioni, materiali, efficienza, suolo e acqua, fauna, salute), ognuna con la sua tendina per l'indicatore; un valore per fonte, ordinato, con etichette dirette |
| Consumo di suolo | Dati ISPRA 2026 sul consumo di suolo in Italia per causa (FV a terra, eolico, edifici, cantieri…), uso di suolo per MWh lungo il ciclo di vita, dati FVG |
| Le esternalità del fossile | Dove ricadono gli impatti, fattori di emissione e inquinanti del termoelettrico italiano (ISPRA), costi esterni per MWh, sussidi ambientalmente dannosi, infrastrutture fossili in FVG |
| Shale gas e olio di scisto | Quota stimata di gas e greggio da fracking nelle importazioni italiane, calcolatore delle emissioni del gas in funzione delle perdite di metano, impatti locali (acqua, salute, sismicità), scisti bituminosi estoni |
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
| `indicatori.csv` | Valori quantitativi: una riga per valore, con min / centrale / max, unità, regione, anno, fase, fonte bibliografica, tipo di dato e `riferimento` (`sì` per il valore mostrato nei grafici di confronto, al massimo uno per fonte e indicatore) |
| `sintesi_fonti.csv` | Il testo esplicativo per ogni fonte e categoria nell'Analisi per fonte |
| `fonti_bibliografiche.csv` | Bibliografia, con link e ID del file sul Drive |
| `matrice_qualitativa.csv` | Descrizione degli impatti non misurati negli LCA (biodiversità, paesaggio, odori…), mostrata nell'Analisi per fonte |
| `profilo_fonti.csv` | Famiglia, dove ricadono gli impatti, chi li subisce, aree PPE |
| `conflitti_fvg.csv` | I 21 conflitti in FVG, con i motivi codificati |
| `consumo_suolo_cause.csv` | Nuovo consumo di suolo in Italia per causa (ISPRA 2026, dati 2025) |
| `costi_esterni.csv` | Costi esterni dell'elettricità per tecnologia (€/MWh) |
| `termoelettrico_italia.csv` | Inquinanti per kWh del termoelettrico italiano, 2005 e 2024 (ISPRA) |
| `importazioni_shale.csv` | Quota degli Stati Uniti nelle importazioni italiane e quota di shale nella produzione USA |
| `temi_conflitto.csv` | Per ogni motivo di protesta: natura, evidenza, stato (misurato / plausibile / non supportato) |

### Regole

- Ogni numero ha fonte, anno, regione e perimetro. Il campo `tipo_dato` vale `letteratura`, `misurato` o `stima nostra`.
- Si riportano intervalli, non solo medie. Se due fonti divergono si tengono entrambe e si scrive perché nella colonna `note` (iniziando con `FONTI DIVERGENTI:` la nota viene evidenziata nell'app).
- Le descrizioni di biodiversità, paesaggio e territorio sono **valutazioni preliminari del gruppo**, da validare.
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
