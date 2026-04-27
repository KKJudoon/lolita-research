#!/usr/bin/env python3
"""Render data/*.json to:
  - index.html         (summary: responsive card list)
  - items/<id>.html    (per-款 detail page)

Idempotent — re-run after editing data."""
import json
import pathlib
import html
import datetime
import re

ROOT = pathlib.Path(__file__).resolve().parent
DATA_DIR = ROOT / "data"
ITEMS_DIR = ROOT / "items"
INDEX = ROOT / "index.html"


def esc(s):
    return html.escape(str(s)) if s is not None else ""


def normalize_xhs_url(u):
    """XHS opencli returns /search_result/<id> URLs which redirect away when
    opened directly (search route, not share route). Transform to /explore/<id>
    which is the stable share form. Also fixes empty xsec_source."""
    if not isinstance(u, str) or "/search_result/" not in u:
        return u
    out = u.replace("/search_result/", "/explore/", 1)
    # Replace empty xsec_source= with xsec_source=pc_user
    out = re.sub(r"xsec_source=(?=&|$)", "xsec_source=pc_user", out)
    return out


def kv_row(k, v, link=False, note=False):
    if v is None or v == "":
        return ""
    if link:
        v_norm = normalize_xhs_url(v)
        v_html = f'<a href="{esc(v_norm)}" target="_blank" rel="noopener">{esc(v_norm[:80])}</a>'
    else:
        v_html = esc(v)
    cls = "row note" if note else "row"
    return f'<div class="{cls}"><span class="k">{esc(k)}</span><span class="v">{v_html}</span></div>'


def shop_block(label, data, fields):
    if not data:
        return ""
    rows = []
    for entry in fields:
        if len(entry) == 3:
            lbl, key, is_link = entry
        else:
            lbl, key = entry
            is_link = False
        if data.get(key):
            rows.append(kv_row(lbl, data[key], link=is_link))
    if data.get("note"):
        rows.append(f'<div class="row note">{esc(data["note"])}</div>')
    return f'<div class="shop-block"><h4>{esc(label)}</h4>{"".join(rows)}</div>'


def render_hot_post(p):
    url = normalize_xhs_url(p.get("url", "") or "")
    link_html = f'<div class="post-link"><a href="{esc(url)}" target="_blank" rel="noopener">查看原帖 →</a></div>' if url else ''
    return f'''
    <article class="post">
      <div class="post-head">
        <span class="post-type">{esc(p.get("type",""))}</span>
        <span class="post-meta">@{esc(p.get("author",""))} · {esc(p.get("date",""))} · ❤ {esc(p.get("likes",""))} · 💬 {esc(p.get("comments",""))}</span>
      </div>
      <div class="post-title">{esc(p.get("title",""))}</div>
      <div class="post-summary">{esc(p.get("summary",""))}</div>
      {link_html}
    </article>
    '''


# ---------------------------------------------------------------- common css
COMMON_CSS = '''
  * { box-sizing: border-box; }
  body { font-family: -apple-system, "PingFang SC", sans-serif; background: #f6f4ef; color: #1a1a1a; max-width: 1200px; margin: 0 auto; padding: 24px 16px; line-height: 1.6; }
  h1 { border-bottom: 2px solid #2c2c2c; padding-bottom: 8px; margin-top: 0; }
  .meta { color: #777; font-size: 12px; margin-bottom: 24px; }
  a { color: #5a4a2a; text-decoration: none; border-bottom: 1px dashed #c8a868; }
  a:hover { color: #8a6a3a; }
  a.bare { border-bottom: none; }
'''


# ---------------------------------------------------------------- index page
def render_summary_card(item):
    iid = item.get("id", "")
    name = esc(item["name"])
    brand = esc(item.get("brand", ""))
    designer = esc(item.get("designer", ""))
    sub = brand + ((" · " + designer) if designer else "")

    posters = item.get("posters", [])
    thumb = posters[0] if posters else ""
    thumb_html = f'<img src="{esc(thumb)}" alt="{name}" loading="lazy"/>' if thumb else '<div class="no-thumb">无图</div>'

    rel = item.get("release", {})
    release = esc(rel.get("date_range", ""))

    price = item.get("price", {})
    price_parts = []
    if price.get("op") is not None:
        price_parts.append(f'OP ¥{price["op"]}')
    if price.get("full_set") is not None:
        price_parts.append(f'整套 ¥{price["full_set"]}')
    price_str = " · ".join(price_parts) if price_parts else "—"

    taobao = item.get("shops", {}).get("taobao", {}) or {}
    shop = esc(taobao.get("shop_name", ""))
    sales = esc(taobao.get("sales", ""))

    keywords = item.get("synthesis", {}).get("keywords", []) or []
    kw_html = "".join(f'<span class="kw">{esc(k)}</span>' for k in keywords[:6])

    detail_url = f"items/{iid}.html"

    return f'''
    <a class="summary-card bare" href="{esc(detail_url)}">
      <div class="thumb">{thumb_html}</div>
      <div class="info">
        <div class="title">{name}</div>
        <div class="sub">{sub}</div>
        <div class="facts">
          <span class="fact"><b>价格</b> {esc(price_str)}</span>
          <span class="fact"><b>上新</b> {release or "—"}</span>
          <span class="fact"><b>店铺</b> {shop or "—"}</span>
          <span class="fact"><b>销量</b> {sales or "—"}</span>
        </div>
        <div class="kws">{kw_html}</div>
      </div>
    </a>
    '''


CANONICAL_STYLES = ["甜lo", "军lo", "古典", "哥特", "王子lo", "中华", "海军", "花嫁", "茶会"]


def styles_for_item(item):
    """Return all canonical styles matched by this item's style_tags.
    A card can belong to multiple tabs (e.g. 军lo+王子lo, 中华+军lo)."""
    tags = item.get("style_tags", []) or []
    matched = []
    for s in CANONICAL_STYLES:
        if any(s in t for t in tags):
            matched.append(s)
    if not matched and tags:
        matched.append(tags[0])
    return matched or ["其他"]


def write_index(items):
    # Build groups (one item can appear in multiple groups)
    groups = {}
    for it in items:
        for s in styles_for_item(it):
            groups.setdefault(s, []).append(it)
    ordered = [s for s in CANONICAL_STYLES if s in groups] + sorted([s for s in groups if s not in CANONICAL_STYLES])

    # Tab buttons (count = unique items in that group)
    tab_buttons = f'<button class="tab active" data-style="all">全部 ({len(items)})</button>'
    tab_buttons += "".join(
        f'<button class="tab" data-style="{esc(s)}">{esc(s)} ({len(groups[s])})</button>'
        for s in ordered
    )

    # Cards: render once per item, attach all matched styles as space-separated data-styles
    cards_parts = []
    for it in items:
        styles = styles_for_item(it)
        card = render_summary_card(it)
        attr = " ".join(esc(s) for s in styles)
        card_with_attr = card.replace('<a class="summary-card bare"', f'<a class="summary-card bare" data-styles="{attr}"', 1)
        cards_parts.append(card_with_attr)
    cards_html = "\n".join(cards_parts)

    now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
    doc = f'''<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Lolita 款式调研</title>
<style>
{COMMON_CSS}
  .summary-card {{
    display: flex; gap: 16px; padding: 16px; margin-bottom: 12px;
    background: white; border-radius: 12px; box-shadow: 0 1px 6px rgba(0,0,0,0.05);
    transition: transform 0.15s, box-shadow 0.15s;
    color: #1a1a1a;
  }}
  .summary-card:hover {{ transform: translateY(-2px); box-shadow: 0 4px 16px rgba(0,0,0,0.1); border-bottom: none; }}
  .thumb {{ flex-shrink: 0; width: 140px; height: 180px; border-radius: 8px; overflow: hidden; background: #eee; }}
  .thumb img {{ width: 100%; height: 100%; object-fit: cover; display: block; }}
  .no-thumb {{ width: 100%; height: 100%; display: flex; align-items: center; justify-content: center; color: #aaa; font-size: 12px; }}
  .info {{ flex: 1; min-width: 0; }}
  .title {{ font-size: 18px; font-weight: 600; margin-bottom: 2px; }}
  .sub {{ color: #888; font-size: 13px; margin-bottom: 10px; }}
  .facts {{ display: flex; flex-wrap: wrap; gap: 8px 16px; font-size: 13px; color: #444; margin-bottom: 8px; }}
  .fact b {{ color: #888; font-weight: normal; margin-right: 4px; }}
  .kws {{ display: flex; flex-wrap: wrap; gap: 4px; }}
  .kw {{ background: #efe9d9; color: #5a4a2a; padding: 2px 8px; border-radius: 12px; font-size: 11px; }}

  /* tabs */
  .tabs {{ display: flex; flex-wrap: wrap; gap: 6px; margin: 16px 0 20px; }}
  .tab {{ background: white; border: 1px solid #c8a868; color: #5a4a2a; padding: 6px 14px; border-radius: 18px; font-size: 13px; cursor: pointer; transition: all 0.15s; }}
  .tab:hover {{ background: #faf3e0; }}
  .tab.active {{ background: #c8a868; color: white; }}

  /* mobile: stack vertically */
  @media (max-width: 640px) {{
    body {{ padding: 12px 8px; }}
    .summary-card {{ flex-direction: column; gap: 10px; padding: 12px; }}
    .thumb {{ width: 100%; height: 220px; }}
    .title {{ font-size: 17px; }}
    .facts {{ gap: 6px 12px; font-size: 12px; }}
    .tab {{ font-size: 12px; padding: 5px 10px; }}
  }}
</style>
</head>
<body>
  <h1>Lolita 款式调研</h1>
  <div class="meta">最后更新 {now} · 共 {len(items)} 款 · 点卡片看款式细节</div>
  <div class="tabs">{tab_buttons}</div>
  <div id="cards">
  {cards_html}
  </div>
<script>
  const tabs = document.querySelectorAll(".tab");
  const cards = document.querySelectorAll(".summary-card");
  tabs.forEach(t => t.addEventListener("click", () => {{
    tabs.forEach(x => x.classList.remove("active"));
    t.classList.add("active");
    const style = t.dataset.style;
    cards.forEach(c => {{
      const styles = (c.dataset.styles || "").split(" ");
      c.style.display = (style === "all" || styles.includes(style)) ? "" : "none";
    }});
  }}));
</script>
</body>
</html>'''
    INDEX.write_text(doc)


# ---------------------------------------------------------------- detail page
def render_detail(item):
    iid = item.get("id", "")
    name = esc(item["name"])
    brand = esc(item.get("brand", ""))
    designer = esc(item.get("designer", ""))
    illustrator = esc(item.get("illustrator", ""))
    designer_note = esc(item.get("designer_note", "") or item.get("illustrator_note", ""))
    designer_line = f"品牌：{brand}"
    if designer:
        designer_line += f"　/　服装设计：{designer}"
    if illustrator:
        designer_line += f"　/　画师：{illustrator}"

    tags = " ".join(f'<span class="tag">{esc(t)}</span>' for t in item.get("style_tags", []))
    summary = esc(item.get("style_summary", ""))

    rel = item.get("release", {})
    release_html = "".join([
        kv_row("上新窗口", rel.get("date_range")),
        kv_row("类型", rel.get("type")),
        kv_row("海报首发", rel.get("poster_first_seen")),
    ])
    if rel.get("note"):
        release_html += f'<div class="row note">{esc(rel["note"])}</div>'

    price = item.get("price", {})
    price_html = ""
    if price.get("op") is not None:
        price_html += kv_row("OP", f"¥{price['op']}")
    if price.get("full_set") is not None:
        price_html += kv_row("整套", f"¥{price['full_set']}")
    if price.get("deposit_link_intent") is not None:
        price_html += kv_row("意向金", f"¥{price['deposit_link_intent']} 抵 ¥30")
    if price.get("note"):
        price_html += f'<div class="row note">{esc(price["note"])}</div>'

    colors = " ".join(f'<span class="color-chip">{esc(c)}</span>' for c in item.get("colors", []))
    dropped = item.get("colors_dropped", [])
    if dropped:
        colors += " <span class='color-dropped'>已取消: " + " ".join(esc(c) for c in dropped) + "</span>"

    shops = item.get("shops", {})
    taobao_html = shop_block("淘宝", shops.get("taobao"), [
        ("店铺", "shop_name"), ("店铺主页", "url", True),
        ("店铺备注", "url_note"),
        ("店铺评价", "shop_rating"),
        ("淘宝搜索", "search_url", True),
        ("相关商品", "related_item_url", True),
        ("相关商品备注", "related_item_note"),
        ("当前标题", "list_title"), ("挂牌价", "list_price"),
        ("销量", "sales"), ("销量趋势", "sales_trend"),
        ("销量备注", "sales_note"), ("发货地", "location"),
    ])
    weibo_html = shop_block("微博", shops.get("weibo"), [
        ("官方账号", "official_account"), ("官方主页", "official_url", True),
        ("备用账号 1", "alt_account"), ("备用主页 1", "alt_url", True),
        ("备用账号 2", "alt_account_2"), ("备用主页 2", "alt_url_2", True),
        ("上新海报帖", "upgrade_post_url", True), ("帖子来源", "upgrade_post_account"),
        ("帖子日期", "post_date"),
    ])
    xhs_html = shop_block("小红书", shops.get("xiaohongshu"), [
        ("品牌账号", "official_account"), ("品牌主页", "official_url", True),
        ("画师账号", "illustrator_account"), ("画师主页", "illustrator_url", True),
    ])

    posters = item.get("posters", [])
    poster_html = "".join(f'<img src="../{esc(p)}" loading="lazy" class="lb-img" data-src="../{esc(p)}"/>' for p in posters)
    posters_source = item.get("posters_source", "")
    posters_source_html = f'<div class="posters-source">📷 图源说明：{esc(posters_source)}</div>' if posters_source else ''

    hot_posts = item.get("hot_posts", {}).get("xiaohongshu", [])
    hot_posts_html = ""
    if hot_posts:
        rendered = "".join(render_hot_post(p) for p in hot_posts)
        hot_posts_html = f'<section class="hot-posts"><h3>小红书相关热门帖（{len(hot_posts)}）</h3>{rendered}</section>'

    insp = item.get("design_inspiration", {})
    insp_html = ""
    if insp:
        st = insp.get("source_type", "")
        badge_text = {
            "official": "官方公开",
            "kol_quote": "圈内 KOL 描述",
            "kol_quote_with_ai_analysis": "KOL 描述 + AI 推断",
            "ai_analyzed": "AI 分析（非官方）"
        }.get(st, st)
        badge_class = "insp-official" if st == "official" else ("insp-kol" if "kol" in st else "insp-ai")
        elements_html = ""
        for el in insp.get("elements", []):
            inner = []
            inner.append(f'<div class="el-name">{esc(el.get("element",""))}</div>')
            inner.append(f'<div class="el-src"><b>来源：</b>{esc(el.get("source_lineage",""))}</div>')
            if el.get("purpose"):
                inner.append(f'<div class="el-purpose"><b>设计目的：</b>{esc(el.get("purpose",""))}</div>')
            if el.get("note"):
                inner.append(f'<div class="el-note">{esc(el.get("note",""))}</div>')
            mark = ""
            if el.get("official"):
                mark = '<span class="el-mark official">官方</span>'
            elif el.get("ai_inferred"):
                mark = '<span class="el-mark ai">AI 推断</span>'
            elements_html += f'<div class="el">{mark}{"".join(inner)}</div>'
        official_quote_html = ""
        if insp.get("official_quote"):
            official_quote_html = f'<blockquote class="quote">官方原话：『{esc(insp["official_quote"])}』</blockquote>'
        elif insp.get("kol_quote"):
            official_quote_html = f'<blockquote class="quote">KOL 描述：『{esc(insp["kol_quote"])}』</blockquote>'
        thinking_html = f'<div class="thinking"><b>设计思路：</b>{esc(insp.get("design_thinking",""))}</div>' if insp.get("design_thinking") else ""
        prompt_html = ""
        if insp.get("for_image_gen_prompt"):
            prompt_html = f'<details class="ai-prompt"><summary>📝 AI 生图 prompt（英文，可复制给 GPT/DALL-E）</summary><div class="prompt-text">{esc(insp["for_image_gen_prompt"])}</div></details>'
        n_elements = len(insp.get("elements", []))
        insp_html = f'''
        <details class="inspiration">
          <summary><h3 style="display:inline">设计灵感 / 元素拆解 <span class="insp-badge {badge_class}">{esc(badge_text)}</span> <span class="insp-count">展开看 {n_elements} 个元素 + AI 生图 prompt</span></h3></summary>
          <div class="insp-body">
            <div class="insp-note">{esc(insp.get("source_note",""))}</div>
            {f'<div class="insp-theme"><b>主题：</b>{esc(insp.get("theme",""))}</div>' if insp.get("theme") else ""}
            {official_quote_html}
            <div class="elements">{elements_html}</div>
            {thinking_html}
            {prompt_html}
          </div>
        </details>
        '''

    syn = item.get("synthesis", {})
    syn_html = ""
    if syn:
        kw_html = " ".join(f'<span class="kw">{esc(k)}</span>' for k in syn.get("keywords", []))
        pos_html = "".join(f"<li>{esc(x)}</li>" for x in syn.get("highlights_positive", []))
        neg_html = "".join(f"<li>{esc(x)}</li>" for x in syn.get("highlights_negative", []))
        verdict = esc(syn.get("verdict_short", ""))
        syn_html = f'''
        <section class="synthesis">
          <h3>综合分析</h3>
          <div class="kw-row">{kw_html}</div>
          <div class="syn-grid">
            <div class="syn-block syn-pos"><h4>正面</h4><ul>{pos_html}</ul></div>
            <div class="syn-block syn-neg"><h4>负面 / 争议</h4><ul>{neg_html}</ul></div>
          </div>
          <div class="verdict">{verdict}</div>
        </section>
        '''

    verified_badge = '<span class="verified">✓ verified</span>' if item.get("verified") else '<span class="unverified">unverified</span>'

    doc = f'''<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{name} · 军lo 调研</title>
<style>
{COMMON_CSS}
  .back {{ font-size: 13px; margin-bottom: 12px; display: inline-block; }}
  .card {{ background: white; border-radius: 12px; padding: 24px 28px; box-shadow: 0 2px 12px rgba(0,0,0,0.05); }}
  .card header h2 {{ margin: 0; font-size: 24px; }}
  .brand-line {{ color: #666; font-size: 14px; margin: 4px 0; }}
  .designer-note {{ color: #888; font-size: 12px; font-style: italic; }}
  .verified {{ background: #d4f4d4; color: #2c7a2c; padding: 2px 8px; border-radius: 4px; font-size: 11px; margin-left: 6px; vertical-align: middle; }}
  .tags {{ margin: 8px 0; }}
  .tag {{ display: inline-block; background: #efe9d9; color: #5a4a2a; padding: 2px 8px; border-radius: 12px; font-size: 12px; margin-right: 4px; }}
  .summary {{ color: #444; line-height: 1.7; }}
  .poster-grid {{ display: grid; grid-template-columns: repeat(4, 1fr); gap: 8px; margin: 16px 0; }}
  .poster-grid img {{ width: 100%; height: 320px; object-fit: cover; border-radius: 6px; cursor: pointer; transition: transform 0.2s; }}
  .poster-grid img:hover {{ transform: scale(1.02); }}
  .poster-grid img {{ cursor: zoom-in; }}
  .posters-source {{ font-size: 12px; color: #777; background: #f8f4e8; border-left: 3px solid #c5a572; padding: 8px 12px; margin: 6px 0 16px; border-radius: 0 6px 6px 0; line-height: 1.6; }}
  .lb-overlay {{ position: fixed; inset: 0; background: rgba(0,0,0,0.88); display: none; align-items: center; justify-content: center; z-index: 1000; padding: 30px 60px; }}
  .lb-overlay.open {{ display: flex; }}
  .lb-overlay img {{ max-width: 100%; max-height: 100%; object-fit: contain; box-shadow: 0 8px 32px rgba(0,0,0,0.5); border-radius: 4px; cursor: default; }}
  .lb-close, .lb-prev, .lb-next {{ position: absolute; background: rgba(255,255,255,0.15); color: #fff; border: none; width: 44px; height: 44px; border-radius: 50%; cursor: pointer; font-size: 28px; line-height: 1; display: flex; align-items: center; justify-content: center; transition: background 0.2s; }}
  .lb-close:hover, .lb-prev:hover, .lb-next:hover {{ background: rgba(255,255,255,0.3); }}
  .lb-close {{ top: 16px; right: 16px; }}
  .lb-prev {{ left: 16px; top: 50%; transform: translateY(-50%); }}
  .lb-next {{ right: 16px; top: 50%; transform: translateY(-50%); }}
  .lb-counter {{ position: absolute; bottom: 16px; left: 50%; transform: translateX(-50%); color: #fff; background: rgba(0,0,0,0.5); padding: 4px 12px; border-radius: 12px; font-size: 13px; }}
  details.inspiration {{ background: #fdfaf0; border: 1px solid #e8d8b0; border-radius: 8px; margin: 16px 0; padding: 0; }}
  details.inspiration > summary {{ list-style: none; cursor: pointer; padding: 14px 18px; background: #f7eed5; border-radius: 8px; user-select: none; }}
  details.inspiration > summary::-webkit-details-marker {{ display: none; }}
  details.inspiration > summary::before {{ content: "▸ "; color: #8a6a30; font-weight: bold; transition: transform 0.2s; display: inline-block; }}
  details.inspiration[open] > summary {{ border-radius: 8px 8px 0 0; }}
  details.inspiration[open] > summary::before {{ content: "▾ "; }}
  details.inspiration > summary h3 {{ margin: 0; font-size: 16px; }}
  .insp-count {{ color: #8a6a30; font-size: 12px; font-weight: normal; margin-left: 8px; }}
  .insp-body {{ padding: 16px 18px; }}
  .info-grid {{ display: grid; grid-template-columns: repeat(3, 1fr); gap: 16px; margin: 16px 0; }}
  .info {{ background: #faf7ed; padding: 12px 16px; border-radius: 6px; }}
  .info h3 {{ margin: 0 0 8px 0; font-size: 14px; color: #5a4a2a; }}
  .row {{ font-size: 13px; line-height: 1.8; display: flex; gap: 8px; }}
  .row .k {{ color: #888; min-width: 80px; }}
  .row .v {{ color: #222; flex: 1; word-break: break-word; }}
  .row.note {{ color: #777; font-style: italic; font-size: 12px; }}
  .color-chip {{ background: #f0e8d0; padding: 2px 8px; border-radius: 4px; margin-right: 4px; font-size: 12px; }}
  .color-dropped {{ background: #f8e0e0; color: #a04020; padding: 2px 8px; border-radius: 4px; font-size: 11px; margin-left: 8px; text-decoration: line-through; }}
  .shops {{ display: grid; grid-template-columns: repeat(3, 1fr); gap: 16px; margin-top: 16px; }}
  .shop-block {{ background: #fbf8ee; padding: 12px 16px; border-radius: 6px; border-left: 3px solid #c8a868; }}
  .shop-block h4 {{ margin: 0 0 8px 0; font-size: 14px; color: #5a4a2a; }}
  .hot-posts {{ margin-top: 24px; padding-top: 16px; border-top: 1px solid #ddd; }}
  .hot-posts h3 {{ font-size: 16px; color: #2a2a2a; }}
  .post {{ background: #fafafa; padding: 12px 16px; border-radius: 6px; margin-bottom: 8px; }}
  .post-head {{ display: flex; justify-content: space-between; align-items: center; margin-bottom: 4px; flex-wrap: wrap; gap: 8px; }}
  .post-type {{ background: #e8d8b0; color: #6a4a1a; padding: 2px 8px; border-radius: 12px; font-size: 11px; }}
  .post-meta {{ color: #888; font-size: 11px; }}
  .post-title {{ font-weight: 600; font-size: 14px; margin: 4px 0; }}
  .post-summary {{ color: #444; line-height: 1.7; font-size: 13px; }}
  .post-link {{ font-size: 11px; margin-top: 4px; }}
  .inspiration {{ margin-top: 24px; padding: 16px; background: #f4ecdb; border-radius: 8px; border-left: 4px solid #8a6a3a; }}
  .inspiration h3 {{ margin: 0 0 8px 0; }}
  .insp-badge {{ font-size: 12px; padding: 3px 10px; border-radius: 12px; margin-left: 8px; vertical-align: middle; font-weight: normal; }}
  .insp-badge.insp-official {{ background: #d4f4d4; color: #2c7a2c; }}
  .insp-badge.insp-kol {{ background: #fde8b0; color: #6a4a1a; }}
  .insp-badge.insp-ai {{ background: #fde0d0; color: #a04020; }}
  .insp-note {{ font-size: 12px; color: #777; margin-bottom: 10px; font-style: italic; }}
  .insp-theme {{ font-size: 14px; margin-bottom: 12px; padding: 8px 12px; background: white; border-radius: 4px; }}
  .quote {{ margin: 12px 0; padding: 10px 14px; background: white; border-left: 3px solid #c8a868; font-size: 13px; color: #444; }}
  .elements {{ display: grid; gap: 10px; margin: 12px 0; }}
  .el {{ background: white; padding: 10px 14px; border-radius: 6px; font-size: 13px; line-height: 1.7; }}
  .el-name {{ font-weight: 600; color: #2a2a2a; margin-bottom: 4px; }}
  .el-src {{ color: #444; }}
  .el-src b {{ color: #888; font-weight: normal; }}
  .el-purpose {{ color: #555; font-size: 12px; margin-top: 4px; }}
  .el-purpose b {{ color: #888; font-weight: normal; }}
  .el-note {{ color: #666; font-size: 12px; font-style: italic; margin-top: 4px; }}
  .el-mark {{ display: inline-block; font-size: 10px; padding: 1px 6px; border-radius: 3px; margin-right: 6px; vertical-align: middle; }}
  .el-mark.official {{ background: #d4f4d4; color: #2c7a2c; }}
  .el-mark.ai {{ background: #fde0d0; color: #a04020; }}
  .thinking {{ margin: 12px 0; padding: 10px 14px; background: white; border-radius: 6px; font-size: 13px; line-height: 1.7; }}
  .thinking b {{ color: #5a4a2a; }}
  .ai-prompt {{ margin-top: 12px; background: white; border-radius: 6px; padding: 8px 14px; font-size: 13px; }}
  .ai-prompt summary {{ cursor: pointer; color: #5a4a2a; font-weight: 600; }}
  .prompt-text {{ margin-top: 8px; padding: 10px; background: #f6f4ef; border-radius: 4px; font-family: ui-monospace, monospace; font-size: 12px; line-height: 1.6; user-select: all; }}
  .synthesis {{ margin-top: 24px; padding: 16px; background: #fff8ed; border-radius: 8px; border-left: 4px solid #c8a868; }}
  .synthesis h3 {{ margin: 0 0 12px 0; }}
  .kw-row {{ margin-bottom: 12px; }}
  .kw {{ background: #c8a868; color: white; padding: 3px 10px; border-radius: 14px; font-size: 12px; margin-right: 4px; display: inline-block; margin-bottom: 4px; }}
  .syn-grid {{ display: grid; grid-template-columns: 1fr 1fr; gap: 12px; }}
  .syn-block {{ padding: 12px 16px; border-radius: 6px; }}
  .syn-pos {{ background: #ecf5ec; }}
  .syn-pos h4 {{ color: #2c7a2c; margin: 0 0 8px 0; }}
  .syn-neg {{ background: #fdf0ec; }}
  .syn-neg h4 {{ color: #a04020; margin: 0 0 8px 0; }}
  .syn-block ul {{ margin: 0; padding-left: 20px; line-height: 1.8; font-size: 13px; }}
  .verdict {{ margin-top: 12px; padding: 12px; background: white; border-radius: 6px; line-height: 1.7; font-size: 13px; }}

  /* mobile */
  @media (max-width: 640px) {{
    body {{ padding: 12px 8px; }}
    .card {{ padding: 16px; }}
    .card header h2 {{ font-size: 20px; }}
    .poster-grid {{ grid-template-columns: repeat(2, 1fr); }}
    .poster-grid img {{ height: 240px; }}
    .info-grid {{ grid-template-columns: 1fr; }}
    .shops {{ grid-template-columns: 1fr; }}
    .syn-grid {{ grid-template-columns: 1fr; }}
  }}
</style>
</head>
<body>
  <a class="back" href="../index.html">← 返回所有款</a>
  <article class="card" id="{esc(iid)}">
    <header>
      <h2>{name} {verified_badge}</h2>
      <div class="brand-line">{designer_line}</div>
      {f'<div class="designer-note">{designer_note}</div>' if designer_note else ''}
      <div class="tags">{tags}</div>
    </header>
    <p class="summary">{summary}</p>
    <div class="poster-grid">{poster_html}</div>
    {posters_source_html}
    <div class="info-grid">
      <section class="info"><h3>上新</h3>{release_html}</section>
      <section class="info"><h3>价格</h3>{price_html}</section>
      <section class="info"><h3>配色</h3><div class="row">{colors}</div></section>
    </div>
    <div class="shops">
      {taobao_html}
      {weibo_html}
      {xhs_html}
    </div>
    {insp_html}
    {hot_posts_html}
    {syn_html}
  </article>

  <div id="lightbox" class="lb-overlay" onclick="closeLB(event)" role="dialog" aria-hidden="true">
    <button class="lb-close" onclick="closeLB(event)" aria-label="关闭">×</button>
    <button class="lb-prev" onclick="navLB(event,-1)" aria-label="上一张">‹</button>
    <button class="lb-next" onclick="navLB(event,1)" aria-label="下一张">›</button>
    <img id="lb-img" src="" alt=""/>
    <div class="lb-counter" id="lb-counter"></div>
  </div>
  <script>
    (function() {{
      const overlay = document.getElementById('lightbox');
      const lbImg = document.getElementById('lb-img');
      const counter = document.getElementById('lb-counter');
      const imgs = Array.from(document.querySelectorAll('.poster-grid .lb-img'));
      let cur = -1;
      function openLB(idx) {{
        cur = idx;
        lbImg.src = imgs[cur].dataset.src;
        counter.textContent = (cur+1) + ' / ' + imgs.length;
        overlay.classList.add('open');
        document.body.style.overflow = 'hidden';
      }}
      window.closeLB = function(e) {{
        if (e && e.target.id !== 'lightbox' && !e.target.classList.contains('lb-close')) return;
        overlay.classList.remove('open');
        document.body.style.overflow = '';
        cur = -1;
      }};
      window.navLB = function(e, d) {{
        e.stopPropagation();
        if (cur < 0) return;
        cur = (cur + d + imgs.length) % imgs.length;
        lbImg.src = imgs[cur].dataset.src;
        counter.textContent = (cur+1) + ' / ' + imgs.length;
      }};
      imgs.forEach((img, i) => img.addEventListener('click', () => openLB(i)));
      document.addEventListener('keydown', (e) => {{
        if (!overlay.classList.contains('open')) return;
        if (e.key === 'Escape') window.closeLB({{target:{{id:'lightbox'}}}});
        else if (e.key === 'ArrowLeft') window.navLB(e, -1);
        else if (e.key === 'ArrowRight') window.navLB(e, 1);
      }});
    }})();
  </script>
</body>
</html>'''
    return doc


def main():
    items = []
    for f in sorted(DATA_DIR.glob("*.json")):
        if f.parent.name == "raw":
            continue
        items.append(json.loads(f.read_text()))

    ITEMS_DIR.mkdir(exist_ok=True)
    for it in items:
        iid = it.get("id", "")
        if not iid:
            continue
        (ITEMS_DIR / f"{iid}.html").write_text(render_detail(it))

    write_index(items)
    print(f"wrote index.html + {len(items)} item page(s) to items/")


if __name__ == "__main__":
    main()
