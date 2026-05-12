# Douyin Lolita 创作者角色分类（必须遵守）

继承 lolita-research 21 款 schema 已有的核心分工：**画师 ≠ 设计师 ≠ 品牌方**。
扩展为 5 角色：

| 角色 | 定义 | 抖音上典型行为 |
|---|---|---|
| **brand**（品牌方） | 拥有 IP，卖成品裙子，从画师那里买稿或在内部设计 | 发上新海报、预约金、团长、拍意向金、版型规格 |
| **illustrator**（画师 / 图案设计师） | 画柄图 / 花型 / 设计稿 → 卖给品牌或团长 | 发设计稿手绘过程、约稿、接稿、画稿征集、晒柄图 |
| **wearer**（lo娘 / 穿搭博主） | 买成品穿、晒搭配、写测评 | 真人穿搭照、试色、试穿、上身比例 |
| **tutorial**（绘画/化妆教学） | 教别人画画、化妆、做手作 | 笔刷分享、零基础学画画、绘画过程、教程 |
| **other**（其他/不相关） | 上述都不是 | 段子、生活、动漫教程、绘画通用号 |

---

## 检测信号（按 priority 顺序）

### 1. brand 信号（最容易识别）
- `verified_org` 包含「服饰公司」「服装有限公司」「服装文化」「设计工作室」 ← 抖音企业号认证最强信号
- `custom_verify` = "店铺账号" 或 "原创设计"
- `nickname` 包含「原创设计」「原创工作室」「Lolita原创」「lolita原创」
- 帖子 desc 出现频次 ≥ 3：「上新」「意向金」「团长」「上新海报」「拍下意向金」「预定」「打版」

### 2. illustrator 信号
- `nickname` 包含「画师」「插画师」「图案设计师」「画稿」
- `signature` 提到「约稿」「接稿」「长期接稿」「柄图」
- 帖子 desc 出现频次 ≥ 3：「画稿」「柄图」「手绘过程」「线稿」「分层」「设计稿」「约稿」「接稿」
- **关键区分**：illustrator 是**卖图**的，brand 是**卖成品**的
- 注意：**图案设计师** 是通用图案，可能跨多个行业（lolita / 汉服 / 中式女装），不只 lolita

### 3. wearer 信号
- 帖子封面以**真人穿搭照**为主（图文混排或实拍）
- desc 多是「试穿」「我的穿搭」「上身」「实物」「身高 165...」
- 没有 brand 或 illustrator 的商业词汇

### 4. tutorial 信号（必须强排除）
- nickname 含「插画师」「教学」「画画」但帖子是教程
- 帖子高频出现：「零基础」「画世界」「procreate」「板绘」「笔刷」「人体结构」「线稿教程」
- **典型陷阱**：「插画师Ann/Chris/麦子.手绘」这类——粉丝高、词命中，但全是绘画教学
- **诊断方法**：lolita 浓度 ≤ 25% 且高频出现绘画教学词 → tutorial，丢

### 5. other 信号（最后兜底）
- 不符合上述任一 → other（动漫教程 / 段子 / 通用绘画）

---

## 多角色处理（一个号同时多个标签）

- 抖音上有 brand 自己请画师 → 号上 brand 标签 + 偶尔 illustrator 风格
- 小工作室（独立设计师）→ brand + illustrator + designer 一身
- 算法上：分别独立打 brand_score / illustrator_score / wearer_score，可同时 > 阈值

## 角色 + 风格 组合输出

最终每个创作者应输出：
```jsonc
{
  "sec_uid": "...",
  "nickname": "...",
  "role_scores": {"brand": 12, "illustrator": 3, "wearer": 0, "tutorial": 0, "other": 0},
  "primary_role": "brand",
  "lolita_ratio": 1.0,
  "style_counts": {"军lo": 5, ...},
  "primary_style": "军lo",
  "biz_count": 2,
  "is_high_value_target": true  // = role in (brand, illustrator) AND lolita_ratio ≥ 0.5
}
```

---

## 历史失误案例（写给未来的我）

- **2026-05-11 误判**：把 **樱洛芙Lolita原创设计** 标成 illustrator（出现在 illustrator_pool.jsonl + military_illustrators.md）。**正确角色：brand**（27.6万粉 + 认证「湖北芙樱盈服饰有限公司」+ 帖子全是成品上新 + 意向金 + 团长）。已收录在 21 款 lolita-research 数据库为 brand 类。
- **2026-05-11 误判**：把 **插画师Ann / 插画师Chris / 麦子.手绘** 标成 lolita 画师。**正确角色：tutorial**（绘画教学博主，与 lolita 无关）。
- **教训**：role 判断必须 **先于** style 判断。先 role 过滤掉 tutorial/other，再做 lolita 风格分类。
