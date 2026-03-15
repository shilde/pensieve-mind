import asyncio
from pensieve_mind.scraping.scraper import Scraper

async def main():
    scraper = Scraper()
    result = await scraper.scrape("https://example.com")
    print(f"Title:       {result.title}")
    print(f"Description: {result.description}")
    print(f"Content:     {result.content[:200]}...")

asyncio.run(main())