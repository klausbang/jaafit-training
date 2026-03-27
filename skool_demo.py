"""
skool_demo.py — SKOOL login demo for JAAFIT
Logs in as the configured user, navigates to the JAAFIT classroom,
and lists accessible course/video links without hard-coded URLs.

Usage:
    python skool_demo.py [--headless]

Requirements:
    pip install playwright
    playwright install chromium
"""

import argparse
import re
import sys
from pathlib import Path

# ── Credentials ──────────────────────────────────────────────────────────────

def load_credentials(path="skool_login.txt"):
    """Parse skool_login.txt for email and password."""
    creds = {}
    try:
        for line in Path(path).read_text(encoding="utf-8").splitlines():
            m = re.match(r"^Login:\s*(.+@.+)", line)
            if m:
                creds["email"] = m.group(1).strip()
            m = re.match(r"^Password:\s*(.+)", line)
            if m:
                creds["password"] = m.group(1).strip()
            m = re.match(r"^Jaafit on SKOOL:\s*(https?://\S+)", line)
            if m:
                creds["community_url"] = m.group(1).strip()
    except FileNotFoundError:
        sys.exit("❌  skool_login.txt not found. Create it with Login/Password/Community lines.")
    if not creds.get("email") or not creds.get("password"):
        sys.exit("❌  Could not parse email or password from skool_login.txt")
    return creds


# ── Main ──────────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--headless", action="store_true",
                        help="Run browser in headless mode (no visible window)")
    args = parser.parse_args()

    try:
        from playwright.sync_api import sync_playwright, TimeoutError as PWTimeout
    except ImportError:
        sys.exit(
            "❌  Playwright not installed.\n"
            "    Run:  pip install playwright && playwright install chromium"
        )

    creds = load_credentials()
    community_url = creds.get("community_url", "https://www.skool.com/jaafit")
    classroom_url = community_url.rstrip("/") + "/classroom"

    print(f"Community : {community_url}")
    print(f"Classroom : {classroom_url}")
    print(f"Logging in as {creds['email']} …")

    with sync_playwright() as pw:
        browser = pw.chromium.launch(headless=args.headless)
        ctx = browser.new_context(
            viewport={"width": 1280, "height": 900},
            user_agent=(
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/124.0.0.0 Safari/537.36"
            ),
        )
        page = ctx.new_page()

        # ── 1. Login ──────────────────────────────────────────────────────────
        page.goto("https://www.skool.com/login", wait_until="domcontentloaded")
        page.wait_for_selector("input[type='email'], input[name='email']", timeout=15_000)

        page.fill("input[type='email'], input[name='email']", creds["email"])
        page.fill("input[type='password'], input[name='password']", creds["password"])
        page.click("button[type='submit']")

        # Wait for navigation away from login page
        try:
            page.wait_for_url(lambda url: "login" not in url, timeout=20_000)
            print("✅  Login successful")
        except PWTimeout:
            # Check for error message on page
            err = page.locator("[class*='error'], [class*='Error']").first.inner_text() \
                  if page.locator("[class*='error']").count() else "unknown"
            sys.exit(f"❌  Login failed or timed out. Page error: {err}")

        # ── 2. Navigate to classroom ──────────────────────────────────────────
        print(f"Navigating to classroom …")
        page.goto(classroom_url, wait_until="domcontentloaded")

        try:
            # Wait for course/lesson cards to appear
            page.wait_for_selector(
                "a[href*='/classroom'], [class*='course'], [class*='lesson'], "
                "[class*='Course'], [class*='Lesson'], [class*='module']",
                timeout=20_000,
            )
        except PWTimeout:
            print("⚠️   Classroom content did not load as expected — printing page structure instead.")

        current_url = page.url
        print(f"Current URL: {current_url}")

        # ── 3. Collect course / lesson links ──────────────────────────────────
        page.wait_for_timeout(2000)  # let React render

        links = page.evaluate("""() => {
            const anchors = Array.from(document.querySelectorAll('a[href]'));
            return anchors
                .map(a => ({ text: a.innerText.trim(), href: a.href }))
                .filter(l =>
                    l.href.includes('/classroom') &&
                    l.text.length > 0
                )
                .slice(0, 30);
        }""")

        if links:
            print(f"\n── Classroom links found ({len(links)}) ─────────────────────")
            for lnk in links:
                print(f"  {lnk['text'][:60]:<62}  {lnk['href']}")
        else:
            print("⚠️   No classroom links found via anchor scan.")

        # ── 4. Look for video elements / iframes ─────────────────────────────
        video_srcs = page.evaluate("""() => {
            const vids = [
                ...Array.from(document.querySelectorAll('video[src]')).map(v => v.src),
                ...Array.from(document.querySelectorAll('iframe[src]')).map(f => f.src),
            ];
            return [...new Set(vids)];
        }""")

        if video_srcs:
            print(f"\n── Video sources on page ({len(video_srcs)}) ──────────────────")
            for src in video_srcs:
                print(f"  {src}")
        else:
            print("\n(No video elements on classroom index page — "
                  "open a specific lesson to see its video URL)")

        # ── 5. Try opening the first lesson link ─────────────────────────────
        lesson_links = [l for l in links if "/classroom/" in l["href"] and l["href"] != classroom_url]
        if lesson_links:
            first = lesson_links[0]
            print(f"\nOpening first lesson: {first['text']}")
            page.goto(first["href"], wait_until="domcontentloaded")
            page.wait_for_timeout(3000)

            lesson_videos = page.evaluate("""() => {
                return [
                    ...Array.from(document.querySelectorAll('video[src]')).map(v => v.src),
                    ...Array.from(document.querySelectorAll('iframe[src]')).map(f => f.src),
                    ...Array.from(document.querySelectorAll('source[src]')).map(s => s.src),
                ];
            }""")

            if lesson_videos:
                print(f"✅  Video sources in lesson ({len(lesson_videos)}):")
                for src in lesson_videos:
                    print(f"    {src}")
            else:
                print("   (no <video>/<iframe> found; video may load on user interaction)")
            print(f"   Lesson URL: {page.url}")

        if not args.headless:
            print("\nBrowser stays open — press Enter to close …")
            input()

        ctx.close()
        browser.close()
        print("\nDone.")


if __name__ == "__main__":
    main()
