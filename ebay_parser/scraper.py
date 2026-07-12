"""Fetch and parse eBay UK search results."""

from __future__ import annotations

import re
from dataclasses import dataclass
from urllib.parse import urlencode

from bs4 import BeautifulSoup
from curl_cffi import requests

BASE_URL = "https://www.ebay.co.uk"
SEARCH_PATH = "/sch/i.html"

# Impersonate a real Chrome TLS fingerprint; eBay's edge rejects the default
# Python client fingerprint outright.
IMPERSONATE = "chrome"

BOT_PROTECTION_MARKERS = (
    "pardon our interruption",
    "checking your browser",
    "to best protect our members",
    "verify you're a real person",
)

# eBay network failures the caller may want to retry.
NetworkError = requests.RequestsError


class BlockedError(RuntimeError):
    """Raised when eBay serves its bot-protection page instead of results."""


@dataclass(frozen=True)
class Listing:
    item_id: str
    title: str
    url: str
    price: float
    delivery: float
    image: str

    @property
    def total(self) -> float:
        return round(self.price + self.delivery, 2)


class Scraper:
    """Runs eBay UK searches and returns parsed Buy It Now listings."""

    def __init__(
        self,
        proxy: str | None = None,
        results_per_page: int = 60,
        timeout: int = 30,
    ):
        self.results_per_page = results_per_page
        self.timeout = timeout
        proxies = {"http": proxy, "https": proxy} if proxy else None
        self.session = requests.Session(impersonate=IMPERSONATE, proxies=proxies)
        self.session.headers.update({"Accept-Language": "en-GB,en;q=0.9"})
        self._primed = False

    def _prime(self) -> None:
        """Visit the homepage once to obtain the session cookies eBay's search
        endpoint requires; without them it answers every query with 403."""
        try:
            self.session.get(f"{BASE_URL}/", timeout=self.timeout)
            self._primed = True
        except requests.RequestsError:
            pass

    def build_url(self, keyword: str, category_id: int | None) -> str:
        params = {
            "_nkw": keyword,
            "LH_BIN": "1",          # Buy It Now only
            "LH_PrefLoc": "1",      # UK sellers
            "_sop": "10",           # newest first
            "_ipg": str(self.results_per_page),
        }
        if category_id:
            params["_sacat"] = str(category_id)
        return f"{BASE_URL}{SEARCH_PATH}?{urlencode(params)}"

    def search(self, keyword: str, category_id: int | None = None) -> list[Listing]:
        """Return the current listings for a search, newest first.

        Raises:
            BlockedError: if eBay returns its bot-protection page.
            NetworkError: on network failure.
        """
        if not self._primed:
            self._prime()

        response = self.session.get(
            self.build_url(keyword, category_id), timeout=self.timeout
        )
        # eBay returns 403/429 when it throttles a connection rather than a
        # normal error, so treat those as a block the caller can back off from.
        if response.status_code in (403, 429):
            raise BlockedError(f"eBay returned HTTP {response.status_code}")
        response.raise_for_status()
        return self._parse(response.text)

    def _parse(self, html: str) -> list[Listing]:
        soup = BeautifulSoup(html, "lxml")
        cards = soup.find_all("li", attrs={"data-listingid": True})

        if not cards:
            lowered = html.lower()
            if any(marker in lowered for marker in BOT_PROTECTION_MARKERS):
                raise BlockedError("eBay served its bot-protection page")
            return []

        listings = []
        for card in cards:
            listing = self._parse_card(card)
            if listing is not None:
                listings.append(listing)
        return listings

    def _parse_card(self, card) -> Listing | None:
        item_id = card.get("data-listingid", "")
        if not item_id:
            return None

        price = self._price(card)
        if price <= 0:
            return None

        return Listing(
            item_id=item_id,
            title=self._title(card),
            url=self._url(card, item_id),
            price=price,
            delivery=self._delivery(card),
            image=self._image(card),
        )

    @staticmethod
    def _parse_amount(text: str) -> float:
        if "$" in text or "usd" in text.lower():
            return 0.0
        cleaned = re.sub(r"[£,\s]", "", text)
        try:
            return float(cleaned)
        except ValueError:
            return 0.0

    def _price(self, card) -> float:
        # eBay varies the price markup between card layouts, so fall back
        # through progressively looser selectors.
        span = card.find("span", class_=lambda c: c and "price" in str(c))
        if span:
            amount = self._parse_amount(span.get_text(strip=True))
            if amount > 0:
                return amount

        elem = card.find(class_=re.compile(r"price", re.I))
        if elem:
            amount = self._parse_amount(elem.get_text(strip=True))
            if amount > 0:
                return amount

        for elem in card.find_all(["span", "div"]):
            text = elem.get_text(strip=True)
            if "£" in text and not any(
                word in text.lower() for word in ("delivery", "postage", "shipping")
            ):
                amount = self._parse_amount(text)
                if amount > 0:
                    return amount
        return 0.0

    def _delivery(self, card) -> float:
        for span in card.find_all("span"):
            text = span.get_text(strip=True)
            low = text.lower()
            if any(word in low for word in ("delivery", "postage", "shipping")):
                if "free" in low:
                    return 0.0
                match = re.search(r"£[\d,]+\.?\d*", text)
                if match:
                    return self._parse_amount(match.group(0))
        return 0.0

    def _title(self, card) -> str:
        title_div = card.find("div", class_=lambda c: c and "title" in str(c))
        if title_div:
            span = title_div.find("span", class_=lambda c: c and "primary" in str(c))
            text = (span or title_div).get_text(strip=True)
            text = re.sub(r"^New listing\s*", "", text, flags=re.IGNORECASE)
            if text:
                return text
        img = card.find("img", alt=True)
        return img["alt"] if img else "Untitled listing"

    def _url(self, card, item_id: str) -> str:
        link = card.find("a", href=re.compile(r"/itm/"))
        if link and link.get("href"):
            href = link["href"].split("?")[0]
            return href if href.startswith("http") else f"{BASE_URL}{href}"
        return f"{BASE_URL}/itm/{item_id}"

    def _image(self, card) -> str:
        img = card.find("img", class_=lambda c: c and "image" in str(c))
        if img:
            return img.get("src") or img.get("data-src") or ""
        img = card.find("img")
        return (img.get("src") or "") if img else ""
