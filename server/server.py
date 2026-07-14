#!/usr/bin/env python3
"""HotSpot Tracker v2.0 - Multi-platform global hot topic aggregator."""
import json, time, threading, urllib.request, re, os, html as html_mod
from datetime import datetime, timezone, timedelta
from http.server import HTTPServer, SimpleHTTPRequestHandler

DEEPSEEK_KEY = os.environ.get("DEEPSEEK_KEY", "")
PORT = int(os.environ.get("PORT", 3001))
FETCH_INTERVAL = 45
REPO_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")
GIT_PUSH_CYCLE = 3  # git push every N fetch cycles
TZ = timezone(timedelta(hours=8))
CATEGORIES = ["娱乐","体育","科技","财经","游戏","社会","教育","旅游","军事","国际","其他"]
REGIONS = {
    "CN":{"name":"中国","flag":"🇨🇳"},
    "HK":{"name":"香港","flag":"🇭🇰"},
    "JP":{"name":"日本","flag":"🇯🇵"},
    "KR":{"name":"韩国","flag":"🇰🇷"},
    "TH":{"name":"泰国","flag":"🇹🇭"},
    "IN":{"name":"印度","flag":"🇮🇳"},
    "SA":{"name":"沙特","flag":"🇸🇦"},
    "BR":{"name":"巴西","flag":"🇧🇷"},
    "US":{"name":"美国","flag":"🇺🇸"},
    "EU":{"name":"欧洲","flag":"🇪🇺"},
    "GB":{"name":"英国","flag":"🇬🇧"},
    "RU":{"name":"俄罗斯","flag":"🇷🇺"},
}
PLATFORM_META = {
    "weibo":{"name":"微博","icon":"\U0001f4e2","type":"real"},
    "bilibili":{"name":"B站","icon":"\U0001f4fa","type":"real"},
    "youtube":{"name":"YouTube","icon":"\u25b6\ufe0f","type":"real"},
    "x":{"name":"X","icon":"\U0001f426","type":"real"},
    "tiktok":{"name":"TikTok","icon":"\U0001f3ac","type":"inferred"},
    "instagram":{"name":"Instagram","icon":"\U0001f4f7","type":"inferred"},
    "facebook":{"name":"Facebook","icon":"\U0001f4d8","type":"inferred"},
}

cache = {}
for p in ["weibo","bilibili","youtube","x","inferred"]:
    cache[p] = {"data":[],"ts":0,"error":None}
cache["merged"] = {"data":None,"ts":0}
cache["classified"] = {"data":None,"ts":0}

UA = "Mozilla/5.0 (compatible; HotSpotBot/2.0)"
DEF_HEADERS = {"User-Agent":UA,"Accept":"application/json, text/plain, */*","Accept-Language":"zh-CN,zh;q=0.9,en;q=0.8"}

def fetch_weibo():
    items = []
    for url in ["https://weibo.com/ajax/side/hotSearch","https://weibo.com/ajax/statuses/hot_band"]:
        try:
            hdrs = dict(DEF_HEADERS)
            hdrs["Referer"] = "https://weibo.com/hot/search"
            req = urllib.request.Request(url, headers=hdrs)
            resp = urllib.request.urlopen(req, timeout=12)
            data = json.loads(resp.read())
            source = data.get("data", {})
            lst = source.get("realtime") or source.get("band_list") or []
            for idx, item in enumerate(lst):
                title = str(item.get("word", item.get("note", ""))).strip()
                if title and len(title) > 3:
                    items.append({"title":title,"rank":item.get("realpos",idx+1),
                        "heat_raw":item.get("num",0) or item.get("raw_hot",0),"platform":"weibo"})
            if items: break
        except: continue
    return items[:25]

def fetch_bilibili():
    hdrs = dict(DEF_HEADERS)
    hdrs["Referer"] = "https://www.bilibili.com/v/popular/rank/all"
    try:
        req = urllib.request.Request("https://api.bilibili.com/x/web-interface/popular?ps=50", headers=hdrs)
        resp = urllib.request.urlopen(req, timeout=12)
        data = json.loads(resp.read())
        items = []
        for idx, item in enumerate(data.get("data",{}).get("list",[])):
            stat = item.get("stat",{})
            title = str(item.get("title","")).strip()
            if title and len(title) > 3:
                items.append({"title":title,"rank":idx+1,"heat_raw":stat.get("view",0),
                    "discussion_raw":stat.get("danmaku",0),"platform":"bilibili"})
        return items[:30]
    except: return []

def fetch_youtube():
    feeds = ["https://www.youtube.com/feeds/videos.xml?gl=US&hl=en",
        "https://www.youtube.com/feeds/videos.xml?gl=JP&hl=ja",
        "https://www.youtube.com/feeds/videos.xml?gl=KR&hl=ko",
        "https://www.youtube.com/feeds/videos.xml?gl=GB&hl=en"]
    all_titles = []
    for furl in feeds:
        try:
            req = urllib.request.Request(furl, headers={"User-Agent":UA})
            resp = urllib.request.urlopen(req, timeout=15)
            xml = resp.read().decode('utf-8', errors='replace')
            for entry in re.findall(r'<entry>(.*?)</entry>', xml, re.DOTALL):
                m = re.search(r'<title>(.*?)</title>', entry)
                if m:
                    t = html_mod.unescape(m.group(1).strip())
                    if t and len(t) > 3: all_titles.append(t)
        except: continue
    seen = set(); items = []
    for t in all_titles:
        k = re.sub(r'\W+','',t.lower())[:40]
        if k not in seen and len(k) > 3:
            seen.add(k)
            items.append({"title":t,"rank":len(items)+1,"heat_raw":max(10,95-len(items)),"platform":"youtube"})
    return items[:25]

def fetch_x():
    for url in ["https://nitter.net/tweets/trending/rss","https://nitter.privacydev.net/tweets/trending/rss"]:
        try:
            req = urllib.request.Request(url, headers={"User-Agent":UA})
            resp = urllib.request.urlopen(req, timeout=12)
            content = resp.read().decode('utf-8', errors='replace')
            items = []
            for entry in re.findall(r'<item>(.*?)</item>', content, re.DOTALL):
                m = re.search(r'<title>(.*?)</title>', entry)
                if m:
                    title = html_mod.unescape(m.group(1).strip())
                    if title and len(title) > 3 and not title.startswith("RT "):
                        items.append({"title":title,"rank":len(items)+1,"heat_raw":max(10,85-len(items)*3),"platform":"x"})
            if items: return items[:25]
        except: continue
    return []

def fetch_inferred(domestic):
    if not DEEPSEEK_KEY or not domestic: return []
    titles_block = "\n".join("{}. {}".format(i+1,t["title"]) for i,t in enumerate(domestic[:8]))
    prompt = ("You are a global social media trend analyst. Generate PLAUSIBLE current trending topics "
        "for Facebook, Instagram, and TikTok RIGHT NOW. Chinese trending for context:\n"
        + titles_block + "\n\n"
        "Return JSON array: [{\"id\":1,\"title\":\"...\",\"platform\":\"facebook\"|\"instagram\"|\"tiktok\","
        "\"rank\":1,\"heat\":9.5},...]\n"
        "Make titles REALISTIC global trends. 30 items total (10 per platform). Return ONLY valid JSON array.")
    body = json.dumps({"model":"deepseek-chat","messages":[{"role":"user","content":prompt}],
        "temperature":0.5,"max_tokens":3000}).encode()
    try:
        req = urllib.request.Request("https://api.deepseek.com/v1/chat/completions", data=body)
        req.add_header("Content-Type","application/json")
        req.add_header("Authorization","Bearer {}".format(DEEPSEEK_KEY))
        resp = urllib.request.urlopen(req, timeout=60)
        text = json.loads(resp.read())["choices"][0]["message"]["content"].strip()
        m = re.search(r'\[.*\]', text, re.DOTALL)
        if m:
            items = json.loads(m.group(0))
            valid = []
            for item in items:
                if isinstance(item,dict) and "title" in item and len(str(item["title"])) > 3:
                    item["platform"] = item.get("platform","facebook")
                    item["heat_raw"] = float(item.get("heat",5.0))
                    item["rank"] = int(item.get("rank",len(valid)+1))
                    item["source_type"] = "inferred"
                    valid.append(item)
            return valid
    except Exception as e: print("[DeepSeek] infer err: {}".format(e))
    return []

def normalize_title(title):
    return re.sub(r'[#\s\W]+','',str(title)).lower()[:60]

def merge(platform_data):
    all_items = {}
    for platform, items in platform_data.items():
        if not items: continue
        for item in items:
            key = normalize_title(item.get("title",""))
            if not key or len(key) < 4: continue
            if key not in all_items: all_items[key] = {"title":item["title"],"platforms":[]}
            all_items[key]["platforms"].append({"platform":item.get("platform",platform),
                "heat_raw":item.get("heat_raw",0),"rank":item.get("rank",0),
                "discussion_raw":item.get("discussion_raw",0),
                "source_type":item.get("source_type","real"),"label":item.get("label","")})
    topics = []
    for key, data in all_items.items():
        plats = data["platforms"]
        total_heat = sum(p["heat_raw"] for p in plats)
        num = max(len(plats),1)
        heat_score = round(min(10,(total_heat/num)*0.1),1) if total_heat > 0 else 5.0
        plats.sort(key=lambda p: p["heat_raw"], reverse=True)
        topics.append({"title":data["title"],"heat_score":heat_score,"heat_trend":"up",
            "first_seen_at":datetime.now(TZ).isoformat(),"category":"其他","regions":["CN"],
            "platforms":[{"platform":p["platform"],"platform_rank":p["rank"],
                "platform_heat":round(min(10,p["heat_raw"]*0.1),1) if p["heat_raw"] else 5.0,
                "discussion_count":p.get("discussion_raw",0),"interaction_count":0,
                "read_count":p["heat_raw"],"source_type":p.get("source_type","real")} for p in plats],
            "primary_platform":plats[0]["platform"]})
    return topics

def classify(topics):
    if not topics: return topics
    try:
        titles_str = "\n".join("{}. {}".format(i+1,t["title"]) for i,t in enumerate(topics[:20]))
        cats = " ".join(CATEGORIES)
        regions_str = " ".join(REGIONS.keys())
        prompt = "Classify trending topics. Return JSON array with id, category (from: {}), regions (from: {}).\nTopics:\n{}\nReturn ONLY: [{{\"id\":1,\"category\":\"娱乐\",\"regions\":[\"CN\",\"US\"]}},...]".format(cats, regions_str, titles_str)
        body = json.dumps({"model":"deepseek-chat","messages":[{"role":"user","content":prompt}],"temperature":0.2,"max_tokens":2000}).encode()
        req = urllib.request.Request("https://api.deepseek.com/v1/chat/completions", data=body)
        req.add_header("Content-Type","application/json")
        req.add_header("Authorization","Bearer {}".format(DEEPSEEK_KEY))
        resp = urllib.request.urlopen(req, timeout=30)
        text = json.loads(resp.read())["choices"][0]["message"]["content"].strip()
        m = re.search(r'\[.*\]', text, re.DOTALL)
        if m:
            for item in json.loads(m.group(0)):
                idx = item.get("id",0) - 1
                if 0 <= idx < len(topics):
                    topics[idx]["category"] = item.get("category","其他")
                    topics[idx]["regions"] = item.get("regions",["CN"])
            return topics
    except Exception as e: print("[DeepSeek] classify err: {}".format(e))
    rules = [
        (["比赛","队","世界杯","NBA","欧冠","体育","足球","篮球","奥运"], "体育"),
        (["AI","科技","芯片","苹果","华为","特斯拉","小米","OpenAI","GPT","ChatGPT"], "科技"),
        (["明星","电影","音乐","演唱会","综艺","剧","演员","歌手","Eras","Taylor"], "娱乐"),
        (["股票","基金","经济","金融","房价","汇率","A股","投资"], "财经"),
        (["游戏","电竞","英雄联盟","王者","原神","黑神话"], "游戏"),
        (["台风","地震","天气","灾害","事故","洪水","火灾"], "社会"),
        (["高考","学校","大学","考试","教育","学生"], "教育"),
        (["旅游","旅行","景点","酒店"], "旅游"),
        (["军事","战争","导弹","航母","军队","国防","NATO"], "军事"),
        (["联合国","WTO","G7","G20","国际","外交"], "国际"),
    ]
    for i, t in enumerate(topics):
        title = t["title"].lower()
        if t.get("category","其他") != "其他": continue
        for keywords, c in rules:
            if any(kw.lower() in title for kw in keywords):
                t["category"] = c; break
        regions = t.get("regions",["CN"])
        for code in REGIONS:
            if code == "CN": continue
            if REGIONS[code]["name"] in title or code.lower() in title:
                if code not in regions: regions.append(code)
        t["regions"] = regions[:3]
    return topics

def git_push_data():
    """Write data.json and git push to GitHub."""
    try:
        merged = cache.get("merged", {})
        if not merged or not merged.get("data"):
            return
        data_path = os.path.join(REPO_DIR, "data.json")
        topics = merged["data"]
        # Simplify for frontend: keep only essential fields
        compact = []
        for t in topics:
            compact.append({
                "title": t["title"],
                "heat_score": t["heat_score"],
                "category": t.get("category", "其他"),
                "regions": t.get("regions", ["CN"]),
                "primary_platform": t.get("primary_platform", "weibo"),
                "platforms": [{"platform": p["platform"], "platform_rank": p["platform_rank"],
                    "platform_heat": p["platform_heat"], "discussion_count": p.get("discussion_count", 0),
                    "read_count": p.get("read_count", 0), "source_type": p.get("source_type", "real")}
                    for p in t.get("platforms", [])[:4]]
            })
        payload = {
            "topics": compact,
            "meta": {
                "updated_at": datetime.fromtimestamp(merged.get("ts", 0), TZ).isoformat(),
                "total": len(compact),
                "platform_stats": merged.get("platform_stats", {}),
                "source": "微博热搜 + B站热门"
            }
        }
        # Check if data changed significantly
        old_text = ""
        if os.path.exists(data_path):
            with open(data_path, 'r') as f:
                old_text = f.read()
        new_text = json.dumps(payload, ensure_ascii=False, separators=(",", ":"))
        if old_text == new_text:
            return  # No change, skip push
        with open(data_path, 'w') as f:
            f.write(new_text)
        # Git push
        import subprocess
        subprocess.run(["git", "-C", REPO_DIR, "add", "data.json"], capture_output=True, timeout=10)
        subprocess.run(["git", "-C", REPO_DIR, "commit", "-m",
            f"Auto-update: {len(compact)} topics [{datetime.now(TZ).strftime('%H:%M')}]"],
            capture_output=True, timeout=10)
        result = subprocess.run(["git", "-C", REPO_DIR, "push", "origin", "main"],
            capture_output=True, timeout=30)
        if result.returncode == 0:
            print(f"[GitPush] Pushed {len(compact)} topics to GitHub")
        else:
            print(f"[GitPush] Push result: {result.returncode} {result.stderr.decode()[:150]}")
    except Exception as e:
        print(f"[GitPush] Error: {e}")

def fetch_loop():
    cycle_count = 0
    while True:
        cycle_start = time.time()
        all_topics = []
        for fetcher, name in [(fetch_weibo,"weibo"),(fetch_bilibili,"bilibili"),(fetch_youtube,"youtube"),(fetch_x,"x")]:
            try:
                data = fetcher()
                if data:
                    cache[name] = {"data":data,"ts":time.time(),"error":None}
                    all_topics.extend([dict(t,platform=name) for t in data])
                    print("[Fetch] {}: {}".format(name,len(data)))
            except Exception as e: cache[name]["error"] = str(e)[:100]
        try:
            domestic = [t for t in all_topics if t.get("platform") in ("weibo","bilibili")]
            if domestic:
                infr = fetch_inferred(domestic)
                if infr:
                    cache["inferred"] = {"data":infr,"ts":time.time(),"error":None}
                    all_topics.extend([dict(t) for t in infr])
                    fb = sum(1 for t in infr if t["platform"]=="facebook")
                    ig = sum(1 for t in infr if t["platform"]=="instagram")
                    tk = sum(1 for t in infr if t["platform"]=="tiktok")
                    print("[Fetch] Inferred: FB={} IG={} TK={}".format(fb,ig,tk))
        except Exception as e: cache["inferred"]["error"] = str(e)[:100]
        if all_topics:
            pd = {}
            for t in all_topics:
                p = t.get("platform","unknown")
                pd.setdefault(p,[]).append(t)
            merged = merge(pd)
            merged.sort(key=lambda t: t["heat_score"], reverse=True)
            merged = classify(merged)
            cache["merged"] = {"data":merged,"ts":time.time(),"count":len(merged),
                "platform_stats":{p:len(cache[p]["data"]) for p in ["weibo","bilibili","youtube","x","inferred"]}}
            print("[Merge] Total: {} | {}".format(len(merged),cache["merged"]["platform_stats"]))
        elapsed = time.time() - cycle_start
        # Git push data every N cycles
        cycle_count += 1
        if cycle_count % GIT_PUSH_CYCLE == 0:
            threading.Thread(target=git_push_data, daemon=True).start()
        time.sleep(max(5, FETCH_INTERVAL - elapsed))

class Handler(SimpleHTTPRequestHandler):
    def do_GET(self):
        path = self.path.split("?")[0]
        if path == "/api/v1/hotlist": self._hotlist()
        elif path.startswith("/api/v1/hotlist/"): self._hotlist(region=path.split("/")[-1].upper())
        elif path == "/api/v1/topics": self._topics()
        elif path == "/api/v1/status": self._status()
        elif path == "/api/health": self._json({"status":"ok","time":datetime.now(TZ).isoformat()})
        elif path in ("/","/index.html"): self._serve_h5()
        else: super().do_GET()
    def _hotlist(self, region=None):
        merged = cache.get("merged",{})
        if not merged.get("data"):
            self._json({"error":"Initializing data collection...","status":"loading"},503); return
        topics = merged["data"]
        if region and region in REGIONS:
            topics = [t for t in topics if region in t.get("regions",["CN"])]
            topics.sort(key=lambda t: t["heat_score"], reverse=True)
        self._json({"topics":topics[:50],"meta":{"updated_at":datetime.fromtimestamp(merged.get("ts",0),TZ).isoformat(),
            "total":len(topics),"region":region or "all","platform_stats":merged.get("platform_stats",{}),
            "regions_available":list(REGIONS.keys())}})
    def _topics(self):
        merged = cache.get("merged",{})
        if not merged or not merged.get("data"): self._json({"error":"No data yet"},503); return
        self._json({"topics":merged["data"][:50],"updated_at":datetime.fromtimestamp(merged.get("ts",0),TZ).isoformat(),"total":len(merged["data"])})
    def _status(self):
        errors = {p:cache[p]["error"] for p in ["weibo","bilibili","youtube","x","inferred"] if cache[p].get("error")}
        self._json({"status":"ok","time":datetime.now(TZ).isoformat(),
            "platforms":{p:{"count":len(cache[p]["data"]),
                "last_fetch":datetime.fromtimestamp(cache[p].get("ts",0),TZ).isoformat() if cache[p].get("ts") else None,
                "age_sec":int(time.time()-cache[p].get("ts",0)) if cache[p].get("ts") else None}
                for p in ["weibo","bilibili","youtube","x","inferred"]},
            "merged":{"count":cache["merged"].get("count",0) if cache["merged"] else 0,
                "last_update":datetime.fromtimestamp(cache["merged"].get("ts",0),TZ).isoformat() if cache["merged"] else None},
            "errors":errors})
    def _serve_h5(self):
        h5_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "index.html")
        try:
            with open(h5_path, 'rb') as f: content = f.read()
            self.send_response(200)
            self.send_header("Content-Type","text/html; charset=utf-8")
            self.send_header("Content-Length",len(content))
            self.send_header("Access-Control-Allow-Origin","*")
            self.send_header("Cache-Control","public, max-age=60")
            self.end_headers()
            self.wfile.write(content)
        except FileNotFoundError: self.send_error(404, "index.html not found")
    def _json(self, data, status=200):
        body = json.dumps(data, ensure_ascii=False).encode('utf-8')
        self.send_response(status)
        self.send_header("Content-Type","application/json; charset=utf-8")
        self.send_header("Content-Length",len(body))
        self.send_header("Access-Control-Allow-Origin","*")
        self.send_header("Cache-Control","no-cache")
        self.end_headers()
        self.wfile.write(body)
    def log_message(self, format, *args): pass

def main():
    print("="*60)
    print("  HotSpot Tracker v2.0 - Multi-Platform Global Aggregator")
    print("  Port: {}".format(PORT))
    print("  API: http://localhost:{}/api/v1/hotlist".format(PORT))
    print("  Status: http://localhost:{}/api/v1/status".format(PORT))
    print("="*60)
    threading.Thread(target=fetch_loop, daemon=True).start()
    server = HTTPServer(("0.0.0.0", PORT), Handler)
    try: server.serve_forever()
    except KeyboardInterrupt: print("\n[Server] Shutting down...")

if __name__ == "__main__":
    main()
