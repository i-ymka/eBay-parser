<div align="center">

# eBay Parser

**Spot underpriced eBay UK listings the moment they appear — right from your terminal**

[![status](https://img.shields.io/badge/status-working%20v0.1-2ECC71?style=flat-square)](#)&nbsp;&nbsp;[![platform](https://img.shields.io/badge/runs-anywhere-2ECC71?style=flat-square)](#)&nbsp;&nbsp;[![built with](https://img.shields.io/badge/built%20with-Python-3776AB?style=flat-square)](#)

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

## Install and run

Runs on your own machine. No account, no server to rent. Python 3.9+.

```bash
pipx install git+https://github.com/i-ymka/eBay-parser
ebay-parser
```

First run asks what to track and your price limit — that's it. Matches show up live in your terminal, with a desktop notification on macOS and Linux. Run `ebay-parser setup` any time to change your searches.

> **Heads up:** eBay blocks some connections outright. If yours is one of them,
> the setup lets you add a proxy. Try without one first.

---

## How it works

- **Looks like a normal browser to eBay.** Requests go through `curl_cffi` with Chrome's TLS fingerprint, and the session visits the homepage once to pick up the cookies eBay's search expects.
- **Knows when it's being turned away.** A 403/429 or eBay's "Pardon our interruption" page is treated as a block: the monitor backs off for 10 minutes instead of hammering the site.
- **Parses defensively.** Price, delivery cost, title and link each have fallbacks for eBay's different card layouts; foreign-currency listings are skipped so totals stay in £.
- **Alerts once per item.** Seen listing IDs are stored locally, and the first pass only records what's already listed, so you're alerted to genuinely new items.
- **Polite timing.** Each check waits your interval with ±10% jitter.

Plain HTTP, no headless browser — light enough to leave running on a laptop.

## Roadmap

- [x] Install straight from GitHub with `pipx`
- [x] Interactive first-run setup — no config files to edit
- [x] Live terminal alerts + desktop notifications (macOS / Linux)
- [x] Optional proxy support
- [x] Block detection with automatic back-off
- [ ] Publish to PyPI (`pipx install ebay-parser`)
- [ ] Discord & Telegram alert channels
- [ ] Guide for running 24/7 on a cheap VPS
- [ ] More marketplaces beyond eBay UK

## Stack

Python · curl_cffi · BeautifulSoup · lxml
