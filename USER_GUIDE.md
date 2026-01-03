# 📖 Oda Meal Planner - Brukerveiledning

Komplett guide for å bruke Oda Meal Planner med Claude Code.

## 🎯 Hva kan systemet gjøre?

Oda Meal Planner hjelper deg med å:
- **Finne oppskrifter** som passer familien (barnevennlige, raske, sunne)
- **Planlegge ukesmeny** med smart optimalisering av grønnsaker
- **Handle smart** ved å finne tilbud og generere handlekurv
- **Lagre favoritter** og bygge oppskriftshistorikk
- **Se visuelt** på oppskrifter og handlekurv i nettleseren

---

## 🚀 Kom i gang

### Start serveren
```bash
cd oda-meal-planner
source .venv/bin/activate
python server.py
```

Serveren kjører nå og du kan bruke Claude Code til å snakke naturlig med systemet!

---

## 📝 Slik bruker du systemet

### 1. Søk etter oppskrifter

**Generelt søk:**
```
"Finn 5 oppskrifter med kylling"
```

**Barnevennlige oppskrifter:**
```
"Finn barnevennlige oppskrifter med pasta"
"Vis meg middager barna liker"
```

**Raske og lette oppskrifter:**
```
"Finn raske og lette oppskrifter under 30 minutter"
"Vis meg enkle middager"
```

**Høyt proteininnhold:**
```
"Finn oppskrifter med minst 30g protein per porsjon"
"Vis meg proteinrike middager"
```

**Meal prep / Instant Pot:**
```
"Finn oppskrifter som egner seg til meal prep"
"Vis meg Instant Pot oppskrifter"
```

**Kombinert søk:**
```
"Finn 5 barnevennlige oppskrifter med høyt protein som er raske å lage"
```

### 2. Lag ukeplan

**Enkel ukeplan:**
```
"Lag en ukeplan for 5 dager"
```

**Optimalisert for gjenbruk:**
```
"Lag en ukeplan for 5 middager som gjenbruker brokkoli og paprika"
"Planlegg uke med minst mulig matsvinn"
```

**Med spesifikke krav:**
```
"Lag ukeplan for 5 dager med barnevennlige middager og høyt protein"
```

### 3. Se på ukesplanen

```
"Vis meg ukesplanen min"
"Hva skal vi ha til middag denne uken?"
```

### 4. Analyser planen

```
"Analyser ukesplanen - hvor mye gjenbruker vi grønnsaker?"
"Vis meg hvilke ingredienser brukes mest"
```

### 5. Generer handlekurv

```
"Generer handlekurv basert på ukesplanen"
"Lag en handlekurv av middagene mine"
```

### 6. Søk produkter og tilbud

**Søk produkter:**
```
"Søk etter økologisk melk"
"Finn brokkoli"
```

**Finn tilbud:**
```
"Hva er på tilbud?"
"Finn tilbud på kjøtt"
"Vis meg produkter på salg i kategorien grønnsaker"
```

**Høyprotein produkter:**
```
"Finn høyprotein produkter"
"Vis meg produkter med over 20g protein per 100g"
```

### 7. Legg i handlekurv på Oda

```
"Legg alle ingrediensene i Oda handlekurven"
"Legg handlekurven inn på Oda.no"
```

### 8. Visuell preview (NYT!)

**Se handlekurv visuelt:**
```
"Åpne handlekurven min i nettleseren"
"Vis meg handlekurven visuelt"
```
→ Browser åpnes med din Oda handlekurv. Playwright Inspector vises - klikk "Resume" når ferdig.

**Bla gjennom oppskrifter:**
```
"Vis meg Oda oppskrifter i nettleseren"
"Åpne oppskriftssiden"
```
→ Du kan bla, filtrere og utforske visuelt.

**Se spesifikk oppskrift:**
```
"Åpne denne oppskriften i browseren: https://oda.com/no/recipes/123"
```
→ Full oppskrift med bilder og ingredienser.

### 9. Favoritter og historikk (NYT!)

**Lagre favoritter:**
```
"Legg til oppskrift [ID] som favoritt"
"Merk oppskriften som favoritt"
```

**Se favoritter:**
```
"Vis mine favorittoppskrifter"
"Hva er favorittene mine?"
```

**Rate oppskrifter:**
```
"Gi oppskrift [ID] 5 stjerner"
"Rate denne oppskriften 4/5 med notat: Barna elsket dette!"
```

**Se historikk:**
```
"Hva har vi laget nylig?"
"Vis oppskriftshistorikken min"
```

**Populære oppskrifter:**
```
"Hva lager vi oftest?"
"Vis mest brukte oppskrifter"
```

### 10. Checkout med guardrail

```
"Forbered checkout"
```
→ Browser åpnes på checkout-siden, men kjøpet fullføres **IKKE** automatisk. Du må selv trykke "Betal" i nettleseren.

---

## 💡 Praktiske arbeidsflyter

### Workflow 1: Ukesplanlegging fra bunnen

```
Du: "Finn 8 barnevennlige oppskrifter med variasjon"
→ Systemet finner 8 oppskrifter

Du: "Lag en optimalisert ukeplan for 5 middager"
→ Systemet velger 5 oppskrifter som gjenbruker grønnsaker

Du: "Analyser ukesplanen"
→ Ser gjenbruk av ingredienser

Du: "Generer handlekurv"
→ Konsolidert handleliste

Du: "Legg alt i Oda handlekurven"
→ Produkter legges til

Du: "Åpne handlekurven så jeg kan se den"
→ Browser viser handlekurv visuelt

Du: "Forbered checkout"
→ Klar til å fullføre kjøp manuelt
```

### Workflow 2: Bruk favoritter

```
Du: "Hva er mine favorittoppskrifter?"
→ Ser liste over favoritter

Du: "Lag ukeplan med mine 5 mest populære oppskrifter"
→ Bruker oppskrifter du allerede har lagd før

Du: "Generer handlekurv"
→ Du vet allerede at disse oppskriftene fungerer!
```

### Workflow 3: Tilbudsjakt

```
Du: "Finn tilbud på kjøtt og fisk"
→ Ser hva som er billig

Du: "Finn oppskrifter som bruker kylling"
→ Basert på tilbudene

Du: "Lag ukeplan med disse oppskriftene"
→ Spar penger!
```

### Workflow 4: Rask middag i dag

```
Du: "Finn raske og lette oppskrifter under 30 minutter"
→ Enkle middager

Du: "Åpne den første oppskriften i browseren"
→ Se visuelt med bilder

Du: "Legg ingrediensene i handlekurv"
→ Klar til å handle
```

---

## 🔧 Tilgjengelige kommandoer (MCP Tools)

Systemet har **19 tools** tilgjengelig:

### Produkter & Tilbud
1. `search_products` - Søk produkter med filtre
2. `find_deals` - Finn tilbud
3. `find_high_protein_products` - Finn høyprotein produkter

### Oppskrifter
4. `search_recipes` - Søk oppskrifter (barnevennlig, rask, høyt protein, meal prep)
5. `get_favorites` - Vis favorittoppskrifter
6. `get_recipe_history` - Vis nylig brukte oppskrifter
7. `get_popular_recipes` - Vis mest brukte oppskrifter
8. `mark_favorite` - Merk som favoritt
9. `rate_recipe` - Gi rating og notater

### Måltidsplanlegging
10. `create_meal_plan` - Lag optimalisert ukeplan
11. `get_meal_plan` - Vis gjeldende plan
12. `analyze_meal_plan` - Analyser gjenbruk av ingredienser

### Handlekurv
13. `generate_shopping_list` - Generer handlekurv
14. `add_to_cart` - Legg til i Oda handlekurv
15. `view_cart` - Vis handlekurv
16. `checkout_guardrail` - Forbered checkout (manuell betaling)

### Visuell preview
17. `preview_cart` - Åpne handlekurv i browser
18. `preview_recipes` - Bla gjennom oppskrifter visuelt
19. `preview_recipe` - Vis spesifikk oppskrift med bilder

---

## ⚙️ Innstillinger

Rediger `.env` filen for å tilpasse:

```env
# Vis/skjul browser
HEADLESS_BROWSER=false          # false = vis browser, true = skjul

# Måltidsplanlegging
DEFAULT_MEAL_DAYS=5             # Antall dager å planlegge
PROTEIN_GOAL_PER_MEAL=30        # Protein-mål (gram)
CHILD_FRIENDLY_MODE=true        # Foretrekk barnevennlige
MEAL_PREP_MODE=true             # Foretrekk meal-prep vennlige
```

---

## 🎨 Tips & Triks

### Bruk naturlig språk
Du trenger ikke å huske eksakte kommandoer. Snakk naturlig:
- ❌ "execute search_recipes with family_friendly=true"
- ✅ "Finn noen barnevennlige middager"

### Kombiner krav
```
"Finn 5 raske, barnevennlige oppskrifter med høyt protein som egner seg til meal prep"
```

### Bygg historikk over tid
Jo mer du bruker systemet, desto mer nyttig blir det:
- Favoritter bygges opp
- Historikk viser hva familien liker
- Populære oppskrifter = middager som fungerer

### Optimaliser for matsvinn
```
"Lag ukeplan som gjenbruker mest mulig grønnsaker"
```
→ Reduserer svinn og shopping-kompleksitet

### Bruk visuell preview
Når du er usikker:
```
"Vis meg denne oppskriften i nettleseren før jeg legger den i planen"
```

---

## 🐛 Feilsøking

**"Login failed"**
- Sjekk Oda-kredentialer i `.env`
- Prøv med `HEADLESS_BROWSER=false` for å se login-siden

**"API Key invalid"**
- Verifiser Kassal.app API nøkkel i `.env`
- Sjekk at nøkkelen er aktiv på kassal.app

**"No recipes found"**
- Prøv bredere søk
- Fjern noen filtre
- Sjekk at du er logget inn på Oda

**Browser lukker for raskt**
- Dette er normalt! Playwright Inspector lar deg pause
- Når Inspector vises, klikk "Resume" for å lukke

**Produkter mangler priser**
- Noen produkter i Kassal-databasen mangler priser
- Prøv å søke etter andre produkter
- Rapporter manglende data til kassal.app

---

## 📚 Eksempler på komplette samtaler

### Eksempel 1: Full ukesplanlegging

```
Du: "Hei! Jeg trenger hjelp med å planlegge middag for neste uke"

Claude: La meg hjelpe deg! Hva slags middager liker familien?

Du: "Vi er 2 voksne og 2 barn. Vi liker kylling, pasta og grønnsaker.
     Viktig at det er barnevennlig og ikke tar for lang tid"

Claude: Perfekt! Jeg skal finne noen oppskrifter som passer.
[Søker etter oppskrifter]

Claude: Jeg fant 8 oppskrifter som passer! Her er de:
- Kyllingpasta med brokkoli (20 min)
- Taco med kylling (25 min)
[osv...]

Du: "Lag en ukeplan for 5 dager med disse"

Claude: [Lager optimalisert plan]
Jeg har laget en ukeplan som gjenbruker brokkoli og paprika
i 3 av middagene for å redusere matsvinn!

Du: "Perfekt! Generer handlekurv"

Claude: [Genererer handlekurv]
Handlekurven inneholder:
- Grønnsaker: brokkoli (1 pose), paprika (2 stk)
[osv...]

Du: "Legg alt i Oda handlekurven og vis meg den"

Claude: [Legger til produkter og åpner browser]
Browser er åpnet med handlekurven! Du kan se alle produktene nå.

Du: "Takk! Denne uken var perfekt. Lagre disse oppskriftene som favoritter"

Claude: [Markerer som favoritter]
Alle 5 oppskriftene er lagret som favoritter!
```

---

## 🎓 Lær mer

- **README.md** - Teknisk dokumentasjon
- **QUICKSTART.md** - 5-minutters oppsett
- **USER_GUIDE.md** - Denne filen!

---

## 🆘 Hjelp

**Problemer?**
1. Les "Feilsøking" seksjonen over
2. Sjekk at `.env` er riktig konfigurert
3. Prøv å restarte serveren

**Spørsmål?**
Bare spør Claude Code! For eksempel:
```
"Hvordan søker jeg etter raske oppskrifter?"
"Kan du vise meg hvordan jeg lagrer favoritter?"
```

---

Lykke til med måltidsplanleggingen! 🍽️
