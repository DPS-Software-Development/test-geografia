# Test di Geografia — Regioni d'Italia

Web app responsive per studiare le **regioni italiane** (capoluoghi, confini, posizione geografica, fiumi, monti, laghi), pensata per cellulari e bambini di scuola elementare/media.

## Caratteristiche

- 📱 **Mobile-first**, funziona perfettamente su telefono
- 👥 **Profili multipli** con storico punteggi separato (Emma, Sofia + custom)
- 🗺️ **Mappa SVG interattiva** con regioni evidenziate
- ✅ **9 tipi di domanda** (capoluogo, confina/non confina, posizione, identifica regione, fiume, monte, lago, Italia generale)
- 📖 **Modalità Studio** — scheda per regione + mini-quiz dedicato
- 👨‍👩‍👧 **Card "Progressi famiglia"** — overview di tutti i profili
- 🎯 **Feedback adattivo** — raccomandazioni basate sugli errori recenti
- 🎉 Confetti per i punteggi alti, suoni opzionali (Web Audio API)
- 💾 **Punteggi salvati localmente** (localStorage), niente cloud, niente account
- 📦 **Singolo file HTML** auto-sufficiente (~160 KB)

## Come usare in locale

Apri direttamente `index.html` nel browser, oppure servi la cartella:

```powershell
python -m http.server 8000
# poi vai su http://localhost:8000
```

## Deploy (Railway)

Il repo contiene `Dockerfile` + `railway.json` per il deploy nginx-based.

```powershell
railway login
railway up --detach
railway domain   # genera l'URL pubblico *.up.railway.app
```

## Struttura

```
index.html              # L'app completa (SVG + CSS + JS inline)
app_template.html       # Template sorgente
italy_clean.svg         # SVG delle 20 regioni (id="r-<regione>")
geo-data.json           # Dataset fatti geografici (pubblico)
build_svg.py            # GeoJSON regioni → italy_clean.svg
build_app.py            # app_template.html + italy_clean.svg → index.html
Dockerfile              # nginx alpine con $PORT envsubst
nginx.conf.template     # Config nginx
railway.json            # Config Railway
```

## Rigenerare la mappa o l'app

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
