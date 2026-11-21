#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
按 emos 动态片单规范生成 JSON
规范来源：https://wiki.emos.best/api/watch
  { name, cover, updated_at, videos:[{tmdb_id, tmdb_type, title, sort}] }

用法：
  TMDB_KEY=xxx python3 generate.py      # 需要 TMDB v3 api_key
输出：watch/*.json（每个文件对应一个片单，URL 直接填进 emos 面板）
"""

import json
import os
import sys
import time
import urllib.parse
import urllib.request

TMDB_KEY = os.environ.get("TMDB_KEY", "").strip()
LANG = os.environ.get("TMDB_LANG", "zh-CN")
IMG = "https://image.tmdb.org/t/p/w500"
OUT_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "watch")

# slug: (片单标题, 数据源, 只取 movie/tv 类型?, 条数, 额外查询参数)
FEEDS = {
    "hot-movies": ("今日热门电影", "/movie/popular", "movie", 20, {}),
    "hot-tv": ("今日热门剧集", "/tv/popular", "tv", 20, {}),
    "trending-week": ("本周趋势", "/trending/all/week", None, 20, {}),
    "top-rated": ("高分电影 Top250", "/movie/top_rated", "movie", 20, {}),
    # 最新国漫 TOP50：中国大陆出品、按首播日期倒序
    "guoman-top50": ("最新国漫TOP50", "/discover/tv", "tv", 50,
                     {"with_origin_country": "CN", "sort_by": "first_air_date.desc",
                      "vote_count.gte": "0"}),
}
LIMIT = 20  # 默认条数；emos 的 sort 范围 1-100


def api(path, page=1, extra=None):
    params = {"api_key": TMDB_KEY, "language": LANG, "page": page}
    if extra:
        params.update(extra)
    q = urllib.parse.urlencode(params)
    url = f"https://api.themoviedb.org/3{path}?{q}"
    with urllib.request.urlopen(url, timeout=30) as r:
        return json.loads(r.read().decode())


def beijing_now():
    return time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime(time.time() + 8 * 3600))


def build(slug, title, path, forced_type, limit=LIMIT, extra=None):
    items = []
    page = 1
    while len(items) < limit and page <= 5:
        data = api(path, page, extra)
        items.extend(data.get("results", []))
        if page >= int(data.get("total_pages") or 1):
            break
        page += 1

    videos = []
    cover = None
    for it in items:
        mt = forced_type or it.get("media_type")
        if mt not in ("movie", "tv"):
            continue
        if not it.get("id"):
            continue
        if cover is None and it.get("poster_path"):
            cover = IMG + it["poster_path"]
        videos.append({
            "tmdb_id": int(it["id"]),
            "tmdb_type": mt,
            "title": (it.get("title") or it.get("name") or "").strip() or "未命名",
            "sort": len(videos) + 1,
        })
        if len(videos) >= limit:
            break

    payload = {
        "name": title,
        "cover": cover or "https://emos.dpdns.org/img/docusaurus-social-card.jpg",
        "updated_at": beijing_now(),
        "videos": videos,
    }
    os.makedirs(OUT_DIR, exist_ok=True)
    out = os.path.join(OUT_DIR, f"{slug}.json")
    with open(out, "w", encoding="utf-8") as f:
        json.dump(payload, f, ensure_ascii=False, indent=1)
    print(f"{slug}: {len(videos)} 条 -> {out}")


def main():
    if not TMDB_KEY:
        print("跳过：未设置 TMDB_KEY")
        return 1
    for slug, (title, path, forced, limit, extra) in FEEDS.items():
        try:
            build(slug, title, path, forced, limit, extra)
        except Exception as e:
            print(f"{slug} 失败：{e}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
