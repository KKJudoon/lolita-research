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

## 数据完整度 audit（4 档）

字段维度：海报数 / price.op·full_set·list / shops 三平台 / hot_posts.xiaohongshu ≥3 / synthesis 正负面各 ≥4 / design_inspiration.elements + prompt / illustrator·designer。

| 档 | 款数 | 款 | 缺什么 |
|---|---|---|---|
| **A 完整** | 3 | Alicegirl 破晓者 · 未知星辰 继承人 · 第二城堡 糖果铺 | — |
| **B 小修（只缺 price 字段）** | 8 | PC 红与黑 4.0 · Vancy 搜查者 · 少女的永无岛 祷告者 · 樱洛芙 终焉圣骸 2.0 · 猫咪晚安 卷卷 · YourHighness 骑士精神 · 映月 龙曜 · 樱洛芙 骨龙 | `price.op` / `price.full_set` / `price.list_price_at_research`（骨龙额外缺 1 张海报到 4 张） |
| **C 中缺（结构 OK，内容浅）** | 4 | PC 人偶 · YourHighness 黎明之战 · 少女的永无岛 誓约王座 · 沉默火星 星巡夜骑士 | XHS 帖 0/5 · 正面亮点 1/4 · 负面亮点 1/4 · `design_inspiration.elements` · `price` |
| **D 占位级（minimal entry）** | 6 | 时代眼泪 帝国荆棘 · 是只猫 白衬衫 · 白茶语鹿 暴君加冕 · 设计师的礼物 小王子装 · 造梦境 少女暴君 · **月夜熊 皇权加冕（0 海报）** | 全字段都缺；当前只有淘宝缩略图 1 张（月夜熊 0 张） |

⚠ **D 档 6 款是 4-30 一次性补的 top-畅销度 minimal 条目**（commit `8104bf5`），不是真实调研结果，下一阶段必须升级。

## 未决 / 待办

- D 档 6 款全维度补全（每款一轮 browser-harness 抓取）
- C 档 4 款补 XHS 帖 + 正负面亮点 + 灵感 elements
- B 档 8 款补 price 字段（XHS 长贴里抠全款价）
- 月夜熊 海报从 0 张补到 ≥4 张
- `index-Magellan.html` 是 4-30 14:35 实验的另一套首页模板，untracked，未决定是否替换 `index.html` ⚠ 启动 watcher 前要么 `.gitignore` 它，要么删/改名（见下方"自动部署 watcher"）

## 目录

- `data/<品牌_款名>.json` — 每款一个 JSON 文件，结构化字段
- `data/raw/` — 原始抓取结果（含早期 opencli 残留，仅追溯用，不直接渲染）
- `images/<品牌_款名>/` — 海报、模特图（本地下载）
- `index.html` — 综合卡片墙（响应式，按 style_tags 分组筛选）
- `items/<id>.html` — 每款独立 detail 页
- `reports/` — 跨款综合研究报告（md + html）
- `build.py` — 读 `data/*.json` 生成 `index.html` + `items/*.html`
- `apply_popularity.py` — 把淘宝销量/缩略图回填到 JSON `posters[]`
- `deploy.sh` — `git add . && git commit "Update site: <ts>" && git push` 到 GitHub Pages（须 m87 GUI session 跑，ssh 调用 keychain 读不到 push 凭证）— 一般不直接调，靠下方 watcher 触发

## 工作流（每加一款）

1. 在 m87 用 **browser-harness** 跨平台搜款名（淘宝 sale 排序 + xhs/weibo 关键词）—— opencli **禁用**
2. 进 `taobao detail` / `weibo post` / `xiaohongshu note` 拿正文/海报/评论
3. **价格优先 XHS 找**（淘宝意向金价 ≠ 全款价；详见 wiki/SKILL.md）
4. 交叉验证图片确认风格匹配；找出同名款警告（圈内菀菀类卿现象）
5. 海报下载到 `images/<品牌_款名>/`
6. 写 `data/<品牌_款名>.json`（schema 见下）
7. 跑 `python3 build.py` 重新渲染
8. `git commit`（如果 watcher 已跑就只 commit；watcher 没跑就 commit 后跑 `lolita-autodeploy run` 一次或者直接 `./deploy.sh`）

## 自动部署 watcher

m87 上 `~/.local/bin/lolita-autodeploy` 是 git watcher，每 30s 轮询本仓库，发现以下任一情况就触发 `deploy.sh`：

- worktree 有未提交改动（modified / untracked）
- index 有 staged 未 commit
- 本地有未推送 commit

触发流程：检测到改动 → 等 5s 防抖 → 跑 `deploy.sh`（自动 `git add . && git commit "Update site: <ts>" && git push`）。锁文件防并发。

| 命令 | 用途 |
|---|---|
| `lolita-autodeploy start` | 后台启动 watcher（写 pid + log） |
| `lolita-autodeploy stop` | 停 |
| `lolita-autodeploy status` | 查状态 |
| `lolita-autodeploy run` | 一次性检查 + deploy（不开 watcher） |
| `lolita-autodeploy watch` | 前台跑 watcher loop |

环境变量：`LOLITA_DEPLOY_INTERVAL`（默认 30s）/ `LOLITA_DEPLOY_DEBOUNCE`（默认 5s）。
状态目录：`~/.local/state/lolita-research/`（pid / log / 锁）。

⚠ **使用注意**：

- watcher 跑 `git add .`（含 untracked，遵守 `.gitignore`）—— **任何 untracked 文件都会被自动 commit**，实验性/草稿文件要放 `.gitignore` 或挪出 repo
- 每个原子改动建议先**自己 commit 一次**（写好 message），watcher 只负责把它 push；不要全靠 watcher 的 "Update site: <ts>" 兜底，会丢语义
- m87 重启后 watcher 不会自启（无 launchd 包装），需要手动 `start`
- ssh 远程触发 deploy 会卡 keychain push 凭证，所以 watcher 必须跑在 m87 GUI session 下

## JSON schema

详见 lolita-fashion-research skill SKILL.md（在 `~/.openclaw/workspace/skills/lolita-fashion-research/`）；本目录每条 JSON 都遵循它。

## 新对话接手指引

进入新对话要继续这个项目时：

1. 项目根：`m87:~/OneDrive/Workbench/2 Area/lolita-research/`（**走 `~/OneDrive` 软链接，不是 `OneDrive-Personal`**）
2. 先读本 README → `git log --oneline | head -20` 看最近动作 → `git status` 看脏文件
3. **抓数据一律走 `~/.local/bin/browser-harness`，禁用 opencli**（见上方硬规则段）
4. 方法论 single source：`~/.openclaw/workspace/skills/lolita-fashion-research/SKILL.md`
