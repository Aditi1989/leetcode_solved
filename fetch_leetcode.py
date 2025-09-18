#!/usr/bin/env python3
"""
fetch_leetcode.py
Fetches all unique Accepted submissions from your LeetCode account (uses LEETCODE_SESSION from .env)
and saves them under ./solutions/<language>/{title_slug}.{ext}

Requirements:
    pip install requests python-dotenv
Run:
    python fetch_leetcode.py
"""

import os, time, re, sys
from pathlib import Path
import requests
from dotenv import load_dotenv
from html import unescape

# --- config ---
load_dotenv()
SESSION = os.getenv("LEETCODE_SESSION")
OUTDIR = Path("solutions")
PAGE_SIZE = 20   # number of submissions per page (20 is safe); will page automatically
SLEEP_BETWEEN_REQUESTS = 0.25
# ----------------

if not SESSION:
    print("LEETCODE_SESSION not found in environment (.env). Exiting.")
    sys.exit(1)

s = requests.Session()
s.headers.update({"User-Agent": "Mozilla/5.0", "Referer": "https://leetcode.com"})
s.cookies.set("LEETCODE_SESSION", SESSION, domain=".leetcode.com")

OUTDIR.mkdir(parents=True, exist_ok=True)

EXT = {
    'cpp': '.cpp', 'c++': '.cpp', 'java': '.java',
    'python3': '.py', 'python': '.py',
    'c': '.c', 'csharp': '.cs', 'c#': '.cs',
    'javascript': '.js', 'js': '.js', 'typescript': '.ts',
    'golang': '.go', 'ruby': '.rb', 'swift': '.swift',
    'kotlin': '.kt', 'php': '.php', 'rust': '.rs'
}

seen_slugs = set()
saved = 0
failed = []

def safe_name(s):
    return re.sub(r'[^A-Za-z0-9_\-]', '_', s)

def save_code(code, slug, lang, title):
    lang_dir = OUTDIR / (lang.lower() if lang else "other")
    lang_dir.mkdir(parents=True, exist_ok=True)
    ext = EXT.get(lang.lower() if lang else "", ".txt")
    filename = f"{safe_name(slug)}{ext}"
    path = lang_dir / filename
    # write code
    path.write_text(unescape(code), encoding="utf-8")
    # write a small metadata md for reference
    md = lang_dir / (safe_name(slug) + ".md")
    md.write_text(f"# {title}\n\nLeetCode: https://leetcode.com/problems/{slug}/\n\nLanguage: {lang}\n", encoding="utf-8")
    return path

def fetch_submission_code(submission_id):
    # Use GraphQL submissionDetail to get code
    gql = {
        "operationName":"submissionDetail",
        "variables":{"submissionId": str(submission_id)},
        "query": """
        query submissionDetail($submissionId: ID!) {
          submissionDetail(submissionId: $submissionId) {
            id
            code
            lang
            question {
              title
              titleSlug
            }
          }
        }
        """
    }
    try:
        r = s.post("https://leetcode.com/graphql", json=gql, timeout=15)
        if r.status_code == 200:
            j = r.json()
            detail = j.get("data", {}).get("submissionDetail")
            if detail:
                return detail.get("code"), detail.get("lang"), detail.get("question", {}).get("title"), detail.get("question", {}).get("titleSlug")
    except Exception as e:
        pass
    # fallback: try to fetch HTML detail page and extract code
    try:
        url = f"https://leetcode.com/submissions/detail/{submission_id}/"
        r = s.get(url, timeout=15)
        if r.status_code == 200:
            # look for submissionCode":"(escaped...)"
            m = re.search(r'submissionCode":"(.*?)"', r.text, re.DOTALL)
            if m:
                code = m.group(1).encode('utf-8').decode('unicode_escape')
                # get titleSlug from url or page
                m2 = re.search(r'question-title.*?href=".*?/problems/(.*?)/', r.text)
                slug = None
                if m2:
                    slug = m2.group(1)
                return code, None, None, slug
    except Exception:
        pass
    return None, None, None, None

# paging through submissions
offset = 0
while True:
    url = f"https://leetcode.com/api/submissions/?offset={offset}&limit={PAGE_SIZE}"
    print(f"Fetching page offset={offset} ...", end=" ", flush=True)
    r = s.get(url)
    if r.status_code != 200:
        print(f"FAILED (HTTP {r.status_code}). Response snippet: {r.text[:200]}")
        break
    data = r.json()
    subs = data.get("submissions_dump", [])
    print(f"got {len(subs)} submissions")
    if not subs:
        break

    for sub in subs:
        try:
            if sub.get("status_display") != "Accepted":
                continue
            slug = sub.get("title_slug") or sub.get("title")
            if not slug:
                continue
            if slug in seen_slugs:
                continue
            seen_slugs.add(slug)
            sid = sub.get("id")
            # fetch code (graphql)
            code, lang, title, qslug = fetch_submission_code(sid)
            if not code:
                failed.append((sid, slug))
                print(f" -> {slug}: FAILED to get code")
                continue
            real_slug = qslug or slug
            lang = lang or sub.get("lang") or "text"
            path = save_code(code, real_slug, lang, title or real_slug)
            print(f" -> saved {path}")
            saved += 1
            time.sleep(SLEEP_BETWEEN_REQUESTS)
        except Exception as e:
            print("error:", e)
            failed.append((sub.get("id"), sub.get("title_slug")))

    if not data.get("has_next", False):
        break
    offset += PAGE_SIZE
    # small pause between pages
    time.sleep(0.3)

print(f"\nDone. Saved {saved} problems.")
if failed:
    print("Failed to fetch code for these submission IDs (locked/premium or other):")
    for f in failed:
        print("  ", f)
