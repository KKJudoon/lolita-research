# Lolita 款式调研

记录国内 lolita 圈热门款（含军lo / 哥特 / 王子系 / 甜系等），每款含品牌、画师、店铺、上新时间、价格、销量、海报、综合分析。

> 本项目的 **prior 知识库（圈内术语/业态/工艺/品牌）**在兄弟目录：[`../lolita-domain-knowledge/`](../lolita-domain-knowledge/)。
> 调研某款前必先读那 5 个 .md（terminology / industry-norms / style-genres / quality-flags / brands-reference）。
> 调研中发现新术语 / 规则 / 避雷信号，**马上更新 wiki**，不要让知识停在单个款的 JSON 里。

## 目录

- `data/<品牌_款名>.json` — 每款一个 JSON 文件，结构化字段
- `data/raw/` — 原始 opencli 抓取结果（追溯用，不直接渲染）
- `images/<品牌_款名>/` — 海报、模特图（本地下载）
- `index.html` — 综合卡片墙（响应式，按 style_tags 分组筛选）
- `items/<id>.html` — 每款独立 detail 页
- `build.py` — 读 `data/*.json` 生成 `index.html` + `items/*.html`
- `deploy.sh` — git add+commit+push 到 GitHub Pages（须 m87 GUI session 跑，ssh 调用 keychain 读不到）

## 工作流（每加一款）

1. 用 opencli 在 m87 跨平台搜款名（淘宝 sale 排序 + xhs/weibo 关键词）
2. 进 `taobao detail` / `weibo post` / `xiaohongshu note` 拿正文/海报/评论
3. **价格优先 XHS 找**（淘宝意向金价 ≠ 全款价；详见 wiki/SKILL.md）
4. 交叉验证图片确认风格匹配；找出同名款警告（圈内菀菀类卿现象）
5. 海报下载到 `images/<品牌_款名>/`
6. 写 `data/<品牌_款名>.json`（schema 见下）
7. 跑 `python3 build.py` 重新渲染
8. m87 GUI 终端跑 `./deploy.sh` 上 GitHub Pages

## JSON schema

详见 lolita-fashion-research skill SKILL.md（在 `~/.openclaw/workspace/skills/lolita-fashion-research/`）；本目录每条 JSON 都遵循它。

## 已收录款

按 `style_tags` 区分：
- **军lo**：樱洛芙 终焉圣骸 2.0 / 猫咪晚安 卷卷 / YourHighness 骑士精神
- **哥特**：樱洛芙 骨龙
