# JAAFIT App – Opgaveoversigt

> Opdateret: 2026-03-16 | Fil til at holde styr på implementeringsstatus

---

## Status-nøgle
- ✅ **Færdig** – implementeret og testet
- 🔄 **I gang** – delvist implementeret
- ⬜ **Ikke startet** – kun planlagt
- 🚫 **Blokeret** – afventer andet

---

## Opgaver

### T01 – Grundlæggende database ✅
**Fil:** `jaafit_database.json`, `jaafit_graph.html`, `jaafit_oevelsesdatabase.md`
- [x] 49 øvelser med URL, muskelgruppe, udstyr
- [x] 5 træningsprogrammer med dage og øvelser
- [x] Graf-visualisering (vis-network)
- [x] Dokumentations-MD fil

---

### T02 – Brugeradministration ✅
**Fil:** `jaafit_app.html` (localStorage)
- [x] Tilføj bruger Klaus
- [x] Tilføj bruger Dorte
- [x] Bruger-vælger i UI
- [x] Tildel program til bruger (Klaus → Fundamental Styrke, Dorte → Feminin Styrke)
- [x] Gem brugerdata i localStorage

---

### T03 – Træningslog ✅
**Fil:** `jaafit_app.html`
- [x] Formular: vælg program + dag
- [x] Autoudfyld øvelser fra valgt dag
- [x] Felt per øvelse: kilo, sæt, reps, bemærkning
- [x] Generel bemærkning til sessionen
- [x] Gem log med dato
- [x] Vis loggede sessioner i historik

---

### T04 – Vægt-tracking ✅
**Fil:** `jaafit_app.html`
- [x] Spor kilo per øvelse per dato
- [x] Vis seneste brugte vægt for øvelse
- [x] Chart.js linjegraf: vægtudvikling per øvelse over tid

---

### T05 – Fremdriftsoversigt ✅
**Fil:** `jaafit_app.html`
- [x] Samlet træningsoversigt (antal sessioner, dage siden sidst)
- [x] Volumen per uge (Chart.js)
- [x] Antal træninger per uge/måned
- [x] Træningshistorik tabel (dato, program, dag, øvelser)

---

### T06 – Muskelgruppe-heatmap ✅
**Fil:** `jaafit_app.html`
- [x] Oversigt over alle muskelgrupper
- [x] Farveintensitet baseret på recency:
  - I dag / igår → fuldt oplyst (100%)
  - 2–3 dage siden → 70%
  - 4–7 dage siden → 40%
  - 8–14 dage siden → 20%
  - >14 dage eller aldrig → gråt (5%)
- [x] Tooltip med "sidst trænet" dato

---

### T07 – Krops-diagram (SVG) ✅
**Fil:** `jaafit_app.html`
- [x] SVG figur (forfra og bagfra)
- [x] Muskelregioner markeret og farvekodet
- [x] Farveintensitet efter recency (samme logik som T06)
- [x] Klik på muskel → vis øvelser + seneste træning
- [x] Legende

---

### T08 – Næste træning ✅
**Fil:** `jaafit_app.html`
- [x] Vis brugerens aktuelle program
- [x] Beregn hvilken dag der er næste (baseret på sidst loggede dag)
- [x] Vis øvelsesliste for næste dag med seneste brugte vægt
- [x] Vis alle programdage med status (gennemført / ikke gennemført denne uge)

---

## Teknisk arkitektur

### Filer
| Fil | Rolle |
|-----|-------|
| `jaafit_database.json` | Master-database (øvelser, programmer) |
| `jaafit_app.html` | Komplet single-page app |
| `jaafit_graph.html` | Graf-visualisering (eksisterende) |
| `jaafit_oevelsesdatabase.md` | Dokumentation |
| `jaafit_tasks.md` | Denne fil |

### Data-persistens
Brugerdata gemmes i **localStorage** under nøglen `jaafit_v1`:
```json
{
  "users": {
    "Klaus": {
      "program_id": "prog4",
      "workouts": [ ...sessions... ]
    },
    "Dorte": {
      "program_id": "prog2",
      "workouts": [ ...sessions... ]
    }
  }
}
```

### Session-struktur
```json
{
  "id": "uuid",
  "date": "2026-03-16",
  "program_id": "prog4",
  "day_number": 2,
  "day_type": "Upper 1",
  "exercises": [
    {
      "exercise_id": "...",
      "exercise_title": "Overhead Press m. bar",
      "weight_kg": 15,
      "sets": 3,
      "reps": "12,12,10",
      "note": "stod på elastik med samlede ben"
    }
  ],
  "note": "God session"
}
```

### Afhængigheder (CDN, virker offline efter første load)
- vis-network (graf) — `unpkg.com/vis-network`
- Chart.js (grafer) — `cdn.jsdelivr.net/npm/chart.js`

---

## Kendte begrænsninger / fremtidigt arbejde
- [ ] **T09** – Export til CSV / PDF
- [ ] **T10** – Flere brugere (tilføj/slet via UI, ikke kun Klaus+Dorte)
- [ ] **T11** – Synkronisering på tværs af enheder (kræver server/cloud)
- [ ] **T12** – Periodisering: automatisk progression af vægt
- [ ] **T13** – Integration med JAAFIT live-data (kræver API/login)
- [ ] **T14** – Notifikationer / påmindelser om næste træning
- [ ] **T15** – Sammenligning af to brugere

---

*Sidst opdateret: 2026-03-16*
