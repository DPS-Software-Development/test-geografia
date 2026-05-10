# Test di Geografia — Regioni d'Italia

Web app responsive per studiare le **regioni italiane** (capoluoghi, confini, posizione geografica), pensata per cellulari e bambini di scuola elementare/media.

## Caratteristiche

- 📱 **Mobile-first**, funziona perfettamente su telefono
- 👥 **Due profili** con storico punteggi separato
- 🗺️ **Mappa SVG interattiva** con regioni evidenziate
- ✅ **5 tipi di domanda** (capoluogo, "confina con", "non confina con", posizione, identifica regione)
- 🎯 **Feedback immediato** verde/rosso + riepilogo finale con mappa colorata
- 🎉 **Confetti** per i punteggi alti
- 🔊 Suoni opzionali (Web Audio API, niente file esterni)
- 💾 **Punteggi salvati localmente** (localStorage), niente cloud, niente account
- 📦 **Singolo file HTML** auto-sufficiente (~110KB)
- 🚫 **Niente dipendenze runtime**, niente build step per usarlo

## Come usare in locale

Apri direttamente `index.html` nel browser, oppure servi la cartella:

```powershell
python -m http.server 8000
# poi vai su http://localhost:8000
```

## Deploy

### GitHub Pages (automatico)

Già abilitato sul repo: `https://<owner>.github.io/<repo>/`.
Ogni push su `main` ridistribuisce.

### Railway

Il repo contiene `Dockerfile` + `railway.json` per deploy nginx-based.

```powershell
railway login
railway init
railway up --detach
railway domain   # genera l'URL pubblico *.up.railway.app
```

## Struttura

```
index.html              # L'app completa (SVG + CSS + JS inline)
Dockerfile              # Per Railway (nginx alpine, 3 righe)
railway.json            # Config Railway
app_template.html       # Template usato dalla build pipeline
italy_clean.svg         # SVG delle 20 regioni con id="r-<regione>"
build_svg.py            # Script: GeoJSON regioni → italy_clean.svg
build_app.py            # Script: app_template.html + italy_clean.svg → index.html
```

## Rigenerare la mappa o il file index.html

```powershell
# 1. Scarica il GeoJSON sorgente (escluso dal repo per dimensione)
curl -L "https://raw.githubusercontent.com/openpolis/geojson-italy/master/geojson/limits_IT_regions.geojson" -o italy_regions.geojson

# 2. Rigenera l'SVG semplificato
python build_svg.py

# 3. Inietta l'SVG nel template per produrre index.html
python build_app.py
```

## Crediti dati

- Geometrie regionali: [openpolis/geojson-italy](https://github.com/openpolis/geojson-italy) (CC-BY 4.0)

## Licenza

MIT.
