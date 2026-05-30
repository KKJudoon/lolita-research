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
import subprocess

ROOT = pathlib.Path(__file__).resolve().parent
DATA_DIR = ROOT / "data"
ITEMS_DIR = ROOT / "items"
INDEX = ROOT / "index.html"
REPO_URL = "https://github.com/KKJudoon/lolita-research"


def esc(s):
    return html.escape(str(s)) if s is not None else ""


def _version_info():
    try:
        h_short = subprocess.check_output(
            ["git", "rev-parse", "--short", "HEAD"], cwd=ROOT, stderr=subprocess.DEVNULL
        ).decode().strip()
        h_full = subprocess.check_output(
            ["git", "rev-parse", "HEAD"], cwd=ROOT, stderr=subprocess.DEVNULL
        ).decode().strip()
        c_time = subprocess.check_output(
            ["git", "log", "-1", "--format=%ci", "HEAD"], cwd=ROOT, stderr=subprocess.DEVNULL
        ).decode().strip()
    except Exception:
        h_short, h_full, c_time = "dev", "", ""
    b_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
    return h_short, h_full, c_time, b_time


def _version_footer_html():
    hs, hf, ct, bt = _version_info()
    link = f'<a href="{REPO_URL}/commit/{hf}" target="_blank" rel="noopener" style="color:#555;text-decoration:none;border-bottom:1px dotted #999;">v {hs}</a>' if hf else f'<span>v {hs}</span>'
    ct_short = ct.split(" ")[0] if ct else ""
    return (
        '<div style="position:fixed;bottom:8px;right:12px;'
        'font:11px/1.4 -apple-system,Menlo,monospace;color:#666;'
        'background:rgba(255,255,255,0.9);padding:4px 10px;'
        'border:1px solid #ddd;border-radius:4px;z-index:9999;'
        'box-shadow:0 1px 3px rgba(0,0,0,0.05);">'
        f'{link}'
        f'<span style="color:#999;"> · commit {ct_short} · build {bt}</span>'
        '</div>'
    )


def _inject_version(doc):
    footer = _version_footer_html()
    return doc.replace("</body>", footer + "\n</body>", 1)


def _parse_sales_value(s):
    """Parse taobao sales string to integer. '4万+人付款' → 40000; '100+人付款' → 100; '95人付款' → 95."""
    if not s:
        return 0
    s = str(s)
    if '看过' in s and '付款' not in s:
        return 0
    m = re.search(r'(\d+(?:\.\d+)?)\s*万', s)
    if m:
        return int(float(m.group(1)) * 10000)
    m = re.search(r'(\d+)\s*\+', s)
    if m:
        return int(m.group(1))
    if '千人加购' in s:
        return 1000
    if '百人加购' in s:
        return 100
    m = re.search(r'(\d+)', s)
    if m:
        return int(m.group(1))
    return 0


def _parse_research_ts(date_str):
    """Parse verified_at ISO date to ms timestamp for client-side sort. Fallback 0."""
    if not date_str:
        return 0
    try:
        return int(datetime.datetime.strptime(date_str, "%Y-%m-%d").timestamp() * 1000)
    except Exception:
        return 0


def _extract_status(item):
    """Return (label, priority). priority 高的在前；加购未上架=0 永远在最后。"""
    sales = (item.get("shops", {}).get("taobao", {}) or {}).get("sales", "") or ""
    sales_v = _parse_sales_value(sales)
    rel = item.get("release", {}) or {}
    rel_type = rel.get("type") or ""
    rel_note = rel.get("note") or ""
    blob = rel_type + rel_note

    if "现货" in blob:
        return ("现货", 5)
    if sales_v >= 95 and "千人加购" not in sales:
        return ("已开团", 4)
    if "再贩" in blob or "再片反" in blob or "重团" in blob:
        return ("再贩团", 3)
    if "千人加购" in sales or sales_v == 1000:
        return ("加购中", 2)
    if not sales or sales == "—" or sales_v == 0:
        return ("加购未上架", 0)
    return ("调研中", 1)


def _extract_release_dates(item):
    """Return (publish_short, tuán_short) — 简化的发布 / 一团时间字符串。
    严格只接受 YYYY-MM 格式，非日期返回空（避免截『未明（多平台搬』之类的乱码）。"""
    rel = item.get("release", {}) or {}
    posters_first = rel.get("poster_first_seen") or ""
    date_range = rel.get("date_range") or ""
    pm = re.match(r'(\d{4}-\d{2})', posters_first)
    publish_short = pm.group(1) if pm else ""
    # fallback: 从 date_range 找日期作为 publish_short
    if not publish_short:
        m_dr = re.search(r'(\d{4}-\d{2})', date_range)
        if m_dr:
            publish_short = m_dr.group(1)
    tuan_short = ""
    rng = re.search(r'(\d{4}-\d{1,2}-\d{1,2})\s*~\s*(\d{4}-\d{1,2}-\d{1,2})', date_range)
    if rng:
        tuan_short = rng.group(1)[:10]
    else:
        m2 = re.search(r'(\d{4}-\d{1,2}-\d{1,2})', date_range)
        if m2:
            tuan_short = m2.group(1)[:10]
    return publish_short, tuan_short


def _shorten_name(name):
    """去括号副标题，只留主名"""
    if not name:
        return ""
    m = re.match(r'^([^（(]+)', name)
    return (m.group(1) if m else name).strip()


def _render_name_cell(item, detail_url):
    """名称单元格：精简款名 + 品牌 + 完整名 ⓘ button → modal"""
    full = item.get("name", "")
    short = _shorten_name(full)
    brand = item.get("brand", "")
    designer = item.get("designer", "")
    illustrator = item.get("illustrator", "")
    designer_note = item.get("designer_note") or item.get("illustrator_note") or ""
    style_summary = item.get("style_summary", "")
    detail = {
        "name": full, "brand": brand,
        "designer": designer, "illustrator": illustrator,
        "designer_note": designer_note, "style_summary": style_summary,
    }
    detail = {k: v for k, v in detail.items() if v}
    has_extra = full != short or designer or illustrator or designer_note or style_summary
    detail_json = html.escape(json.dumps(detail, ensure_ascii=False))
    info_btn = f'<button class="name-info-btn" data-name-detail="{detail_json}" title="完整名 / 设计师 / 风格说明">ⓘ</button>' if has_extra else ''
    return f'''<a class="bare" href="{esc(detail_url)}"><div class="title">{esc(short)}</div><div class="brand">{esc(brand)}</div></a>{info_btn}'''


def _render_price_btn(price, name):
    """价格按钮（点击展开 modal 显示完整 price 字段）"""
    short = _extract_main_prices(price or {})
    if not price:
        price = {}
    detail = {
        "name": name,
        "short": short,
        "op": price.get("op"),
        "full_set": price.get("full_set"),
        "currency": price.get("currency", "CNY"),
        "deposit_link_intent": price.get("deposit_link_intent"),
        "list_price_at_research": price.get("list_price_at_research"),
        "op_note": price.get("op_note"),
        "full_set_note": price.get("full_set_note"),
        "list_price_note": price.get("list_price_note"),
        "list_price_priority_note": price.get("list_price_priority_note"),
        "full_set_estimate": price.get("full_set_estimate"),
        "full_set_estimate_v2": price.get("full_set_estimate_v2"),
        "full_set_estimate_v3": price.get("full_set_estimate_v3"),
        "full_set_history": price.get("full_set_history"),
        "full_set_status": price.get("full_set_status"),
        "skus_known": price.get("skus_known"),
        "price_breakdown": price.get("price_breakdown"),
        "note": price.get("note"),
    }
    detail = {k: v for k, v in detail.items() if v not in (None, "", [], {})}
    detail_json = html.escape(json.dumps(detail, ensure_ascii=False))
    return f'<button class="price-btn" data-price-detail="{detail_json}" title="{esc(short)}"><span class="lbl">{esc(short)}</span><span class="pop-info">ⓘ</span></button>'


def _render_release_btn(release, name):
    """时间按钮（点击展开 modal 显示完整 release 字段）"""
    rel = release or {}
    publish_short, tuan_short = _extract_release_dates({"release": rel})
    parts = []
    if publish_short:
        parts.append(f"上新 {publish_short}")
    if tuan_short:
        parts.append(f"团 {tuan_short[5:]}")
    if parts:
        short = " · ".join(parts)
    else:
        # 没拿到日期：给个 status 提示
        rt = (rel.get("type") or "").strip()
        if "现货" in rt:
            short = "现货"
        elif "再贩" in rt or "重团" in rt:
            short = "再贩"
        elif "厂原" in rt or "持续" in rt:
            short = "持续供货"
        elif rt:
            short = "见详情"
        else:
            short = "—"
    detail = {
        "name": name,
        "short": short,
        "type": rel.get("type"),
        "date_range": rel.get("date_range"),
        "poster_first_seen": rel.get("poster_first_seen"),
        "note": rel.get("note"),
    }
    detail = {k: v for k, v in detail.items() if v not in (None, "", [], {})}
    detail_json = html.escape(json.dumps(detail, ensure_ascii=False))
    return f'<button class="release-btn" data-release-detail="{detail_json}" title="{esc(short)}"><span class="lbl">{esc(short)}</span><span class="pop-info">ⓘ</span></button>'


def _extract_main_prices(price):
    """整套 + OP + JSK 主价（不展示定金/配饰）；fallback 到 estimate / breakdown / list."""
    if not price:
        return "—"
    parts = []
    fs = price.get("full_set") or price.get("set_3pc_total")
    if fs:
        parts.append(f'整套 ¥{fs}')
    if price.get("op"):
        parts.append(f'OP ¥{price["op"]}')
    if price.get("jsk"):
        parts.append(f'JSK ¥{price["jsk"]}')
    if parts:
        return " · ".join(parts)
    # fallback: SKU 单件 estimate（PC 红黑 / 永无岛 等）
    shirt = price.get("shirt_estimate")
    vest = price.get("vest_estimate")
    if shirt or vest:
        sub = []
        if shirt: sub.append(f'衬衫 ¥{shirt}')
        if vest: sub.append(f'马甲 ¥{vest}')
        return " · ".join(sub)
    # fallback: full_set_estimate (短数字才显示)
    fse = price.get("full_set_estimate") or price.get("full_set_estimate_v2") or price.get("full_set_estimate_v3")
    if fse:
        s = str(fse)
        if len(s) > 24:
            return '整套估算 见详情'
        return s if s.startswith('¥') or s.startswith('约') or s.startswith('整套') else f'整套 {s}'
    # fallback: price_breakdown 取『非意向金 · 大全套』优先
    pb = price.get("price_breakdown")
    if pb and isinstance(pb, dict):
        # 优先非意向金 + 大全套 / 全套 / 整套
        for keyword in ['非意向金 · 大全套', '非意向金 · 小全套', '大全套', '小全套', '基础套', '整套', '全套']:
            for k, v in pb.items():
                if keyword in k:
                    label = "整套" if "全套" in k or "整套" in k else k.split("·")[-1].strip() if "·" in k else "套"
                    return f'{label} {v}'
    # fallback: list_price_at_research（剔除意向金 / 定金 抵扣 / 长 note 字符串）
    lpr = price.get("list_price_at_research") or ""
    if lpr and "意向金" not in lpr and "定金" not in lpr:
        # 长字符串（>24 字 或 含 markdown / note 标记）→ 简化
        if len(lpr) > 24 or "**" in lpr or "已搜" in lpr or "圈内" in lpr or "未明文" in lpr:
            return "未公开 见详情"
        return lpr
    return "未公开"


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
# 综合畅销度标签 → 排序权重（高的在前）
POPULARITY_RANK = {
    "现象级爆款": 100,
    "帝政走量冠军": 98,
    "头部 IP": 90,
    "帝政品类爆款": 88,
    "帝政国民爆款": 87,
    "工艺型小众": 80,
    "帝政天花板绝版款": 78,
    "帝政经典绝版": 77,
    "4 月军lo 爆款": 75,
    "看家款多团迭代": 72,
    "暗黑哥特主流": 70,
    "中华细分主流": 70,
    "甜系王子主流": 70,
    "话题中心争议款": 68,
    "品牌力限定款": 67,
    "现货畅销": 65,
    "白菜入门走量王": 63,
    "照片种草翻车款": 62,
    "白菜畅销": 60,
    "小众精品高保值": 58,
    "viral 借势新品": 55,
    "帝政稳健中间款": 53,
    "微胖友好口碑款": 52,
    "日常实用入门款": 51,
    "白菜单品畅销": 50,
    "设计师诚意小众": 48,
    "种草陷阱型": 45,
    "仿冒受害腰部": 40,
    "腰部": 40,
    "低调入门补充款": 38,
    "丝绒小众款": 35,
    "考古标本": 33,
    "反面教材": 30,
    "高端押注未验证": 25,
    "调研中": 20,
    "加购未上架": 0,
}


def render_summary_row(item):
    iid = item.get("id", "")
    name = esc(item["name"])
    brand = esc(item.get("brand", ""))

    taobao = item.get("shops", {}).get("taobao", {}) or {}
    sales_raw = taobao.get("sales", "") or ""
    sales_v = _parse_sales_value(sales_raw)
    research_ts = _parse_research_ts(item.get("verified_at"))

    status_label, status_priority = _extract_status(item)
    publish_short, tuan_short = _extract_release_dates(item)
    price_str = _extract_main_prices(item.get("price", {}) or {})

    pop = item.get("popularity", {}) or {}
    composite = pop.get("composite_label", "调研中")
    pop_rank = POPULARITY_RANK.get(composite, 20)
    evidence = pop.get("evidence", []) or []
    scale_t = pop.get("scale_tier", "—")
    buzz_t = pop.get("buzz_tier", "—")
    auth_t = pop.get("authority_tier", "—")
    resale_t = pop.get("resale_tier", "—")
    evidence_json = html.escape(json.dumps({
        "name": item.get("name", ""),
        "label": composite,
        "scale": scale_t,
        "buzz": buzz_t,
        "authority": auth_t,
        "resale": resale_t,
        "evidence": evidence,
    }, ensure_ascii=False))

    posters = item.get("posters", []) or []
    thumb = posters[0] if posters else ""
    thumb_html = f'<img src="{esc(thumb)}" loading="lazy" alt="" />' if thumb else '<div class="no-thumb">—</div>'

    style_tags = item.get("style_tags", []) or []
    canonical = []
    for s in CANONICAL_STYLES:
        if any(s in t for t in style_tags):
            canonical.append(s)
    if not canonical and style_tags:
        canonical = [style_tags[0]]
    style_chips = "".join(f'<span class="chip">{esc(s)}</span>' for s in canonical[:3])

    detail_url = f"items/{iid}.html"

    pop_class = "pop-" + (
        "top" if pop_rank >= 90 else
        "high" if pop_rank >= 70 else
        "mid" if pop_rank >= 50 else
        "low" if pop_rank >= 30 else
        "none"
    )
    status_class = f'status-{status_priority}'

    return f'''
    <tr data-sales="{sales_v}" data-time="{research_ts}" data-pop="{pop_rank}" data-status-priority="{status_priority}" data-styles="{" ".join(esc(s) for s in canonical)}">
      <td class="col-thumb"><a class="bare" href="{esc(detail_url)}">{thumb_html}</a></td>
      <td class="col-name">{_render_name_cell(item, detail_url)}</td>
      <td class="col-pop"><button class="pop-btn {pop_class}" data-evidence="{evidence_json}">{esc(composite)} <span class="pop-info">ⓘ</span></button></td>
      <td class="col-price">{_render_price_btn(item.get("price", {}) or {}, item.get("name",""))}</td>
      <td class="col-status"><span class="status {status_class}">{esc(status_label)}</span></td>
      <td class="col-time">{_render_release_btn(item.get("release", {}) or {}, item.get("name",""))}</td>
      <td class="col-style">{style_chips}</td>
    </tr>
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


def _count_illustrators():
    """Count illustrator HTML pages (excluding index.html)."""
    illust_dir = ROOT / "illustrators"
    if not illust_dir.is_dir():
        return 0
    return len([f for f in illust_dir.glob("*.html") if f.name != "index.html"])


def write_index(items):
    # Build groups (one item can appear in multiple groups)
    groups = {}
    for it in items:
        for s in styles_for_item(it):
            groups.setdefault(s, []).append(it)
    ordered = [s for s in CANONICAL_STYLES if s in groups] + sorted([s for s in groups if s not in CANONICAL_STYLES])

    tab_buttons = f'<button class="tab active" data-style="all">全部 ({len(items)})</button>'
    tab_buttons += "".join(
        f'<button class="tab" data-style="{esc(s)}">{esc(s)} ({len(groups[s])})</button>'
        for s in ordered
    )

    rows_html = "\n".join(render_summary_row(it) for it in items)

    now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
    doc = f'''<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Lolita 款式调研</title>
<style>
{COMMON_CSS}
  body {{ max-width: 1280px; }}
  .reports-bar {{ margin: 12px 0 20px; padding: 14px 18px; background: linear-gradient(95deg, #f7eed5 0%, #fdfaf0 100%); border: 1px solid #e8d8b0; border-radius: 8px; display: flex; flex-wrap: wrap; align-items: center; gap: 12px; }}
  .report-link {{ color: #5a4a2a; font-weight: 600; font-size: 15px; text-decoration: none; }}
  .report-link:hover {{ color: #c5a572; text-decoration: underline; }}

  .module-nav {{ display:flex; gap:8px; flex-wrap:wrap; margin:4px 0 16px; padding:8px 0; border-bottom:1px solid #ddd; }}
  .module-nav .mod {{ padding:6px 14px; background:#fff; border:1px solid #ddd; border-radius:18px; font-size:13px; color:#333; text-decoration:none; }}
  .module-nav .mod:hover {{ border-color:#f0c674; background:#fffaf0; }}
  .module-nav .mod.active {{ background:#f0c674; border-color:#f0c674; color:#000; font-weight:600; }}
  .module-nav .mod.disabled {{ color:#999; background:#f5f5f5; cursor:not-allowed; }}

  .toolbar {{ display: flex; flex-wrap: wrap; gap: 14px; align-items: center; margin: 14px 0 14px; padding: 10px 14px; background: white; border: 1px solid #e8d8b0; border-radius: 8px; }}
  .toolbar-section {{ display: flex; flex-wrap: wrap; align-items: center; gap: 6px; }}
  .toolbar-label {{ color: #999; font-size: 12px; }}
  .tab {{ background: white; border: 1px solid #d8c898; color: #5a4a2a; padding: 4px 12px; border-radius: 14px; font-size: 12px; cursor: pointer; transition: all 0.15s; }}
  .tab:hover {{ background: #faf3e0; }}
  .tab.active {{ background: #c8a868; color: white; border-color: #c8a868; }}
  .sort {{ background: #fbf7e8; border: 1px solid #d8c898; color: #6a5a30; padding: 4px 10px; border-radius: 14px; font-size: 12px; cursor: pointer; transition: all 0.15s; }}
  .sort:hover {{ background: #f7eed5; }}
  .sort.active {{ background: #6a5a30; color: white; border-color: #6a5a30; }}
  .search-input {{ border: 1px solid #d8c898; background: white; padding: 4px 10px; border-radius: 14px; font-size: 12px; outline: none; min-width: 160px; }}
  .search-input:focus {{ border-color: #c5a572; }}

  .table-wrap {{ overflow-x: auto; border-radius: 8px; box-shadow: 0 1px 6px rgba(0,0,0,0.05); }}
  table.research {{ width: 100%; border-collapse: separate; border-spacing: 0; background: white; font-size: 13px; }}
  table.research th {{ background: #2c2418; color: #efe9d9; padding: 9px 10px; text-align: left; font-weight: 600; font-size: 12px; position: sticky; top: 0; z-index: 5; }}
  table.research td {{ padding: 10px; border-top: 1px solid #f0e8d0; vertical-align: middle; background: white; }}
  table.research tr:hover td {{ background: #fbf7e8; }}
  /* sticky 左 2 列：缩略图 + 标题 */
  table.research th.col-thumb, table.research td.col-thumb {{ position: sticky; left: 0; z-index: 4; }}
  table.research th.col-name, table.research td.col-name {{ position: sticky; left: 64px; z-index: 4; box-shadow: 1px 0 3px rgba(0,0,0,0.04); }}
  table.research thead th.col-thumb, table.research thead th.col-name {{ z-index: 6; }}

  .col-thumb {{ width: 64px; padding: 4px 6px; }}
  .col-thumb img {{ width: 50px; height: 64px; object-fit: cover; border-radius: 4px; display: block; background: #eee; }}
  .col-thumb .no-thumb {{ width: 50px; height: 64px; border-radius: 4px; background: #f0eee8; color: #ccc; display: flex; align-items: center; justify-content: center; font-size: 11px; }}
  .col-status {{ width: 78px; }}
  .col-name {{ min-width: 140px; max-width: 180px; position: relative; }}
  .col-name a.bare {{ color: #2c2418; display: block; padding-right: 18px; }}
  .col-name .title {{ font-weight: 600; font-size: 14px; line-height: 1.3; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }}
  .col-name .brand {{ color: #888; font-size: 11px; margin-top: 2px; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }}
  .name-info-btn {{ position: absolute; top: 50%; right: 6px; transform: translateY(-50%); background: none; border: none; color: #999; cursor: pointer; font-size: 13px; padding: 2px 4px; }}
  .name-info-btn:hover {{ color: #5a4a2a; }}
  .col-price {{ width: 150px; white-space: nowrap; }}
  .col-time {{ width: 130px; white-space: nowrap; }}
  .col-pop {{ width: 150px; white-space: nowrap; }}
  .pop-btn {{ display: inline-flex; align-items: center; gap: 4px; padding: 3px 9px; border-radius: 11px; font-size: 11px; font-weight: 600; border: none; cursor: pointer; transition: filter 0.15s; }}
  .pop-btn:hover {{ filter: brightness(1.1); }}
  .pop-btn .pop-info {{ font-size: 10px; opacity: 0.7; }}
  .price-btn, .release-btn {{ display: inline-flex; align-items: center; gap: 4px; padding: 3px 9px; border-radius: 11px; font: 500 11px/1.2 -apple-system, "PingFang SC", "Helvetica Neue", sans-serif; border: 1px solid #d8c89a; background: #fbf7e8; color: #5a4a2a; cursor: pointer; transition: background 0.15s; font-variant-numeric: tabular-nums; max-width: 100%; overflow: hidden; }}
  .price-btn:hover, .release-btn:hover {{ background: #f5ecc8; }}
  .price-btn .pop-info, .release-btn .pop-info {{ font-size: 10px; opacity: 0.6; color: #888; flex-shrink: 0; }}
  .price-btn .lbl, .release-btn .lbl {{ overflow: hidden; text-overflow: ellipsis; white-space: nowrap; min-width: 0; }}
  .pop-label {{ display: inline-block; padding: 2px 8px; border-radius: 10px; font-size: 11px; font-weight: 600; }}
  .pop-top {{ background: #b00020; color: white; }}
  .pop-high {{ background: #c5a572; color: white; }}
  .pop-mid {{ background: #efe9d9; color: #5a4a2a; }}
  .pop-low {{ background: #f0eee8; color: #999; }}
  .pop-none {{ background: #f0eee8; color: #ccc; }}
  .col-publish, .col-tuan {{ display: none; }}
  .col-style {{ min-width: 110px; }}

  /* popularity modal */
  .pop-modal {{ position: fixed; inset: 0; background: rgba(0,0,0,0.55); display: none; align-items: center; justify-content: center; z-index: 1000; padding: 20px; }}
  .pop-modal.open {{ display: flex; }}
  .pop-modal-card {{ background: white; border-radius: 12px; max-width: 560px; width: 100%; padding: 24px 26px; box-shadow: 0 12px 48px rgba(0,0,0,0.25); position: relative; max-height: 85vh; overflow-y: auto; }}
  .pop-modal-close {{ position: absolute; top: 12px; right: 14px; background: none; border: none; font-size: 24px; cursor: pointer; color: #999; line-height: 1; }}
  .pop-modal-close:hover {{ color: #2c2418; }}
  .pop-modal-name {{ font-size: 18px; font-weight: 600; color: #2c2418; margin: 0 30px 6px 0; }}
  .pop-modal-tag-row {{ margin: 4px 0 14px; }}
  .pop-modal-dims {{ display: grid; grid-template-columns: repeat(4, 1fr); gap: 8px; margin: 12px 0 16px; }}
  .pop-modal-dim {{ background: #fbf7e8; padding: 8px 10px; border-radius: 6px; }}
  .pop-modal-dim .dim-label {{ font-size: 11px; color: #888; }}
  .pop-modal-dim .dim-value {{ font-size: 13px; font-weight: 600; color: #5a4a2a; margin-top: 2px; }}
  .pop-modal-evlabel {{ font-size: 12px; color: #6a5a30; font-weight: 600; margin: 8px 0 6px; }}
  .pop-modal-ev {{ margin: 0; padding-left: 18px; font-size: 13px; line-height: 1.7; color: #444; }}
  .pop-modal-ev li {{ margin-bottom: 4px; }}
  @media (max-width: 600px) {{ .pop-modal-dims {{ grid-template-columns: repeat(2, 1fr); }} }}

  .status {{ display: inline-block; padding: 2px 8px; border-radius: 10px; font-size: 11px; white-space: nowrap; font-weight: 500; }}
  .status-5 {{ background: #d4f4d4; color: #2c7a2c; }}     /* 现货 */
  .status-4 {{ background: #fde0e0; color: #a04020; }}     /* 已开团 */
  .status-3 {{ background: #fff2c8; color: #8a6a30; }}     /* 再贩团 */
  .status-2 {{ background: #e0e8f0; color: #506a8a; }}     /* 加购中 */
  .status-1 {{ background: #efe9d9; color: #6a5a30; }}     /* 调研中 */
  .status-0 {{ background: #f0eee8; color: #999; }}        /* 加购未上架 */

  .sales-top {{ color: #b00020; }}
  .sales-high {{ color: #c5a572; }}
  .sales-mid {{ color: #5a4a2a; }}
  .sales-low {{ color: #888; }}
  .sales-none {{ color: #ccc; font-weight: 400; }}

  .chip {{ display: inline-block; background: #efe9d9; color: #5a4a2a; padding: 1px 7px; border-radius: 9px; font-size: 11px; margin-right: 3px; margin-bottom: 2px; }}

  @media (max-width: 720px) {{
    body {{ padding: 12px 8px; }}
    table.research {{ font-size: 11px; }}
    table.research th, table.research td {{ padding: 6px 8px; }}
    .col-name .brand {{ font-size: 10px; }}
    .col-time, .col-price {{ width: auto; min-width: 100px; }}
    .col-name {{ max-width: 130px; }}
  }}
</style>
</head>
<body>
  <div class="module-nav">
    <a href="index.html" class="mod active">📐 款式调研 ({len(items)})</a>
    <a href="illustrators/index.html" class="mod">🎨 画师调研 ({_count_illustrators()})</a>
    <a href="illustrators/military_research/index.html" class="mod">⭐ 军lo 稿件</a>
    <span class="mod disabled">🏷 品牌（Phase 4）</span>
    <span class="mod disabled">👤 模特（Phase 4）</span>
    <a href="reports/junlo_prince_report.html" class="mod">📊 综合报告</a>
  </div>
  <h1>Lolita 款式调研</h1>
  <div class="meta">最后更新 {now} · 共 {len(items)} 款 · 点行查看详情</div>
  <div class="reports-bar">
    <a href="reports/junlo_prince_report.html" class="report-link">📊 中国军lo王子系市场进入研究报告 (2026 Q2)</a>
  </div>
  <div class="toolbar">
    <div class="toolbar-section">
      <span class="toolbar-label">风格</span>
      {tab_buttons}
    </div>
    <div class="toolbar-section">
      <span class="toolbar-label">排序</span>
      <button class="sort active" data-sort="time">最近调研 ↓</button>
      <button class="sort" data-sort="pop">畅销度 ↓</button>
    </div>
    <div class="toolbar-section">
      <input type="search" class="search-input" id="search" placeholder="搜索款名 / 品牌">
    </div>
  </div>
  <div class="table-wrap">
  <table class="research">
    <thead>
      <tr>
        <th></th>
        <th>款名 / 品牌</th>
        <th>畅销度</th>
        <th>价格</th>
        <th>状态</th>
        <th>时间</th>
        <th>风格</th>
      </tr>
    </thead>
    <tbody id="rows">
{rows_html}
    </tbody>
  </table>
  </div>

  <div id="pop-modal" class="pop-modal" onclick="closePopModal(event)" aria-hidden="true">
    <div class="pop-modal-card" onclick="event.stopPropagation()">
      <button class="pop-modal-close" onclick="closePopModal(event)" aria-label="关闭">×</button>
      <div class="pop-modal-name" id="pop-modal-name"></div>
      <div class="pop-modal-tag-row"><span id="pop-modal-label" class="pop-label"></span></div>
      <div class="pop-modal-dims" id="pop-modal-dims"></div>
      <div class="pop-modal-evlabel">销量与畅销度证据（4 维交叉）</div>
      <ul class="pop-modal-ev" id="pop-modal-ev"></ul>
    </div>
  </div>

  <div id="price-modal" class="pop-modal" onclick="closePriceModal(event)" aria-hidden="true">
    <div class="pop-modal-card" onclick="event.stopPropagation()">
      <button class="pop-modal-close" onclick="closePriceModal(event)" aria-label="关闭">×</button>
      <div class="pop-modal-name" id="price-modal-name"></div>
      <div class="pop-modal-evlabel">价格详情</div>
      <div id="price-modal-body" style="font-size:13px;line-height:1.7;color:#444;"></div>
    </div>
  </div>

  <div id="release-modal" class="pop-modal" onclick="closeReleaseModal(event)" aria-hidden="true">
    <div class="pop-modal-card" onclick="event.stopPropagation()">
      <button class="pop-modal-close" onclick="closeReleaseModal(event)" aria-label="关闭">×</button>
      <div class="pop-modal-name" id="release-modal-name"></div>
      <div class="pop-modal-evlabel">销售时间详情</div>
      <div id="release-modal-body" style="font-size:13px;line-height:1.7;color:#444;"></div>
    </div>
  </div>

  <div id="name-modal" class="pop-modal" onclick="closeNameModal(event)" aria-hidden="true">
    <div class="pop-modal-card" onclick="event.stopPropagation()">
      <button class="pop-modal-close" onclick="closeNameModal(event)" aria-label="关闭">×</button>
      <div class="pop-modal-name" id="name-modal-name"></div>
      <div class="pop-modal-evlabel">完整名 / 品牌 / 设计师 / 风格</div>
      <div id="name-modal-body" style="font-size:13px;line-height:1.7;color:#444;"></div>
    </div>
  </div>

<script>
  const tabs = document.querySelectorAll(".tab");
  const sorts = document.querySelectorAll(".sort");
  const search = document.getElementById("search");
  const tbody = document.getElementById("rows");
  const allRows = Array.from(tbody.querySelectorAll("tr"));

  let curStyle = "all";
  let curQuery = "";

  function applyFilter() {{
    allRows.forEach(r => {{
      const styles = (r.dataset.styles || "").split(" ");
      const styleOk = curStyle === "all" || styles.includes(curStyle);
      const text = r.textContent.toLowerCase();
      const queryOk = !curQuery || text.includes(curQuery);
      r.style.display = styleOk && queryOk ? "" : "none";
    }});
  }}
  function applySort(key) {{
    const sorted = [...allRows].sort((a, b) => {{
      const pa = parseInt(a.dataset.statusPriority || 0);
      const pb = parseInt(b.dataset.statusPriority || 0);
      // 加购未上架(0) 永远在最后，不论按什么排序
      if (pa === 0 && pb !== 0) return 1;
      if (pb === 0 && pa !== 0) return -1;
      const va = parseInt(a.dataset[key] || 0);
      const vb = parseInt(b.dataset[key] || 0);
      return vb - va;
    }});
    sorted.forEach(r => tbody.appendChild(r));
  }}

  tabs.forEach(t => t.addEventListener("click", () => {{
    tabs.forEach(x => x.classList.remove("active"));
    t.classList.add("active");
    curStyle = t.dataset.style;
    applyFilter();
  }}));
  sorts.forEach(s => s.addEventListener("click", () => {{
    sorts.forEach(x => x.classList.remove("active"));
    s.classList.add("active");
    applySort(s.dataset.sort);
  }}));
  search.addEventListener("input", () => {{
    curQuery = search.value.trim().toLowerCase();
    applyFilter();
  }});

  applySort("time");

  // popularity click → modal with evidence
  const popModal = document.getElementById("pop-modal");
  const popModalName = document.getElementById("pop-modal-name");
  const popModalLabel = document.getElementById("pop-modal-label");
  const popModalDims = document.getElementById("pop-modal-dims");
  const popModalEv = document.getElementById("pop-modal-ev");
  document.querySelectorAll(".pop-btn").forEach(btn => {{
    btn.addEventListener("click", (e) => {{
      e.preventDefault();
      e.stopPropagation();
      let data;
      try {{ data = JSON.parse(btn.dataset.evidence); }} catch (err) {{ return; }}
      popModalName.textContent = data.name || "";
      popModalLabel.textContent = data.label || "";
      popModalLabel.className = "pop-label " + btn.className.replace("pop-btn ", "");
      popModalDims.innerHTML = `
        <div class="pop-modal-dim"><div class="dim-label">规模</div><div class="dim-value">${{data.scale}}</div></div>
        <div class="pop-modal-dim"><div class="dim-label">传播</div><div class="dim-value">${{data.buzz}}</div></div>
        <div class="pop-modal-dim"><div class="dim-label">权威</div><div class="dim-value">${{data.authority}}</div></div>
        <div class="pop-modal-dim"><div class="dim-label">保值</div><div class="dim-value">${{data.resale}}</div></div>
      `;
      popModalEv.innerHTML = (data.evidence || []).map(x => `<li>${{x.replace(/&/g,"&amp;").replace(/</g,"&lt;")}}</li>`).join("");
      popModal.classList.add("open");
    }});
  }});
  window.closePopModal = function(e) {{
    if (e && e.target.closest && e.target.closest(".pop-modal-card") && !e.target.classList.contains("pop-modal-close")) return;
    popModal.classList.remove("open");
  }};
  document.addEventListener("keydown", (e) => {{
    if (e.key === "Escape" && popModal.classList.contains("open")) popModal.classList.remove("open");
  }});

  // price click → modal
  const priceModal = document.getElementById("price-modal");
  const priceModalName = document.getElementById("price-modal-name");
  const priceModalBody = document.getElementById("price-modal-body");
  function fmtPriceVal(v) {{
    if (v === null || v === undefined) return "—";
    if (typeof v === "number") return "¥" + v;
    return String(v);
  }}
  function escHtml(s) {{
    return String(s).replace(/&/g,"&amp;").replace(/</g,"&lt;").replace(/>/g,"&gt;");
  }}
  document.querySelectorAll(".price-btn").forEach(btn => {{
    btn.addEventListener("click", (e) => {{
      e.preventDefault(); e.stopPropagation();
      let d;
      try {{ d = JSON.parse(btn.dataset.priceDetail); }} catch(err) {{ return; }}
      priceModalName.textContent = d.name || "";
      const rows = [];
      const numFields = [["op","OP 单件"],["full_set","整套"],["deposit_link_intent","意向金"]];
      for (const [k,label] of numFields) {{
        if (d[k] !== undefined && d[k] !== null) rows.push(`<div><strong>${{label}}</strong>: ¥${{d[k]}}</div>`);
      }}
      const strFields = [["list_price_at_research","调研当时挂牌价"],["full_set_estimate","整套估算"],["full_set_estimate_v2","整套估算 v2"],["full_set_estimate_v3","整套估算 v3"],["full_set_history","价格历史"],["full_set_status","整套价 status"],["op_note","OP 注"],["full_set_note","整套 注"],["list_price_note","挂牌价 注"],["list_price_priority_note","价格优先级"],["note","总注"]];
      for (const [k,label] of strFields) {{
        if (d[k]) rows.push(`<div style="margin-top:6px;"><strong>${{label}}</strong>: ${{escHtml(d[k])}}</div>`);
      }}
      if (d.skus_known) rows.push(`<div style="margin-top:6px;"><strong>SKU 拆分</strong>:<br>${{Object.entries(d.skus_known).map(([k,v])=>`&nbsp;&nbsp;${{escHtml(k)}}: ${{fmtPriceVal(v)}}`).join("<br>")}}</div>`);
      if (d.price_breakdown) rows.push(`<div style="margin-top:6px;"><strong>价格分档</strong>:<br>${{Object.entries(d.price_breakdown).map(([k,v])=>`&nbsp;&nbsp;${{escHtml(k)}}: ${{escHtml(v)}}`).join("<br>")}}</div>`);
      priceModalBody.innerHTML = rows.join("") || "<em>—</em>";
      priceModal.classList.add("open");
    }});
  }});
  window.closePriceModal = function(e) {{
    if (e && e.target.closest && e.target.closest(".pop-modal-card") && !e.target.classList.contains("pop-modal-close")) return;
    priceModal.classList.remove("open");
  }};

  // release click → modal
  const releaseModal = document.getElementById("release-modal");
  const releaseModalName = document.getElementById("release-modal-name");
  const releaseModalBody = document.getElementById("release-modal-body");
  document.querySelectorAll(".release-btn").forEach(btn => {{
    btn.addEventListener("click", (e) => {{
      e.preventDefault(); e.stopPropagation();
      let d;
      try {{ d = JSON.parse(btn.dataset.releaseDetail); }} catch(err) {{ return; }}
      releaseModalName.textContent = d.name || "";
      const rows = [];
      const fields = [["type","类型"],["date_range","上新窗口"],["poster_first_seen","海报首发"],["note","注"]];
      for (const [k,label] of fields) {{
        if (d[k]) rows.push(`<div style="margin-top:4px;"><strong>${{label}}</strong>: ${{escHtml(d[k])}}</div>`);
      }}
      releaseModalBody.innerHTML = rows.join("") || "<em>—</em>";
      releaseModal.classList.add("open");
    }});
  }});
  window.closeReleaseModal = function(e) {{
    if (e && e.target.closest && e.target.closest(".pop-modal-card") && !e.target.classList.contains("pop-modal-close")) return;
    releaseModal.classList.remove("open");
  }};
  // name click → modal
  const nameModal = document.getElementById("name-modal");
  const nameModalName = document.getElementById("name-modal-name");
  const nameModalBody = document.getElementById("name-modal-body");
  document.querySelectorAll(".name-info-btn").forEach(btn => {{
    btn.addEventListener("click", (e) => {{
      e.preventDefault(); e.stopPropagation();
      let d;
      try {{ d = JSON.parse(btn.dataset.nameDetail); }} catch(err) {{ return; }}
      nameModalName.textContent = d.name || "";
      const rows = [];
      const fields = [["brand","品牌"],["designer","设计师"],["illustrator","画师"],["designer_note","设计师注"],["style_summary","风格说明"]];
      for (const [k,label] of fields) {{
        if (d[k]) rows.push(`<div style="margin-top:4px;"><strong>${{label}}</strong>: ${{escHtml(d[k])}}</div>`);
      }}
      nameModalBody.innerHTML = rows.join("") || "<em>—</em>";
      nameModal.classList.add("open");
    }});
  }});
  window.closeNameModal = function(e) {{
    if (e && e.target.closest && e.target.closest(".pop-modal-card") && !e.target.classList.contains("pop-modal-close")) return;
    nameModal.classList.remove("open");
  }};

  document.addEventListener("keydown", (e) => {{
    if (e.key === "Escape") {{
      if (priceModal.classList.contains("open")) priceModal.classList.remove("open");
      if (releaseModal.classList.contains("open")) releaseModal.classList.remove("open");
      if (nameModal.classList.contains("open")) nameModal.classList.remove("open");
    }}
  }});
</script>
</body>
</html>'''
    INDEX.write_text(_inject_version(doc))


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
    poster_links = []
    weibo = item.get("shops", {}).get("weibo", {})
    if weibo.get("upgrade_post_url"):
        poster_links.append((f"微博 上新海报", weibo["upgrade_post_url"]))
    for bsp in weibo.get("brand_self_posts", [])[:3]:
        if bsp.get("url"):
            label = f"微博 {bsp.get('type','官号自发')}"
            poster_links.append((label, bsp["url"]))
    if not weibo.get("upgrade_post_url") and not weibo.get("brand_self_posts"):
        if weibo.get("current_post_url"):
            poster_links.append(("微博 官号海报", weibo["current_post_url"]))
    taobao = item.get("shops", {}).get("taobao", {})
    if "淘宝" in (item.get("posters_source") or "") and taobao.get("url"):
        poster_links.append(("淘宝商品页", taobao["url"]))
    posters_source_html = ""
    if poster_links:
        link_html = " · ".join(f'<a href="{esc(u)}" target="_blank">{esc(l)} ↗</a>' for l, u in poster_links)
        posters_source_html = f'<div class="posters-source">📷 来源：{link_html}</div>'

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
            inner.append(f'<div class="el-name">{esc(el.get("element", el.get("name", "")))}</div>')
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

    pop = item.get("popularity", {}) or {}
    pop_html = ""
    if pop:
        composite = esc(pop.get("composite_label", ""))
        ev_html = "".join(f"<li>{esc(e)}</li>" for e in pop.get("evidence", []))
        tier_rows = []
        tier_map = [
            ("规模", "scale_tier", "真实付款规模量级"),
            ("传播", "buzz_tier", "圈内自然传播深度"),
            ("权威", "authority_tier", "圈内权威背书"),
            ("保值", "resale_tier", "二级市场长尾"),
        ]
        for label, key, desc in tier_map:
            v = pop.get(key, "—")
            tier_rows.append(f'<div class="pop-dim"><div class="pop-dim-label">{label}</div><div class="pop-dim-value">{esc(v)}</div><div class="pop-dim-desc">{desc}</div></div>')
        tiers_html = "".join(tier_rows)
        pop_rank = POPULARITY_RANK.get(pop.get("composite_label", ""), 20)
        pop_class = "pop-" + (
            "top" if pop_rank >= 90 else
            "high" if pop_rank >= 70 else
            "mid" if pop_rank >= 50 else
            "low" if pop_rank >= 30 else
            "none"
        )
        pop_html = f'''
        <section class="popularity-section">
          <h3>畅销度评估 <span class="pop-label {pop_class}">{composite}</span></h3>
          <div class="pop-dims">{tiers_html}</div>
          <div class="pop-evidence-block">
            <div class="pop-evidence-label">证据清单（4 维交叉验证）</div>
            <ul class="pop-evidence">{ev_html}</ul>
          </div>
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
  .posters-source {{ font-size: 12px; color: #888; padding: 4px 0 12px; line-height: 1.6; }}
  .posters-source a {{ color: #6a5a30; text-decoration: none; }}
  .posters-source a:hover {{ color: #2c2418; text-decoration: underline; }}
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
  .info-grid {{ display: grid; grid-template-columns: repeat(2, 1fr); gap: 16px; margin: 16px 0; grid-auto-rows: max-content; }}
  .info {{ background: #faf7ed; padding: 12px 16px; border-radius: 6px; }}
  .info h3 {{ margin: 0 0 8px 0; font-size: 14px; color: #5a4a2a; }}
  .row {{ font-size: 13px; line-height: 1.8; display: flex; gap: 8px; }}
  .row .k {{ color: #888; min-width: 80px; }}
  .row .v {{ color: #222; flex: 1; word-break: break-word; }}
  .row.note {{ color: #777; font-style: italic; font-size: 12px; }}
  .color-chip {{ background: #f0e8d0; padding: 2px 8px; border-radius: 4px; margin-right: 4px; font-size: 12px; }}
  .color-dropped {{ background: #f8e0e0; color: #a04020; padding: 2px 8px; border-radius: 4px; font-size: 11px; margin-left: 8px; text-decoration: line-through; }}
  .shops {{ display: grid; grid-template-columns: repeat(2, 1fr); gap: 16px; margin-top: 16px; grid-auto-rows: max-content; }}
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
  .popularity-section {{ margin: 16px 0; padding: 16px 18px; background: #fffaee; border-radius: 8px; border: 1px solid #e8d8b0; }}
  .popularity-section > h3 {{ margin: 0 0 10px 0; font-size: 15px; color: #5a4a2a; display: flex; align-items: center; gap: 10px; }}
  .pop-label {{ display: inline-block; padding: 3px 10px; border-radius: 12px; font-size: 12px; font-weight: 600; }}
  .pop-top {{ background: #b00020; color: white; }}
  .pop-high {{ background: #c5a572; color: white; }}
  .pop-mid {{ background: #efe9d9; color: #5a4a2a; }}
  .pop-low {{ background: #f0eee8; color: #999; }}
  .pop-none {{ background: #f0eee8; color: #ccc; }}
  .pop-dims {{ display: grid; grid-template-columns: repeat(4, 1fr); gap: 8px; margin: 10px 0; }}
  .pop-dim {{ background: white; padding: 8px 10px; border-radius: 6px; }}
  .pop-dim-label {{ font-size: 11px; color: #888; }}
  .pop-dim-value {{ font-size: 14px; font-weight: 600; color: #5a4a2a; margin: 2px 0; }}
  .pop-dim-desc {{ font-size: 10px; color: #aaa; }}
  .pop-evidence-block {{ margin-top: 10px; padding: 10px 12px; background: #f8f4e8; border-radius: 6px; }}
  .pop-evidence-label {{ font-size: 11px; color: #777; margin-bottom: 4px; }}
  .pop-evidence {{ margin: 0; padding-left: 18px; font-size: 12px; line-height: 1.7; color: #444; }}
  @media (max-width: 640px) {{ .pop-dims {{ grid-template-columns: repeat(2, 1fr); }} }}

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
    {pop_html}
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
    return _inject_version(doc)


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
