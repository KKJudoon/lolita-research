#!/usr/bin/env python3
"""Build 军lo + 王子军lo 销量排行榜 (HTML page)."""
import json, re, os, html, datetime, pathlib

INPUTS = [
    "/tmp/taobao_junlo_search.json",
    "/tmp/taobao_ouji_search.json",
    "/tmp/taobao_junlolita_search.json",
]

# 已调研 11 款的 item_id → 站内 detail 链接
RESEARCHED_MAP_FILE = None  # build dynamically below

# ----- 1. 合并去重 -----
all_items = {}
for f in INPUTS:
    if not os.path.exists(f): continue
    data = json.load(open(f, encoding='utf-8'))
    for d in data:
        iid = d.get("item_id")
        if not iid: continue
        if iid not in all_items:
            all_items[iid] = d

# ----- 2. 销量解析 -----
def parse_sales(s):
    """'4万+人付款' → 40000; '1000+人付款' → 1000; '95人付款' → 95; '500+人看过' → -1 (no purchase)"""
    if not s: return 0
    s = str(s)
    if '看过' in s and '付款' not in s:
        return -1  # 浏览量不计入
    m = re.search(r'(\d+(?:\.\d+)?)\s*万', s)
    if m:
        return int(float(m.group(1)) * 10000)
    m = re.search(r'(\d+)\s*\+', s)
    if m:
        return int(m.group(1))
    m = re.search(r'(\d+)', s)
    if m:
        return int(m.group(1))
    return 0

# ----- 3. 风格 tag 推断 -----
def infer_tags(title):
    title_l = title.lower() if title else ''
    tags = []
    if any(k in title for k in ['军lo','军lolita','军装','军绿','军礼','军lolita']):
        tags.append('军lo')
    if any(k in title for k in ['王子','基佬','正太','少年','骑士']):
        tags.append('王子')
    if any(k in title for k in ['哥特','暗黑','蝙蝠','十字','废土','黑暗']):
        tags.append('哥特')
    if any(k in title for k in ['汉','中华','旗袍','仙鹤','牡丹','汉洋']):
        tags.append('中华')
    if any(k in title for k in ['现货','7天无理由']):
        tags.append('现货')
    if any(k in title for k in ['定金','意向金','5r抵','1r抵']):
        tags.append('定金/意向金')
    if any(k in title for k in ['cos','cosplay','二次元','虚拟']):
        tags.append('cos跨圈')
    if any(k in title for k in ['学院','制服']):
        tags.append('学院风')
    if any(k in title for k in ['甜','糖果','马卡龙','童话']):
        tags.append('甜系')
    if any(k in title for k in ['圣职','神父','修女','教堂','祷告']):
        tags.append('圣职/神职')
    if any(k in title for k in ['暴君','加冕','荣耀']):
        tags.append('viral 借势')
    return tags or ['其他']

# ----- 4. 站内款映射 -----
RESEARCHED = {
    '1037713255465': ('items/yingluofu_zhongyan_2.0.html', '终焉圣骸 2.0（已调研）'),
    '968203147040':  ('items/yingluofu_gulong.html', '骨龙（已调研）'),
    '838292216852':  ('items/yourhighness_qishijingshen.html', '骑士精神（已调研）'),
    '1032462582002': ('items/yingyue_longyao.html', '龙曜（已调研）'),
    '868385609180':  ('items/weizhixingchen_jichengren.html', '继承人 红款（已调研）'),
    '868666300494':  ('items/weizhixingchen_jichengren.html', '神权使者（继承人姐妹款，参见已调研）'),
    '917187493014':  ('items/dierchengbao_tangguopu.html', '糖果铺老链接（已调研）'),
    '1030474963498': ('items/dierchengbao_tangguopu.html', '糖果铺新链接（已调研）'),
    '869541734831':  ('items/shaonyongdao_daogaozhe.html', '祷告者（已调研）'),
    '1014052144471': ('items/alicegirl_poxiaozhe.html', '破晓者 斗篷外套（已调研）'),
    '1012446126033': ('items/alicegirl_poxiaozhe.html', '破晓者 JSK（已调研）'),
    '1011766487968': ('items/alicegirl_poxiaozhe.html', '破晓者 配件（已调研）'),
    '857920989550':  ('items/pc_hongyuhei_4.0.html', '红与黑 4.0（已调研）'),
}

# ----- 5. 构建 ranked rows -----
rows = []
for iid, d in all_items.items():
    sales_raw = d.get('sales', '')
    sales = parse_sales(sales_raw)
    if sales <= 0: continue  # 剔除『看过』『0 付款』
    title = d.get('title', '')
    shop = d.get('shop', '')
    price = d.get('price', '')
    location = d.get('location', '')
    url = d.get('url', f'https://item.taobao.com/item.htm?id={iid}')
    tags = infer_tags(title)

    if any(k in title for k in ['cos','cosplay','二次元','虚拟','机箱','键盘','鼠标','手机壳']):
        if 'lolita' not in title.lower() and '军lo' not in title:
            continue  # 剔除明显不相关

    researched = iid in RESEARCHED
    research_link = RESEARCHED.get(iid)

    rows.append({
        'iid': iid,
        'sales': sales,
        'sales_raw': sales_raw,
        'title': title,
        'shop': shop,
        'price': price,
        'location': location,
        'url': url,
        'tags': tags,
        'researched': researched,
        'research_link': research_link,
    })

rows.sort(key=lambda r: (-r['sales'], r['title']))

# ----- 6. 渲染 HTML -----
esc = html.escape
now = datetime.datetime.now().strftime('%Y-%m-%d %H:%M')

def render_row(r, rank):
    tags_html = ''.join(f'<span class="tag tag-{t}">{esc(t)}</span>' for t in r['tags'])
    if r['researched']:
        link, label = r['research_link']
        title_link = f'<a href="../{link}" class="researched-link">{esc(r["title"][:55])}</a> <span class="researched-mark">✓ 已调研</span>'
    else:
        title_link = f'<a href="{esc(r["url"])}" target="_blank" rel="noopener">{esc(r["title"][:55])}</a>'
    sales_class = 'sales-tier-' + (
        'top' if r['sales'] >= 10000 else
        'high' if r['sales'] >= 1000 else
        'mid' if r['sales'] >= 300 else
        'low'
    )
    rank_class = 'rank-1-3' if rank <= 3 else ('rank-4-10' if rank <= 10 else 'rank-rest')
    return f'''<tr>
      <td class="rank {rank_class}">{rank}</td>
      <td class="sales {sales_class}">{esc(r["sales_raw"])}</td>
      <td class="price">{esc(r["price"])}</td>
      <td class="shop">{esc(r["shop"])}</td>
      <td class="title">{title_link}</td>
      <td class="tags">{tags_html}</td>
    </tr>'''

# 简单统计
top_brands = {}
top_tags = {}
for r in rows:
    top_brands[r['shop']] = top_brands.get(r['shop'], 0) + r['sales']
    for t in r['tags']:
        top_tags[t] = top_tags.get(t, 0) + r['sales']

top_brands_sorted = sorted(top_brands.items(), key=lambda x: -x[1])[:10]
top_tags_sorted = sorted(top_tags.items(), key=lambda x: -x[1])

def fmt_num(n):
    if n >= 10000: return f'{n/10000:.1f}万'
    if n >= 1000: return f'{n/1000:.1f}k'
    return str(n)

brands_html = '\n'.join(f'<tr><td>{i+1}</td><td>{esc(b[0])}</td><td>{fmt_num(b[1])}+</td></tr>' for i, b in enumerate(top_brands_sorted))
tags_html = '\n'.join(f'<tr><td>{esc(t)}</td><td>{fmt_num(s)}+</td></tr>' for t, s in top_tags_sorted)

rows_html = '\n'.join(render_row(r, i+1) for i, r in enumerate(rows))

CSS = '''
* { box-sizing: border-box; }
body {
  font-family: -apple-system, BlinkMacSystemFont, 'PingFang SC', 'Microsoft YaHei', sans-serif;
  background: #faf7ed; color: #2c2418; line-height: 1.6;
  max-width: 1200px; margin: 0 auto; padding: 24px;
  font-size: 14px;
}
h1 { font-size: 26px; color: #2c2418; margin: 16px 0 8px; padding-bottom: 12px; border-bottom: 2px solid #c5a572; }
h2 { font-size: 18px; color: #5a4a2a; margin: 24px 0 8px; }
.meta { color: #888; font-size: 12px; margin-bottom: 16px; }
.back { font-size: 13px; display: inline-block; margin-bottom: 8px; color: #6a5a30; text-decoration: none; }
.back:hover { color: #c5a572; text-decoration: underline; }
.summary {
  display: grid; grid-template-columns: 1fr 1fr; gap: 16px; margin: 16px 0 24px;
}
.summary-block {
  background: white; padding: 14px 18px; border-radius: 8px;
  box-shadow: 0 1px 6px rgba(0,0,0,0.05);
}
.summary-block h3 { font-size: 14px; color: #5a4a2a; margin: 0 0 8px; }
.summary-block table { width: 100%; font-size: 13px; }
.summary-block td { padding: 4px 8px; border-top: 1px solid #f0e8d0; }
table.main {
  width: 100%; border-collapse: collapse; margin-top: 12px;
  background: white; border-radius: 8px; overflow: hidden;
  box-shadow: 0 2px 12px rgba(0,0,0,0.05); font-size: 13px;
}
.main th { background: #2c2418; color: #efe9d9; padding: 10px 12px; text-align: left; position: sticky; top: 0; z-index: 5; }
.main td { padding: 10px 12px; border-top: 1px solid #f0e8d0; vertical-align: top; }
.main tr:hover td { background: #fbf7e8; }
.rank { font-weight: 700; width: 50px; text-align: center; }
.rank-1-3 { color: #c5a572; font-size: 17px; }
.rank-4-10 { color: #6a5a30; font-size: 15px; }
.rank-rest { color: #888; }
.sales { white-space: nowrap; font-weight: 600; }
.sales-tier-top { color: #b00020; }
.sales-tier-high { color: #c5a572; }
.sales-tier-mid { color: #5a4a2a; }
.sales-tier-low { color: #888; }
.price { color: #444; white-space: nowrap; }
.shop { color: #5a4a2a; max-width: 180px; word-break: break-word; }
.title { max-width: 460px; }
.title a { color: #2c2418; text-decoration: underline; text-decoration-color: #c5a572; }
.title a:hover { color: #c5a572; }
.researched-link { font-weight: 600; }
.researched-mark { background: #d4f4d4; color: #2c7a2c; padding: 1px 6px; border-radius: 4px; font-size: 11px; margin-left: 4px; }
.tags { font-size: 11px; }
.tag { background: #efe9d9; color: #5a4a2a; padding: 1px 6px; border-radius: 8px; margin-right: 3px; display: inline-block; margin-bottom: 2px; }
.tag-军lo { background: #4a3020; color: white; }
.tag-王子 { background: #2c4a3a; color: white; }
.tag-哥特 { background: #1a1a2a; color: #c5a572; }
.tag-中华 { background: #aa3030; color: white; }
.tag-甜系 { background: #f4c5d9; color: #6a3a4a; }
.tag-学院风 { background: #506a8a; color: white; }
.tag-圣职/神职 { background: #6a5a8a; color: white; }
.tag-viral\\ 借势 { background: #c5a572; color: #2c2418; }
.tag-cos跨圈 { background: #5a8aa5; color: white; }
.tag-现货 { background: #d4f4d4; color: #2c7a2c; }
.legend { font-size: 12px; color: #777; margin: 12px 0; }
.legend-tier { display: inline-block; margin-right: 16px; }
@media (max-width: 720px) {
  body { padding: 12px; font-size: 13px; }
  .summary { grid-template-columns: 1fr; }
  .main { font-size: 11px; }
  .main th, .main td { padding: 6px 8px; }
  .title { max-width: 200px; }
  .title a { font-size: 12px; }
}
'''

doc = f'''<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>军lo + 王子系 销量排行榜（淘宝 snapshot）</title>
<style>{CSS}</style>
</head>
<body>
<a class="back" href="../index.html">← 返回款式调研主页</a> · <a class="back" href="junlo_prince_report.html">📊 进入研究报告</a>
<h1>军lo + 王子系 销量排行榜</h1>
<div class="meta">数据 snapshot {now} · 共 {len(rows)} 个有付款 SKU · 来源：淘宝 search by sale 排序（"军lo" / "王子系 lolita" / "军lolita 套装" 三关键词合并去重）</div>

<div class="legend">
  <span class="legend-tier">销量等级：<span class="sales-tier-top">≥ 1万 顶级</span> · <span class="sales-tier-high">≥ 1000 高位</span> · <span class="sales-tier-mid">≥ 300 中位</span> · <span class="sales-tier-low">< 300 长尾</span></span>
</div>

<h2>头部品牌（按累计销量）</h2>
<div class="summary">
<div class="summary-block">
<h3>Top 10 品牌（按 SKU 累计销量）</h3>
<table>
<tr><th>排名</th><th>品牌</th><th>累计销量</th></tr>
{brands_html}
</table>
</div>
<div class="summary-block">
<h3>风格 tag 销量分布</h3>
<table>
<tr><th>风格</th><th>累计销量</th></tr>
{tags_html}
</table>
</div>
</div>

<h2>完整 SKU 排行榜</h2>
<table class="main">
<thead><tr><th>#</th><th>销量</th><th>价格</th><th>品牌</th><th>款名</th><th>风格 tag</th></tr></thead>
<tbody>
{rows_html}
</tbody>
</table>

<div style="margin-top: 30px; font-size: 12px; color: #777; line-height: 1.7;">
<strong>说明</strong>：
<ul>
  <li>销量数据为淘宝平台显示值（"4万+ / 1000+ / 95人付款"），为方便排序统一解析为数值；"4万+" → 40000，"1000+" → 1000，"500+" → 500。同等级（如多个 1000+）按款名字母序排</li>
  <li>"<span class="researched-mark">✓ 已调研</span>" 标记的款链接到本研究项目内的详细 detail 页（11 款落档）</li>
  <li>未调研款链接到淘宝商品页</li>
  <li>风格 tag 由款名关键词自动推断（"暴君/加冕/荣耀" → viral 借势 / "学院/制服" → 学院风 / "圣职/神父/教堂/祷告" → 圣职 等）</li>
  <li>已剔除明显非 lolita（cos 战术娘 / 机箱 / 键盘等）+ 0 付款 / 仅"X 人看过"无付款数据</li>
</ul>
</div>
</body>
</html>
'''

OUT = "/tmp/junlo_leaderboard.html"
with open(OUT, 'w', encoding='utf-8') as f:
    f.write(doc)
print(f"wrote {OUT} - {len(rows)} ranked SKU, {len(top_brands_sorted)} brands")
