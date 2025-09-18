import os
import requests
from bs4 import BeautifulSoup

# Load session and CSRF tokens (replace with your real values or load from .env)
LEETCODE_SESSION = os.getenv("LEETCODE_SESSION")
CSRFTOKEN = os.getenv("LEETCODE_CSRF")

if not LEETCODE_SESSION or not CSRFTOKEN:
    raise ValueError("Please set LEETCODE_SESSION and LEETCODE_CSRF in environment variables")

HEADERS = {
    "User-Agent": "Mozilla/5.0",
    "Referer": "https://leetcode.com",
    "cookie": f"LEETCODE_SESSION={LEETCODE_SESSION}; csrftoken={CSRFTOKEN}",
    "x-csrftoken": CSRFTOKEN,
}

GRAPHQL_URL = "https://leetcode.com/graphql"
SOLUTIONS_DIR = "solutions"
os.makedirs(SOLUTIONS_DIR, exist_ok=True)


def fetch_submissions():
    submissions = []
    offset = 0
    limit = 20

    while True:
        query = """
        query recentAcSubmissions($offset: Int!, $limit: Int!) {
          submissionList(offset: $offset, limit: $limit) {
            submissions {
              id
              titleSlug
              statusDisplay
              lang
            }
          }
        }
        """
        variables = {"offset": offset, "limit": limit}
        resp = requests.post(GRAPHQL_URL, json={"query": query, "variables": variables}, headers=HEADERS)
        data = resp.json()

        subs = data["data"]["submissionList"]["submissions"]
        if not subs:
            break

        submissions.extend(subs)
        print(f"📥 Fetching submissions offset={offset} ... got {len(subs)}")

        offset += limit

    return submissions


def fetch_code(submission_id):
    """Try GraphQL first, fallback to scraping HTML"""
    # GraphQL query for submission detail
    query = """
    query submissionDetail($id: ID!) {
      submissionDetail(submissionId: $id) {
        code
      }
    }
    """
    resp = requests.post(GRAPHQL_URL, json={"query": query, "variables": {"id": submission_id}}, headers=HEADERS)
    try:
        code = resp.json()["data"]["submissionDetail"]["code"]
        if code:
            return code
    except:
        pass

    # Fallback: scrape HTML
    url = f"https://leetcode.com/submissions/detail/{submission_id}/"
    r = requests.get(url, headers=HEADERS)
    soup = BeautifulSoup(r.text, "html.parser")

    script = soup.find("script", string=lambda t: t and "submissionCode" in t)
    if script:
        text = script.string
        start = text.find("submissionCode: '")
        if start != -1:
            start += len("submissionCode: '")
            end = text.find("',", start)
            raw_code = text[start:end]
            return raw_code.encode().decode("unicode_escape")

    return None


def save_code(slug, lang, code):
    ext = {
        "python3": "py",
        "cpp": "cpp",
        "java": "java",
        "c": "c",
        "csharp": "cs",
        "javascript": "js",
    }.get(lang, lang)

    filename = f"{slug}.{ext}"
    filepath = os.path.join(SOLUTIONS_DIR, filename)

    with open(filepath, "w", encoding="utf-8") as f:
        f.write(code)

    print(f"💾 Saved {slug} -> {filepath}")


def main():
    print("✅ Loaded session and CSRF tokens")
    submissions = fetch_submissions()
    print(f"✅ Total accepted submissions fetched: {len(submissions)}")

    for sub in submissions:
        slug = sub["titleSlug"]
        sid = sub["id"]
        lang = sub["lang"]

        code = fetch_code(sid)
        if code:
            save_code(slug, lang, code)
        else:
            print(f"   ⚠️  {slug}: FAILED to get code")


if __name__ == "__main__":
    main()
