# 🔥 HotSpot Tracker v2.0

全球社交媒体热点聚合平台 - 实时追踪微博、B站、YouTube、X、Facebook、Instagram、TikTok 热门话题。

## 功能

- 🔥 **今日最热 TOP 3** - 跨平台综合热度排名，展示来源平台
- 📡 **实时快讯 TOP 10** - 最新上榜话题，含来源标识
- 🌍 **区域热点 TOP 20** - 按国家/地区查看热门话题，展示来源平台
- 🔍 **全站搜索** - 搜索全球热点话题
- 📊 **多平台溯源** - 每个话题展示跨平台热度与来源
- ⭐ **关注追踪** - 关注感兴趣的话题

## 数据源

| 平台 | 类型 | 获取方式 |
|------|------|----------|
| 微博 | CN | 实时API |
| Bilibili | CN | 实时API |
| YouTube | Global | RSS Feed |
| X (Twitter) | Global | RSS (Nitter) |
| Facebook | Global | AI推断 |
| Instagram | Global | AI推断 |
| TikTok | Global | AI推断 |

## 部署

GitHub Pages 自动部署：推送到 `main` 分支即可自动部署。

## 本地开发

```bash
cd server
python3 server.py  # 启动 API server on port 3001
```

前端静态文件可直接打开 `index.html`。

## 技术栈

- 前端：Vanilla HTML5/CSS3/JavaScript (SPA)
- 后端：Python3 HTTP Server + 多平台数据抓取
- AI：DeepSeek 话题分类 + 海外热度推断
