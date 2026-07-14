#!/usr/bin/env python3
"""Overseas platform inference using DeepSeek.
Given domestic topics, infer plausible overseas ranking data."""
import json, urllib.request, re, time

DEEPSEEK_KEY = os.environ.get("DEEPSEEK_KEY", "")

OVERSEAS_PLATFORMS = [
    "x", "youtube", "tiktok", "instagram",
    "facebook", "google_trends", "snapchat"
]

def infer_overseas(topics):
    """Use DeepSeek to infer overseas platform rankings for domestic topics."""
    if not topics:
        return None

    titles_block = []
    for i, t in enumerate(topics[:20]):
        rnk = t.get("rank", i+1)
        ht = t.get("heat", 0)
        cat = t.get("category", "N/A")
        titles_block.append(
            f"{i+1}. [rank:{rnk}][heat:{ht}][cat:{cat}] {t['title']}"
        )

    prompt = (
        "You are a global social media analyst. Given hot topics below from China, "
        "plausibly infer their performance on overseas platforms.\n\n"
        "Platforms to estimate: x (Twitter), youtube, tiktok, instagram, "
        "facebook, google_trends, snapchat\n\n"
        "Rules:\n"
        "1. China domestic policy topics = rank 40-50 overseas, very low heat\n"
        "2. Natural disasters = moderate global interest, rank 15-25\n"
        "3. Tech/manufacturing = moderate STEM interest, rank 20-30\n"
        "4. Social phenomena = mostly CN only, rank 40-50\n"
        "5. Entertainment/sports/music = broad global appeal, rank 1-15\n"
        "6. Cross-cultural content = moderate, rank 15-30\n"
        "7. For each topic estimate per-platform rank (1=top, 50=very low), "
        "and heat score (1-10, 10=hottest)\n\n"
        "Return ONLY valid JSON array. Example of one item:\n"
        '{"id":1,"x":{"rank":5,"heat":7,"discussion_k":120},'
        '"youtube":{"rank":8,"heat":6,"views_k":350},'
        '"tiktok":{"rank":6,"heat":7,"hashtag_views_m":2.5},'
        '"instagram":{"rank":10,"heat":5,"engagement_k":30},'
        '"facebook":{"rank":12,"heat":5,"discussion_k":40},'
        '"google_trends":{"rank":8,"heat":6,"search_index":50},'
        '"snapchat":{"rank":15,"heat":4,"story_mentions_k":10},'
        '"justification":"1-line reasoning"}\n\n'
        "Topics:\n" + "\n".join(titles_block)
    )

    body = json.dumps({
        "model": "deepseek-chat",
        "messages": [{"role": "user", "content": prompt}],
        "temperature": 0.3,
        "max_tokens": 3000,
    }).encode()

    try:
        req = urllib.request.Request(
            "https://api.deepseek.com/v1/chat/completions", data=body
        )
        req.add_header("Content-Type", "application/json")
        req.add_header("Authorization", f"Bearer {DEEPSEEK_KEY}")
        resp = urllib.request.urlopen(req, timeout=60)
        result = json.loads(resp.read())
        text = result["choices"][0]["message"]["content"].strip()
        json_match = re.search(r"\[.*\]", text, re.DOTALL)
        if json_match:
            return json.loads(json_match.group(0))
    except Exception as e:
        print(f"[Overseas] DeepSeek error: {e}")

    return None


def apply_overseas_to_topics(topics, overseas_data):
    """Merge overseas inference data into topics."""
    if not overseas_data:
        return topics

    for item in overseas_data:
        idx = item.get("id", 0) - 1
        if 0 <= idx < len(topics):
            platforms = topics[idx].get("platforms", [])

            for pname in OVERSEAS_PLATFORMS:
                pd = item.get(pname, {})
                if pd:
                    platform_entry = {
                        "platform": pname,
                        "platform_rank": pd.get("rank", 50),
                        "platform_heat": pd.get("heat", 5),
                    }
                    if pname in ("x", "facebook"):
                        platform_entry["discussion_count"] = pd.get("discussion_k", 0) * 1000
                    elif pname == "instagram":
                        platform_entry["engagement_k"] = pd.get("engagement_k", 0)
                    elif pname == "youtube":
                        platform_entry["views_k"] = pd.get("views_k", 0)
                    elif pname == "tiktok":
                        platform_entry["hashtag_views_m"] = pd.get("hashtag_views_m", 0)
                    elif pname == "google_trends":
                        platform_entry["search_index"] = pd.get("search_index", 0)
                    elif pname == "snapchat":
                        platform_entry["story_mentions_k"] = pd.get("story_mentions_k", 0)
                    platforms.append(platform_entry)

            topics[idx]["platforms"] = platforms
            topics[idx]["_overseas_justification"] = item.get("justification", "")

    return topics


def get_overseas_stats(topics):
    """Get summary of overseas coverage."""
    total = len(topics)
    with_overseas = sum(
        1 for t in topics
        if any(p["platform"] in OVERSEAS_PLATFORMS for p in t.get("platforms", []))
    )
    return {
        "total_topics": total,
        "with_overseas_data": with_overseas,
        "platforms": OVERSEAS_PLATFORMS,
        "method": "DeepSeek inference based on domestic ranking correlation",
    }
