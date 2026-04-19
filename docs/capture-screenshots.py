#!/usr/bin/env python3
"""Automated screenshot capture for CallSense application.

Usage:
  python3 capture-screenshots.py                                                        # admin
  python3 capture-screenshots.py --email manager1@totogi.com --password Password@1234 --role manager
"""

import argparse
import asyncio
import os
from playwright.async_api import async_playwright

parser = argparse.ArgumentParser()
parser.add_argument("--email",    default="admin@totogi.com")
parser.add_argument("--password", default="Password@12")
parser.add_argument("--role",     default="admin", help="Subfolder name under images/")
parser.add_argument("--url",      default="https://call-processing-dev-1242253893.ap-southeast-1.elb.amazonaws.com")
args = parser.parse_args()
URL = args.url
EMAIL = args.email
PASSWORD = args.password
BASE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(BASE, "images", args.role)
os.makedirs(OUT, exist_ok=True)


async def capture(page, name, scroll_steps=None, wait_ms=3000):
    await page.wait_for_timeout(wait_ms)
    await page.evaluate("window.scrollTo(0, 0)")
    await page.wait_for_timeout(500)

    path = os.path.join(OUT, f"{name}.png")
    await page.screenshot(path=path, full_page=False)
    print(f"  {name}.png")

    if scroll_steps:
        for i, pos in enumerate(scroll_steps, 1):
            await page.evaluate(f"window.scrollTo(0, {pos})")
            await page.wait_for_timeout(600)
            p = os.path.join(OUT, f"{name}-{i}.png")
            await page.screenshot(path=p, full_page=False)
            print(f"  {name}-{i}.png")

    fp = os.path.join(OUT, f"{name}-full.png")
    await page.screenshot(path=fp, full_page=True)
    print(f"  {name}-full.png")
    await page.evaluate("window.scrollTo(0, 0)")


async def expand_sidebar(page):
    btn = page.locator("button[title='Expand sidebar']")
    if await btn.count() > 0 and await btn.is_visible():
        await btn.click()
        await page.wait_for_timeout(500)
        return True
    return False


async def collapse_sidebar(page):
    btn = page.locator("button[title='Collapse sidebar']")
    if await btn.count() > 0 and await btn.is_visible():
        await btn.click()
        await page.wait_for_timeout(300)


async def click_sidebar_item(page, label):
    """Expand sidebar, look for label, click it, collapse, return True if found."""
    await expand_sidebar(page)
    span = page.locator("span").filter(has_text=label).first
    if await span.count() > 0 and await span.is_visible():
        await span.click()
        await page.wait_for_timeout(500)
        await collapse_sidebar(page)
        return True
    await collapse_sidebar(page)
    return False


async def main():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        ctx = await browser.new_context(viewport={"width": 1440, "height": 900})
        page = await ctx.new_page()

        # ── Login ────────────────────────────────────────────────────────
        print(f"Logging in as {EMAIL} (role: {args.role})...")
        await page.goto(f"{URL}/login", wait_until="networkidle")
        await page.wait_for_selector("input[placeholder='you@company.com']", timeout=15000)
        await page.screenshot(path=os.path.join(OUT, "00-login.png"), full_page=False)
        print("  00-login.png")

        await page.fill("input[placeholder='you@company.com']", EMAIL)
        await page.fill("input[placeholder='••••••••••••']", PASSWORD)
        await page.click("button:has-text('Sign In')")
        try:
            await page.wait_for_selector("text=Executive Summary", timeout=15000)
        except Exception:
            await page.wait_for_timeout(8000)
        await page.wait_for_timeout(4000)

        # ── Dashboard pages ──────────────────────────────────────────────
        # Each entry: (list of possible labels, filename, scroll positions)
        dashboard_pages = [
            (["Executive Summary"],               "01-executive-summary", [700, 1400, 2100]),
            (["Call Analysis", "My Calls"],        "02-call-analysis",     [700, 1400, 2100, 2800]),
            (["Rep Performance", "My Dashboard"],  "03-rep-performance",   [700, 1400, 2100]),
            (["Deal Analysis"],                    "04-deal-analysis",     [700, 1400, 2100]),
            (["Email Analysis"],                   "05-email-analysis",    [700, 1400]),
            (["Tools Catalogue"],                  "09-tools-catalogue",   [700, 1400]),
        ]

        for labels, filename, scrolls in dashboard_pages:
            found = False
            for label in labels:
                found = await click_sidebar_item(page, label)
                if found:
                    print(f"\n{label}")
                    await page.wait_for_timeout(3500)
                    await capture(page, filename, scrolls)
                    break
            if not found:
                print(f"\n{labels[0]}: not available, skipping")

        # ── AI Workspace ─────────────────────────────────────────────────
        found = await click_sidebar_item(page, "AI Workspace")
        if found:
            print("\nAI Workspace")
            await page.wait_for_timeout(3500)
            await capture(page, "08-ai-workspace", [700, 1400])
        else:
            print("\nAI Workspace: not available, skipping")

        # ── Operations ───────────────────────────────────────────────────
        found = await click_sidebar_item(page, "Operations")
        if found:
            print("\nOperations")
            await page.wait_for_timeout(3000)
            await capture(page, "06-operations", [700])
        else:
            print("\nOperations: not available, skipping")

        # ── Settings (bottom gear icon) ──────────────────────────────────
        settings_btn = page.locator("button[title='Settings']")
        if await settings_btn.count() == 0:
            await expand_sidebar(page)
            settings_span = page.locator("span").filter(has_text="Settings").first
            if await settings_span.count() > 0 and await settings_span.is_visible():
                await settings_span.click()
                await collapse_sidebar(page)
                print("\nSettings")
                await page.wait_for_timeout(3000)
                await capture(page, "07-settings", [700])
            else:
                await collapse_sidebar(page)
                print("\nSettings: not available, skipping")
        else:
            await settings_btn.click()
            print("\nSettings")
            await page.wait_for_timeout(3000)
            await capture(page, "07-settings", [700])

        await browser.close()

    # ── Summary ──────────────────────────────────────────────────────────
    print(f"\n=== All screenshots in {OUT} ===")
    for f in sorted(os.listdir(OUT)):
        if f.endswith(".png"):
            kb = os.path.getsize(os.path.join(OUT, f)) // 1024
            print(f"  {f} ({kb}KB)")


if __name__ == "__main__":
    asyncio.run(main())
