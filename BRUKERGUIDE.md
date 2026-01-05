# 🍽️ Oda Meal Planner - Brukerguide

Velkommen til Oda Meal Planner! Dette er din komplette guide til smart middagsplanlegging og handlekurv-styring.

## 📋 Innholdsfortegnelse

1. [Kom i gang](#kom-i-gang)
2. [Oppskriftssøk](#oppskriftssøk)
3. [Middagsplanlegging](#middagsplanlegging)
4. [Faste varer & Smart innkjøp](#faste-varer--smart-innkjøp)
5. [Handlekurv & Bestilling](#handlekurv--bestilling)
6. [Tips & Triks](#tips--triks)

---

## 🚀 Kom i gang

### Første gangs oppsett

1. **Installer og aktiver MCP serveren** (gjøres automatisk via Claude Code)
2. **Konfigurer innlogging** - Oda email og passord er satt i `.env`
3. **Scrape bestillingshistorikk** (første gang):
   ```
   Spør Claude: "Scrape min bestillingshistorikk fra Oda"
   ```

---

## 🔍 Oppskriftssøk

### Søk etter oppskrifter

**Eksempel:**
```
"Finn 5 barnevennlige kyllingoppskrifter"
```

**Tilgjengelige filtre:**
- `family_friendly` - Barnevennlige oppskrifter
- `high_protein` - Høyt proteininnhold (>25g per porsjon)
- `meal_prep` - Egnet for meal prep
- `quick_and_easy` - Raske og enkle oppskrifter

**Hva du får:**
- Oppskriftens navn og ID
- Porsjoner og tilberedningstid
- **Proteininnhold per porsjon**
- Hovedgrønnsaker
- **Forslag til tilbehør** (ris, poteter, salat, etc.)
- **Forslag til drikke** (vann, melk, juice)
- Link til full oppskrift på Oda

### Favoritter & Historikk

**Se favoritter:**
```
"Vis mine favorittoppskrifter"
```

**Se historikk:**
```
"Hvilke oppskrifter har jeg brukt nylig?"
```

**Se mest brukte:**
```
"Hvilke oppskrifter lager jeg oftest?"
```

### Vurder oppskrifter

**Legg til favoritt:**
```
"Legg til oppskrift [recipe_id] som favoritt"
```

**Gi rating:**
```
"Gi oppskrift [recipe_id] 5 stjerner med notat: 'Barna elsket dette!'"
```

---

## 📅 Middagsplanlegging

### Lag ukesplan

**Eksempel:**
```
"Lag en middagsplan for 5 dager basert på disse oppskriftene: [recipe_id1, recipe_id2, ...]"
```

**Smartfunksjoner:**
- Optimaliserer gjenbruk av grønnsaker (reduserer matsvinn)
- Balanserer ernæring
- Variasjon i måltider

### Se gjeldende plan

```
"Vis middagsplanen min"
```

### Generer handleliste

```
"Lag handleliste basert på middagsplanen"
```

**Handlelisten inkluderer:**
- Alle ingredienser fra middagsplanen
- Konsoliderte mengder (hvis samme vare brukes flere ganger)
- Gruppering etter kategori
- Forslag til tilbehør og drikke for hver middag

---

## 🛒 Faste varer & Smart innkjøp

Dette er den **mest kraftfulle funksjonen** - automatisk sporing av faste varer!

### Hvordan det fungerer

1. **Scrape bestillingshistorikk** (første gang + oppdatering månedlig)
2. **Analyser mønstre** - Systemet finner automatisk varer du kjøper regelmessig
3. **Prediker behov** - AI beregner når du går tom for melk, brød, tannkrem, etc.
4. **Automatisk påminnelse** - Får varsler når varer snart går tomt

### Steg-for-steg guide

#### 1. Scrape bestillingshistorikk (første gang)

```
"Scrape min bestillingshistorikk fra Oda"
```

Dette henter **alle** dine bestillinger tilbake til 2017!

**Forventet tid:** 5-10 minutter for 50-100 bestillinger

#### 2. Analyser faste varer

```
"Analyser mine faste varer"
```

Systemet finner automatisk:
- **Meieriprodukter** (melk, yoghurt, ost)
- **Brød & bakevarer**
- **Husholdningsprodukter** (tannkrem, såpe, papir)
- **Pålegg & frokost**
- **Alle andre gjentakende kjøp**

**Hva du får:**
- Antall ganger kjøpt
- Gjennomsnittlig frekvens (f.eks. "hver 7. dag")
- Siste kjøpsdato
- Predikert neste kjøpsdato
- ⚠️ Varsler for varer som snart går tomt

#### 3. Se low-stock varsler

```
"Hvilke faste varer går snart tomt?"
```

**Eksempel output:**
```
⚠️ Low Stock Warnings - 3 items need attention:

🔴 Tine Lettmelk 1,7% 1L
   Last purchased: 2025-12-28
   Predicted need: in 2 days
   Typical purchase: Every 7 days

🔴 Gilde Pålegg Skinke
   Last purchased: 2025-12-20
   Predicted need: in 1 day
   Typical purchase: Every 14 days
```

#### 4. Legg til i handlekurv

```
"Legg til faste varer som går tomt i handlelisten"
```

Eller spesifiser spesifikke produkter:
```
"Legg til melk og brød i handlelisten"
```

### Intelligente funksjoner

**Produktlevetid-estimering:**
- Melk/brød: Kort levetid (7 dager)
- Meieriprodukter: Medium levetid (14 dager)
- Husholdning: Lang levetid (30-60 dager)

**Forbrukspredikering:**
Basert på:
- Din historiske kjøpsfrekvens
- Familiens størrelse (2 voksne + 2 barn)
- Produkttype
- Sesongvariasjoner

---

## 🛍️ Handlekurv & Bestilling

### Legg til produkter

**Fra handleliste:**
```
"Legg til alle produkter fra handlelisten i Oda-kurven"
```

**Spesifikke produkter:**
```
"Legg til 2 liter melk og 1 brød i kurven"
```

**Fra produktsøk:**
```
"Søk etter brokkoli og legg billigste i kurven"
```

### Forhåndsvisning

**Se handlekurv visuelt:**
```
"Vis handlekurven min i nettleseren"
```

Dette åpner Oda.com i nettleser **uten cookie popup** for en ren opplevelse!

**Se oppskrift visuelt:**
```
"Vis oppskrift [recipe_id] i nettleseren"
```

### Checkout

```
"Forbered checkout"
```

⚠️ **VIKTIG:** Systemet stopper FØR betaling. Du må selv fullføre bestillingen manuelt.

---

## 💡 Tips & Triks

### Ukentlig rutine

**Mandag:**
```
1. "Hvilke faste varer går snart tomt?"
2. "Finn 5 barnevennlige middagsoppskrifter"
3. "Lag middagsplan for uken"
4. "Generer handleliste"
5. "Legg til faste varer i handlelisten"
6. "Legg alt i Oda-kurven"
```

### Review av forrige uke

```
"Hvordan gikk middagene forrige uke?"
```

Claude vil:
- Vise hvilke oppskrifter du brukte
- Spørre om tilbakemelding
- Foreslå å legge til favoritter
- Justere for neste uke

### Spare penger

**Finn tilbud:**
```
"Finn produkter på tilbud i grønnsaker-kategorien"
```

**Sammenlign priser:**
```
"Søk etter kyllingfilet og sorter etter pris"
```

**Bulkkjøp:**
Systemet foretrekker automatisk bulk-produkter (store poser) over pre-cut/små pakker.

### Ernæringsfokus

**Høyt proteininnhold:**
```
"Finn high-protein produkter"
```

**Balansert ukesmeny:**
```
"Lag en middagsplan med variasjon i protein og grønnsaker"
```

---

## 🔧 Feilsøking

### Login-problemer

Hvis login feiler:
1. Sjekk at `.env` har riktig email/passord
2. Prøv å logge inn manuelt på Oda.com først
3. Sjekk at du ikke har 2FA aktivert (ikke støttet ennå)

### Scraping feiler

Hvis scraping ikke fungerer:
1. Oda kan ha endret websiden - kontakt utvikler
2. Sjekk internettforbindelse
3. Prøv med `headless=False` for å se hva som skjer

### Database-problemer

Hvis du vil starte på nytt:
```bash
rm data/meal_planner.db
```

---

## 📊 Eksempel-arbeidsflyt

### Scenario: Planlegg uke 2

**Dag 1 - Søndag kveld:**
```
Du: "Scrape bestillingshistorikk" (hvis første gang)
Claude: ✓ Scraped 87 orders!

Du: "Analyser faste varer"
Claude: ✓ Found 45 recurring items!

Du: "Hvilke faste varer går tomt?"
Claude: ⚠️ Melk (2 dager), Brød (1 dag), Yoghurt (3 dager)

Du: "Finn 5 barnevennlige middagsoppskrifter med høyt protein"
Claude: [Viser 5 oppskrifter med tilbehør og drikke-forslag]

Du: "Lag middagsplan for 5 dager med disse: [IDs]"
Claude: ✓ Created meal plan! Vegetable reuse: 78%

Du: "Generer handleliste"
Claude: [Viser komplett handleliste gruppert etter kategori]

Du: "Legg til faste varer som går tomt"
Claude: ✓ Added 3 recurring items to shopping list

Du: "Legg alt i Oda-kurven"
Claude: ✓ Added 32 items to cart

Du: "Vis handlekurven i nettleseren"
Claude: ✅ Browser åpnet! [Åpner Oda.com uten cookie popup]
```

**Resultat:**
- Komplett ukesmeny
- Alle ingredienser i handlekurv
- Faste varer automatisk inkludert
- Klar for bestilling!

---

## 🎯 Avanserte funksjoner

### Auto-add favoritter

Marker oppskrifter for automatisk inkludering:
```
"Sett [recipe_id] til å alltid inkluderes i ukesplanen"
```

### Sett preferanser for faste varer

```
"Sett melk til å automatisk legges til handlelisten hver uke"
```

### Eksporter middagsplan

```
"Eksporter middagsplanen til tekstfil"
```

---

## 📞 Support

Hvis du har spørsmål eller problemer, spør Claude Code direkte:

```
"Hvordan fungerer [funksjon]?"
"Jeg får feilmelding når jeg [handling]"
```

---

**Laget med ❤️ og AI av Claude Code**

_Versjon 1.0 - Januar 2025_
