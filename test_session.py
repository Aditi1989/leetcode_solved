# test_session.py
from dotenv import load_dotenv
import os, requests
load_dotenv()
s = requests.Session()
s.cookies.set("LEETCODE_SESSION", os.getenv("LEETCODE_SESSION"), domain=".leetcode.com")
r = s.get("https://leetcode.com/api/problems/all/")
print("HTTP", r.status_code)
try:
    print("Keys:", list(r.json().keys())[:6])
except Exception as e:
    print("JSON parse error (maybe HTML response):", e)
