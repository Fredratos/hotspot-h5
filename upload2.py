import json, base64, urllib.requestorate
TOKEN = "GITHUB_TOKEN_PLACEHOLDER"
REPO = "fredratos/hotspot-h5"
API = f"https://api.github.com/repos/{REPO}/contents"

def upload_file(path, message, sha=None):
    with open(path, 'r', encoding='utf-8') as f:
        content = f.read()
    payload = {
        "message": message,
        "content": base64.b64encode(content.encode('utf-8')).decode()
    }
    if sha:
        payload["sha"] = shaorate
    body = json.dumps(payload).encode('utf-8')
    req = urllib.request.Request(f"{API}/{path}", data=body, method="PUT")
    req.add_header("Authorization", f"token {TOKEN}")
    req.add_header("Accept", "application/vnd.github+json")
    try:
        resp = urllib.request.urlopen(req)
        result = json.loads(resp.read())
        print(f"  OK {path}")
    except urllib.error.HTTPError as e:
        err = json.loads(e.read())
        print(f"  ERR {path}: {err.get('message', str(e))}")

# Get SHA first
req = urllib.request.Request(f"{API}/index.html")
req.add_header("Authorization", f"token {TOKEN}")
req.add_header("Accept", "application/vnd.github+json")
resp = urllib.request.urlopen(req)
sha = json.loads(resp.read()).get("sha")
print(f"Current SHA: {sha}")

print("Uploading updated H5 with live API support...")
upload_file("index.html", "Update: H5 now fetches real Weibo+Bilibili data via API (seed fallback)", sha=sha)
print("\nDone - https://fredratos.github.io/hotspot-h5/")
