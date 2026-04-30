#!/usr/bin/env python3
"""把 11 款的 popularity 评分写入 JSON。基于 4 维独立 tier + 综合标签 + evidence。"""
import json, os

DATA = "data"

POPULARITY = {
    "yingluofu_zhongyan_2.0": {
        "scale_tier": "现象级",
        "buzz_tier": "破圈",
        "authority_tier": "头部 IP",
        "resale_tier": "中保值",
        "composite_label": "现象级爆款",
        "evidence": [
            "淘宝意向金 4w+ 付款 → 按 30% 真实转化估 1.2w 真实付款（已超『现象级 ≥ 1w 单』阈值）",
            "宇宙太 2025-10 真人成片 8451 likes（樱洛芙终焉圣骸帖）",
            "viral『少女暴君』2026 Q2 浪潮同期款，破圈帖最高 36w likes",
            "画师叁狐 1117 likes 自发『是我画的』为品牌 IP 加持",
            "白金色被砍 / 红黑色褪色担忧 → 保值打中保值（非高）"
        ]
    },
    "yingluofu_gulong": {
        "scale_tier": "头部",
        "buzz_tier": "中位",
        "authority_tier": "普通",
        "resale_tier": "中保值",
        "composite_label": "暗黑哥特主流",
        "evidence": [
            "淘宝意向金 1w+ 付款 → 真实付款估 3-5k（『头部』3k-1w 单档）",
            "孝红服装细节控 04-27 3737 likes 工艺测评帖（樱洛芙整体做工对照信号）",
            "同名款冲突（Alicegirl 也有骨龙）增加搜索流量但分散品牌识别",
            "樱洛芙整体在 brands-reference top，但骨龙单款未进 KOL 横评 → 权威『普通』"
        ]
    },
    "yourhighness_qishijingshen": {
        "scale_tier": "腰部",
        "buzz_tier": "中位",
        "authority_tier": "黑红常驻",
        "resale_tier": "低保值",
        "composite_label": "反面教材",
        "evidence": [
            "淘宝 300+ 付款（『腰部』100-500 单档）",
            "yuancilang 2024-09 4445 likes『lo圈皇帝穿搭』圈内点评（讽刺意味）",
            "圈内挂烂记录：抄袭质疑（明承认参考嘉德礼服+夏尔斗篷被吐照搬）+ 6-7 斤超重 + PDD 厂货加价 + ¥1700 全套 = 终焉圣骸 ¥648 的 2.6 倍",
            "高单价低口碑反面教材（lolita-domain-knowledge brands-reference 黑红常驻记录）"
        ]
    },
    "yingyue_longyao": {
        "scale_tier": "中位",
        "buzz_tier": "中位",
        "authority_tier": "知名",
        "resale_tier": "中保值",
        "composite_label": "中华细分主流",
        "evidence": [
            "淘宝 700+ 付款（『中位』500-3k 单档）",
            "初柒顾 1665 likes KOL 设计帖明确公开 4 档价格 + 设计解读（中华军lo 赛道头部 KOL 帖）",
            "叁狐 04-10 1086 likes『平平无奇的军lo罢了』提及军lo赛道（含龙曜同期对照）",
            "汉洋折衷主题填补市场空白（中华+军lo 双标签独家覆盖）"
        ]
    },
    "weizhixingchen_jichengren": {
        "scale_tier": "中位",
        "buzz_tier": "中位",
        "authority_tier": "普通",
        "resale_tier": "中保值",
        "composite_label": "白菜畅销",
        "evidence": [
            "淘宝 400+ 现货付款（最准——下单即发，无意向金水分）",
            "圈内王子系科普 9619 likes 帖（明确未列入五大原创头部清单 → 腰部品牌定位）",
            "白菜价 ¥369 全套（继承人红 / 神权使者绿双 SKU 系列）",
            "同品牌 兔叽侦探 ¥68.6 衬衫 600+ 付款 → 整店白菜段稳定走量"
        ]
    },
    "maomiwanan_juanjuan": {
        "scale_tier": "加购未上架",
        "buzz_tier": "冷启动",
        "authority_tier": "未提及",
        "resale_tier": "不流通",
        "composite_label": "加购未上架",
        "evidence": [
            "淘宝无独立 SKU（运营路径：试样图 → 投票 → 开订）",
            "XHS 投票帖 2349 likes 但是品牌官号自发，剔除集赞营销 / 官号自发后无自然 KOL 真人成片",
            "微博渠道几乎缺位 → 多渠道营销弱",
            "未在任何 KOL 横评帖出现"
        ]
    },
    "dierchengbao_tangguopu": {
        "scale_tier": "中位",
        "buzz_tier": "中位",
        "authority_tier": "知名",
        "resale_tier": "中保值",
        "composite_label": "甜系王子主流",
        "evidence": [
            "淘宝老链接 400+ 付款（『中位』500-3k 单档下沿）",
            "无人区自助售卖机 2025-06 真人成片 1626 likes + 蓝空koko 2025-05 真人成片 1376 likes 累计 ~3k（『中位』传播）",
            "圈内『小甜基』标签共识形成（甜系 × 王子复合赛道）",
            "本款『久违的小甜基』暗示重团 + 命中 2026 Q2 viral 浪潮（但开团早于 viral 爆点）"
        ]
    },
    "shaonyongdao_daogaozhe": {
        "scale_tier": "腰部",
        "buzz_tier": "长尾",
        "authority_tier": "普通",
        "resale_tier": "低保值",
        "composite_label": "仿冒受害腰部",
        "evidence": [
            "淘宝『千人加购』+ 现货销售 → 真实付款估 50-150（『腰部』100-500 单档）",
            "圣职系赛道头部款是另一品牌『安缇娅的祷告』（小蝴蝶 1506 likes 帖明确 tag #安缇娅的祷告）→ 该款赛道内非头部",
            "啊不许烦 2024-06 344 likes『重复的已经不想截了』直接吐槽：识图发现『不下三十家店在卖』 → 品牌仿冒泛滥实证",
            "圈内对少女的永无岛 PDD 厂货争议（@JK日常 2025-02 微博）→ 原版稀缺性受损",
            "保值降级原因：仿冒泛滥而非工艺翻车（与 YourHighness 黑红性质不同）"
        ]
    },
    "pc_hongyuhei_4.0": {
        "scale_tier": "中位",
        "buzz_tier": "中位",
        "authority_tier": "头部 IP",
        "resale_tier": "高保值",
        "composite_label": "头部 IP",
        "evidence": [
            "淘宝『千人加购』→ 真实付款估 100-200（淘宝层面腰部），但 PC 主战场是微博团购 + 客服私单（淘宝数据被低估）→ 综合判中位",
            "Duuu 04-06 真人成片 1002 likes（『#黑与红』tag 命中系列）+ 圈内 KOL 流量集中在 PC 其他款（猎兔 / 兔子剧场）→ 红与黑单款传播中位",
            "**王子系五大原创之一**（lolita-domain-knowledge style-genres 9619 赞圈内科普帖明文）= 头部 IP",
            "**红与黑系列 1.0 → 4.0 跨 5 年看家款**（2019-2024）= 高保值 IP 资产化典范",
            "微博营销节奏完整：图透 → 视频 → 截单预告 → lookbook 五段式（5 个 brand_self_posts）"
        ]
    },
    "alicegirl_poxiaozhe": {
        "scale_tier": "腰部",
        "buzz_tier": "长尾",
        "authority_tier": "普通",
        "resale_tier": "中保值",
        "composite_label": "腰部",
        "evidence": [
            "拆 4 SKU 各 95-100+ 付款 → 取最低（jsk 95+）作为成套数估算（『腰部』100-500 单档）",
            "Alicegirl XHS 官号自发『剑和玫瑰』2026-01 仅 39 likes 真人成片（极薄）",
            "圈内 651 likes 拔草帖（Xxxxxz 2024-12『lo娘真好欺负』）但未明确是破晓者",
            "Alicegirl 进入 brands-reference『原创设计师线』列表（普通），未进王子系五大",
            "改 4 版品控信号：官号原话『这款改了四版终于可以给老婆们看了』"
        ]
    },
    "vancy_souchazhe": {
        "scale_tier": "长尾",
        "buzz_tier": "冷启动",
        "authority_tier": "头部 IP",
        "resale_tier": "高保值",
        "composite_label": "工艺型小众",
        "evidence": [
            "淘宝本款无直挂（走微博团购 + 快团团 + 客服私单）→ 淘宝规模长尾，但同店探索者 2 套装 100+ 付款做参照",
            "Vancy XHS 官号自发『搜查者｜军绿色』119 likes 是最高赞，剔除官号自发后无 KOL 真人成片 → 传播冷启动",
            "**圈内『梵希 yyds』顶级口碑** 2022 KOL 君不见鹿原话流通到 2026 → 头部 IP（圈内权威 + 长尾 KOL 引用）",
            "**5 年长寿款 IP**（2021-08 首发 → 2026-04 第 6 团再贩）= 高保值 IP 资产化典范",
            "枪套配件『腿肯』+ 船帽 + 军绿主推差异化 = 工艺差异化锚点（工艺型而非流量型品牌）"
        ]
    }
}

count_done = 0
for fname in os.listdir(DATA):
    if not fname.endswith(".json"):
        continue
    p = os.path.join(DATA, fname)
    with open(p, encoding='utf-8') as f:
        d = json.load(f)
    iid = d.get("id", "")
    if iid in POPULARITY:
        d["popularity"] = POPULARITY[iid]
        with open(p, 'w', encoding='utf-8') as f:
            json.dump(d, f, ensure_ascii=False, indent=2)
        count_done += 1
        print(f"  ✓ {iid}: {POPULARITY[iid]['composite_label']}")
    else:
        print(f"  ⚠ {iid}: no popularity defined (skipped)")

print(f"\nDone: {count_done}/11 款已写入 popularity")
