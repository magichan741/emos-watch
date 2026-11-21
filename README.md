# emos 动态片单接口

按 emos 动态片单规范（<https://wiki.emos.best/api/watch>）生成片单 JSON，托管在 GitHub Pages，
把 URL 填进 emos 面板即可让服务每天 8:00 / 17:00 自动抓取。

## 生成后的地址

| 片单 | URL |
|---|---|
| 今日热门电影 | `https://magichan741.github.io/emos-watch/watch/hot-movies.json` |
| 今日热门剧集 | `https://magichan741.github.io/emos-watch/watch/hot-tv.json` |
| 本周趋势 | `https://magichan741.github.io/emos-watch/watch/trending-week.json` |
| 高分电影 Top250 | `https://magichan741.github.io/emos-watch/watch/top-rated.json` |
| 最新国漫TOP50 | `https://magichan741.github.io/emos-watch/watch/guoman-top50.json` |

每个文件就是一个片单，字段严格按规范：`name` / `cover` / `updated_at` / `videos[].tmdb_id, tmdb_type, title, sort`。

## 接真实数据

1. TMDB 申请 v3 API Key：<https://www.themoviedb.org/settings/api>
2. 仓库 Settings → Secrets → Actions → 新增 `TMDB_KEY`
3. 手动跑一次 `Refresh watchlists`，`watch/*.json` 会被真实热榜覆盖并自动 commit

之后由 workflow 定时更新：北京时间每天 **7:50** 和 **16:50** 各跑一次，
比 emos 的抓取时间（8:00 / 17:00）提前 10 分钟，保证它抓到的是当天数据。

## 本地跑

```bash
TMDB_KEY=你的key python3 generate.py
```

## 注意事项

- `sort` 必须在 1–100，脚本按排名顺序从 1 递增，常规片单取前 20 条，国漫片单取 50 条
- 最新国漫TOP50 用 `/discover/tv?with_origin_country=CN&sort_by=first_air_date.desc`，翻 3 页凑 50 条
- `updated_at` 用北京时间 `YYYY-MM-DD HH:MM:SS`，不带时区后缀
- `cover` 取该片单第一条的 TMDB 海报（`w500`），静态样例阶段用了占位图
- 仓库 60 天无提交会暂停定时任务，Actions 页面点一下 Enable 即可恢复
