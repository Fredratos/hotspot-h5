import json, base64, urllib.request, sys

TOKEN = "GITHUB_TOKEN_PLACEHOLDER"
REPO = "fredratos/hotspot-h5"
API = f"https://api.github.com/repos/{REPO}/contents"

def upload_file(path, message):
    with open(path, 'r') as f:
        content = f.read()
    body = json.dumps({
        "message": message,
        "content": base64.b64encode(content.encode()).decode()
    }).encode()
    req = urllib.request.Request(f"{API}/{path}", data=body, method="PUT")
    req.add_header("Authorization", f"token {TOKEN}")
    req.add_header("Accept", "application/vnd.github+json")
    try:
        resp = urllib.request.urlopen(req)
        result = json.loads(resp.read())
        print(f"  ✅ {path}: {result.get('commit', {}).get('html_url', 'OK')}")
    except urllib.error.HTTPError as e:
        err = json.loads(e.read())
        print(f"  ❌ {path}: {err.get('message', str(e))}")

# Upload files
print("Uploading to github.com/fredratos/hotspot-h5 ...")
upload_file("index.html", "🔥 Initial commit: HotSpot Tracker H5 SPA")
upload_file("README.md", "📝 Add README")
upload_file(".github/workflows/deploy.yml", "⚙️ Add GitHub Pages deploy workflow")

print("\n✅ Done! Visit: https://fredratos.github.io/hotspot-h5/")
print("(GitHub Pages may take 1-2 minutes to deploy after first push)")
