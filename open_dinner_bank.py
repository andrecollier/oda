"""Open Oda.no Dinner Bank for weekly meal planning."""

import asyncio
import sys
from datetime import datetime
from src.config import settings
from src.oda.recipes import OdaRecipeScraper


async def open_dinner_bank():
    """Open Oda.no Dinner Bank."""
    week_num = datetime.now().isocalendar()[1]
    year = datetime.now().year

    print("\n" + "=" * 80, flush=True)
    print(f"🍽️  Ukesmeny - Uke {week_num} {year}", flush=True)
    print("=" * 80, flush=True)
    print(f"\n👨‍👩‍👧‍👦 Familie: 2 voksne + 2 barn", flush=True)
    print(f"🎯 Mål: 4 sunne familiemiddager + 1 barnevennlig suppe", flush=True)
    print(f"📅 Dato: {datetime.now().strftime('%Y-%m-%d')}", flush=True)

    async with OdaRecipeScraper(
        email=settings.oda_email,
        password=settings.oda_password,
        headless=False
    ) as scraper:
        print("\n🔐 Logger inn på Oda.no...", flush=True)
        await scraper.login()
        print("✅ Innlogget!", flush=True)

        print("\n🏦 Åpner 'Dine middager' - Middagsbanken...", flush=True)
        dinner_bank_url = "https://oda.com/no/recipes/dinner-bank/"
        await scraper.page.goto(dinner_bank_url, wait_until="networkidle")

        print("\n" + "=" * 80, flush=True)
        print("🌐 NETTLESER ÅPEN - Dine middager", flush=True)
        print("=" * 80, flush=True)

        print("\n📋 OPPGAVE: Finn 5 oppskrifter", flush=True)
        print("  1️⃣  Barnevennlig suppe (med hvitløksbaguetter)", flush=True)
        print("  2️⃣  Familiemiddag 1 (sunn, rask)", flush=True)
        print("  3️⃣  Familiemiddag 2 (sunn, rask)", flush=True)
        print("  4️⃣  Familiemiddag 3 (sunn, rask)", flush=True)
        print("  5️⃣  Familiemiddag 4 (sunn, rask)", flush=True)

        print("\n💡 SÅ GÅR DU FRAM:", flush=True)
        print("  ✓ Bla gjennom oppskrifter på siden", flush=True)
        print("  ✓ Klikk på en oppskrift for å se detaljer", flush=True)
        print("  ✓ Klikk 'Legg til i Dine middager' hvis du liker den", flush=True)
        print("  ✓ Gjenta til du har 5 oppskrifter", flush=True)

        print("\n📝 OPPRETT MIDDAGSLISTE:", flush=True)
        print(f"  ✓ Klikk 'Opprett ny middagsliste' (om tilgjengelig)", flush=True)
        print(f"  ✓ Gi den navnet: 'Uke {week_num} {year}'", flush=True)
        print(f"  ✓ Legg dine 5 valgte oppskrifter til listen", flush=True)

        print("\n🛒 HANDLELISTE:", flush=True)
        print("  ✓ Oda genererer automatisk handleliste fra middagslisten", flush=True)
        print("  ✓ Du kan legge produkter rett i handlekurven", flush=True)

        print("\n⏸️  Nettleseren forblir åpen...", flush=True)
        print("  Når du har valgt oppskrifter, skriv ned URL-ene her i chatten", flush=True)
        print("  Så kan jeg hjelpe deg med å legge ingrediensene i handlekurven!", flush=True)
        print("\n  Trykk Ctrl+C for å avslutte når du er ferdig", flush=True)

        # Keep browser open indefinitely
        try:
            while True:
                await asyncio.sleep(10)
        except KeyboardInterrupt:
            print("\n\n✅ Avslutter...", flush=True)


if __name__ == "__main__":
    try:
        asyncio.run(open_dinner_bank())
    except KeyboardInterrupt:
        print("\n\n👋 Hadet!", flush=True)
