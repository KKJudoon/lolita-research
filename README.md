# Lolita 款式调研

记录国内 lolita 圈热门款（含军lo / 哥特 / 王子系 / 甜系等），每款含品牌、画师、店铺、上新时间、价格、销量、海报、综合分析。

> 本项目的 **prior 知识库（圈内术语/业态/工艺/品牌）**在兄弟目录：[`../lolita-domain-knowledge/`](../lolita-domain-knowledge/)。
> 调研某款前必先读那 5 个 .md（terminology / industry-norms / style-genres / quality-flags / brands-reference）。
> 调研中发现新术语 / 规则 / 避雷信号，**马上更新 wiki**，不要让知识停在单个款的 JSON 里。

## ⚠ 调研工具硬规则：统一走 browser-harness

**本项目所有抓取（淘宝 / 微博 / XHS / 千牛）一律走 m87 上的 `~/.local/bin/browser-harness`，不再用 opencli。**

- **原因**：opencli 已被站点指纹探测（XHS captcha / 淘宝风控对它的浏览器指纹有记忆），继续用会污染整个 m87 的会话信誉
- **入口**：`ssh kangchen@192.168.31.3 '~/.local/bin/browser-harness ...'`，CDP 直连真 Chrome，行为指纹接近真人
- **常用动作**：`new_tab` / `js`（执行任意 DOM 取值）/ `capture_screenshot` / `click_at_xy`
- **背景**：详见 memory `reference_browser_harness` + `feedback_tool_preference_opencli` + `feedback_taobao_humanlike`（淘宝/千牛要拟人节奏）
- **历史 JSON 里 `data/raw/` 还残留 opencli 抓的结果**，结构上能继续用，但**新调研一律新工具产出**，不要混

## 当前进度（截至 2026-04-30）

**21 款已建档**（每款 = 1 JSON + 1 detail 页 + images 子目录），分布：

- **军lo / 军lo×王子系**（12）：Alicegirl 破晓者 · 樱洛芙 终焉圣骸 2.0 · 猫咪晚安 卷卷 · YourHighness 骑士精神 · YourHighness 少女暴君黎明之战 · Vancy 搜查者 · 时代眼泪 帝国荆棘 · 映月 龙曜 · 月夜熊 皇权加冕 · 未知星辰 继承人 · 沉默火星 星巡夜骑士 · 白茶语鹿 暴君加冕
- **王子lo / 王子系**（8）：PC 人偶 · PC 红与黑 4.0 · 少女的永无岛 祷告者 · 少女的永无岛 誓约王座 · 是只猫 王子系白衬衫 · 第二城堡 糖果铺 · 设计师的礼物 小王子装 · 造梦境 少女暴君系列
- **哥特**（1）：樱洛芙 骨龙

**已产出报告**：`reports/junlo_prince_report.{md,html}` — 中国军lo王子系市场进入研究报告（44KB md / 67KB html，2026-04-30）。

## 数据完整度 audit（4 档，2026-05-02 全 21 款收尾后重测）

按 SKILL.md schema 全维度评估（price 双段 / shops 三平台 / hot_posts.xhs ≥3 / synthesis 正负面 ≥4 / `design_inspiration` 必填 / posters ≥4 / verified）。

| 档 | 款数 | 款 | 状态 |
|---|---|---|---|
| **A 完整** | 8 | Alicegirl 破晓者 · PC 红与黑 4.0 · Vancy 搜查者 · YourHighness 骑士精神 · 少女的永无岛 祷告者 · 未知星辰 继承人 · 樱洛芙 终焉圣骸 2.0 · 第二城堡 糖果铺 | 0 缺项；verified=True |
| **B 几近完整** | 6 | 映月 龙曜 · 樱洛芙 骨龙 · 猫咪晚安 卷卷 · PC 人偶 · YourHighness 黎明之战 · 永无岛 誓约王座 | 各缺 1 项（多数是 shops.weibo URL；骨龙缺 1 张海报；known fact 已 note） |
| **C 待补 shops** | 1 | 沉默火星 星巡夜骑士 | 缺 shops.xhs URL（hot_posts 用 KOL 园有桃 而非品牌官号 SilentMars） |
| **D minimal upgrade（verified=False）** | 6 | 时代眼泪 帝国荆棘 · 是只猫 白衬衫 · 月夜熊 皇权加冕（0 海报）· 白茶语鹿 暴君加冕 · 设计师的礼物 小王子装 · 造梦境 少女暴君 | schema 框架补齐 + ai_analyzed `design_inspiration` + 已知信号 hot_posts，但 XHS 自然流量低 / 调研深度浅；下阶段需独立 XHS 完整调研 + 微博/淘宝交叉验证 |

**核心质量信号**（本会话调研中新发现）：

- ✅ **少女的永无岛 / 设计师的礼物 = 厂原店**（圈内 2025-04-18 对比帖确认，已写入 synthesis 负面）
- ✅ **沉默火星 星巡夜骑士 = 工艺/版型差评**（2024-07 上身长文 + 评论 8+ 条交叉验证）
- ✅ **YH 黎明之战 viral 借势**（XHS 26.2万 likes 法语音乐剧 cover 帖驱动『少女暴君』标签破圈）
- ✅ **永无岛 誓约王座 = 希腊神女 IP**（赫拉王冠官号 547 likes 帖明确）
- ✅ **PC 人偶 = 双子星公主（小法）IP 联想**（路人 443 likes 帖 hashtag）

⚠ **D 档 `verified=False`**：标识 minimal upgrade（schema 完整但内容深度浅，依赖 ai_analyzed 推断），下阶段需独立调研验证。

## 未决 / 待办

按性价比排序：

1. **D 档 6 款独立调研深化**（每款 30 min）：跑独立 XHS 搜索（叠 lolita / 王子装 / 军lo 关键词避免被同名词覆盖）+ 微博 s.weibo.com/weibo 搜款名 + 淘宝详情页正文价格抓取 → 升 verified=True
2. **月夜熊 海报 0→4**（独立任务）：去微博 / 淘宝 SKU 抓 ≥4 张高清
3. **沉默火星 shops.xiaohongshu URL**：跑 XHS type=user 搜『SilentMars』/『沉默火星』找品牌官号 profile
4. **B 档 5 款 shops.weibo 验证**：对每个原创小品牌跑微博 s.weibo.com/user?q= 验证『确实没微博官号』vs『漏抓』
5. `index-Magellan.html` 已 `.gitignore`，未决定是否替换 `index.html`

## 目录

- `data/<品牌_款名>.json` — 每款一个 JSON 文件，结构化字段
- `data/raw/` — 原始抓取结果（含早期 opencli 残留，仅追溯用，不直接渲染）
- `images/<品牌_款名>/` — 海报、模特图（本地下载）
- `index.html` — 综合卡片墙（响应式，按 style_tags 分组筛选）
- `items/<id>.html` — 每款独立 detail 页
- `reports/` — 跨款综合研究报告（md + html）
- `build.py` — 读 `data/*.json` 生成 `index.html` + `items/*.html`
- `apply_popularity.py` — 把淘宝销量/缩略图回填到 JSON `posters[]`
- `deploy.sh` — `git add . && git commit "Update site: <ts>" && git push` 到 GitHub Pages。**必须在 m87 GUI Terminal 里跑**（ssh 调用 keychain 读不到 push 凭证）。手动部署是当前唯一稳定方式（watcher 实验过被弃用，原因见下文 README 历史）

## 工作流（每加一款）

1. 在 m87 用 **browser-harness** 跨平台搜款名（淘宝 sale 排序 + xhs/weibo 关键词）—— opencli **禁用**
2. 进 `taobao detail` / `weibo post` / `xiaohongshu note` 拿正文/海报/评论
3. **价格优先 XHS 找**（淘宝意向金价 ≠ 全款价；详见 wiki/SKILL.md）
4. 交叉验证图片确认风格匹配；找出同名款警告（圈内菀菀类卿现象）
5. 海报下载到 `images/<品牌_款名>/`
6. 写 `data/<品牌_款名>.json`（schema 见下）
7. 跑 `python3 build.py` 重新渲染
8. `git commit -m "<语义 message>"`
9. **m87 GUI Terminal 跑 `./deploy.sh`** 推到 GitHub Pages

## 部署说明（手动）

部署一律在 **m87 GUI Terminal** 里跑 `./deploy.sh`——手动稳定，不依赖任何后台进程。

`deploy.sh` 行为：
1. 如果 worktree 有未提交改动（modified/untracked，遵守 `.gitignore`）→ `git add . && git commit "Update site: <ts>"` 兜底 commit
2. 如果有未推送 commit → `git push`
3. 否则报 `No changes to deploy.`

⚠ **必须在 m87 GUI Terminal 跑**：ssh 启动的进程没 GUI keychain 上下文，push 会报 `fatal: could not read Username for 'https://github.com'`（2026-05-02 实测）。`~/.local/bin/lolita-autodeploy` 后台 watcher 之前实验过自动化，因 keychain 问题废弃，已弃用。

⚠ **每次原子改动 Claude 自己先写语义 commit**，留给 deploy.sh 的应该是干净 worktree（只剩未推送 commit 待 push），别让它兜底 commit 成 `Update site: <ts>` 丢语义。

## 网页版本对照（footer）

每个 HTML 页面（index + 21 个 detail）右下角固定一个版本标签：

```
v <短 hash> · commit <YYYY-MM-DD> · build <YYYY-MM-DD HH:MM>
```

- **v 短 hash**：html 被 build 时的 git HEAD（短 hash），点击跳 GitHub commit URL 看 diff
- **commit 日期**：那次 commit 的日期
- **build 时间**：`python3 build.py` 跑的时刻（每次 build 必更新）

⚠ **footer 的 hash ≠ 当前 HEAD**——git 本性，commit 之前不可能知道自己的 hash。每次循环 commit + build 时 footer hash 会落后 HEAD 1 个 commit。**对照同步状态时优先看 build 时间**——它代表"网页是几点 build 出来的"。

**新对话开始流程**：
1. 浏览器开 https://kkjudoon.github.io/lolita-research/ 看右下角 footer
2. m87 上 `git log --oneline -5` 看最近 commit
3. 对照：footer hash 应该 ≈ origin/main 上某个最近 commit；build 时间应该 ≈ 那次 commit 后的时间
4. 不匹配 → 说明本地有未 deploy 的改动，或 Pages 还没部署完最近 push（GitHub Pages 部署延迟通常 30s–2min）

## JSON schema

详见 lolita-fashion-research skill SKILL.md（在 `~/.openclaw/workspace/skills/lolita-fashion-research/`）；本目录每条 JSON 都遵循它。

## 新对话接手指引

进入新对话要继续这个项目时：

1. 项目根：`m87:~/OneDrive/Workbench/2 Area/lolita-research/`（**走 `~/OneDrive` 软链接，不是 `OneDrive-Personal`**）
2. 先读本 README → `git log --oneline | head -20` 看最近动作 → `git status` 看脏文件
3. **抓数据一律走 `~/.local/bin/browser-harness`，禁用 opencli**（见上方硬规则段）
4. 方法论 single source：`~/.openclaw/workspace/skills/lolita-fashion-research/SKILL.md`
