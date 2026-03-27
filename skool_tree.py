"""
skool_tree.py — Crawls the JAAFIT SKOOL classroom and builds an interactive
HTML tree page with inline video playback.

Handles:
  - Paginated module cards on the classroom index
  - Nested modules → lessons structure
  - Vimeo / YouTube / Wistia / <video> embeds

Usage:
    python skool_tree.py [--headless]

Output:
    skool_classroom_tree.html   (opened automatically in authenticated browser)
    skool_classroom_tree.json   (raw data for debugging)
"""

import argparse
import json
import re
import sys
import time
from pathlib import Path

# ── credentials ───────────────────────────────────────────────────────────────

def load_credentials(path="skool_login.txt"):
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
        sys.exit("skool_login.txt not found.")
    if not creds.get("email") or not creds.get("password"):
        sys.exit("Could not parse email/password from skool_login.txt")
    return creds


# ── login ─────────────────────────────────────────────────────────────────────

def skool_login(page, email, password):
    from playwright.sync_api import TimeoutError as PWTimeout
    print("  Logging in …")
    page.goto("https://www.skool.com/login", wait_until="domcontentloaded")
    page.wait_for_selector("input[type='email'], input[name='email']", timeout=15_000)
    page.fill("input[type='email'], input[name='email']", email)
    page.fill("input[type='password'], input[name='password']", password)
    page.click("button[type='submit']")
    try:
        page.wait_for_url(lambda url: "login" not in url, timeout=20_000)
        print("  ✅ Login successful")
    except PWTimeout:
        sys.exit("❌ Login failed or timed out.")


# ── video extraction ──────────────────────────────────────────────────────────

def extract_videos(page):
    """Return list of {type, src} dicts for all videos on the current page."""
    return page.evaluate("""() => {
        const results = [];
        const seen = new Set();
        function add(type, src) {
            if (src && src.startsWith('http') && !seen.has(src)) {
                seen.add(src);
                results.push({ type, src });
            }
        }

        // iframes (Vimeo / Wistia / YouTube)
        document.querySelectorAll('iframe[src]').forEach(f => {
            const s = f.src;
            if (s.includes('vimeo') || s.includes('wistia') ||
                s.includes('youtube') || s.includes('youtu.be'))
                add('iframe', s);
        });

        // <video> and <source>
        document.querySelectorAll('video[src], source[src]').forEach(v => add('video', v.src));

        // data attributes
        document.querySelectorAll('[data-src],[data-video-url],[data-embed-url]').forEach(el => {
            add('data', el.dataset.src || el.dataset.videoUrl || el.dataset.embedUrl);
        });

        // Wistia hashedId in JSON blobs / scripts
        const text = document.body.innerHTML;
        const wids = text.match(/hashedId["':\\s]+["']([a-z0-9]{10,})/g);
        if (wids) wids.forEach(m => {
            const id = m.replace(/.*["']/, '');
            add('wistia', `https://fast.wistia.net/embed/iframe/${id}`);
        });

        return results;
    }""")


# ── page dump (for debugging new pages) ──────────────────────────────────────

def dump_all_links(page, slug):
    """Return every unique href on the page — useful for understanding structure."""
    return page.evaluate(f"""() => {{
        return [...new Set(
            Array.from(document.querySelectorAll('a[href*="/{slug}"]'))
                .map(a => a.href)
        )];
    }}""")


# ── collect module cards by clicking each card div ────────────────────────────
# SKOOL renders module cards as styled divs with onClick — no <a href>.
# Strategy: find all CourseLinkWrapper divs, click each one, record URL, go back.

def get_card_count(page):
    return page.evaluate("""() =>
        document.querySelectorAll('[class*="CourseLinkWrapper"]').length
    """)

def get_card_info(page, index):
    """Return {text, desc} for the card at position index."""
    return page.evaluate(f"""() => {{
        const cards = document.querySelectorAll('[class*="CourseLinkWrapper"]');
        const card = cards[{index}];
        if (!card) return null;
        const title = card.querySelector('[class*="CourseTitle"]');
        const desc  = card.querySelector('[class*="CourseDescription"]');
        return {{
            text: title ? title.innerText.trim() : card.innerText.split('\\n')[0].trim(),
            desc: desc  ? desc.innerText.trim()  : ''
        }};
    }}""")

def click_next_page(page):
    """Click the Next pagination button if present. Returns True if clicked."""
    btn = page.locator("button:has-text('Next'), [aria-label='Next page']").first
    if btn.count() > 0:
        try:
            btn.click()
            page.wait_for_timeout(2000)
            return True
        except Exception:
            pass
    return False

def collect_module_cards(page, classroom_url, slug):
    """
    Click every module card on every page of the classroom index.
    Returns [{text, desc, href}].
    """
    page.goto(classroom_url, wait_until="networkidle")
    page.wait_for_timeout(3000)

    all_cards = []

    while True:
        count = get_card_count(page)
        print(f"    {count} cards on this page")

        for i in range(count):
            # Re-query cards each iteration (DOM may refresh after navigation)
            info = get_card_info(page, i)
            if not info:
                continue

            # Click the card
            cards = page.locator('[class*="CourseLinkWrapper"]')
            try:
                cards.nth(i).click()
                page.wait_for_url(lambda url: "/classroom/" in url, timeout=10_000)
                page.wait_for_timeout(1000)
                module_url = page.url
                print(f"    [{i}] {info['text'][:50]}  →  {module_url}")
                all_cards.append({
                    "text": info["text"],
                    "desc": info["desc"],
                    "href": module_url,
                })
            except Exception as e:
                print(f"    [{i}] click failed: {e}")
            finally:
                # Always go back to the index
                page.goto(classroom_url, wait_until="networkidle")
                page.wait_for_timeout(2000)

        if not click_next_page(page):
            break

    return all_cards


# ── collect lessons inside a module ──────────────────────────────────────────
# Inside a module, lessons ARE rendered as <a href="…?md=…"> links.

def collect_lesson_links(page, module_url, slug):
    """
    Visit a module page and return [{text, href}] for every lesson.
    Lessons link via ?md= query parameter.
    Handles Next pagination within the module.
    """
    page.goto(module_url, wait_until="networkidle")
    page.wait_for_timeout(2500)

    all_lessons = []

    while True:
        lessons = page.evaluate("""() => {
            const results = [];
            const seen = new Set();
            document.querySelectorAll('a[href]').forEach(a => {
                const href = a.href;
                if (!href.includes('?md=') && !href.includes('&md=')) return;
                if (seen.has(href)) return;
                seen.add(href);
                const text = (a.innerText || a.textContent || '').trim()
                             || href.split('?')[0].split('/').pop();
                results.push({ text, href });
            });
            return results;
        }""")

        for l in lessons:
            if not any(x["href"] == l["href"] for x in all_lessons):
                all_lessons.append(l)

        if not click_next_page(page):
            break

    return all_lessons


# ── main crawl ────────────────────────────────────────────────────────────────

def crawl_classroom(page, community_url):
    base = community_url.rstrip("/")
    classroom_url = base + "/classroom"
    slug = base.split("/")[-1]

    print(f"\n  Collecting module cards from {classroom_url} …")
    modules_raw = collect_module_cards(page, classroom_url, slug)
    print(f"  Found {len(modules_raw)} modules")

    tree = []

    for mod in modules_raw:
        mod_url = mod["href"]
        mod_text = mod["text"]
        mod_desc = mod.get("desc", "")
        print(f"\n  ┌ Module: {mod_text}")

        # Try to find lessons within this module
        lesson_links = collect_lesson_links(page, mod_url, slug)

        if lesson_links:
            print(f"  │  {len(lesson_links)} lessons")
            lessons = []
            for les in lesson_links:
                les_url = les["href"]
                les_text = les["text"]
                print(f"  │  • {les_text}")
                page.goto(les_url, wait_until="domcontentloaded")
                page.wait_for_timeout(2500)
                videos = extract_videos(page)
                print(f"  │    videos: {len(videos)}" + (
                    f"  → {videos[0]['src'][:60]}…" if videos else ""))
                lessons.append({
                    "text": les_text,
                    "url": les_url,
                    "videos": videos,
                })
            mod_videos = []
        else:
            # Module IS the lesson (no sub-pages found)
            print(f"  │  (no sub-lessons — scanning for video on module page)")
            page.goto(mod_url, wait_until="domcontentloaded")
            page.wait_for_timeout(2500)
            mod_videos = extract_videos(page)
            lessons = []
            print(f"  │  videos on module page: {len(mod_videos)}")

        print(f"  └ done")
        tree.append({
            "text": mod_text,
            "desc": mod_desc,
            "url": mod_url,
            "videos": mod_videos,
            "lessons": lessons,
        })

    return tree


# ── HTML ──────────────────────────────────────────────────────────────────────

def video_embed_html(video):
    src = video["src"]

    if "vimeo.com" in src:
        m = re.search(r"vimeo\.com/(?:video/)?(\d+)", src)
        if m:
            embed = f"https://player.vimeo.com/video/{m.group(1)}?autoplay=1&color=e94560"
            return (f'<iframe src="{embed}" width="700" height="394" frameborder="0" '
                    f'allowfullscreen allow="autoplay; fullscreen; picture-in-picture"></iframe>')

    if "youtube.com/embed" in src or "youtu.be" in src or "youtube.com/watch" in src:
        m = re.search(r"(?:embed/|youtu\.be/|v=)([A-Za-z0-9_-]{11})", src)
        if m:
            embed = f"https://www.youtube.com/embed/{m.group(1)}?autoplay=1"
            return (f'<iframe src="{embed}" width="700" height="394" '
                    f'frameborder="0" allowfullscreen></iframe>')

    if "wistia" in src:
        return (f'<iframe src="{src}" width="700" height="394" '
                f'frameborder="0" allowfullscreen></iframe>')

    if video["type"] == "video":
        return f'<video src="{src}" controls width="700"></video>'

    return f'<a href="{src}" target="_blank" class="vid-ext">↗ Open video in new tab</a>'


def build_html(tree, community_url):
    module_count = len(tree)
    lesson_count = sum(len(m["lessons"]) or (1 if m["videos"] else 0) for m in tree)
    video_count  = sum(
        sum(len(l["videos"]) for l in m["lessons"]) + len(m["videos"])
        for m in tree
    )

    def lesson_block(les, idx):
        vids_html = ""
        for v in les.get("videos", []):
            vids_html += f"""
              <div class="video-wrap" id="vw-{idx}" style="display:none">
                {video_embed_html(v)}
              </div>"""
        btn = (f'<button class="play-btn" onclick="toggleVideo(this,\'vw-{idx}\')">▶ Afspil</button>'
               if les.get("videos") else
               '<span class="no-vid">ingen video</span>')
        return f"""
            <li class="lesson">
              <div class="lesson-row">
                <a class="les-title" href="{les['url']}" target="_blank">{les['text']}</a>
                {btn}
              </div>{vids_html}
            </li>"""

    vid_idx = 0
    modules_html = ""
    for mi, mod in enumerate(tree):
        items_html = ""
        if mod["lessons"]:
            for les in mod["lessons"]:
                items_html += lesson_block(les, f"m{mi}l{vid_idx}")
                vid_idx += 1
        elif mod["videos"]:
            fake = {"text": "(video på modulside)", "url": mod["url"], "videos": mod["videos"]}
            items_html += lesson_block(fake, f"m{mi}l{vid_idx}")
            vid_idx += 1
        else:
            items_html = '<li class="lesson"><span class="no-vid">ingen videoer fundet</span></li>'

        desc_html = f'<div class="mod-desc">{mod["desc"]}</div>' if mod.get("desc") else ""
        modules_html += f"""
          <li class="module" id="mod-{mi}">
            <div class="mod-header" onclick="toggleMod(this)">
              <span class="chevron">▶</span>
              <div class="mod-info">
                <span class="mod-name">{mod['text']}</span>
                {desc_html}
              </div>
              <a href="{mod['url']}" target="_blank" class="mod-ext"
                 onclick="event.stopPropagation()" title="Åbn på SKOOL">↗</a>
            </div>
            <ul class="lessons">{items_html}
            </ul>
          </li>"""

    return f"""<!DOCTYPE html>
<html lang="da">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>JAAFIT Classroom – Oversigt</title>
<style>
*{{box-sizing:border-box;margin:0;padding:0}}
body{{font-family:'Segoe UI',Arial,sans-serif;background:#0f0f1a;color:#e0e0e0;
     min-height:100vh;padding:28px 20px}}

h1{{color:#fff;font-size:1.5rem;margin-bottom:4px}}
h1 span{{color:#e94560}}
.subtitle{{color:#888;font-size:.85rem;margin-bottom:22px}}
.subtitle a{{color:#4fc3f7;text-decoration:none}}
.subtitle a:hover{{text-decoration:underline}}

/* stats */
.stats{{display:flex;gap:14px;flex-wrap:wrap;margin-bottom:22px}}
.stat{{background:#1a1a2e;border:1px solid #2a2a4a;border-radius:8px;
       padding:10px 20px;text-align:center}}
.stat .n{{font-size:1.7rem;font-weight:700;color:#e94560}}
.stat .lbl{{font-size:.72rem;color:#888;margin-top:2px}}

/* toolbar */
.toolbar{{display:flex;gap:10px;margin-bottom:18px;flex-wrap:wrap}}
.toolbar button{{background:transparent;border:1px solid #3a3a5a;color:#aaa;
                 border-radius:6px;padding:5px 16px;cursor:pointer;font-size:.85rem}}
.toolbar button:hover{{background:#1a1a2e;color:#fff}}

/* tree */
ul.tree{{list-style:none;padding:0}}
li.module{{margin-bottom:10px}}

.mod-header{{display:flex;align-items:flex-start;gap:10px;
             background:#1a1a2e;border:1px solid #2a2a4a;
             border-radius:10px;padding:12px 16px;cursor:pointer;
             transition:background .15s}}
.mod-header:hover{{background:#22223a}}
.chevron{{color:#e94560;font-size:.75rem;transition:transform .2s;
          flex-shrink:0;margin-top:3px}}
.chevron.open{{transform:rotate(90deg)}}
.mod-info{{flex:1;min-width:0}}
.mod-name{{font-weight:700;font-size:1rem}}
.mod-desc{{color:#888;font-size:.8rem;margin-top:3px;
           white-space:nowrap;overflow:hidden;text-overflow:ellipsis}}
.mod-ext{{color:#4fc3f7;font-size:.8rem;text-decoration:none;
          border:1px solid #4fc3f7;border-radius:4px;padding:2px 8px;
          flex-shrink:0;margin-top:2px}}
.mod-ext:hover{{background:#4fc3f720}}

ul.lessons{{list-style:none;padding:0 0 0 32px;margin-top:6px;display:none}}
ul.lessons.open{{display:block}}
li.lesson{{border-left:2px solid #2a2a4a;padding:7px 14px;margin:3px 0;
           border-radius:0 6px 6px 0;transition:border-color .15s}}
li.lesson:hover{{border-left-color:#e94560}}
.lesson-row{{display:flex;align-items:center;gap:12px}}
.les-title{{color:#ccc;text-decoration:none;flex:1;font-size:.92rem;
            line-height:1.3}}
.les-title:hover{{color:#fff;text-decoration:underline}}

.play-btn{{background:#e94560;color:#fff;border:none;border-radius:20px;
           padding:4px 14px;font-size:.8rem;cursor:pointer;white-space:nowrap;
           flex-shrink:0}}
.play-btn:hover{{background:#c73850}}
.play-btn.open{{background:#444}}
.no-vid{{color:#555;font-size:.78rem}}

.video-wrap{{margin-top:10px;border-radius:8px;overflow:hidden;background:#000;
             max-width:720px}}
.video-wrap iframe,.video-wrap video{{display:block;max-width:100%}}
.vid-ext{{color:#4fc3f7;font-size:.88rem;display:inline-block;padding:8px}}
</style>
</head>
<body>
<h1>JAAFIT <span>Classroom</span> – Oversigt</h1>
<p class="subtitle">
  Kilde: <a href="{community_url}/classroom" target="_blank">{community_url}/classroom</a>
  &nbsp;·&nbsp; Klik ▶ Afspil for at se video inline &nbsp;·&nbsp;
  Klik lektionstitel for at åbne på SKOOL
</p>

<div class="stats">
  <div class="stat"><div class="n">{module_count}</div><div class="lbl">Moduler</div></div>
  <div class="stat"><div class="n">{lesson_count}</div><div class="lbl">Lektioner</div></div>
  <div class="stat"><div class="n">{video_count}</div><div class="lbl">Videoer</div></div>
</div>

<div class="toolbar">
  <button onclick="expandAll()">Udvid alle</button>
  <button onclick="collapseAll()">Luk alle</button>
</div>

<ul class="tree">
{modules_html}
</ul>

<script>
function toggleMod(header) {{
  const ul = header.nextElementSibling;
  const ch = header.querySelector('.chevron');
  if (!ul) return;
  const open = ul.classList.toggle('open');
  ch.classList.toggle('open', open);
}}
function toggleVideo(btn, wrapId) {{
  const wrap = document.getElementById(wrapId);
  if (!wrap) return;
  const showing = wrap.style.display !== 'none';
  wrap.style.display = showing ? 'none' : 'block';
  btn.classList.toggle('open', !showing);
  btn.textContent = showing ? '▶ Afspil' : '✕ Luk';
}}
function expandAll() {{
  document.querySelectorAll('ul.lessons').forEach(u => u.classList.add('open'));
  document.querySelectorAll('.chevron').forEach(c => c.classList.add('open'));
}}
function collapseAll() {{
  document.querySelectorAll('ul.lessons').forEach(u => u.classList.remove('open'));
  document.querySelectorAll('.chevron').forEach(c => c.classList.remove('open'));
  document.querySelectorAll('.video-wrap').forEach(w => w.style.display = 'none');
  document.querySelectorAll('.play-btn').forEach(b => {{
    b.classList.remove('open'); b.textContent = '▶ Afspil';
  }});
}}
// auto-expand first module
const first = document.querySelector('.mod-header');
if (first) toggleMod(first);
</script>
</body>
</html>"""


# ── debug helper ─────────────────────────────────────────────────────────────

def run_debug(page, community_url):
    """
    Navigate to the classroom, wait generously, then dump:
      - skool_debug_links.txt   all hrefs found on the page
      - skool_debug.png         screenshot
      - skool_debug.html        full page HTML
    """
    classroom_url = community_url.rstrip("/") + "/classroom"
    print(f"\n[DEBUG] Loading {classroom_url} …")
    page.goto(classroom_url, wait_until="networkidle")
    page.wait_for_timeout(5000)   # extra wait for React hydration

    # Dump every href on the page
    all_links = page.evaluate("""() =>
        [...new Set(
            Array.from(document.querySelectorAll('a[href]'))
                .map(a => a.href)
        )]
    """)
    link_text = "\n".join(all_links)
    Path("skool_debug_links.txt").write_text(link_text, encoding="utf-8")
    print(f"[DEBUG] {len(all_links)} unique hrefs → skool_debug_links.txt")

    # Dump full page HTML
    html = page.content()
    Path("skool_debug.html").write_text(html, encoding="utf-8")
    print(f"[DEBUG] page HTML → skool_debug.html ({len(html):,} bytes)")

    # Screenshot
    page.screenshot(path="skool_debug.png", full_page=True)
    print(f"[DEBUG] screenshot → skool_debug.png")

    print("\nPress Enter to close browser …")
    input()


# ── entry point ───────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--headless", action="store_true",
                        help="Crawl headlessly (browser invisible)")
    parser.add_argument("--debug", action="store_true",
                        help="Dump all links + screenshot from classroom index and exit")
    args = parser.parse_args()

    try:
        from playwright.sync_api import sync_playwright
    except ImportError:
        sys.exit("Run: pip install playwright && python -m playwright install chromium")

    creds = load_credentials()
    community_url = creds.get("community_url", "https://www.skool.com/jaafit")
    out_html = Path("skool_classroom_tree.html")
    out_json = Path("skool_classroom_tree.json")

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

        skool_login(page, creds["email"], creds["password"])

        if args.debug:
            run_debug(page, community_url)
            ctx.close()
            browser.close()
            return

        print("\nCrawling … (this takes 1–3 minutes)")
        t0 = time.time()
        tree = crawl_classroom(page, community_url)
        elapsed = time.time() - t0

        total_lessons = sum(len(m["lessons"]) for m in tree)
        total_videos  = sum(
            sum(len(l["videos"]) for l in m["lessons"]) + len(m["videos"])
            for m in tree
        )
        print(f"\nCrawl done in {elapsed:.1f}s")
        print(f"  {len(tree)} modules  |  {total_lessons} lessons  |  {total_videos} videos")

        out_json.write_text(json.dumps(tree, ensure_ascii=False, indent=2), encoding="utf-8")
        print(f"  → {out_json}")

        html = build_html(tree, community_url)
        out_html.write_text(html, encoding="utf-8")
        print(f"  → {out_html}")

        # Open the tree in the same authenticated browser
        abs_uri = out_html.resolve().as_uri()
        print(f"\nOpening: {abs_uri}")
        page.goto(abs_uri, wait_until="domcontentloaded")

        print("\nBrowser open — click ▶ Afspil or lesson titles.")
        print("Press Enter to close …")
        input()

        ctx.close()
        browser.close()

    print("Done.")


if __name__ == "__main__":
    main()
