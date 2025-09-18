import os
import requests
from dotenv import load_dotenv

# Load environment variables from .env
load_dotenv()

LEETCODE_SESSION = os.getenv("LEETCODE_SESSION")
LEETCODE_CSRF = os.getenv("LEETCODE_CSRF")

if not LEETCODE_SESSION or not LEETCODE_CSRF:
    raise ValueError("Please set LEETCODE_SESSION and LEETCODE_CSRF in environment variables or .env file")

headers = {
    "x-csrftoken": LEETCODE_CSRF,
    "referer": "https://leetcode.com",
    "user-agent": "Mozilla/5.0"
}
cookies = {
    "LEETCODE_SESSION": LEETCODE_SESSION,
    "csrftoken": LEETCODE_CSRF
}

GRAPHQL_URL = "https://leetcode.com/graphql"
SUBMISSION_DETAIL_URL = "https://leetcode.com/api/submissions/{}/"

def fetch_submissions():
    """Fetch all accepted submissions"""
    has_more = True
    offset = 0
    limit = 20
    submissions = []

    while has_more:
        query = """
        query submissionList($offset: Int!, $limit: Int!) {
          submissionList(offset: $offset, limit: $limit) {
            hasNext
            submissions {
              id
              title
              titleSlug
              lang
              statusDisplay
            }
          }
        }
        """
        payload = {"query": query, "variables": {"offset": offset, "limit": limit}}
        r = requests.post(GRAPHQL_URL, json=payload, headers=headers, cookies=cookies)

        if r.status_code != 200:
            print(f"❌ Failed to fetch submissions at offset={offset}")
            break

        data = r.json()["data"]["submissionList"]
        subs = data["submissions"]
        has_more = data["hasNext"]
        offset += limit

        print(f"📥 Fetching submissions offset={offset - limit} ... got {len(subs)}")

        for s in subs:
            if s["statusDisplay"] == "Accepted":
                submissions.append(s)

    return submissions


def fetch_submission_code(submission_id):
    """Fetch code for a single submission"""
    url = SUBMISSION_DETAIL_URL.format(submission_id)
    r = requests.get(url, headers=headers, cookies=cookies)
    if r.status_code == 200:
        return r.json().get("code", "")
    return ""


def save_solution(sub):
    """Save submission code into folder"""
    code = fetch_submission_code(sub["id"])
    if not code:
        print(f"⚠️ Could not fetch code for {sub['titleSlug']}")
        return

    # Normalize language extensions
    lang_map = {
        "python": "py",
        "python3": "py",
        "cpp": "cpp",
        "java": "java",
        "c": "c",
        "csharp": "cs",
        "javascript": "js",
        "typescript": "ts",
        "go": "go",
        "ruby": "rb",
        "swift": "swift",
        "kotlin": "kt",
        "rust": "rs",
    }
    ext = lang_map.get(sub["lang"], sub["lang"])

    folder = f"{sub['id']}-{sub['titleSlug']}"
    os.makedirs(folder, exist_ok=True)
    filename = os.path.join(folder, f"solution.{ext}")

    with open(filename, "w", encoding="utf-8") as f:
        f.write(code)

    print(f"✅ Saved {filename}")


if __name__ == "__main__":
    print("✅ Loaded session and CSRF tokens")
    subs = fetch_submissions()
    print(f"📦 Total accepted submissions: {len(subs)}")

    for sub in subs:
        save_solution(sub)

    print("🎉 Done! All solutions saved.")
