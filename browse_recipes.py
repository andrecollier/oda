"""Browse Oda.no recipes visually to find family-friendly meals."""

import asyncio
from src.config import settings
from src.oda.recipes import OdaRecipeScraper


async def browse_oda_recipes():
    """Open Oda.no recipes page for manual browsing."""
    print("\n" + "=" * 70)
    print("🍽️  Oda.no Oppskrifter - Visuell Søk")
    print("=" * 70)
    print("\nJeg åpner Oda.no oppskrifter i nettleseren så du kan:")
    print("  • Søke etter 'barnevennlig'")
    print("  • Søke etter 'suppe'")
    print("  • Filtrere på kategorier (middag, supper, etc.)")
    print("  • Se bilder og beskrivelser")
    print("\nForslag til søk:")
    print("  🥣 'suppe' - for å finne suppeoppskrifter")
    print("  👨‍👩‍👧‍👦 'barnevennlig' - for familievennlige retter")
    print("  🥦 'grønnsaker' - for grønnsaksretter")
    print("  🍗 'kylling' - for kyllingretter")
    print("\n" + "=" * 70)

    async with OdaRecipeScraper(
        email=settings.oda_email,
        password=settings.oda_password,
        headless=False  # Show browser
    ) as scraper:
        print("\n🔐 Logger inn på Oda.no...")
        await scraper.login()
        print("✅ Innlogget!")

        # Navigate to recipes page
        recipes_url = "https://oda.com/no/recipes/all/"
        await scraper.page.goto(recipes_url, wait_until="networkidle")

        print("\n🌐 Nettleser åpen med Oda oppskrifter!")
        print("\nDu kan nå:")
        print("  1. Bruk søkefeltet øverst til høyre")
        print("  2. Søk etter 'suppe' for å finne suppeoppskrifter")
        print("  3. Søk etter 'barnevennlig' for familiemåltider")
        print("  4. Klikk på oppskrifter for å se detaljer")
        print("  5. Noter ned 4-5 oppskrifter du liker")
        print("\nSpesielt relevant for deg:")
        print("  🥣 Suppe med hvitløksbaguetter")
        print("  👨‍👩‍👧‍👦 Barnevennlige middager (2 voksne + 2 barn)")
        print("  🥗 Sunne og næringsrike retter")

        print("\n⏸️  Nettleseren forblir åpen...")
        print("  Når du er ferdig, lukk nettleservinduet eller trykk Ctrl+C her")

        # Keep browser open indefinitely
        try:
            while True:
                await scraper.page.wait_for_timeout(10000)
        except KeyboardInterrupt:
            print("\n\n✅ Avslutter...")


if __name__ == "__main__":
    try:
        asyncio.run(browse_oda_recipes())
    except KeyboardInterrupt:
        print("\n\n👋 Hadet!")
