# Software Requirements Specification
## JAAFIT – Træningsapp og Øvelsesdatabase

**Version:** 1.0
**Dato:** 2026-03-25
**Sprog:** Dansk (UI); Engelsk (SRS)

---

## 1. Introduktion

### 1.1 Formål
Dette dokument beskriver softwarekravene for to sammenhængende single-page web-applikationer:
- **jaafit_app.html** – Træningsapp til logning, fremgangsmåde og programoversigt
- **jaafit_graph.html** – Øvelsesdatabase med interaktiv grafvisualisering

Applikationerne er udviklet til brug af JAAFIT-træningskonceptet og er designet til selvhosting i en lokal eller privat webserver.

### 1.2 Scope
Applikationerne dækker:
- Registrering og historik af træningssessioner
- Programstyring og fremdriftsvisualisering
- Muskelgruppe-heatmap og kropsdiagram
- Interaktiv grafvisning af relationer mellem øvelser, muskelgrupper, udstyr og programmer

### 1.3 Definitioner og forkortelser

| Term | Betydning |
|------|-----------|
| Session | Én gennemført træningsdag med øvelser |
| Program | Et navngivet træningsprogram med én eller flere dage |
| Dag | En navngivet underenhed i et program med et fast sæt øvelser |
| Øvelse | En enkelt styrkeøvelse med muskelgruppe og udstyrskrav |
| MG | Muskelgruppe |
| Elastik | Modstandsbånd brugt som udstyr |
| Skool | Ekstern platform (skool.com/jaafit) til videoer og program-beskrivelser |

### 1.4 Referencer
- Chart.js 4.4.0 (CDN: `cdn.jsdelivr.net`)
- vis-network (CDN: `unpkg.com/vis-network`)
- JAAFIT Skool øvelsesbibliotek og træningsprogrammer (kræver login)

---

## 2. Systemarkitektur

Begge applikationer er **selvstændige HTML-filer** med indlejret CSS og JavaScript. De deler samme øvelses- og programdata, som er hardkodet i JavaScript.

```
jaafit_app.html          jaafit_graph.html
      │                         │
      │   ←── link ──────────── │
      │                         │
      ▼                         ▼
/api/userdata (POST/GET)     [vis-network]
      │
jaafit_userdata.json
```

### 2.1 Datapersistens (jaafit_app.html)
- Data læses ved opstart via et HTTP `fetch` mod `/api/userdata`
- Data gemmes ved ændringer via HTTP `POST` til `/api/userdata` med JSON-body
- En in-memory kopi (`DB`) bruges som cache
- `jaafit_userdata.json` er serverens backing store

### 2.2 Statisk data (begge apps)
Øvelser, muskelgrupper, udstyr og programmer er hardkodet i JavaScript og identiske i begge filer.

---

## 3. jaafit_app.html – Træningsapp

### 3.1 Overordnet beskrivelse
En mørktema (dark mode) single-page app til logning af styrketræning. Understøtter to brugere og tilbyder syv sider (faner).

### 3.2 Brugerskift
- Applikationen understøtter to brugerprofiler: **Klaus** og **Dorte**
- Skift sker via knapper i headeren; aktiv bruger highlightes
- Al data (workouts, program-valg, mine programmer) er bruger-specifik

### 3.3 Datamodel

**Bruger-objekt** (i `jaafit_userdata.json`):
```json
{
  "program_id": "prog1",
  "workouts": [...],
  "myPrograms": [...]
}
```

**Workout-objekt:**
```json
{
  "id": "string (base36+random)",
  "date": "YYYY-MM-DD",
  "program_id": "string",
  "day_number": 1,
  "day_type": "string",
  "note": "string",
  "exercises": [
    {
      "exercise_id": "UUID",
      "exercise_title": "string",
      "weight_kg": number,
      "sets": number,
      "reps": "string (kan være kommasepareret)",
      "note": "string"
    }
  ]
}
```

### 3.4 Øvelsesdatabase

50 øvelser er registreret, hver med:
- **UUID** (32 hex-tegn)
- **Titel** (dansk navn inkl. udstyrstype)
- **Muskelgruppe** (én per øvelse)
- **Udstyr** (liste; mulige værdier: `elastik`, `bar`, `haandtag`, `ankelstropper`, `PowerPress`, `kropsvagt`)
- **Anchor-flag** (`true` = kræver døranker)

Muskelgrupper (10):

| Nøgle | Visningsnavn | Farve |
|-------|-------------|-------|
| Bryst | Bryst | `#c0392b` |
| Ryg | Ryg | `#1a6a9a` |
| Forlaar | Forlår | `#27ae60` |
| Baglaar og baller | Baglår & baller | `#8e44ad` |
| Inder og ydersiden af laarene | Inderlår/Yderlår | `#d35400` |
| Biceps | Biceps | `#e74c3c` |
| Triceps | Triceps | `#2980b9` |
| Skulder | Skulder | `#16a085` |
| Mave | Mave | `#e67e22` |
| Laeg | Læg | `#7f8c8d` |

### 3.5 Træningsprogrammer

5 programmer med følgende dagstruktur:

| ID | Navn | Antal dage |
|----|------|-----------|
| prog1 | 1: Effektiv Velvære | 2 (Fullbody × 2) |
| prog2 | 2: Feminin Styrke | 3 (Fullbody × 3) |
| prog3 | 3: Hverdagskrigeren | 5 (splitprogram) |
| prog4 | 4: Fundamental Styrke | 4 (Upper/Lower split) |
| prog5 | 5: Maksimal Styrke | 6 (Push/Pull/Legs × 2) |

Hvert dag-objekt indeholder:
- Dagnummer og type (fx "Push 1", "Lower 2", "Fullbody")
- Liste af øvelses-UUID'er (excl. opvarmning)
- URL til Skool-programside (kan være `null`)
- Opvarmning: metadata (tekst + udstyrliste) per dag

### 3.6 Sider og funktionskrav

#### 3.6.1 Dashboard
**Visningsformål:** Overblik over træningsstatus.

Krav:
- Viser 4 statistikbokse: total antal sessioner, dage siden sidst træning, sessioner denne uge, aktiv bruger
- Viser "Næste træning"-kort: næste dags øvelser fra aktivt program, med sidst brugte vægt per øvelse og udstyrsoversigt
- Dagstitel er klikbar (link til Skool-side) hvis URL er angivet
- Viser seneste 4 sessioner med dato, program, dag og øvelser (kompakt)
- Viser søjlediagram (Chart.js): træningsfrekvens per uge de seneste 8 uger
- Inkluderer opvarmning som trin 0 i næste-træning-visning
- Viser elastik-vægte separat per øvelse hvis relevant

#### 3.6.2 Log træning
**Visningsformål:** Registrering af ny træningssession.

Krav:
- Formular med: datovælger (default: dags dato), program-dropdown, dag-dropdown
- Dag-dropdown opdateres automatisk ved ændring af program
- Øvelsestabel genereres automatisk fra valgt dag med felter: Kilo (kg), Sæt, Reps, Bemærkning
- Reps-felt understøtter kommaseparerede værdier (fx "10,8,8")
- Sidst brugte vægt vises som hint per øvelse
- Sessionsnote-felt (fritekst)
- Gem-knap: gemmer session i brugerdata; viser toast-bekræftelse
- Ryd-knap: nulstiller formularen
- Træningshistorik vises nedenfor med mulighed for sletning per session (med ID)
- Historik sorteres omvendt kronologisk

#### 3.6.3 Fremdrift
**Visningsformål:** Visualisering af træningsudvikling over tid.

Krav:
- **Vægtudvikling per øvelse:** linjediagram (Chart.js) med datovælger; viser kun øvelser med mindst ét vægtsæt
- **Volumen per uge:** søjlediagram; volumen = kg × sæt × reps; viser seneste 12 uger
- **Antal sessioner per uge:** søjlediagram; viser seneste 12 uger
- **Komplet træningshistorik:** tabel med: dato, program, dag, øvelser med vægt, note, slet-knap
- Alle tabeller og diagrammer er brugerpecifikke

#### 3.6.4 Muskler
**Visningsformål:** Visualisering af hvilke muskelgrupper der er trænet.

Krav:
- **Muskelgruppe-heatmap:** farvede tiles per muskelgruppe; farveintensitet baseret på recency (se tabel nedenfor)
- **Krops-diagram:** SVG-illustration set forfra og bagfra; muskelregioner klikbare og farvet efter recency
- Klik på muskelregion viser muskelgruppenavnet

Recency-farvemodel (baseret på dage siden sidst trænet):

| Dage siden sidst | Opacitet |
|-----------------|----------|
| 0 (i dag) | 1.0 |
| 1 | 0.9 |
| 2–3 | 0.7 |
| 4–7 | 0.45 |
| 8–14 | 0.22 |
| >14 | 0.08 |
| Aldrig | 0.06 |

SVG-kroppen tegnet med SVG-elementer (rects, ellipses, circles) med `data-mg`-attributter der binder dem til muskelgrupper.

#### 3.6.5 Program
**Visningsformål:** Programoversigt og næste træningsdag.

Krav:
- Dropdown til valg af program for den aktive bruger; gemmes øjeblikkeligt i userdata
- **Programoversigt:** Alle dage i programmet vises som kort med:
  - Badge: grøn hak (gennemført denne uge), rød pil (næste), grå (afventende)
  - Øvelses-tags med sidst brugte vægt
  - Opvarmning som kompakt tag
- **Næste træning (detaljer):** udvidet visning af næste dag inkl. opvarmning og vægte
- **Alle programmer:** Visning af alle 5 programmers dage og øvelser i kompakt form

#### 3.6.6 Mine data
**Visningsformål:** Oversigt over seneste brugte vægt per øvelse med dato.

Krav:
- Øvelser grupperet per muskelgruppe
- Tabel per gruppe med: øvelsesnavn, udstyr, seneste vægt (kg), dato
- Udskrivningsknap (browser print)
- **Print-layout (A4):**
  - Print-header med brugernavnet og dato
  - Visuel sektion: muskelgruppe-heatmap-tiles (5 kolonner) + SVG-kropsdiagrammer (forfra/bagfra)
  - Øvelsesliste i 2-kolonne-layout
  - Tabeloverskrifter skjult; muskelgruppe-kolonne skjult ved print
  - Sideformat: A4 portræt med 20mm/28mm margener

#### 3.6.7 Mine programmer
**Visningsformål:** Administration og udskrivning af personlige træningsprogrammer.

Krav:
- Brugeren kan tilføje et eller flere programmer til sin liste (fra de 5 tilgængelige)
- Programmer kan fjernes fra listen
- Hvert programs kort viser: programnavn, status-badge, alle dage med øvelser og vægte inkl. muskelgruppe og udstyr
- Checkbox-markering: om programmet skal udskrives
- **Print-layout:**
  - Udskriver kun markerede programmer
  - Hvert program starter på ny side (undtagen det første)
  - Tabeller med øvelsesnavn, muskelgruppe, sidst brugte vægt og udstyr
  - Sideformat: A4 portræt

### 3.7 Navigation og UI
- Header: app-titel, brugerskifter, link til jaafit_graph.html
- Nav-bar: 7 faneblade (scrollbar horisontalt på mobil)
- Responsivt grid: 2- og 3-kolonner på desktop, 1-kolonne på mobil (breakpoint 700px)
- Toast-notifikation (grøn): vises 2 sekunder ved gem
- Mørkt tema: baggrund `#0f0f1a`, accent `#e94560`, sekundær `#4fc3f7`
- Links til JAAFIT Skool åbner i nyt tab

### 3.8 Eksterne afhængigheder
| Bibliotek | Version | Formål |
|-----------|---------|--------|
| Chart.js | 4.4.0 | Diagrammer (bar, line) |
| Skool.com | N/A | Øvelsesvideoer og dagsprogrammer |

---

## 4. jaafit_graph.html – Øvelsesdatabase

### 4.1 Overordnet beskrivelse
En interaktiv grafvisualisering af relationer mellem øvelser, muskelgrupper, udstyr og træningsprogrammer. Data er identisk med jaafit_app.html. Ingen brugerpersistens.

### 4.2 Layout
- **Header:** titel, beskrivelse, links til jaafit_app.html, Skool øvelsesbibliotek og Skool programmer
- **Sidebar (300px):** visningsfaner, søgefelt, filterknapper, farveforklaring
- **Graf-område (flex:1):** vis-network canvas, info-panel (overlay), statistikbar

### 4.3 Visningstyper (faner)

| Fane | Indhold i grafen |
|------|----------------|
| Muskler | Øvelser + muskelgruppe-noder + kanter |
| Prog. | Programmer + dag-noder + øvelses-noder + kanter |
| Udstyr | Øvelser + udstyrsnoder + kanter |
| Alle | Alle nodetyper og kanter kombineret |

### 4.4 Noder

| Nodetype | Form | Farve |
|----------|------|-------|
| Øvelse | roundRect | Muskelgruppens farve (halvgennemsigtig) |
| Muskelgruppe | box | Muskelgruppens farve (solid) |
| Træningsprogram | box | Programmets farve |
| Dag | ellipse | Programmets farve (halvgennemsigtig) |
| Udstyr | diamond | `#0f3460` med `#4fc3f7` kant |

### 4.5 Kanter
- Øvelse → Muskelgruppe: farvet med muskelgruppens farve
- Øvelse → Udstyr: `#4fc3f7` (halvgennemsigtig)
- Program → Dag: stiplet linje, ingen pil
- Dag → Øvelse: farvet med programmets farve, pil til øvelse

### 4.6 Filtrering

**Søgefelt:**
- Realtidssøgning på øvelsesnavne (case-insensitive)
- Filtrerer synlige øvelser; tilhørende noder opdateres

**Filterknapper:**
- Én aktiv filter ad gangen (toggle)
- Muskelgruppe-filter: viser kun øvelser i valgt MG + tilhørende noder
- Program-filter: viser kun øvelser der indgår i valgt program + dage + programnode
- Udstyr-filter: viser kun øvelser med valgt udstyr + udstyrsnode

Søgning og filter kombineres (AND-logik).

### 4.7 Info-panel
Overlay-panel (top-right) der vises ved klik på en node.

**Øvelse:**
- Navn, muskelgruppe-tag, udstyrs-tags
- Tag for døranker/uden døranker
- Link til Skool øvelses-side (kræver login)

**Muskelgruppe:**
- Navn, antal øvelser, liste af øvelses-tags

**Udstyr:**
- Navn, antal øvelser med dette udstyr, liste af øvelses-tags

**Program:**
- Navn, antal dage, antal unikke øvelser
- Liste af dage med type og øvelser (inkl. opvarmning)
- Link til Skool program-side

**Dag:**
- Program-navn + dagnummer og dagtype
- Liste: 0. Opvarmning, 1. Øvelse 1, ...

Panel lukkes med ✕ eller klik på tom canvas.

### 4.8 Statistikbar
Fastgjort i bunden af grafområdet:
- Viser antal synlige noder og kanter
- Hjælpetekst: "Klik på en node for detaljer"

### 4.9 Graf-fysik og layout

| Visning | Layout |
|---------|--------|
| Muskler, Udstyr, Alle | Fri placering med Barnes-Hut fysiksimulation |
| Programmer | Hierarkisk (venstre→højre), rettet, fysik deaktiveret |

Fysik-parametre:
- `gravitationalConstant: -3000`
- `springLength: 120`
- `springConstant: 0.04`
- Stabilisering: 100 iterationer

Interaktion: zoom, pan, drag, hover-tooltip.

### 4.10 Eksterne afhængigheder
| Bibliotek | Formål |
|-----------|--------|
| vis-network (unpkg.com) | Graf-visualisering |

---

## 5. Ikke-funktionelle krav

### 5.1 Platform
- Kørende i moderne webbrowsere (Chrome, Edge, Firefox, Safari)
- Ingen serverside-rendering; ren frontend
- Responsivt design; mobil-understøttelse via CSS breakpoints

### 5.2 Tilgængelighed
- Dansk UI-sprog
- Datoer formateret med `da-DK` lokale
- Dark theme med høj kontrast (hvid tekst på mørk baggrund)

### 5.3 Ydelse
- Grafen genbygges ved enhver filter- eller søgeændring
- Chart.js-instanser destroyes og genskabes ved sideskift for at undgå memory leaks

### 5.4 Sikkerhed
- Ingen autentifikation i applikationen selv
- Skool-links kræver eksternt JAAFIT-login
- Data eksponeres ikke udover den lokale server

### 5.5 Udvidelsesmuligheder (out of scope for nuværende version)
- Tilføjelse af nye brugere (pt. hardkodet: Klaus og Dorte)
- Tilføjelse af nye øvelser eller programmer uden kode-ændringer
- Eksport/import af userdata (pt. kun via server-filadgang)

---

## 6. Dataflow-oversigt

```
Bruger vælger dag
       │
       ▼
jaafit_app.html henter øvelsesliste fra PROGRAMS[] + EX{}
       │
       ▼
Bruger udfylder vægt/sæt/reps
       │
       ▼
saveWorkout() → POST /api/userdata → jaafit_userdata.json
       │
       ▼
Dashboard/Fremdrift/Muskler/MineData opdateres fra in-memory DB
```

```
Graf-visning
       │
       ├── Vælg visning (Muskler/Prog./Udstyr/Alle)
       ├── Søg øvelse
       └── Filtrer på MG/program/udstyr
                │
                ▼
         buildGraph() → vis-network.setData()
                │
                ▼
         Klik på node → onNodeClick() → info-panel
```

---

*SRS genereret 2026-03-25 ud fra analyse af jaafit_app.html og jaafit_graph.html.*
