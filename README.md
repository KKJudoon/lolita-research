# 军lo 热门款调研

记录国内 lolita 圈 **军lo（military Lolita）** 风格热门款，含设计师、店铺、上新时间、价格、销量、海报。

## 目录

- `data/<品牌_款名>.json` — 每款一个 JSON 文件，结构化字段
- `data/raw/` — 原始 opencli 抓取结果（追溯用，不直接渲染）
- `images/<品牌_款名>/` — 海报、模特图（本地下载）
- `index.html` — 由 `build.py` 渲染的展示页
- `build.py` — 读 `data/*.json` 生成 `index.html`

## 字段（JSON schema）

```jsonc
{
  "id": "string",                 // 唯一 id：拼音/英文，避免特殊字符
  "name": "款名",
  "designer": "设计师/品牌",
  "style_tags": ["军lo", ...],
  "style_summary": "一段视觉/工艺描述",
  "release": {
    "type": "意向金 + 全款 / 直接现货 / 众筹",
    "date_range": "YYYY-MM-DD ~ YYYY-MM-DD",
    "poster_first_seen": "YYYY-MM-DD",
    "note": "..."
  },
  "price": {
    "op": 520, "full_set": 648, "currency": "CNY",
    "deposit_link_intent": 5, "note": "..."
  },
  "colors": ["蓝黑", "红黑", ...],
  "shops": {
    "taobao":      { "url", "item_id", "shop_name", "list_title", "list_price", "sales", "sales_note", "location" },
    "weibo":       { "official_account", "alt_account", "upgrade_post_url", "upgrade_post_account", "post_date", "note" },
    "xiaohongshu": { "official_account", "note", "user_post_samples": [...] }
  },
  "posters": ["images/.../poster_xxx.jpg", ...],
  "verified": true,
  "verified_at": "YYYY-MM-DD",
  "verified_by": "Claude / 人工",
  "raw_sources": { "<key>": "data/raw/<file>.json" }
}
```

## 工作流

1. 用 opencli 在 m87 上跨平台搜款名（淘宝 sale 排序 + xhs/weibo 关键词）
2. 进 `taobao detail` / `weibo post` / `xiaohongshu note` 拿正文/海报
3. 交叉验证图片确认风格匹配军lo
4. 下载海报到 `images/<品牌_款名>/`
5. 写 `data/<品牌_款名>.json`
6. 跑 `python3 build.py` 重新渲染 `index.html`

## 已收录

- **樱洛芙Lolita · 终焉圣骸 2.0**（pilot）— 见 `data/樱洛芙_终焉圣骸2.0.json`
