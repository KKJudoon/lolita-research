# 抖音 Lolita 画师监控战略 v2

最后更新：2026-05-11

## 🎯 核心战略（2026-05-11 重新对齐）

**旧模型**：找"专画军lo 的画师" → 监控他们 → 抢稿
**新模型**：**画师都不专精军lo，但偶尔一张军lo 设计稿会 viral 爆红** → 监控**所有 lolita 画师**的**新帖**，识别军lo 类型，捕捉**早期 viral 信号**，赶在大 brand 抢稿前介入

**这个改写的根据**：
- 抖音 v3 全 145 候选风格分类，军lo primary 只有 3 个（都是 brand 不是 illustrator）
- 收藏夹 + 4 个 confirmed 画师全是杂画各种风格（哥特 / 汉 / cla / 甜lo），没军lo 专家
- 21 款 lolita-research 数据库中军lo 设计的"画师 → brand"工作流：叁狐画终焉圣骸不代表她专画军lo
- 圈内事实：高质量画师每月接 3-5 个稿子，可能 1 个是军lo，绝大部分是其他风格

## 🔭 监控管线 v1（Phase 2 实现）

```
┌──────────────────────────────────────────┐
│  画师池 (illustrators_master.jsonl)      │  ← Phase 1 已建
│  ~40-50 高置信 lolita 画师 sec_uid       │
└────────────┬─────────────────────────────┘
             │
             ▼
┌──────────────────────────────────────────┐
│  Snapshot 循环 (Hermes profile, 每 4h)   │
│  for each illustrator:                   │
│    1. fetch /aweme/post/?count=10        │
│       (拿最近 10 帖元数据 + 计数)         │
│    2. detect new aweme_id (vs 上次)      │
│    3. for each known aweme_id:           │
│       refresh statistics → 写时间序列   │
│    4. classify style of new posts:       │
│       军lo / 王子 / 甜 / 哥特 / ...      │
└────────────┬─────────────────────────────┘
             │
             ▼
┌──────────────────────────────────────────┐
│  Viral 早期信号检测                       │
│  for each tracked aweme:                 │
│    growth_rate = (digg_t - digg_{t-1})   │
│                  / hours_since_publish   │
│    baseline = author 历史新帖 24h 增速   │
│    if growth_rate > 3x baseline:         │
│      → 触发"早期 viral"告警              │
└────────────┬─────────────────────────────┘
             │
             ▼
┌──────────────────────────────────────────┐
│  推送 (TG + 日报)                         │
│  - 高优先级 → TG 立即推                  │
│  - 每日 markdown 报告                    │
└──────────────────────────────────────────┘
```

## 📊 数据结构

### 后台原始（time-series 全量）

`illustrators/<sec_uid>.json`:
```jsonc
{
  "sec_uid": "...",
  "nickname": "...",
  "uid": "...",
  "signature": "...",
  "role_tag": "illustrator",
  "sig_score": 35,
  "source_origins": ["favorites", "v2_search"],
  "snapshots": [
    {"ts": "2026-05-11T20:34:00+08:00",
     "follower_count": 14559,
     "post_count_total": 200,
     "favorite_count_total": ...}
  ],
  "posts": {
    "<aweme_id>": {
      "desc": "...",
      "create_time": 1750754348,
      "hashtags": ["军lo", "圣骸"],
      "style_tags_detected": ["军lo", "圣职"],
      "post_url": "https://www.douyin.com/video/<aweme_id>",
      "snapshots": [
        {"ts": "2026-05-11T20:34:00+08:00",
         "digg_count": 124000,
         "comment_count": 2408,
         "share_count": 18000,
         "play_count": 800000}
      ]
    }
  }
}
```

### 前台 HTML 展示

- **顶部全局**：「数据时点：YYYY-MM-DD HH:MM」(max snapshot ts)
- **画师卡片**：粉丝量 + 增量「↗ +200/7d」(若有历史)
- **作品卡片**：点赞 + 增量「↗ +3000/24h」
- **军lo 稿件聚合页**：所有 style_tags_detected 含「军lo」的 post 按 24h 增速排序

## 🚦 节奏与风控

| 项 | 安全值 | 原因 |
|---|---|---|
| 单次 snapshot 调用 | ≤50 画师 / 4h | 抖音 API 不主动限速，但批量行为指纹 |
| 间隔 | 单调用之间 5-10s | humanlike |
| 单画师 count | 10 帖 / 4h | 拿到最近一周新帖足够 |
| 错误重试 | 5 fail → 长 pause 60s | 累积避封 |

## 🎯 Viral 信号公式（待 Phase 2 调参）

```python
def viral_score(post, history):
    hours_since_publish = (now - post.create_time) / 3600
    if hours_since_publish < 1: 
        return 0  # 新帖噪音，等过 1h
    
    digg_rate = post.snapshots[-1].digg_count / hours_since_publish
    
    author_baseline = mean(
        p.snapshots[-1].digg_count / hours_since_publish
        for p in author.posts.values()
        if p.create_time > now - 30 * 86400  # 30 天内
    )
    
    multiplier = digg_rate / (author_baseline + 1)
    
    # 加权
    score = log(digg_rate + 1) * multiplier
    
    # 风格加成
    if "军lo" in post.style_tags_detected:
        score *= 1.5  # 我们重点关注军lo
    
    return score
```

阈值（待调）：
- score > 5 → 早期 viral，TG 推送
- score > 2 → 写入日报 watch list
- score < 1 → 忽略

## 💼 商业决策窗口（用户介入点）

1. **TG 收到告警** → 用户人工评估画师 + 稿件质量
2. **判断**：是否值得买稿？
3. **行动**：联系画师（DM / 进群 / 留言）→ 谈价 → 买断 → 自家做衣
4. **复盘**：viral 是否兑现（30 天后看流量峰值）→ 调权重

## 📅 实施阶段

### Phase 1（这次会话 → 完成基线）
- ✅ 画师池整合 (illustrators_master.jsonl)
- ✅ 基线 snapshot（每画师 t0 数据）
- ✅ HTML 画师调研页（含数据时点）
- ✅ HTML 军lo 稿件专题页

### Phase 2（下次 → 监控自动化）
- monitor.py：定时拉 snapshot
- Hermes profile：每 4h 触发
- Viral 公式上线
- TG 告警

### Phase 3（继续 → 数据沉淀）
- 30 天后 viral 信号回测
- 加入微博平台（21 款 illustrator 字段 anchor 在微博）
- Cross-platform 联动
