#!/usr/bin/env python3
"""
build.py — 帝政裙调研项目 HTML 渲染脚本
读取 data/*.json，生成 index.html（卡片墙）+ items/<id>.html（详情页）
幂等：重复执行覆盖输出
"""
import json, os, glob, html as html_mod
from pathlib import Path

BASE = Path(__file__).parent
DATA = BASE / "data"
ITEMS_DIR = BASE / "items"
ITEMS_DIR.mkdir(exist_ok=True)

def load_all():
    items = []
    for f in sorted(DATA.glob("*.json")):
        with open(f, encoding="utf-8") as fh:
            items.append(json.load(fh))
    return items

def e(s):
    """HTML escape"""
    return html_mod.escape(str(s)) if s else ""

def render_index(items):
    # Collect all style_tags for filter buttons
    all_tags = set()
    for it in items:
        for t in it.get("style_tags", []):
            all_tags.add(t)
    
    cards_html = []
    for it in items:
        item_id = it["id"]
        name = e(it["name"])
        brand = e(it["brand"])
        price_op = it.get("price", {}).get("op")
        price_str = f"¥{price_op}" if price_op else "价格待确认"
        sales = it.get("shops", {}).get("taobao", {}).get("sales", "")
        tags = it.get("style_tags", [])
        tags_html = " ".join(f'<span class="tag">{e(t)}</span>' for t in tags[:5])
        keywords = it.get("synthesis", {}).get("keywords", [])
        kw_html = " · ".join(e(k) for k in keywords[:4])
        verdict = e(it.get("synthesis", {}).get("verdict_short", "")[:120])
        data_tags = " ".join(tags)
        
        cards_html.append(f'''
    <a href="items/{item_id}.html" class="card" data-tags="{e(data_tags)}">
      <div class="card-head">
        <div class="brand">{brand}</div>
        <div class="name">{name}</div>
      </div>
      <div class="card-body">
        <div class="price">{price_str}</div>
        <div class="sales">{e(sales)}</div>
        <div class="tags">{tags_html}</div>
        <div class="keywords">{kw_html}</div>
        <div class="verdict">{verdict}…</div>
      </div>
    </a>''')
    
    filter_btns = ['<button class="filter-btn active" data-tag="all">全部</button>']
    for tag in sorted(all_tags):
        filter_btns.append(f'<button class="filter-btn" data-tag="{e(tag)}">{e(tag)}</button>')
    
    index_html = f'''<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>Lolita 款式调研 — 卡片墙</title>
<style>
:root {{ --bg: #f8f6f3; --card-bg: #fff; --text: #2c2c2c; --sub: #888; --accent: #b8860b; --tag-bg: #f0ebe3; }}
* {{ margin:0; padding:0; box-sizing:border-box; }}
body {{ font-family: -apple-system, "PingFang SC", "Microsoft YaHei", sans-serif; background:var(--bg); color:var(--text); padding:24px; }}
h1 {{ font-size:1.6rem; margin-bottom:8px; }}
.subtitle {{ color:var(--sub); margin-bottom:20px; font-size:0.9rem; }}
.filters {{ display:flex; flex-wrap:wrap; gap:8px; margin-bottom:24px; }}
.filter-btn {{ padding:6px 14px; border:1px solid #ddd; border-radius:20px; background:#fff; cursor:pointer; font-size:0.85rem; transition:all 0.2s; }}
.filter-btn.active {{ background:var(--accent); color:#fff; border-color:var(--accent); }}
.grid {{ display:grid; grid-template-columns:repeat(auto-fill, minmax(320px, 1fr)); gap:20px; }}
.card {{ display:block; background:var(--card-bg); border-radius:12px; padding:20px; text-decoration:none; color:inherit; box-shadow:0 2px 8px rgba(0,0,0,0.06); transition:transform 0.2s, box-shadow 0.2s; }}
.card:hover {{ transform:translateY(-3px); box-shadow:0 6px 20px rgba(0,0,0,0.1); }}
.card.hidden {{ display:none; }}
.brand {{ font-size:0.8rem; color:var(--sub); text-transform:uppercase; letter-spacing:0.5px; }}
.name {{ font-size:1.25rem; font-weight:600; margin:4px 0 12px; }}
.price {{ font-size:1.1rem; color:var(--accent); font-weight:600; }}
.sales {{ font-size:0.85rem; color:var(--sub); margin-top:2px; }}
.tags {{ margin-top:10px; display:flex; flex-wrap:wrap; gap:6px; }}
.tag {{ font-size:0.75rem; background:var(--tag-bg); padding:3px 10px; border-radius:12px; }}
.keywords {{ font-size:0.8rem; color:var(--sub); margin-top:10px; }}
.verdict {{ font-size:0.82rem; color:#555; margin-top:10px; line-height:1.5; }}
@media (max-width:600px) {{ body {{ padding:12px; }} .grid {{ grid-template-columns:1fr; }} }}
</style>
</head>
<body>
<h1>Lolita 款式调研</h1>
<p class="subtitle">共 {len(items)} 款 · 数据来源：XHS / 微博 / 淘宝交叉验证</p>
<div class="filters">
{"".join(filter_btns)}
</div>
<div class="grid">
{"".join(cards_html)}
</div>
<script>
document.querySelectorAll('.filter-btn').forEach(btn => {{
  btn.addEventListener('click', () => {{
    document.querySelectorAll('.filter-btn').forEach(b => b.classList.remove('active'));
    btn.classList.add('active');
    const tag = btn.dataset.tag;
    document.querySelectorAll('.card').forEach(card => {{
      if (tag === 'all' || card.dataset.tags.includes(tag)) {{
        card.classList.remove('hidden');
      }} else {{
        card.classList.add('hidden');
      }}
    }});
  }});
}});
</script>
</body>
</html>'''
    return index_html

def render_detail(it):
    item_id = it["id"]
    name = e(it["name"])
    brand = e(it["brand"])
    summary = e(it.get("style_summary", ""))
    
    # Price
    p = it.get("price", {})
    price_lines = []
    if p.get("op"): price_lines.append(f"单裙 OP: ¥{p['op']}")
    if p.get("full_set"): price_lines.append(f"套装: ¥{p['full_set']}")
    if p.get("note"): price_lines.append(e(p["note"]))
    
    # Release
    r = it.get("release", {})
    release_html = f'<p><strong>发售方式:</strong> {e(r.get("type",""))}</p>'
    if r.get("date_range"): release_html += f'<p><strong>时间:</strong> {e(r["date_range"])}</p>'
    if r.get("note"): release_html += f'<p class="note">{e(r["note"])}</p>'
    
    # Colors
    colors = it.get("colors", [])
    colors_html = " ".join(f'<span class="color-chip">{e(c)}</span>' for c in colors)
    
    # Tags
    tags = it.get("style_tags", [])
    tags_html = " ".join(f'<span class="tag">{e(t)}</span>' for t in tags)
    
    # Shops
    shops = it.get("shops", {})
    tb = shops.get("taobao", {})
    wb = shops.get("weibo", {})
    xhs = shops.get("xiaohongshu", {})
    
    shop_html = '<div class="section"><h2>店铺信息</h2>'
    if tb.get("shop_name"):
        shop_html += f'<h3>淘宝</h3><p>店铺: {e(tb["shop_name"])} · {e(tb.get("location",""))}</p>'
        if tb.get("sales"): shop_html += f'<p>销量: {e(tb["sales"])}</p>'
        if tb.get("sales_note"): shop_html += f'<p class="note">{e(tb["sales_note"])}</p>'
    if wb.get("official_account"):
        shop_html += f'<h3>微博</h3><p>官号: {e(wb["official_account"])}</p>'
        if wb.get("note"): shop_html += f'<p class="note">{e(wb["note"])}</p>'
    if xhs.get("note"):
        shop_html += f'<h3>小红书</h3><p class="note">{e(xhs["note"])}</p>'
    shop_html += '</div>'
    
    # Hot posts
    hp = it.get("hot_posts", {}).get("xiaohongshu", [])
    posts_html = ""
    if hp:
        posts_html = '<div class="section"><h2>热门帖子 (XHS)</h2>'
        for post in hp:
            posts_html += f'''
            <div class="post-card">
              <div class="post-meta">
                <span class="post-likes">❤ {e(post.get("likes",""))}</span>
                <span class="post-type">{e(post.get("type",""))}</span>
              </div>
              <div class="post-title">{e(post.get("title",""))}</div>
              <div class="post-summary">{e(post.get("summary",""))}</div>
            </div>'''
        posts_html += '</div>'
    
    # Synthesis
    syn = it.get("synthesis", {})
    pos = syn.get("highlights_positive", [])
    neg = syn.get("highlights_negative", [])
    verdict = e(syn.get("verdict_short", ""))
    
    syn_html = '<div class="section"><h2>综合分析</h2>'
    if pos:
        syn_html += '<h3 class="positive">✓ 正面</h3><ul class="pos-list">'
        for p_item in pos:
            syn_html += f'<li>{e(p_item)}</li>'
        syn_html += '</ul>'
    if neg:
        syn_html += '<h3 class="negative">✗ 负面</h3><ul class="neg-list">'
        for n_item in neg:
            syn_html += f'<li>{e(n_item)}</li>'
        syn_html += '</ul>'
    if verdict:
        syn_html += f'<div class="verdict-box">{verdict}</div>'
    syn_html += '</div>'
    
    # Design inspiration
    di = it.get("design_inspiration", {})
    di_html = ""
    if di:
        di_html = '<div class="section"><h2>设计灵感</h2>'
        if di.get("theme"): di_html += f'<p><strong>主题:</strong> {e(di["theme"])}</p>'
        if di.get("official_quote"): di_html += f'<blockquote>{e(di["official_quote"])}</blockquote>'
        elements = di.get("elements", [])
        if elements:
            di_html += '<div class="elements">'
            for el in elements:
                di_html += f'''<div class="element">
                  <strong>{e(el.get("name",""))}</strong>
                  <p class="lineage">{e(el.get("source_lineage",""))}</p>
                  <p>{e(el.get("purpose",""))}</p>
                </div>'''
            di_html += '</div>'
        if di.get("design_thinking"): di_html += f'<p class="note">{e(di["design_thinking"])}</p>'
        di_html += '</div>'
    
    detail_html = f'''<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>{name} — {brand}</title>
<style>
:root {{ --bg:#f8f6f3; --card-bg:#fff; --text:#2c2c2c; --sub:#888; --accent:#b8860b; --tag-bg:#f0ebe3; --pos:#2e7d32; --neg:#c62828; }}
* {{ margin:0; padding:0; box-sizing:border-box; }}
body {{ font-family:-apple-system,"PingFang SC","Microsoft YaHei",sans-serif; background:var(--bg); color:var(--text); padding:24px; max-width:800px; margin:0 auto; }}
a {{ color:var(--accent); }}
.back {{ display:inline-block; margin-bottom:20px; font-size:0.9rem; }}
h1 {{ font-size:1.8rem; margin-bottom:4px; }}
.brand-line {{ font-size:0.9rem; color:var(--sub); margin-bottom:16px; text-transform:uppercase; letter-spacing:0.5px; }}
.summary {{ font-size:1rem; line-height:1.6; margin-bottom:20px; color:#444; }}
.section {{ background:var(--card-bg); border-radius:12px; padding:20px; margin-bottom:16px; box-shadow:0 1px 4px rgba(0,0,0,0.05); }}
.section h2 {{ font-size:1.15rem; margin-bottom:12px; color:var(--accent); }}
.section h3 {{ font-size:0.95rem; margin:12px 0 6px; }}
.note {{ font-size:0.85rem; color:var(--sub); line-height:1.5; margin-top:6px; }}
.tag {{ display:inline-block; font-size:0.75rem; background:var(--tag-bg); padding:3px 10px; border-radius:12px; margin:2px; }}
.color-chip {{ display:inline-block; padding:4px 12px; border-radius:16px; background:#eee; font-size:0.85rem; margin:3px; }}
.post-card {{ border-left:3px solid var(--accent); padding:10px 14px; margin-bottom:12px; background:#faf8f5; border-radius:0 8px 8px 0; }}
.post-meta {{ font-size:0.8rem; color:var(--sub); margin-bottom:4px; }}
.post-likes {{ color:var(--neg); font-weight:600; margin-right:12px; }}
.post-type {{ background:var(--tag-bg); padding:2px 8px; border-radius:8px; }}
.post-title {{ font-weight:600; margin-bottom:4px; }}
.post-summary {{ font-size:0.88rem; line-height:1.5; color:#555; }}
.positive {{ color:var(--pos); }}
.negative {{ color:var(--neg); }}
.pos-list li,.neg-list li {{ font-size:0.9rem; line-height:1.6; margin:6px 0 6px 20px; }}
.pos-list li {{ color:#333; }}
.neg-list li {{ color:#333; }}
.verdict-box {{ margin-top:16px; padding:16px; background:#fdf6e3; border-radius:8px; font-size:0.92rem; line-height:1.7; }}
.elements {{ display:flex; flex-direction:column; gap:10px; margin-top:10px; }}
.element {{ background:#faf8f5; padding:12px; border-radius:8px; }}
.element .lineage {{ font-size:0.83rem; color:var(--sub); margin-top:4px; }}
blockquote {{ border-left:3px solid var(--accent); padding:8px 14px; margin:10px 0; font-style:italic; color:#555; }}
@media (max-width:600px) {{ body {{ padding:12px; }} }}
</style>
</head>
<body>
<a href="../index.html" class="back">← 返回卡片墙</a>
<h1>{name}</h1>
<div class="brand-line">{brand}</div>
<div class="tags">{tags_html}</div>
<p class="summary">{summary}</p>

<div class="section">
  <h2>价格</h2>
  {"<br>".join(f"<p>{line}</p>" for line in price_lines)}
</div>

<div class="section">
  <h2>发售信息</h2>
  {release_html}
</div>

<div class="section">
  <h2>颜色</h2>
  {colors_html}
</div>

{shop_html}
{posts_html}
{syn_html}
{di_html}

<p class="note" style="margin-top:24px; text-align:center;">
  验证时间: {e(it.get("verified_at",""))} · {e(it.get("verified_by",""))}
</p>
</body>
</html>'''
    return detail_html

def main():
    items = load_all()
    if not items:
        print("No JSON files found in data/")
        return
    
    # Write index.html
    idx = render_index(items)
    (BASE / "index.html").write_text(idx, encoding="utf-8")
    print(f"index.html: {len(items)} cards")
    
    # Write items/<id>.html
    for it in items:
        detail = render_detail(it)
        out = ITEMS_DIR / f'{it["id"]}.html'
        out.write_text(detail, encoding="utf-8")
        print(f"  items/{it['id']}.html")
    
    print("Done.")

if __name__ == "__main__":
    main()
