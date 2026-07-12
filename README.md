<div align="center">

# eBay Parser

**Spot underpriced eBay UK listings the moment they appear — right from your terminal**

[![status](https://img.shields.io/badge/status-early%20development-F5A623?style=flat-square)](#)&nbsp;&nbsp;[![platform](https://img.shields.io/badge/runs-anywhere-2ECC71?style=flat-square)](#)&nbsp;&nbsp;[![built with](https://img.shields.io/badge/built%20with-Python-3776AB?style=flat-square)](#)

</div>

---

## The idea

Good deals on eBay sell in minutes. By the time you refresh the page, they're gone.

**eBay Parser** keeps checking for you. Tell it what you're hunting and your max price — it pings you the second a matching Buy It Now listing appears. No browser tabs, no refreshing.

```
you: "nintendo switch under £50"
      ↓
eBay Parser checks eBay UK every minute
      ↓
new match found → alert in your terminal (instantly)
```

## Try it in one command

Runs on your own machine. No account, no server to rent.

```bash
pipx install ebay-parser
ebay-parser
```

First run asks what to track and your price limit — that's it. Matches show up live in your terminal.

> **Heads up:** eBay blocks some connections outright as a bot-protection
> measure. If yours is one of them, the setup lets you add a proxy — that fixes
> it. Try without one first; add a proxy only if eBay turns you away.

---

## Optional extras (add when you want them)

Start simple. Level up only if you need to.

| Want… | Add |
|-------|-----|
| Alerts in Discord | paste your channel's webhook URL |
| Alerts in Telegram | connect your own bot in one step |
| To get past eBay blocking your connection | add a proxy in the setup |
| 24/7 running | move it to a cheap VPS (guide included) |

The default — live alerts in your terminal — works out of the box on connections eBay doesn't block.

---

## How it works

A lightweight Python script checks eBay UK search results on a timer, parses new Buy It Now listings, filters by your price limit, and alerts you once per item (no repeats). It's deliberately simple: plain HTTP requests, no headless browser, so it's light enough to run on a laptop and leave open.

## Roadmap

- [ ] One-command install (`pipx install ebay-parser`)
- [ ] Interactive first-run setup — no config files to edit
- [ ] Live terminal + desktop notifications (zero accounts)
- [ ] Discord & Telegram alert channels (optional)
- [ ] Optional proxy support for heavier use
- [ ] More marketplaces beyond eBay UK

## Stack

Python · curl_cffi · BeautifulSoup

---

<div align="center">

*Early development — star the repo to follow along.*

</div>
