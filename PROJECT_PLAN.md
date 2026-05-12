# lolita-research 项目规划

最后更新：2026-05-12

## 🎯 项目愿景

lolita-research 是中国 lolita 行业**主要玩家全景调研**项目，目标是把这个圈子的关键角色（**画师 / 品牌 / 款式 / 模特 / 工厂**）的数据**沉淀+互通**，支撑商业决策（最直接：早期识别 viral 画稿，提前买稿做衣）。

## 🧩 模块划分

| 模块 | 状态 | 内容 | 入口 |
|---|---|---|---|
| **款式调研** | ✅ 21 款 v1 | 每款的设计/价格/海报/shops/syntheis | `styles/index.html`（即原 `index.html`） |
| **画师调研** | ✅ 41 画师 v1 基线 | profile / signature / 黑话评分 / 近 20 帖 + 计数 / 时间序列 | `illustrators/index.html` |
| **军lo 稿件专题** | ✅ 38 帖 v1 基线 | 军lo style 帖跨画师聚合 | `illustrators/military_research/index.html` |
| **品牌调研** | 🚧 占位 | 抖音 17 个 brand（已识别）+ 21款 brand 字段 cross | 暂未 |
| **模特调研** | 🚧 占位 | KOL / lo娘 / 试穿博主 | 暂未 |
| **工厂调研** | 🚧 占位 | 打版/印花/缝制工厂（圈内 QQ 群信息） | 暂未 |

**当前重点（本周）**：**画师 + 军lo 扩充** —— 池子加大、风格识别更精、时序监控上线。

## 🔄 数据互通愿景（远期）

```
画师 → 卖稿 → 品牌 → 设计成款式 → 穿在 模特 身上 → 工厂 生产
  ↑                                                          ↓
  └────── 模特 viral 把款式带火 ←─── 模特 穿着照片 ←─────────────┘
```

每条核心 link 都有 sec_uid / 链接 / 数据互引：
- 每个**款式**记录 `illustrator` / `brand` 字段，可点击进画师/品牌 detail
- 每个**画师** detail 显示其稿件流向了哪些 **款式**（cross-link）
- 每个**品牌** detail 显示他们买稿来自哪些 **画师**（出现频次）
- 每个**模特**记录他/她穿过/带火过哪些 **款式**

## 🌐 跨平台

| 平台 | 状态 | 用途 |
|---|---|---|
| 抖音 | ✅ 第一战场 | 实时 viral 信号、画师社交图谱、新帖检测 |
| 微博 | 🚧 待开 | 画师圈核心活跃地（抖音是营销渠道，微博是创作生态） |
| 小红书 | 🚧 部分已用 | 用户穿搭、避雷帖、价格信号 |
| 淘宝 | ✅ 21款用过 | 价格、销量、SKU |
| QQ 群 | 🚧 远期 | 工厂、画师米米计价沟通现场 |

## 🛠 工作流程（agent + 用户协作）

### Agent（我）做什么
- 跑抖音 API：抓画师/帖子/计数（每 4h 自动）
- 用 黑话词典识别画师 vs brand vs wearer vs tutorial
- 渲染网页（每次数据更新后跑 build/render 脚本）
- 写沉淀文档（capability_map / role_taxonomy / jargon / strategy）
- 检测 viral 信号 → push 用户

### 用户做什么
- 在抖音正常使用（关注/收藏画师 → 是 ground truth）
- 看日报，决定哪些画师 / 哪条稿件值得介入
- 联系画师谈稿 / 买断
- 偶尔反馈 agent 错判（已多次纠正：樱洛芙=brand 不是 illustrator / "无军lo 专家画师" 战略修正）

## 📐 网站结构

```
lolita-research/                          (项目根，部署到 GH Pages)
├── index.html                            ⭐ 模块门户（5 卡片）
├── styles/                               (款式调研，原 index.html 内容)
├── illustrators/                         画师调研
│   ├── index.html                        画师总览（排序+过滤）
│   ├── <sec_uid>.html × 41               单画师详情
│   └── military_research/index.html      军lo 稿件专题
├── brands/                               🚧 placeholder
├── models/                               🚧 placeholder
├── reports/                              横向报告
│   └── junlo_prince_report.html          (2026 Q2 报告)
└── douyin-monitor/                       后台元数据（jsonl + 文档，不渲染）
    ├── capability_map.md
    ├── role_taxonomy.md
    ├── jargon_dictionary.md
    ├── monitor_strategy.md
    ├── illustrators_master.jsonl
    ├── illustrators_snapshots/*.json
    └── ... (一些中间 jsonl)
```

## 📅 路线图

### Phase 1（已完成 2026-05-12）
- ✅ 抖音能力栈、API、DOM 摸清
- ✅ 5 角色分类 + 画师黑话词典 + viral 战略文档
- ✅ 54 画师候选池 + 41 基线 snapshot
- ✅ 画师调研网页 + 军lo 专题 + 时间戳

### Phase 2（下周开始）
- monitor.py：定时刷 snapshot
- 接 Hermes profile（每 4h 触发）
- 网页加 24h 增速差量显示
- viral 公式 + TG 告警
- 画师页加排序/过滤（**马上加**）

### Phase 3（一个月后）
- 30 天 viral 数据回测，调权重
- 加微博平台（画师圈主战场）
- 款式 ↔ 画师 cross-link
- 评论扫购买意图

### Phase 4（远期）
- 品牌 / 模特 / 工厂 模块
- 跨平台 data互通

## 🚨 关键约束 / 教训

- **画师 ≠ 设计师 ≠ 品牌方** — role 判断先于 style，曾误标樱洛芙=illustrator 被纠正
- **不假设有"军lo 专家"** — 画师都杂画，军lo 是偶发 viral，不要找"专家"找"事件"
- **登录态过期会失效搜索** — 抖音对搜索风控严，登录态健康检测要纳入循环
- **UI cache bug 不信按钮文字** — 写操作（关注/点赞）成功后，UI 可能短暂 stale，要 server API 验证
- **画师 following list 有隐私** — 用 @mention + hashtag 替代社交图谱挖掘
- **OneDrive 写操作走 m87** — 本机不留副本，详见 memory feedback_onedrive_via_m87
- **页面 deploy 必须 m87 GUI 跑 deploy.sh** — ssh 没 keychain，git push fail

## 📂 当前文件清单（Phase 1 落档）

**前台（GH Pages 渲染）**：
- `index.html` ← 即将改为模块门户
- `styles/` ← 即将从 index.html 内容迁出
- `illustrators/` ← 41 画师 + 总览 + 军lo 专题

**后台（douyin-monitor/，不渲染）**：
- 4 份 .md 文档（capability/role/jargon/strategy）
- 5 份 .jsonl（master/v2 search/v3 creators/favorites/following）
- 41 份 snapshot json（illustrators_snapshots/）
- 候选 raw 文件（raw/、illustrator_raw/）

## 🤝 用户偏好（学习中）

- 慢速、安全优先（验证→批量）
- 不接受低级错误（樱洛芙误标后强调"做好文档规划分类"）
- 期望沉淀+可复用（"沉淀一下"、"做一个规划文件"）
- 战略迭代敏捷（"我觉得不一定有专门画军lo 的画师"修正了整个战略）

---

⚠ **此文档随项目演进持续更新**。新洞察、新模块、新教训请直接加在对应区块。
