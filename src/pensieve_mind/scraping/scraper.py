import logging
from dataclasses import dataclass

import httpx
from bs4 import BeautifulSoup

from pensieve_mind.config import settings

logger = logging.getLogger(__name__)

@dataclass
class ScrapeResult:
    url: str
    title: str | None
    description: str | None
    content: str

class Scraper:

    async def scrape(self, url: str) -> ScrapeResult:
        try:
            result = await self._scrape_simple(url)
            if len(result.content) < 200:
                logger.info(f"Wenig Content für {url}, versuche Playwright...")
                return await self._scrape_playwright(url)
            return result
        except Exception as e:
            logger.warning(f"Simple scrape fehlgeschlagen für {url}: {e}")
            return await self._scrape_playwright(url)
        
    async def _scrape_simple(self, url: str) -> ScrapeResult:
        async with httpx.AsyncClient(
            timeout=settings.scraper_timeout_seconds,
            follow_redirects=True,
            headers={"User-Agent": "Pensieve/1.0 (self-hosted bookmark manager)"},
        ) as client:
            response = await client.get(url)
            response.raise_for_status()
            return self._parse_html(url, response.text)
        
    async def _scrape_playwright(self, url: str) -> ScrapeResult:
        from playwright.async_api import async_playwright

        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True)
            try:
                page = await browser.new_page()
                await page.goto(url, timeout=settings.scraper_timeout_seconds * 1000)
                await page.wait_for_load_state("networkidle", timeout=10_000)
                html = await page.content()
                return self._parse_html(url, html)
            finally:
                await browser.close()

    def _parse_html(self, url: str, html: str) -> ScrapeResult:
        soup = BeautifulSoup(html, "html.parser")

        for tag in soup(["script", "style", "nav", "footer", "header", "aside"]):
            tag.decompose()

        return ScrapeResult(
            url=url,
            title=self._extract_title(soup),
            description=self._extract_description(soup),
            content=self._extract_content(soup)[:settings.scraper_max_content_length],
        )

    def _extract_title(self, soup: BeautifulSoup) -> str | None:
        og_title = soup.find("meta", property="og:title")
        if og_title and og_title.get("content"):
            return og_title["content"].strip()
        if soup.title and soup.title.string:
            return soup.title.string.strip()
        h1 = soup.find("h1")
        if h1:
            return h1.get_text(strip=True)
        return None

    def _extract_description(self, soup: BeautifulSoup) -> str | None:
        og_desc = soup.find("meta", property="og:description")
        if og_desc and og_desc.get("content"):
            return og_desc["content"].strip()
        meta_desc = soup.find("meta", attrs={"name": "description"})
        if meta_desc and meta_desc.get("content"):
            return meta_desc["content"].strip()
        return None

    def _extract_content(self, soup: BeautifulSoup) -> str:
        for selector in ["article", "main", "[role='main']", ".content", "#content"]:
            element = soup.select_one(selector)
            if element:
                return element.get_text(separator=" ", strip=True)
        body = soup.find("body")
        if body:
            return body.get_text(separator=" ", strip=True)
        return soup.get_text(separator=" ", strip=True)