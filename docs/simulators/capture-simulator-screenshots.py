#!/usr/bin/env python3
"""Automated screenshot capture for WXCC and SFDC Simulator pages.

Captures screenshots of both simulator tabs for use in documentation.

Usage:
  python3 capture-simulator-screenshots.py
  python3 capture-simulator-screenshots.py --url https://your-env.elb.amazonaws.com
  python3 capture-simulator-screenshots.py --email admin@totogi.com --password Password@12
"""

import argparse
import asyncio
import os
from playwright.async_api import async_playwright

parser = argparse.ArgumentParser()
parser.add_argument("--email",    default="admin@totogi.com")
parser.add_argument("--password", default="Password@12")
parser.add_argument("--url",      default="https://call-processing-dev-1242253893.us-east-1.elb.amazonaws.com")
args = parser.parse_args()

URL = args.url
EMAIL = args.email
PASSWORD = args.password
BASE = os.path.dirname(os.path.abspath(__file__))
WXCC_OUT = os.path.join(BASE, "wxcc", "images")
SFDC_OUT = os.path.join(BASE, "sfdc", "images")
os.makedirs(WXCC_OUT, exist_ok=True)
os.makedirs(SFDC_OUT, exist_ok=True)


async def screenshot(page, out_dir, name, wait_ms=2000, full_page=False):
    """Take a single screenshot."""
    await page.wait_for_timeout(wait_ms)
    path = os.path.join(out_dir, f"{name}.png")
    await page.screenshot(path=path, full_page=full_page)
    print(f"  {name}.png")


async def capture_viewport_and_full(page, out_dir, name, scroll_steps=None, wait_ms=2500):
    """Capture viewport screenshot, optional scroll steps, and full-page screenshot."""
    await page.wait_for_timeout(wait_ms)
    await page.evaluate("window.scrollTo(0, 0)")
    await page.wait_for_timeout(500)

    path = os.path.join(out_dir, f"{name}.png")
    await page.screenshot(path=path, full_page=False)
    print(f"  {name}.png")

    if scroll_steps:
        for i, pos in enumerate(scroll_steps, 1):
            await page.evaluate(f"window.scrollTo(0, {pos})")
            await page.wait_for_timeout(600)
            p = os.path.join(out_dir, f"{name}-{i}.png")
            await page.screenshot(path=p, full_page=False)
            print(f"  {name}-{i}.png")

    fp = os.path.join(out_dir, f"{name}-full.png")
    await page.screenshot(path=fp, full_page=True)
    print(f"  {name}-full.png")
    await page.evaluate("window.scrollTo(0, 0)")


async def main():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        ctx = await browser.new_context(viewport={"width": 1440, "height": 900})
        page = await ctx.new_page()

        # ── Login ─────────────────────────────────────────────────────────
        print(f"Logging in as {EMAIL}...")
        await page.goto(f"{URL}/login", wait_until="networkidle")
        await page.wait_for_selector("input[placeholder='you@company.com']", timeout=15000)
        await page.fill("input[placeholder='you@company.com']", EMAIL)
        await page.fill("input[placeholder='••••••••••••']", PASSWORD)
        await page.click("button:has-text('Sign In')")
        try:
            await page.wait_for_selector("text=Executive Summary", timeout=15000)
        except Exception:
            await page.wait_for_timeout(8000)
        await page.wait_for_timeout(3000)

        # ── Navigate to Simulators page ───────────────────────────────────
        print("\nNavigating to Simulators...")
        await page.goto(f"{URL}/operations/simulators", wait_until="networkidle")
        await page.wait_for_timeout(3000)

        # ══════════════════════════════════════════════════════════════════
        # WXCC SIMULATOR TAB
        # ══════════════════════════════════════════════════════════════════
        print("\n=== WXCC Simulator Tab ===")

        wxcc_tab = page.locator("button:has-text('WXCC Simulator')")
        if await wxcc_tab.count() > 0:
            await wxcc_tab.click()
            await page.wait_for_timeout(2000)

        # 01 - Overview (status, statistics, server config)
        await capture_viewport_and_full(page, WXCC_OUT, "01-wxcc-overview", [600, 1200])

        # 02 - Seed Data dialog
        seed_btn = page.locator("button:has-text('Seed Data')")
        if await seed_btn.count() > 0 and await seed_btn.is_enabled():
            await seed_btn.click()
            await page.wait_for_timeout(1000)
            await screenshot(page, WXCC_OUT, "02-seed-data-dialog")
            cancel_btn = page.locator("button:has-text('Cancel')")
            if await cancel_btn.count() > 0:
                await cancel_btn.click()
                await page.wait_for_timeout(500)

        # 03 - Sample Recordings section (try to expand)
        sample_section = page.locator("text=Sample Recordings").first
        if await sample_section.count() > 0:
            await sample_section.click()
            await page.wait_for_timeout(1000)
            await screenshot(page, WXCC_OUT, "03-sample-recordings", wait_ms=1000)

        # 04 - Scroll to tasks table area
        await page.evaluate("window.scrollTo(0, 800)")
        await page.wait_for_timeout(1000)
        await screenshot(page, WXCC_OUT, "04-tasks-table")

        # 05 - Reset confirmation dialog
        await page.evaluate("window.scrollTo(0, 0)")
        await page.wait_for_timeout(500)
        reset_btn = page.locator("button:has-text('Reset')").first
        if await reset_btn.count() > 0 and await reset_btn.is_enabled():
            await reset_btn.click()
            await page.wait_for_timeout(1000)
            await screenshot(page, WXCC_OUT, "05-reset-dialog")
            cancel_btn = page.locator("button:has-text('Cancel')")
            if await cancel_btn.count() > 0:
                await cancel_btn.click()
                await page.wait_for_timeout(500)

        # ══════════════════════════════════════════════════════════════════
        # SFDC SIMULATOR TAB
        # ══════════════════════════════════════════════════════════════════
        print("\n=== SFDC Simulator Tab ===")

        sfdc_tab = page.locator("button:has-text('Salesforce Simulator')")
        if await sfdc_tab.count() > 0:
            await sfdc_tab.click()
            await page.wait_for_timeout(2500)

        # 01 - Overview (mode toggle, status, statistics)
        await capture_viewport_and_full(page, SFDC_OUT, "01-sfdc-overview", [600, 1200])

        # 02 - Mode toggle area (top of page)
        await page.evaluate("window.scrollTo(0, 0)")
        await page.wait_for_timeout(500)
        await screenshot(page, SFDC_OUT, "02-sfdc-mode-toggle")

        # 03 - FDW Objects table (scroll down)
        await page.evaluate("window.scrollTo(0, 500)")
        await page.wait_for_timeout(1000)
        await screenshot(page, SFDC_OUT, "03-fdw-objects-table")

        # 04 - Dump section (scroll further)
        await page.evaluate("window.scrollTo(0, 1000)")
        await page.wait_for_timeout(1000)
        await screenshot(page, SFDC_OUT, "04-dump-section")

        await browser.close()

    # ── Summary ───────────────────────────────────────────────────────────
    for label, out_dir in [("WXCC", WXCC_OUT), ("SFDC", SFDC_OUT)]:
        print(f"\n=== {label} screenshots in {out_dir} ===")
        if os.path.isdir(out_dir):
            for f in sorted(os.listdir(out_dir)):
                if f.endswith(".png"):
                    kb = os.path.getsize(os.path.join(out_dir, f)) // 1024
                    print(f"  {f} ({kb}KB)")


if __name__ == "__main__":
    asyncio.run(main())
