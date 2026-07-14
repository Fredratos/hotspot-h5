#!/usr/bin/env python3
"""Write server.py cleanly to avoid encoding corruption."""
import sys

content = r'''#!/usr/bin/env python3
"""
HotSpot Tracker - Real-time data collection server
Fetches Weibo + Bilibili hourly hot topics, uses DeepSeek for classification.
Serves REST API + static H5 frontend on port 3001.
"""
import json, time, threading, urllib.request, re, os
from datetime import datetime, timezone, timedelta
from http.server import HTTPServer, SimpleHTTPRequestHandler

#=================================================================
# Config
#=================================================================
DEEPSEEK_KEY = os.environ.get("DEEPSEEK_KEY", "")
PORT = int(os.environ.get("PORT", 3001))
FETCH_INTERVAL = 60
TZ = timezone(timedelta(hours=8))

CATEGORIES = ["娱乐","体育","科技","财经","游戏","社会","教育","旅游","军事","其他"]

REGION_KEYS = {
    "CN": ["中国","国内","北京","上海","广东","深圳","国产","华为"],
    "HK": ["香港","港","Hong Kong"],
    "TH": ["泰国","曼谷","普吉","泰"],
    "SA": ["沙特","中东","阿拉伯","利雅得"],
    "BR": ["巴西","里约","圣保罗","桑巴"],
    "US": ["美国","USA","拜登","特朗普","纽约","华盛顿","好莱坞"],
    "EU": ["欧洲","欧盟","英国","法国","德国","意大利","伦敦","巴黎"],
}

#=================================================================
# Global cache
#=================================================================
cache = {
    "weibo": {"data": [], "ts": 0},
    "bilibili": {"data": [], "ts": 0},
    "classified": {"data": None, "ts": 0},
}

#=================================================================
# Data fetchers
#=================================================================

def fetch_weibo():
    """Fetch Weibo real-time hot search - public API, no auth"""
    url = "https://weibo.com/ajax/side/hotSearch"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
        "Referer": "https://weibo.com/hot/search",
    }
    try:
        req = urllib.request.Request(url, headers=headers)
        resp = urllib.request.urlopen(req, timeout=10)
        data = json.loads(resp.read())
        items = []
        for item in data.get("data", {}).get("realtime", []):
            items.append({
                "title": item.get("word", ""),
                "rank": item.get("realpos", 0) or len(items) + 1,
                "heat": item.get("num", 0),
                "label": item.get("label_name", ""),
                "platform": "weibo",
            })
        return items[:20]
    except Exception as e:
        print(f"[Weibo] Error: {e}")
        # try fallback
        try:
            url2 = "https://weibo.com/ajax/statuses/hot_band"
            req2 = urllib.request.Request(url2, headers=headers)
            resp2 = urllib.request.urlopen(req2, timeout=10)
            d2 = json.loads(resp2.read())
            items = []
            band_list = d2.get("data", {}).get("band_list", [])
            for item in band_list:
                items.append({
                    "title": item.get("word", item.get("note", "")),
                    "rank": item.get("realpos", 0) or len(items) + 1,
                    "heat": item.get("num", 0),
                    "label": item.get("label_name", ""),
                    "platform": "weibo",
                })
            return items[:20]
        except Exception as e2:
            print(f"[Weibo] Fallback also failed: {e2}")
            return []

def fetch_bilibili():
    """Fetch Bilibili popular videos - public API"""
    url = "https://api.bilibili.com/x/web-interface/popular?ps=50"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
        "Referer": "https://www.bilibili.com",
    }
    try:
        req = urllib.request.Request(url, headers=headers)
        resp = urllib.request.urlopen(req, timeout=10)
        data = json.loads(resp.read())
        items = []
        for idx, item in enumerate(data.get("data", {}).get("list", [])):
            stat = item.get("stat", {})
            items.append({
                "title": item.get("title", ""),
                "rank": idx + 1,
                "heat": stat.get("view", 0),
                "discussion": stat.get("danmaku", 0),
                "platform": "bilibili",
            })
        return items[:50]
    except Exception as e:
        print(f"[Bilibili] Error: {e}")
        return []

#=================================================================
# DeepSeek classifier
#=================================================================

def classify_with_deepseek(topics):
    """Use DeepSeek to assign category + regions to topics"""
    titles_list = "\n".join(f"{i+1}. {t['title']}" for i, t in enumerate(topics))
    cats_str = " ".join(CATEGORIES)
    prompt = f"""Classify these hot topics. For each return JSON array with id, category (from: {cats_str}), and regions (from: CN,HK,TH,SA,BR,US,EU - multiple allowed).

Topics:
{titles_list}

Return ONLY valid JSON: [{{"id":1,"category":"娱乐","regions":["CN"]}},...]"""

    body = json.dumps({
        "model": "deepseek-chat",
        "messages": [{"role": "user", "content": prompt}],
        "temperature": 0.2,
        "max_tokens": 2000,
    }).encode()

    try:
        req = urllib.request.Request("https://api.deepseek.com/v1/chat/completions", data=body)
        req.add_header("Content-Type", "application/json")
        req.add_header("Authorization", f"Bearer {DEEPSEEK_KEY}")
        resp = urllib.request.urlopen(req, timeout=30)
        result = json.loads(resp.read())
        text = result["choices"][0]["message"]["content"].strip()
        json_match = re.search(r'\[.*\]', text, re.DOTALL)
        if json_match:
            return json.loads(json_match.group(0))
    except Exception as e:
        print(f"[DeepSeek] Error: {e}")
    return None

def classify_fast(topics):
    """Fast regex-based fallback classifier"""
    rules = [
        (["比赛","队","世界杯","NBA","欧冠","体育","足球","篮球","奥运"], "体育"),
        (["AI","科技","芯片","苹果","华为","特斯拉","小米","OpenAI","GPT"], "科技"),
        (["明星","电影","音乐","演唱会","综艺","剧","演员","歌手"], "娱乐"),
        (["股票","基金","经济","金融","房价","汇率","A股"], "财经"),
        (["游戏","电竞","英雄联盟","王者","原神","黑神话"], "游戏"),
        (["台风","地震","天气","灾害","事故","洪水","火灾"], "社会"),
        (["高考","学校","大学","考试","教育","学生"], "教育"),
        (["旅游","旅行","景点","酒店"], "旅游"),
        (["军事","战争","导弹","航母","军队","国防"], "军事"),
    ]
    results = []
    for i, t in enumerate(topics):
        title = t["title"].lower()
        cat = "其他"
        for keywords, c in rules:
            if any(kw.lower() in title for kw in keywords):
                cat = c
                break
        regions = ["CN"]
        for code, keys in REGION_KEYS.items():
            if code == "CN":
                continue
            if any(k.lower() in title for k in keys):
                regions.append(code)
        results.append({"id": i + 1, "category": cat, "regions": regions[:3]})
    return results

#=================================================================
# Topic merger
#=================================================================

def normalize_title(title):
    """Remove special chars for dedup"""
    return re.sub(r'[#\s\W]+', '', title).lower()

def merge_topics(weibo_items, bilibili_items):
    """Merge Weibo + Bilibili, deduplicate"""
    all_items = []
    seen = set()
    for item in (weibo_items or []) + (bilibili_items or []):
        key = normalize_title(item["title"])
        if key and key not in seen and len(key) > 4:
            seen.add(key)
            all_items.append(item)
    return all_items[:50]

def classify_topics(topics):
    """Apply classifications to topics"""
    try:
        result = classify_with_deepseek(topics[:20])
        if result:
            for item in result:
                idx = item.get("id", 0) - 1
                if 0 <= idx < len(topics):
                    topics[idx]["category"] = item.get("category", "其他")
                    topics[idx]["regions"] = item.get("regions", ["CN"])
            return topics
    except Exception as e:
        print(f"[Classify] DeepSeek failed: {e}")

    # Regex fallback
    classified = classify_fast(topics)
    for item in classified:
        idx = item.get("id", 0) - 1
        if 0 <= idx < len(topics):
            topics[idx]["category"] = item.get("category", "其他")
            topics[idx]["regions"] = item.get("regions", ["CN"])
    return topics

def calc_heat(topic, max_val):
    """Normalize heat 0-10"""
    if not topic.get("heat", 0) or max_val == 0:
        return 5.0
    return round(min(10, (topic["heat"] / max_val) * 10), 1)

def build_response():
    """Build full API response from cache"""
    w = cache["weibo"]["data"]
    b = cache["bilibili"]["data"]
    if not w and not b:
        return None

    all_topics = merge_topics(w, b)

    # Classify if needed
    if time.time() - cache["classified"]["ts"] > 300:
        all_topics = classify_topics(all_topics)
        cache["classified"] = {"data": list(all_topics), "ts": time.time()}
    elif cache["classified"]["data"]:
        # Match cached classifications to current items
        ct_map = {}
        for ct in cache["classified"]["data"]:
            ckey = normalize_title(ct.get("title", ""))
            if ckey:
                ct_map[ckey] = ct
        for t in all_topics:
            key = normalize_title(t["title"])
            if key in ct_map:
                t["category"] = ct_map[key].get("category", "其他")
                t["regions"] = ct_map[key].get("regions", ["CN"])

    # Ensure all have defaults
    max_h = max((t.get("heat", 0) for t in all_topics), default=1)
    for t in all_topics:
        if "category" not in t:
            t["category"] = "其他"
        if "regions" not in t:
            t["regions"] = ["CN"]
        t["heat_score"] = calc_heat(t, max_h)
        t["heat_trend"] = "up"
        t["first_seen_at"] = datetime.now(TZ).isoformat()
        t["platforms"] = [{
            "platform": t.get("platform", "weibo"),
            "platform_rank": t.get("rank", 0),
            "platform_heat": round(t.get("heat_score", 5), 1),
            "discussion_count": t.get("discussion", 0) or t.get("heat", 0),
            "interaction_count": 0,
            "read_count": t.get("heat", 0),
        }]

    return {
        "topics": all_topics[:20],
        "updated_at": datetime.now(TZ).isoformat(),
        "total_platforms": 2,
        "fetch_meta": {
            "weibo_count": len(w),
            "bilibili_count": len(b),
        }
    }

#=================================================================
# Background fetcher thread
#=================================================================

def fetch_all():
    """Loop: fetch all platforms every FETCH_INTERVAL seconds"""
    while True:
        try:
            w = fetch_weibo()
            if w:
                cache["weibo"] = {"data": w, "ts": time.time()}
                print(f"[Fetch] Weibo: {len(w)} topics")

            b = fetch_bilibili()
            if b:
                cache["bilibili"] = {"data": b, "ts": time.time()}
                print(f"[Fetch] Bilibili: {len(b)} topics")
        except Exception as e:
            print(f"[Fetch] Error: {e}")
        time.sleep(FETCH_INTERVAL)

#=================================================================
# HTTP request handler
#=================================================================

class Handler(SimpleHTTPRequestHandler):
    def do_GET(self):
        if self.path == "/api/v1/hotlist":
            data = build_response()
            if data:
                topics = data["topics"]
                self._json({
                    "topics": topics[:20],
                    "meta": {
                        "updated_at": data["updated_at"],
                        "total": len(topics),
                        "region": "all",
                        "fetch_meta": data.get("fetch_meta", {}),
                    }
                })
            else:
                self._json({"error": "No data yet, fetching..."}, 503)
        elif self.path.startswith("/api/v1/hotlist/"):
            region = self.path.split("/")[-1].upper()
            data = build_response()
            if data:
                topics = [t for t in data["topics"] if region in t.get("regions", ["CN"])]
                self._json({
                    "topics": topics[:20],
                    "meta": {
                        "updated_at": data["updated_at"],
                        "total": len(topics),
                        "region": region,
                        "fetch_meta": data.get("fetch_meta", {}),
                    }
                })
            else:
                self._json({"error": "No data yet"}, 503)
        elif self.path == "/api/v1/topics":
            data = build_response()
            self._json(data if data else {"error": "No data yet"}, 200 if data else 503)
        elif self.path == "/api/v1/status":
            self._json({
                "status": "ok",
                "time": datetime.now(TZ).isoformat(),
                "weibo": {"count": len(cache["weibo"]["data"]), "age_sec": int(time.time() - cache["weibo"]["ts"])},
                "bilibili": {"count": len(cache["bilibili"]["data"]), "age_sec": int(time.time() - cache["bilibili"]["ts"])},
            })
        elif self.path == "/api/health":
            self._json({"status": "ok", "time": datetime.now(TZ).isoformat()})
        elif self.path == "/" or self.path == "/index.html":
            self._serve_h5()
        else:
            super().do_GET()

    def _serve_h5(self):
        h5_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "index.html")
        try:
            with open(h5_path, 'rb') as f:
                content = f.read()
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.send_header("Content-Length", len(content))
            self.send_header("Cache-Control", "public, max-age=60")
            self.end_headers()
            self.wfile.write(content)
        except FileNotFoundError:
            self.send_error(404, "index.html not found")

    def _json(self, data, status=200):
        body = json.dumps(data, ensure_ascii=False).encode('utf-8')
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", len(body))
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Cache-Control", "no-cache")
        self.end_headers()
        self.wfile.write(body)

    def log_message(self, format, *args):
        pass

#=================================================================
# Main
#=================================================================

def main():
    print("[Server] Initial data fetch...")
    w = fetch_weibo()
    if w:
        cache["weibo"] = {"data": w, "ts": time.time()}
    b = fetch_bilibili()
    if b:
        cache["bilibili"] = {"data": b, "ts": time.time()}
    print(f"[Server] Weibo={len(w)}, Bilibili={len(b)}")

    # Initial classification
    all_t = merge_topics(w, b)
    if all_t:
        classified = classify_topics(all_t)
        cache["classified"] = {"data": list(classified), "ts": time.time()}

    # Start background fetcher
    threading.Thread(target=fetch_all, daemon=True).start()

    print(f"\n  HotSpot Tracker Server")
    print(f"  API:     http://localhost:{PORT}/api/v1/hotlist")
    print(f"  H5 SPA:  http://localhost:{PORT}/")
    print(f"  Status:  http://localhost:{PORT}/api/v1/status\n")

    server = HTTPServer(("0.0.0.0", PORT), Handler)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass

if __name__ == "__main__":
    main()
'''

with open('server.py', 'w', encoding='utf-8') as f:
    f.write(content)
print("server.py written successfully")
