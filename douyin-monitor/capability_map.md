# Douyin Web 能力图谱

_系统性梳理：每条能力 = 选择器/API + 验证方法 + 已知坑_

最后更新：2026-05-11

---

## 0. 共性规则（绝对要记）

### 0.1 click 必须 JS 点，不能 CDP `click_at_xy`
React 应用绑定 onClick 走 SyntheticEvent，CDP 的 mouseDown/mouseUp 不触发。
**做法**：JS 中 `element.click()` 直接调。

### 0.2 UI cache bug：写操作后按钮文字暂时回滚
关注/取关后服务端确实改了，但 profile 页 React 状态可能 stale，按钮 1-2s 内仍显示原文字，刷新一次同步。**不要信 UI，要验 server 响应或者关注列表**。

### 0.3 daemon 容易累积 state，长跑要主动 reload
连续 30+ CDP 调用后偶尔 `_send recv timeout`。Workaround：每个 batch 跑完 `browser-harness --reload`。

### 0.4 自动 modal 切换
post 详情页（URL 含 `?modal_id=`）会自动播放下一条，modal_id 不停变。要稳态读数据时，**读完立即记**，别等。

### 0.5 抖音号必须登录态做搜索 / profile / 关注列表
匿名状态搜索 2-3 次后弹登录墙，会把账号 cookie 弱化。**登录态健康检测要纳入循环**。

---

## 1. ✅ 搜索（用户 tab）

**URL 形式**：
```
https://www.douyin.com/search/<keyword>?type=user&source=normal_search
```

**关键选择器**：`a[href*="/user/MS"]` → sec_uid 在 URL 的 `/user/(MS...)` 段

**解析卡片**（innerText 拼接）：
```
<nickname>\n\n[认证徽章\n<org>\n][已关注\n]抖音号: <id>[<likes>获赞][<fans>粉]
```

**已验证**：10 个关键词，100% 拿到，每词 10 候选

---

## 2. ✅ 进入 Profile

**URL**：`https://www.douyin.com/user/<sec_uid>`

**关键选择器**：
- 关注按钮：`button` 中 `innerText === '关注' | '已关注' | '互相关注'` 且 `y < 200`
- 签名：`[data-e2e="user-info-desc"]`
- 昵称：`[data-e2e="user-info-nickname"]`
- 总赞：`[data-e2e="user-info-like"]` 含「获赞 X」
- 关注/粉丝数：拼在 `div` 文本里如 `"关注\n14\n粉丝\n1\n获赞\n0"`

---

## 3. ✅ 进入 Post Modal（从 profile 点 grid）

**触发**：在 profile 上 JS click `a[href*="/video/"]` 的 anchor。

**结果**：URL 加上 `?modal_id=<aweme_id>`，渲染全屏 modal。modal 自动播放且会自动切下一条。

**aweme_id 来源**：anchor 的 href 的 `/video/(\d+)` 段。

⚠ 直接访问 `https://www.douyin.com/video/<aweme_id>` 经常返回"视频不存在"——可能这条 ID 只在 modal_id 路由有效，不开放独立页面。

---

## 4. ✅ 关注

**操作**：profile 页找到 `button` 文字为「关注」+ `y < 200`，JS `el.click()`。

**Server API**：
```
POST /aweme/v1/web/commit/follow/user/?device_platform=webapp&aid=6383...
→ {"follow_status":1, "status_code":0, ...}
```

**验证持久化**：去自己 profile（`/user/self`）→ JS click 关注数字 → 拉列表 → sec_uid 比对。

**节奏限制（未实测，估算）**：根据 reference_taobao_humanlike 类比，建议 ≤30 次/天分散。

---

## 5. ✅ 点赞（feed 模式）

**位置**：推荐 feed 中，centered 视频右侧 sidebar。

**选择器**：`[data-e2e="video-player-digg"]`

**操作**：JS `el.click()`。

**验证**：心变红 + 旁边出现「取消点赞 X」浮窗 + 计数 +1。

---

## 6. ✅ 关注列表（自己）

**URL**：`https://www.douyin.com/user/self`

**操作**：JS click 「关注 N」 元素（DIV/SPAN/A 都行，匹配 `^关注\s+\d` 正则）。

**返回**：modal 列表，遍历 `a[href*="/user/MS"]` 拿 sec_uid。

**注意**：列表只渲染前 N 个，滚动加载剩余。

---

## 7. ✅ Post Modal Sidebar 选择器（modal vs feed 同选择器）

**Modal 容器**：`[data-e2e="modal-video-container"]` / `[data-e2e="feed-active-video"]` （全屏 1200×845）

**Sidebar 操作按钮（与 feed 模式完全相同）**：

| 操作 | 选择器 | 典型 y |
|---|---|---|
| 点赞 | `[data-e2e="video-player-digg"]` | ~380 |
| 评论 | `[data-e2e="feed-comment-icon"]` | ~448 |
| 收藏 | `[data-e2e="video-player-collect"]` | ~522 |
| 转发 | `[data-e2e="video-player-share"]` | ~596 |
| 更多 | `[data-e2e="video-play-more"]` | ~745 |
| 上一条 | `[data-e2e="video-switch-prev-arrow"]` | ~150 |
| 下一条 | `[data-e2e="video-switch-next-arrow"]` | ~189 |

**Post metadata（modal 上半部）**：
- `[data-e2e="feed-video-nickname"]` — 作者名
- `[data-e2e="video-desc"]` — 描述全文（含 hashtags）
- `[data-e2e="video-info"]` — 作者 + 发布时间 + desc

**Probe 必须遵守**：
1. JS click 进 modal 后立刻 probe（≤2s），否则 modal 自动播放下一条 selectors 飘
2. 必须过滤 `y in 0..845` 排除 profile 下方 grid 的 hover-state digg
3. 写操作（点赞/收藏）→ `el.click()`，不信 UI 翻转

---

## 8. ✅ 签名 API 直调（关键能力）

**核心发现**：在 douyin.com 页面 context 内 `fetch()` **自动带 cookie + 签名**，根本不用 MediaCrawler 那套外部签名捕获。

**拉指定 sec_uid 的全部帖子**：
```js
fetch('/aweme/v1/web/aweme/post/?sec_user_id=<SEC_UID>&max_cursor=0&count=20&device_platform=webapp&aid=6383&channel=channel_pc_web', {credentials: 'include'}).then(r => r.json())
```

**返回结构**：
```json
{
  "status_code": 0,
  "min_cursor": 0,
  "max_cursor": 1776421904000,   // ← 下一页传这个
  "has_more": 1,
  "aweme_list": [
    {
      "aweme_id": "7519432642443365667",
      "desc": "...",
      "create_time": 1750754348,
      "author": {"uid": "...", "nickname": "...", "follow_status": 0, ...},
      "statistics": {"digg_count": ..., "comment_count": ..., "share_count": ..., "play_count": ...},
      ...
    },
    ...
  ]
}
```

**单次最大 count**：实测 20。要拿全部 → 循环 `max_cursor = response.max_cursor`，`has_more === 1` 时继续。

**调用约束**：必须在 douyin.com 页面里执行（cookie + signature 域绑定）。从外部 curl 不行。`browser-harness -c` 跑 `js('return fetch(...)')` 就够了。

---

## 9. ✅ Profile 帖子分页（已被 §8 覆盖）

DOM 路线（滚动触发 IntersectionObserver）会被预渲染上限 ~65 帖卡死，**用 §8 的 API 路线**。

---

## 10. ✅ 评论分页

**API**：
```
GET /aweme/v1/web/comment/list/?aweme_id=<X>&cursor=0&count=20
```

**返回**：
```json
{
  "status_code": 0,
  "cursor": 20,
  "has_more": 1,
  "total": 2408,        // 总评论数
  "comments": [
    {
      "cid": "7635660067731587859",
      "text": "...",
      "digg_count": 0,
      "user": {"nickname": "..."},
      "create_time": 1777815649,
      "reply_comment_total": 0
    }, ...
  ]
}
```

实测请求 count=20 返回 16 条（可能 server 过滤）。pagination 用 `cursor`。

---

## 11. ✅ 关键词搜索视频（直接拿帖子列表，不用先找博主）

**API**：
```
GET /aweme/v1/web/search/item/?search_channel=aweme_general&keyword=<kw>&offset=0&count=20
```

**返回**：每条结果是 `{type, aweme_info: {aweme_id, desc, create_time, author: {sec_uid, nickname, follower_count, custom_verify}, statistics, ...}}`。

实测「lolita 画稿」第一条 = **`VoiceDie`（25,815 粉），简介"这些爆火的Lolita柄图都是我画的"** —— **真画师！** user-search 没出来。

⇒ **关键策略**：找画师走 **video search**，不要走 user search。

---

## 12. ✅ 关注 / 取消关注 API

**同一 endpoint，type 参数控制**：
```
POST /aweme/v1/web/commit/follow/user/?user_id=<UID>&sec_user_id=<SEC_UID>&type=<0|1>
  type=1 → follow，type=0 → unfollow
```

**响应**：`{"status_code":0, "follow_status":1 (or 0)}`

**UID 来源**：post API 返回里的 `author.uid`（纯数字）。

⚠ 不要 spam，每天 ≤30-50 次以内安全。

---

## 13. 完整 API 一览（已验证）

| 操作 | Endpoint | 关键参数 | 返回 key |
|---|---|---|---|
| 拉用户帖子（分页） | `/aweme/v1/web/aweme/post/` | `sec_user_id`, `max_cursor`, `count` | `aweme_list`, `max_cursor`, `has_more` |
| 拉评论（分页） | `/aweme/v1/web/comment/list/` | `aweme_id`, `cursor`, `count` | `comments`, `cursor`, `has_more`, `total` |
| 搜视频/帖子 | `/aweme/v1/web/search/item/` | `keyword`, `offset`, `count` | `data[]` (含 `aweme_info`) |
| 关注/取关 | `/aweme/v1/web/commit/follow/user/` (POST) | `user_id`, `sec_user_id`, `type` | `follow_status` |
| 用户主页 | `/aweme/v1/web/user/profile/other/` | `sec_user_id` | user object |

**统一前缀参数**（所有 endpoint 都要带）：`device_platform=webapp&aid=6383&channel=channel_pc_web`

**调用方式**：从已登录 douyin.com 页面内 `fetch(url, {credentials:'include'})`。cookie + 签名自动带，**不需要外部签名捕获**。

---

## 14. 综合策略建议（基于上面能力）

| 任务 | 推荐路径 |
|---|---|
| 发现画师 | 搜「lolita 画稿/柄图/设计稿」走 video search API，不走 user search |
| 监控创作者发布 | 定时调 `/aweme/post/?sec_user_id=...&count=5`，对比上次 aweme_id 集合，发现新帖 |
| 监控单帖流量 | 调 `/aweme/post/` 全量返回里含 statistics（digg/comment/share/play_count），按 sec_uid 拉一次能拿到该号最近 20 帖 |
| 评论扫购买意图 | 调 `/comment/list/?aweme_id=...` 拿前 20 条，正则匹配「求踢/收稿/全套多少」 |
| 批量关注画师 | 拿到 sec_uid + uid 后直接 POST follow/user/?type=1，节奏 30-50/天 |

⇒ **大部分监控只读，零 DOM 解析。一个签名 fetch 拿全数据。**
