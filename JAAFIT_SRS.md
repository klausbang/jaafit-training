# Software Requirements Specification
## JAAFIT – Træningsapp og Øvelsesdatabase

**Version:** 1.1
**Dato:** 2026-03-27
**Ændringer fra v1.0:** Personlig øvelses- og programdatabase (CRUD), importfunktion, ny Øvelser-listevisning, personaldata API, warmupId-opvarmning, øvelsesbeskrivelser.
**Sprog:** Dansk (UI); Engelsk (SRS)

---

## 1. Introduktion

### 1.1 Formål
Dette dokument beskriver softwarekravene for to sammenhængende single-page web-applikationer:
- **jaafit_app.html** – Træningsapp til logning, fremgangsmåde og programoversigt
- **jaafit_graph.html** – Øvelsesdatabase med interaktiv grafvisualisering og CRUD for personlige øvelser og programmer

Applikationerne er udviklet til brug af JAAFIT-træningskonceptet og er designet til selvhosting i en lokal eller privat webserver.

### 1.2 Scope
Applikationerne dækker:
- Registrering og historik af træningssessioner
- Programstyring og fremdriftsvisualisering
- Muskelgruppe-heatmap og kropsdiagram
- Interaktiv grafvisning af relationer mellem øvelser, muskelgrupper, udstyr og programmer
- Oprettelse, redigering og sletning af personlige øvelser og programmer
- Batchimport af øvelser via JSON-fil
- Kortbaseret listevisning af øvelsesdatabasen

### 1.3 Definitioner og forkortelser

| Term | Betydning |
|------|-----------|
| Session | Én gennemført træningsdag med øvelser |
| Program | Et navngivet træningsprogram med én eller flere dage |
| Dag | En navngivet underenhed i et program med et fast sæt øvelser |
| Øvelse | En enkelt styrkeøvelse med muskelgruppe og udstyrskrav |
| Personlig øvelse | Brugeroprettet øvelse der supplerer JAAFIT-databasen |
| Personligt program | Brugeroprettet program der supplerer JAAFIT's 5 standardprogrammer |
| MG | Muskelgruppe |
| Elastik | Modstandsbånd brugt som udstyr |
| Skool | Ekstern platform (skool.com/jaafit) til videoer og program-beskrivelser |
| warmupId | UUID der peger på en personlig opvarmningsøvelse knyttet til en programdag |

### 1.4 Referencer
- Chart.js 4.4.0 (CDN: `cdn.jsdelivr.net`)
- vis-network (CDN: `unpkg.com/vis-network`)
- JAAFIT Skool øvelsesbibliotek og træningsprogrammer (kræver login)

---

## 2. Systemarkitektur

Begge applikationer er **selvstændige HTML-filer** med indlejret CSS og JavaScript. De deler tre serverside backing stores og samme hardkodede JAAFIT-stamdata.

```
jaafit_app.html              jaafit_graph.html
      │                              │
      │   ←── link ──────────────── │
      │                              │
      ├── /api/userdata ──────────── ┤ (bruger-workouts, programvalg)
      │         │                    │
      │   jaafit_userdata.json        │
      │                              │
      └── /api/personaldata ─────── ┘ (personlige øvelser, programmer, beskrivelser)
                    │
          jaafit_personaldata.json
```

### 2.1 Brugerdata (jaafit_userdata.json)
- Læses ved opstart via HTTP GET `/api/userdata`
- Gemmes ved ændringer via HTTP POST `/api/userdata` med JSON-body
- In-memory cache (`DB`) i jaafit_app.html
- Indeholder: per-bruger workout-historik, aktivt program-ID og "Mine programmer"-liste

### 2.2 Personlig data (jaafit_personaldata.json)
- Deles mellem begge applikationer
- Læses ved opstart via HTTP GET `/api/personaldata`
- Gemmes ved ændringer via HTTP POST `/api/personaldata` med JSON-body
- Indeholder tre sektioner:
  - `personal_exercises`: brugerdefinerede øvelser
  - `personal_programs`: brugerdefinerede programmer
  - `exercise_descriptions`: brugerforfattede beskrivelser knyttet til UUID for JAAFIT-øvelser
- **Engangs-migration:** ved første start migreres evt. data fra browser localStorage til serverfilen, og localStorage-nøglerne slettes

### 2.3 Statisk JAAFIT-stamdata (begge apps)
JAAFIT's 45 standardøvelser, 10 muskelgrupper, 6 udstyrstyper og 5 standardprogrammer er hardkodet identisk i begge filer og kan ikke ændres via UI.

---

## 3. jaafit_app.html – Træningsapp

### 3.1 Overordnet beskrivelse
En mørktema (dark mode) single-page app til logning af styrketræning. Understøtter to brugere og tilbyder syv sider (faner). Ved opstart indlæses brugerdata og personlig data parallelt.

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

**Personlig data** (i `jaafit_personaldata.json`):
```json
{
  "personal_exercises": [
    {
      "id": "UUID",
      "name": "string",
      "mg": "string",
      "eq": ["string"],
      "door": false,
      "warmup": false,
      "desc": "string",
      "personal": true
    }
  ],
  "personal_programs": [
    {
      "id": "mp_<timestamp>",
      "name": "string",
      "color": "#rrggbb",
      "personal": true,
      "days": [
        {
          "id": "string",
          "n": 1,
          "type": "string",
          "exs": ["UUID"],
          "warmupId": "UUID | null"
        }
      ]
    }
  ],
  "exercise_descriptions": {
    "UUID": "string"
  }
}
```

### 3.4 Øvelsesdatabase

45 JAAFIT-standardøvelser er hardkodet, hver med:
- **UUID** (32 hex-tegn)
- **Titel** (dansk navn inkl. udstyrstype)
- **Muskelgruppe** (én per øvelse)
- **Udstyr** (liste; mulige værdier: `elastik`, `bar`, `haandtag`, `ankelstropper`, `PowerPress`, `kropsvagt`)
- **Anchor-flag** (`true` = kræver døranker)
- **Beskrivelse** (`desc`): kan tilføjes af bruger via jaafit_graph.html og flettes ind ved opstart

Hertil tilkommer **personlige øvelser** fra personaldata (se 3.3). Ved opstart via `applyPersonalData()`:
- Brugerforfattede beskrivelser (`exercise_descriptions`) flettes ind i den tilsvarende JAAFIT-øvelses `desc`-felt
- Personlige øvelser indsættes i den fælles `EX{}`-opslag-tabel, så alle app-funktioner bruger dem transparent

Muskelgrupper (10):

| Nøgle | Visningsnavn | Farve |
|-------|-------------|-------|
| Bryst | Bryst | `#c0392b` |
| Ryg | Ryg | `#1a6a9a` |
| Forlaar | Forlår | `#27ae60` |
| Baglaar og baller | Baglår & baller | `#8e44ad` |
| Inder og ydersiden af laarene | Inderlår/Yderlår | `#d35400` |
| Biceps | Biceps | `#c0392b` |
| Triceps | Triceps | `#2980b9` |
| Skulder | Skulder | `#16a085` |
| Mave | Mave | `#e67e22` |
| Laeg | Læg | `#7f8c8d` |

### 3.5 Træningsprogrammer

5 JAAFIT-standardprogrammer plus eventuelle personlige programmer (indlæst fra personaldata via `allPrograms()`):

| ID | Navn | Antal dage |
|----|------|-----------|
| prog1 | 1: Effektiv Velvære | 2 (Fullbody × 2) |
| prog2 | 2: Feminin Styrke | 3 (Fullbody × 3) |
| prog3 | 3: Hverdagskrigeren | 5 (splitprogram) |
| prog4 | 4: Fundamental Styrke | 4 (Upper/Lower split) |
| prog5 | 5: Maksimal Styrke | 6 (Push/Pull/Legs × 2) |
| mp_* | Personlige programmer | Varierer |

Hvert JAAFIT dag-objekt indeholder:
- Dagnummer og type (fx "Push 1", "Lower 2", "Fullbody")
- Liste af øvelses-UUID'er
- URL til Skool-programside (kan være `null`)
- Opvarmning: tekstbeskrivelse + udstyrliste (`warmup`, `warmupEq`)

Personlige dag-objekter bruger `warmupId` (UUID for en personlig opvarmningsøvelse) i stedet for tekstbeskrivelse.

### 3.6 Opvarmningsvisning

`warmupHtml(day, compact)` bestemmer visningen:
- Hvis `day.warmupId` peger på en JAAFIT/personlig øvelse: vises øvelsens navn, udstyr og evt. beskrivelse
- Ellers: vises tekstbeskrivelse + udstyrliste fra `day.warmup` / `day.warmupEq`
- Kompakt (til Program-side): kun et pill-tag
- Udvidet (til Dashboard/Log/Mine programmer): fuld række med beskrivelse og udstyr

### 3.7 Sider og funktionskrav

#### 3.7.1 Dashboard
**Visningsformål:** Overblik over træningsstatus.

Krav:
- Viser 4 statistikbokse: total antal sessioner, dage siden sidst træning, sessioner denne uge, aktiv bruger
- Viser "Næste træning"-kort: næste dags øvelser fra aktivt program, med sidst brugte vægt per øvelse og udstyrsoversigt
- Dagstitel er klikbar (link til Skool-side) hvis URL er angivet
- Viser seneste 4 sessioner med dato, program, dag og øvelser (kompakt)
- Viser søjlediagram (Chart.js): træningsfrekvens per uge de seneste 8 uger
- Inkluderer opvarmning som trin 0 i næste-træning-visning (via `warmupHtml`)
- Viser elastik-vægte separat per øvelse hvis relevant

#### 3.7.2 Log træning
**Visningsformål:** Registrering af ny træningssession.

Krav:
- Formular med: datovælger (default: dags dato), program-dropdown (inkl. personlige programmer), dag-dropdown
- Dag-dropdown opdateres automatisk ved ændring af program
- Øvelsestabel genereres automatisk fra valgt dag med felter: Kilo (kg), Sæt, Reps, Bemærkning
- Reps-felt understøtter kommaseparerede værdier (fx "10,8,8")
- Sidst brugte vægt vises som hint per øvelse
- Sessionsnote-felt (fritekst)
- Gem-knap: gemmer session i brugerdata; viser toast-bekræftelse
- Ryd-knap: nulstiller formularen
- Træningshistorik vises nedenfor med mulighed for sletning per session (med ID)
- Historik sorteres omvendt kronologisk

#### 3.7.3 Fremdrift
**Visningsformål:** Visualisering af træningsudvikling over tid.

Krav:
- **Vægtudvikling per øvelse:** linjediagram (Chart.js) med datovælger; viser kun øvelser med mindst ét vægtsæt
- **Volumen per uge:** søjlediagram; volumen = kg × sæt × reps; viser seneste 12 uger
- **Antal sessioner per uge:** søjlediagram; viser seneste 12 uger
- **Komplet træningshistorik:** tabel med: dato, program, dag, øvelser med vægt, note, slet-knap
- Alle tabeller og diagrammer er brugerspecifikke

#### 3.7.4 Muskler
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

#### 3.7.5 Program
**Visningsformål:** Programoversigt og næste træningsdag.

Krav:
- Dropdown til valg af program for den aktive bruger; inkluderer personlige programmer; gemmes øjeblikkeligt i userdata
- **Programoversigt:** Alle dage i programmet vises som kort med:
  - Badge: grøn hak (gennemført denne uge), rød pil (næste), grå (afventende)
  - Øvelses-tags med sidst brugte vægt
  - Opvarmning som kompakt tag (via `warmupHtml`)
- **Næste træning (detaljer):** udvidet visning af næste dag inkl. opvarmning, beskrivelse og vægte
- **Alle programmer:** Visning af alle JAAFIT- og personlige programmers dage og øvelser i kompakt form

#### 3.7.6 Mine data
**Visningsformål:** Oversigt over seneste brugte vægt per øvelse med dato.

Krav:
- Øvelser grupperet per muskelgruppe
- Tabel per gruppe med: øvelsesnavn, muskelgruppe, seneste vægt (kg), dato for seneste træning
- Udskrivningsknap (browser print)
- **Print-layout (A4):**
  - Print-header med brugernavnet og dato
  - Visuel sektion: muskelgruppe-heatmap-tiles (5 kolonner) + klonede SVG-kropsdiagrammer (forfra/bagfra) farvet efter recency
  - Øvelsesliste i 2-kolonne-layout
  - Tabeloverskrifter skjult; muskelgruppe-kolonne skjult ved print
  - Sideformat: A4 portræt med 20mm/28mm margener

#### 3.7.7 Mine programmer
**Visningsformål:** Administration og udskrivning af personlige træningsprogrammer.

Krav:
- Brugeren kan tilføje et eller flere programmer til sin liste (fra alle tilgængelige, inkl. personlige)
- Programmer kan fjernes fra listen
- Hvert programs kort viser: programnavn, aktivt-badge, alle dage med øvelser og vægte inkl. muskelgruppe og udstyr
- Opvarmning per dag: vises som øvelsesnavn + udstyr + beskrivelse (hvis `warmupId`) eller tekstbeskrivelse
- Øvelsesbeskrivelse (`ex.desc`) renderes som ekstra kursiv-række i tabellen hvis udfyldt
- Checkbox-markering: om programmet skal udskrives
- **Print-layout:**
  - Udskriver kun markerede programmer
  - Hvert program starter på ny side (undtagen det første)
  - Tabeller med øvelsesnavn, muskelgruppe, sidst brugte vægt og udstyr
  - Sideformat: A4 portræt

### 3.8 Navigation og UI
- Header: app-titel, brugerskifter, link til jaafit_graph.html
- Nav-bar: 7 faneblade (scrollbar horisontalt på mobil)
- Responsivt grid: 2- og 3-kolonner på desktop, 1-kolonne på mobil (breakpoint 700px)
- Toast-notifikation (grøn): vises 2,5 sekunder ved gem
- Mørkt tema: baggrund `#0f0f1a`, accent `#e94560`, sekundær `#4fc3f7`
- Links til JAAFIT Skool åbner i nyt tab

### 3.9 Opstart
`initApp()` henter `/api/userdata` og `/api/personaldata` parallelt (`Promise.allSettled`). Personlig data flettes ind i EX-opslaget via `applyPersonalData()` og personlige programmer gøres tilgængelige via `window._personalPrograms` + `allPrograms()`.

### 3.10 Eksterne afhængigheder
| Bibliotek | Version | Formål |
|-----------|---------|--------|
| Chart.js | 4.4.0 | Diagrammer (bar, line) |
| Skool.com | N/A | Øvelsesvideoer og dagsprogrammer |

---

## 4. jaafit_graph.html – Øvelsesdatabase

### 4.1 Overordnet beskrivelse
En interaktiv grafvisualisering og forvaltningsapp for JAAFIT's øvelses- og programdatabase. Udover den eksisterende grafvisning tilbyder appen CRUD for personlige øvelser og programmer, batchimport samt en kortbaseret listevisning. Personlig data deles med jaafit_app.html via `/api/personaldata`.

### 4.2 Layout
- **Header:** titel, beskrivelse, links til jaafit_app.html, Skool øvelsesbibliotek, Skool programmer, og "⬆ Importer øvelser"-knap
- **Sidebar (300px):** visningsfaner, søgefelt, kontekstfølsomme filterknapper, "Mine øvelser"-sektion, farveforklaring
- **Graf-/listeområde (flex:1):** vis-network canvas ELLER kortbaseret listevisning, info-panel (overlay), statistikbar

### 4.3 Visningstyper (faner)

| Fane | Visningstype | Indhold |
|------|-------------|---------|
| Muskler | Graf | Øvelser + muskelgruppe-noder + kanter |
| Prog. | Graf | JAAFIT- og personlige programmer + dag-noder + øvelser + kanter |
| Udstyr | Graf | Øvelser + udstyrsnoder + kanter |
| Øvelser | Liste (kort) | Alle øvelser som søgbare og filterbare kort |
| Alle | Graf | Alle nodetyper og kanter kombineret |

Søgefeltet i sidebar er kun synligt i graftilstande; listevisningen har sit eget søge- og filterfelt i panelet.

### 4.4 Noder (graftilstande)

| Nodetype | Form | Farve | Særkender |
|----------|------|-------|-----------|
| JAAFIT-øvelse | roundRect | MG-farve (halvgennemsigtig) | – |
| Personlig øvelse | roundRect | MG-farve (halvgennemsigtig) | `★`-præfix på label |
| Muskelgruppe | box | MG-farve (solid) | – |
| JAAFIT-program | box | Programmets farve | Solid kant |
| Personligt program | box | Programmets farve | Stiplet kant (`[5,3]`), `★`-præfix, guldfarvet kant |
| Dag | ellipse | Programmets farve (halvgennemsigtig) | – |
| Udstyr | diamond | `#0f3460` med `#4fc3f7` kant | – |

### 4.5 Kanter
- Øvelse → Muskelgruppe: farvet med muskelgruppens farve
- Øvelse → Udstyr: `#4fc3f7` (halvgennemsigtig)
- Program → Dag: stiplet linje, ingen pil
- Dag → Øvelse: farvet med programmets farve, pil til øvelse

### 4.6 Filtrering (graftilstande)

**Søgefelt (sidebar):**
- Realtidssøgning på øvelsesnavne (case-insensitive) for JAAFIT + personlige øvelser
- Filtrerer synlige øvelser og tilhørende noder

**Filterknapper:**
- Én aktiv filter ad gangen (toggle); deaktiveres ved genklik
- Muskelgruppe-filter (Muskler-tab): viser kun øvelser i valgt MG
- Program-filter (Prog.-tab): viser kun øvelser i valgt program + dage + programnode; JAAFIT-programmer og personlige programmer vises i separate grupper
- Udstyr-filter (Udstyr-tab): viser kun øvelser med valgt udstyr

Søgning og filter kombineres (AND-logik).

### 4.7 Øvelser-listevisning (nyt)

Aktiveres via "Øvelser"-fanen. Erstatter grafcanvas med en kortgitter-visning.

**Filterværktøjslinje:**
- Fritekst-søgefelt
- Muskelgruppe-dropdown (alle / specifik MG)
- Typedropdown: "JAAFIT + Mine", "Kun JAAFIT", "Kun mine"

**Sortering:** Personlige øvelser vises først; inden for hver gruppe sorteres alfabetisk (da-DK).

**Øvelseskort:**
- Navn (personlige øvelser markeret med ★)
- Beskrivelse (`desc`), hvis udfyldt
- Tags: muskelgruppe-tag (farvet), udstyrstagsene, Døranker-tag (rød)
- Handlingsknapper (øverst til højre):
  - For JAAFIT-øvelser: ✏️ Rediger beskrivelse + ↗ Skool-link
  - For personlige øvelser: ✏️ Rediger + 🗑️ Slet

### 4.8 Info-panel (graftilstande)
Overlay-panel (top-right) der vises ved klik på en node.

**Øvelse:**
- Navn, muskelgruppe-tag, udstyrs-tags, Døranker-tag
- Beskrivelse (`desc`), hvis udfyldt
- Skool-link for JAAFIT-øvelser

**Muskelgruppe:**
- Navn, antal øvelser (JAAFIT + personlige), liste af øvelses-tags

**Udstyr:**
- Navn, antal øvelser med dette udstyr, liste af øvelses-tags

**Program (JAAFIT og personligt):**
- Navn (★-præfix for personlige), antal dage, antal unikke øvelser
- Liste af dage med type, opvarmning og øvelsesnavn
- For JAAFIT-programmer: link til Skool-siden

**Dag:**
- Program-navn + dagnummer og dagtype
- Liste: 0. Opvarmning (via `warmupId` eller tekst), 1. Øvelse 1, ...

Panel lukkes med ✕ eller klik på tom canvas.

### 4.9 Statistikbar
Fastgjort i bunden af grafområdet; skjult i listevisning:
- Viser antal synlige noder og kanter
- Hjælpetekst: "Klik på en node for detaljer"

### 4.10 Graf-fysik og layout

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

### 4.11 Mine øvelser – CRUD (nyt)

**Sidebar-sektion "Mine øvelser":**
- Viser liste over personlige øvelsers navne med ✏️ Rediger og 🗑 Slet pr. øvelse
- "+ Tilføj øvelse"-knap åbner øvelsesmodal

**Øvelsesmodal (`#exModal`):**

Tilstanden styres af om en øvelses-ID sendes med (redigér) eller ej (ny):

*For personlige øvelser* vises alle felter:
- Navn (fritekst)
- Muskelgruppe (dropdown over de 10 definerede MG'er)
- Udstyr (multi-select; mulige værdier: `elastik`, `bar`, `haandtag`, `ankelstropper`, `PowerPress`, `kropsvagt`)
- Kræver døranker (checkbox)
- Opvarmningsøvelse (checkbox) – markerer øvelsen som valgbar opvarmning i programbygger

*For JAAFIT-øvelser* (redigér-knap i listevisning) vises kun:
- Gul note-banner med øvelsens navn
- Beskrivelse / udførelse (textarea)
- Personlige felter skjules

**Gem-knap:**
- Ny personlig øvelse: ID genereres som `pe_<timestamp>_<index>`; tilføjes til `personalExercises[]`; gemmes via `savePersonalData()`
- Opdatering: eksisterende objekt muteres og gemmes
- Bygger grafen og listerne om
- Beskrivelse for JAAFIT-øvelse: gemmes i `exDescriptions{uuid: desc}` og sendes med i personaldata-JSON

**Slet:** fjerner fra `personalExercises[]`; opdaterer graf, liste og sidebar

### 4.12 Mine programmer – CRUD (nyt)

**Sidebar under Prog.-fanen:**
- To grupper af filterknapper: JAAFIT-programmer og "Mine programmer"
- "+ Nyt program"-knap åbner programbygger

**Programbygger-modal (`#progModal`):**
- Programnavn (fritekst)
- Farve (HTML color-picker)
- **Dag-blokke** (tilføj/fjern dynamisk):
  - Dagnummer (auto), dagtype (fritekst)
  - Opvarmning-vælger: dropdown med personlige opvarmningsøvelser (`warmup: true`); viser udstyr bag øvelsens navn; gemmes som `warmupId`
  - Øvelses-chips: viser valgte øvelsers navne med ✕-knap
  - **Øvelsesvælger (dropdown-toggle):** søgefelt + scrollbar liste grupperet efter MG med farvede punkter og checkbokse; JAAFIT- og personlige øvelser kombineres; personlige øvelser markeres med ★
- Gem: ID genereres som `mp_<timestamp>`; `personal: true` markeres; program tilføjes til `personalPrograms[]`; grafen og knapgrupperne bygges om
- Slet: bekræftelsesdialog → fjernes fra `personalPrograms[]`

### 4.13 Import (nyt)

**Triggerknap i header:** "⬆ Importer øvelser" → åbner skjult `<input type="file" accept=".json">`

**Importformat** (JSON-array):
```json
[
  {
    "name": "string (påkrævet)",
    "mg":   "string (påkrævet)",
    "eq":   ["string"],
    "door": false,
    "warmup": false,
    "desc": "string",
    "id":   "string (valgfri, ellers auto-genereret)"
  }
]
```

**Validering og preview-modal:**
1. JSON-parse; fejl ved ugyldigt JSON eller ikke-array
2. Per element: kræver `name` og `mg`; `eq` skal være array hvis angivet
3. Duplikat-check: elementer med eksisterende `id` springes over
4. Advarsler (orange) for ukendte muskelgrupper og udstyrstyper
5. Preview viser 4 sektioner: nye MG'er, nyt udstyr, valideringsfejl, og importklare øvelser

**Forhåndsvisning → Bekræft:**
- Viser knap "⬆ Importer N øvelse(r)"
- Ved bekræftelse: tilføjes til `personalExercises[]`; gemmes; toast vises (grøn, 3 sek.); sidebar, liste og graf opdateres

### 4.14 Opstart og datamigration

`initGraph()`:
1. Henter `/api/personaldata`; fylder `personalExercises`, `personalPrograms`, `exDescriptions`
2. Hvis alt er tomt: engangs-migration fra browser localStorage (nøgler: `jaafit_personal_exercises`, `jaafit_personal_programs`, `jaafit_exercise_descriptions`) → POST til server → localStorage-nøgler slettes
3. Kalder `buildButtons()` og `buildGraph()`

### 4.15 Eksterne afhængigheder
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
- Øvelseslisten genrenderes ved enhver søg-/filtreringsændring

### 5.4 Sikkerhed
- Ingen autentifikation i applikationen selv
- Skool-links kræver eksternt JAAFIT-login
- Data eksponeres ikke udover den lokale server

### 5.5 Udvidelsesmuligheder (out of scope for nuværende version)
- Tilføjelse af nye hardkodede brugere (pt. Klaus og Dorte)
- Eksport af personlige øvelser og programmer til JSON-fil
- Deling af personlige programmer mellem brugere

---

## 6. Dataflow-oversigt

```
App-opstart (jaafit_app.html)
       │
       ├── GET /api/userdata      → DB{} (in-memory)
       └── GET /api/personaldata  → applyPersonalData()
                                       ├── EX{} += personlige øvelser
                                       └── window._personalPrograms = [...]
                                              ↓
                                     allPrograms() = PROGRAMS + _personalPrograms
```

```
Bruger logger træning
       │
       ▼
Vælg program (inkl. personlige) → Vælg dag → Udfyld øvelser
       │
       ▼
saveWorkout() → POST /api/userdata → jaafit_userdata.json
       │
       ▼
Dashboard/Fremdrift/Muskler/MineData opdateres fra in-memory DB
```

```
Graf-visning (jaafit_graph.html)
       │
       ├── Vælg visning (Muskler/Prog./Udstyr/Øvelser/Alle)
       ├── Søg øvelse
       └── Filtrer på MG / JAAFIT-program / personligt program / udstyr
                │
                ▼
         buildGraph() → vis-network.setData()   (graftilstande)
         renderExerciseList()                    (listevisning)
                │
                ▼
         Klik på node → onNodeClick() → info-panel
```

```
Personlig øvelse/program CRUD (jaafit_graph.html)
       │
       ├── Opret/Rediger → modal → saveExercise() / saveProgram()
       ├── Slet          → deletePersonalExercise() / deletePersonalProgram()
       └── Import        → triggerImport() → parseAndPreviewImport() → confirmImport()
                │
                ▼
       POST /api/personaldata → jaafit_personaldata.json
                │
                ▼
       buildButtons() + buildGraph() + renderPersonalExList()
```

---

*SRS v1.1 opdateret 2026-03-27.*
