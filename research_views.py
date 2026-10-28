"""Public, source-linked views for the sweet Lolita research batch."""
import html
import json
from pathlib import Path


def esc(value):
    return html.escape(str(value))


CSS = """
*{box-sizing:border-box}body{margin:0;background:#f6f4ef;color:#2c2925;font:15px/1.75 -apple-system,BlinkMacSystemFont,'PingFang SC',sans-serif}a{color:#745744;text-underline-offset:4px}a:hover{color:#a84f61}main,.nav{max-width:1120px;margin:auto;padding:24px}.nav{display:flex;flex-wrap:wrap;gap:10px;padding-bottom:12px}.nav a{font-size:13px;padding:5px 12px;background:#fff;border:1px solid #e4dcd2;border-radius:20px;text-decoration:none}.nav .active{background:#f0dce0;border-color:#dcb8c1;color:#743d4b}h1{font:600 clamp(28px,5vw,44px)/1.25 'Songti SC',serif;margin:10px 0 18px}h2{font-size:22px;margin:0 0 14px}h3{font-size:18px;margin:8px 0}.eyebrow{color:#926d73;font-size:12px;letter-spacing:.12em}.muted,.caption{color:#80776f;font-size:13px}.hero{padding:24px 0 28px;border-bottom:1px solid #ded4c9}.hero p{max-width:760px}.stats{display:flex;gap:24px;flex-wrap:wrap;margin:20px 0}.stats strong{font:600 24px/1.4 'Songti SC',serif;color:#764a56}.stats span{color:#817770;font-size:12px}.controls{display:flex;flex-wrap:wrap;gap:12px;align-items:end;margin:24px 0}.controls label{display:grid;gap:5px;font-size:12px;color:#786b62}.controls input,.controls select,.controls button{font:inherit;padding:10px 14px;border:1px solid #d7ccc0;background:white;border-radius:7px;color:#38312c}.controls input{min-width:240px}.controls button{cursor:pointer}.count{margin-left:auto;color:#817770;font-size:13px}.grid{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:20px}.tile{border:1px solid #e4dcd2;border-radius:12px;background:#fff;overflow:hidden;display:flex;flex-direction:column}.tile .visual{display:block;background:#eee5df;height:285px}.visual img{width:100%;height:100%;object-fit:cover;object-position:center 38%;display:block}.visual.empty{display:flex;align-items:center;justify-content:center;background:#efe8df;color:#96867a;font-size:13px}.tile-body{padding:20px;display:flex;flex-direction:column;flex:1}.brand{color:#8c6d5b;font-size:12px}.tile h2{font-size:21px;line-height:1.4;margin:5px 0 10px}.tile h2 a{text-decoration:none;color:#352d28}.version{font-size:12px;color:#81756b;margin:0 0 14px}.price{font-weight:600;color:#744b53;font-size:15px;margin:8px 0}.pill{font-size:11px;display:inline-block;border:1px solid #ddcdd0;color:#835461;background:#fbf1f3;border-radius:12px;padding:2px 8px;width:fit-content}.tile .caption{font-size:11px;line-height:1.5;margin:8px 0 0}.tile .open{margin-top:auto;padding-top:14px;font-size:13px}.section{margin:32px 0;padding:24px;background:white;border:1px solid #e5ddd3;border-radius:10px}.section ul{padding-left:22px}.section li{margin:8px 0}.notice{padding:14px 18px;background:#eee7da;border-left:3px solid #b19a7d;font-size:13px}.detail-head{margin-bottom:24px}.detail-head h1{font-size:34px}.detail-head .version{font-size:14px}.gallery{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:16px}.gallery figure{margin:0;background:#fff;padding:12px;border:1px solid #e4dcd2;border-radius:8px}.gallery img{width:100%;height:510px;object-fit:contain;display:block;background:#faf9f7}.gallery figcaption{font-size:12px;color:#82766e;margin-top:10px}.feedback{padding:14px 18px;background:#f6f4ef;border-radius:7px;margin:12px 0}.feedback .kind{font-size:12px;color:#906a57}.feedback p{margin:5px 0}.feedback a{font-size:12px}.table-scroll{overflow:auto}table{border-collapse:collapse;width:100%;font-size:13px}th,td{text-align:left;border-bottom:1px solid #e4dcd2;padding:12px;vertical-align:top}th{color:#776454;background:#f4f0ea}td small{display:block;color:#8b7d71}.sources{list-style:none;padding:0!important}.sources li{padding:12px 0;border-bottom:1px solid #eee6df}.sources small{display:block;color:#8a7a70}.back{display:inline-block;margin-bottom:18px}.empty-state{text-align:center;padding:36px;color:#8c776a}[hidden]{display:none!important}.footer{color:#8b8177;font-size:12px;border-top:1px solid #e4dcd2;margin-top:40px;padding:20px 0}.question{color:#714c55}.source-list{columns:2;column-gap:36px}.source-list li{break-inside:avoid;margin-bottom:14px}.source-list small{display:block;color:#897a6e}.link-row{display:flex;gap:16px;flex-wrap:wrap}
@media(max-width:850px){.grid{grid-template-columns:repeat(2,minmax(0,1fr))}.gallery img{height:420px}}
@media(max-width:560px){main,.nav{padding:16px}.hero{padding-top:12px}.grid{grid-template-columns:1fr}.tile .visual{height:350px}.controls{align-items:stretch}.controls label{flex:1;min-width:130px}.controls input{min-width:0;width:100%}.count{width:100%;margin:0}.section{padding:18px}.gallery{grid-template-columns:1fr}.gallery img{height:auto;max-height:620px}.stats{gap:20px}.source-list{columns:1}.detail-head h1{font-size:28px}}
"""


def shell(title, body, prefix="../", updated="2026-10-24"):
    return f'''<!doctype html><html lang="zh-CN"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1"><meta name="description" content="甜系Lolita款式、SKU价格与用户反馈，保留原始来源和待核字段。"><title>{esc(title)} · Lolita 调研</title><style>{CSS}</style></head><body><nav class="nav" aria-label="网站栏目"><a href="{prefix}index.html">全部款式</a><a class="active" href="{prefix}sweet/index.html">甜系专题</a><a href="{prefix}illustrators/index.html">画师调研</a><a href="{prefix}reports/junlo_prince_report.html">综合报告</a></nav><main>{body}<footer class="footer">资料核验日期：{esc(updated)} · 选样与评论不代表整体市场；价格与发货状态以对应SKU及核验时点为限。</footer></main></body></html>'''


KINDS = {
    "brand_weibo": "品牌微博", "store_product": "店铺商品页", "storefront": "店铺首页",
    "third_party_library": "第三方图鉴", "user_post": "用户笔记／购买关系未全部核实",
    "secondary_purchase_post": "二手渠道自述", "brand_named_account": "品牌同名账号／主体关系待核",
    "wear_display_commercial_unknown": "穿着展示／合作关系未知",
    "promotion_purchase_unknown": "推广内容／购买关系未知",
    "third_party_retailer": "独立零售商品页／原店批次待核",
    "brand_profile": "品牌账号自述／商品与经营主体另核",
    "third_party_aggregator": "第三方商品资料／原店现行版另核",
    "brand_named_store": "门店同名账号／主体与直营关系待核",
    "incentivized_post": "集赞参与笔记／激励与购买关系待核",
}


AUDIT_LABELS = {"documented": "有记录", "partial": "部分有据", "unresolved": "未找到可核资料"}


def render_audit_rows(item):
    rows = item["research_record"].get("verification_audit", [])
    sources = item["research_sources"]
    body = '<div class="table-scroll"><table><thead><tr><th scope="col">核查项</th><th scope="col">状态</th><th scope="col">结果与适用范围</th></tr></thead><tbody>'
    for row in rows:
        links = ' '.join(f'<a href="{esc(sources[sid]["url"])}" target="_blank" rel="noopener">{esc(sid)} ↗</a>' for sid in row["sources"])
        body += f'<tr><th scope="row">{esc(row["field"])}</th><td>{esc(AUDIT_LABELS[row["status"]])}</td><td>{esc(row["summary"])}<small>{links}</small></td></tr>'
    return body+'</tbody></table></div>'


def render_documented_reference(reference, sources):
    source = sources[reference["source"]]
    body = '<section class="section"><h2>'+esc(reference["title"])+'</h2>'
    body += f'<p><a href="{esc(source["url"])}" target="_blank" rel="noopener">对应资料 · {esc(reference["source"])} ↗</a> <span class="caption">核读：{esc(reference["observed_at"])}</span></p>'
    body += '<p class="notice">'+esc(reference["scope"])+'</p><ul>'+''.join('<li>'+esc(x)+'</li>' for x in reference["points"])+'</ul>'
    for table in reference.get("tables", []):
        body += '<h3>'+esc(table["title"])+'</h3><div class="table-scroll"><table><thead><tr>'
        body += ''.join('<th scope="col">'+esc(h)+'</th>' for h in table["headers"])
        body += '</tr></thead><tbody>'+''.join('<tr>'+''.join('<td>'+esc(c)+'</td>' for c in row)+'</tr>' for row in table["rows"])
        body += '</tbody></table></div><p class="caption">'+esc(table["note"])+'</p>'
    if reference.get("images"):
        body += '<details><summary>查看所读资料图</summary><div class="gallery">'
        for path in reference["images"]:
            body += f'<figure><a href="../{esc(path)}" target="_blank" rel="noopener"><img src="../{esc(path)}" loading="lazy" alt="{esc(reference["title"])}资料图"></a><figcaption>保留来源原文供核对；历史条件和适用版本见本节说明。</figcaption></figure>'
        body += '</div></details>'
    return body+'</section>'


def render_retailer_reference(reference, sources):
    source = sources[reference["source"]]
    body = '<section class="section" id="retailer-reference"><h2>独立零售页补充</h2>'
    body += f'<p><a href="{esc(source["url"])}" target="_blank" rel="noopener">42Lolita · {esc(reference["name"])} ↗</a><br><span class="caption">零售页品牌标注：{esc(reference["brand_label"])} · 读取日期：{esc(reference["observed_at"])}</span></p>'
    body += '<p class="notice">'+esc(reference["limitations"])+'</p>'
    body += '<h3>对应依据</h3><p>'+esc(reference["identity_summary"])+'</p>'
    body += '<details><summary>查看图源核对记录</summary><ul>'+''.join('<li>'+esc(x)+'</li>' for x in reference["identity_evidence"])+'</ul></details>'
    body += '<p><strong>材质陈述：</strong>'+esc(reference["material"])+ '</p>'
    body += '<p><strong>包含物与分售：</strong>'+esc(reference["components"])+ '</p>'
    body += '<h3>零售商尺码表 · 厘米</h3><div class="table-scroll"><table><thead><tr>'
    body += ''.join('<th scope="col">'+esc(x)+'</th>' for x in reference["size_headers"])
    body += '</tr></thead><tbody>'
    for row in reference["size_rows"]:
        body += '<tr>'+''.join('<td>'+esc(x)+'</td>' for x in row)+'</tr>'
    body += '</tbody></table></div><p class="caption">'+esc(reference["measurement_note"])+'</p>'
    for extra in reference.get("additional_size_tables", []):
        body += '<details><summary>'+esc(extra["title"])+'</summary><div class="table-scroll"><table><thead><tr>'
        body += ''.join('<th scope="col">'+esc(x)+'</th>' for x in extra["headers"])
        body += '</tr></thead><tbody>'+''.join('<tr>'+''.join('<td>'+esc(x)+'</td>' for x in row)+'</tr>' for row in extra["rows"])
        body += '</tbody></table></div></details>'
    offer = reference["offer"]
    body += f'<details><summary>查看海外零售报价记录</summary><p>{esc(offer["selection"])}：{esc(offer["currency"])} {esc(offer["amount"])}；零售SKU {esc(offer["sku"])}。</p><p>{esc(offer["fulfillment"])}</p><p class="caption">该报价仅属于上述海外零售页和所选组合，未核结算运费、税费与实付；不折算成淘宝价，也不替代下方原店交期。</p></details></section>'
    return body


def render_research_detail(item):
    r = item["research_record"]
    sources = item["research_sources"]
    updated = item.get("verified_at", "2026-10-24")
    body = f'<a class="back" href="../sweet/index.html">← 返回甜系专题</a><header class="detail-head"><div class="eyebrow">甜系研究 · {esc(updated.replace("-", "."))}</div><div class="brand">{esc(item["brand"])}</div><h1>{esc(item["name"])}</h1><p class="version">{esc(r["version"])}</p><span class="pill">{esc(item["status_label"])}</span></header>'
    if item.get("posters"):
        figures = []
        for path in item["posters"]:
            figures.append(f'<figure><a href="../{esc(path)}" target="_blank" rel="noopener"><img src="../{esc(path)}" alt="{esc(item["name"])}参考图"></a><figcaption>{esc(item["image_note"])} · 搭配物不自动计入SKU。</figcaption></figure>')
        body += '<div class="gallery">' + ''.join(figures) + '</div>'
    else:
        body += '<p class="notice">本条目的对版图片仍待补齐，先保留已读来源；不以近似款配图。</p>'
    body += '<section class="section"><h2>已核到的材料</h2><ul>' + ''.join('<li>'+esc(x)+'</li>' for x in r["verified_facts"]) + '</ul></section>'
    if r.get("verification_audit"):
        body += '<section class="section" id="verification-audit"><h2>本轮补充与逐项核查</h2><p>'+esc(r["supplement_summary"])+'</p><p class="caption">“有记录”表示取得对应资料，不等于原店现行批次或实物已全部确认；日期：'+esc(r["audit_at"])+'。</p>'
        body += render_audit_rows(item)
        for attempt in r.get("verification_attempts", []):
            body += '<p class="caption">'+esc(attempt)+'</p>'
        body += '<a href="../sweet/review.html">看款式核查总表与设计比较 →</a></section>'
    for reference in r.get("documented_references", []):
        body += render_documented_reference(reference, sources)
    if r.get("retailer_reference"):
        body += render_retailer_reference(r["retailer_reference"], sources)
    body += '<section class="section"><h2>价格与发货</h2><p>'+esc(item["price"]["note"])+'</p>'
    records = r.get("price_records", [])
    selected = [p for p in records if p["basis"] == "selected_sku_display"]
    if selected:
        body += '<div class="table-scroll"><table><thead><tr><th>选定组合</th><th>页面展示价</th><th>发货文案</th><th>商品原页</th></tr></thead><tbody>'
        for p in selected:
            identity = ('SKU '+str(p['sku_id'])) if p.get('sku_id') else ('商品 '+str(p.get('item_id', '')))
            observed = p.get('observed_date') or str(p.get('observed_at', ''))[:10]
            date_zone = '（UTC）' if p.get('observed_at') and not p.get('observed_date') else ''
            metadata = esc(identity + (' · 观察日期 '+observed+date_zone if observed else ''))
            evidence = ' · '.join(f'<a href="../{esc(path)}" target="_blank" rel="noopener">规格截图{n}</a>' for n,path in enumerate(p.get('evidence_images', []), 1))
            evidence_html = '<small>' + evidence + '</small>' if evidence else ''
            stock = '<small>'+esc(p['stock_text'])+'</small>' if p.get('stock_text') else ''
            body += f'<tr><td>{esc(" / ".join(p["selection"]))}<small>{metadata}</small>{evidence_html}</td><td>¥{esc(p["amount_cny"])}{stock}</td><td>{esc(p["shipping_text"])}</td><td><a href="{esc(p["url"])}" target="_blank" rel="noopener">商品来源 ↗</a></td></tr>'
        body += '</tbody></table></div><p class="caption">每行保留各自观察日期；选齐颜色／套餐及尺码后的展示价，未核结算优惠和实付。不同商品链接分列，不合并版本或销量。</p>'
    elif records:
        labels = {"store_card_unselected":"未选SKU的店铺卡片价", "historical_third_party_reference":"历史第三方资料参考", "historical_brand_announcement":"品牌历史公告价，当前SKU另核", "unselected_minimum_not_dress_price":"未选SKU最低展示，不能当单裙价", "promotion_title_sku_unknown":"推广标题线索，SKU与权益未核", "uncertain_visible_comment":"不确定的评论报价，不能当官方价"}
        body += '<ul>' + ''.join(f'<li>¥{esc(p["amount_cny"])}：{esc(labels.get(p["basis"], p["basis"]))}</li>' for p in records) + '</ul>'
    else:
        body += '<p class="muted">尚无与此研究目标对应的官方SKU报价。</p>'
    body += '</section><section class="section"><h2>用户反馈与适用条件</h2>'
    if r["feedback"]:
        for f in r["feedback"]:
            s = sources[f["source"]]
            label = {"retailer_review_visible_self_report":"零售页评价／批次与独立性未核", "retailer_giveaway_self_report":"零售页赠奖自述／非自费购买", "promotion_purchase_unknown":"推广或笼统评价／实购与版本未知", "incentivized_content_not_wear_review":"集赞参与／不作独立实穿证据", "adjacent_version_unconfirmed":"相邻版本评论／不归因本目标", "arrival_version_unconfirmed":"到家自述／版本与身体条件未核", "wear_self_report_unverified_purchase":"实穿自述／批次与购买关系未核"}.get(f["nature"], "个体自述／可见评论")
            body += f'<article class="feedback"><div class="kind">{esc(label)}</div><p>{esc(f["summary"])}</p><a href="{esc(s["url"])}" target="_blank" rel="noopener">查看对应来源 ↗</a></article>'
        body += '<p class="caption">正文与可见评论已读；未观看的视频不写成视频结论。版本、配色、体型、渠道和推广关系未全部统一。</p>'
    else:
        body += '<p class="muted">尚无与本条目具体版本对应的独立实穿材料；宣传不替代用户验收。</p>'
    body += '</section><section class="section"><h2>未找到与尚未核验</h2><p class="caption">按当前材料保留缺口；“未找到”不表示信息或款式不存在，取得新资料后再更新。</p>'
    gaps = r.get("search_gaps", {})
    if gaps:
        body += '<p class="caption">最近查找：'+esc(gaps["checked_at"])+'。范围：'+esc(gaps["scope"])+ '。</p>'
    missing = set(gaps.get("not_found_indexes", []))
    body += '<ul>'+''.join('<li><strong>'+('未找到' if n in missing else '尚未核验')+'：</strong>'+esc(x)+'</li>' for n,x in enumerate(r["unknowns"]))+'</ul></section>'
    body += '<section class="section"><h2>设计讨论问题</h2><p class="question">'+esc(r["discussion"])+'</p><p class="caption">这是后续验证问题，不代表已确定的产品定位、定价或质量结论。</p></section>'
    body += '<section class="section"><h2>原始来源</h2><ul class="sources">'
    for sid in r["source_refs"]:
        s = sources[sid]
        body += f'<li><a href="{esc(s["url"])}" target="_blank" rel="noopener">{esc(KINDS.get(s["kind"],s["kind"]))} · {esc(sid)} ↗</a><small>{esc(s["scope"])}</small></li>'
    if item.get("image_source_url"):
        body += f'<li><a href="{esc(item["image_source_url"])}" target="_blank" rel="noopener">参考图片出处 ↗</a><small>{esc(item.get("image_note", ""))}</small></li>'
    body += '</ul></section>'
    return shell(item["name"], body, updated=updated)


def render_review(items, review):
    by_id = {i["research_record"]["id"]:i for i in items}
    body = '<a class="back" href="index.html">← 返回甜系专题</a><header class="hero"><div class="eyebrow">'+esc(review["updated_at"])+ ' 补充核验</div><h1>'+esc(review["title"])+'</h1><p>'+esc(review["scope"])+'</p></header>'
    body += '<section class="section"><h2>这轮补到哪里</h2><p>'+esc(review.get("latest_summary", "蜜糖邦尼已落实到片裁JSK；草莓猫猫增加原店历史价目及两张厘米表。其余款式分别补分版、名称、入口或图像依据，尚缺原店证据的字段继续保留。"))+'</p><div class="link-row">'
    body += ''.join(f'<a href="#audit-{esc(cid)}">{esc(cid)} {esc(i["name"])} ↓</a>' for cid,i in sorted(by_id.items()))+'</div></section>'
    for cid,item in sorted(by_id.items()):
        r=item["research_record"]
        body += f'<section class="section" id="audit-{esc(cid)}"><div class="brand">{esc(item["brand"])}</div><h2>{esc(cid)} · {esc(item["name"])}</h2><p>{esc(r["supplement_summary"])}</p>'
        body += render_audit_rows(item)
        body += f'<p><a href="../items/{esc(item["id"])}.html#verification-audit">看资料图、完整表格和原始来源 →</a></p></section>'
    body += '<section class="section" id="design-comparison"><h2>从款式资料得到的设计讨论</h2><p class="notice">以下是有出处的样本比较与待验证方向，不是销量排名、普遍质量判断或已经确定的产品开发方案。</p>'
    for theme in review["themes"]:
        body += '<h3>'+esc(theme["title"])+'</h3><p>'+esc(theme["finding"])+'</p><p class="caption">对应材料：'
        body += ' · '.join(f'<a href="../items/{esc(by_id[cid]["id"])}.html">{esc(cid)} {esc(by_id[cid]["name"])}</a>' for cid in theme["records"])
        body += '</p><p><strong>验证方向：</strong>'+esc(theme["next"])+'</p>'
    body += '</section><section class="section"><h2>已排除的混用</h2><ul>'
    for rejected in review["rejected_matches"]:
        body += '<li>'+esc(rejected["record"]+' · '+rejected["name"]+'：'+rejected["reason"])+f' <a href="{esc(rejected["url"])}" target="_blank" rel="noopener">对照来源 ↗</a></li>'
    body += '</ul></section><section class="section"><h2>本次核查的限制</h2><ul>'+''.join('<li>'+esc(x)+'</li>' for x in review["limits"])+'</ul><p>未核事项仍留在各款“还需核验”中；没有用其他配色、近似款或AI无源答案补成已确认事实。</p></section>'
    return shell(review["title"], body, updated=review["updated_at"])


def render_topic(items, sample_sources, sampling=None):
    sampling = sampling or {"read_records":18,"excluded_records":1,"brand_named_account_posts":2}
    updated = max(i.get("verified_at", "2026-10-24") for i in items)
    series_count = sum(i["research_record"].get("record_type") == "series" for i in items)
    brand_count = len({i["brand"] for i in items})
    source_count = len(sample_sources)
    record_summary = f'{series_count}个系列待选款、{len(items)-series_count}个款式候选' if series_count else f'{len(items)}个具体款式候选'
    body = f'<header class="hero"><div class="eyebrow">SWEET LOLITA · {esc(updated.replace("-", "."))} 更新</div><h1>甜系款式调研</h1><p>从具体款式、配件和穿着反馈出发，记录已经读到的材料，也保留版本、价格与规格的缺口。点击款式可看SKU、正反反馈和原始来源。</p><div class="stats"><div><strong>{brand_count}</strong> <span>个品牌／店铺线索</span></div><div><strong>{len(items)}</strong> <span>个研究条目</span></div><div><strong>{source_count}</strong> <span>篇小红书相关材料</span></div></div><p class="muted">现有{record_summary}；{source_count}篇材料中含{sampling["brand_named_account_posts"]}篇品牌或门店同名账号宣传，不代表{source_count}名独立买家。各款的渠道与版本覆盖见详情。</p></header>'
    if sampling.get("latest_summary"):
        body += '<section class="section"><h2>最新补充 · '+esc(sampling["updated_at"])+ '</h2><p>'+esc(sampling["latest_summary"])+ '</p><p><a href="review.html">看补证结果与设计比较 →</a></p></section>'
    if all(i["research_record"].get("verification_audit") for i in items):
        audit_count = sum(len(i["research_record"]["verification_audit"]) for i in items)
        body += f'<section class="section"><h2>款式逐项核查</h2><p>{len(items)}款分别记录版本、入口、价格/包含物、面料、厘米表、交期与反馈；扩样后继续保留旧款缺口，历史公告和当前SKU分开。</p><p><a href="review.html">打开款式核查总表与设计比较 →</a></p><p class="caption">共{audit_count}项核查记录；有记录不等于所有字段已确认。</p></section>'
    added = max((i.get("added_at", "") for i in items), default="")
    newest = [i for i in items if added and i.get("added_at") == added]
    if newest:
        body += '<section class="section"><h2>'+esc(added)+' 新增'+str(len(newest))+'款</h2><p>新增条目分别记录图片、规格、反馈和来源缺口，原店信息不齐的字段继续标注待核。</p><div class="link-row">'+''.join(f'<a href="../items/{esc(i["id"])}.html">{esc(i["name"])} →</a>' for i in newest)+'</div></section>'
    references = [i for i in items if i["research_record"].get("retailer_reference")]
    if references:
        body += '<section class="section"><h2>公开商品资料</h2><p>以下款式已补独立零售页的材质陈述、套装说明和厘米尺码表，可从款式详情直接查看。各款分别注明来源和对应依据；原店同批次参数仍待复核，海外报价与淘宝价分开。</p><div class="link-row">'+''.join(f'<a href="../items/{esc(i["id"])}.html#retailer-reference">{esc(i["name"])} →</a>' for i in references)+'</div></section>'
    body += '<div class="controls"><label>搜索款名或品牌<input id="sweet-search" type="search" placeholder="例如：梦呓蝶、奶油喵"></label><label>店铺<select id="brand-filter"><option value="">全部店铺</option>' + ''.join(f'<option>{esc(b)}</option>' for b in dict.fromkeys(i["brand"] for i in items)) + '</select></label><button id="clear-filter" type="button">清除筛选</button><span class="count" id="result-count" aria-live="polite">显示'+str(len(items))+'个条目</span></div><div class="grid" id="sweet-grid">'
    for item in items:
        url = '../items/'+item['id']+'.html'
        visual = f'<a class="visual" href="{url}"><img src="../{esc(item["posters"][0])}" alt="{esc(item["name"])}参考图" loading="lazy"></a>' if item.get('posters') else f'<a class="visual empty" href="{url}">对版图片待补</a>'
        body += f'<article class="tile" data-brand="{esc(item["brand"])}" data-search="{esc(item["name"]+" "+item["brand"])}">{visual}<div class="tile-body"><div class="brand">{esc(item["brand"])}</div><h2><a href="{url}">{esc(item["name"])}</a></h2><p class="version">{esc(item["research_record"]["version"])}</p><span class="pill">{esc(item["status_label"])}</span><p class="price">{esc(item["price"]["display_label"])}</p><p class="caption">{esc(item.get("image_note") or "先保留有据可查的条目，不用近似款代图")}</p><a class="open" href="{url}">看款式资料与来源 →</a></div></article>'
    body += '</div><p id="empty-state" class="empty-state" hidden>没有匹配条目，试试其他款名或清除筛选。</p>'
    body += '<section class="section"><h2>本批先讨论什么</h2><ol><li>胸口覆盖、裙长与遮蔽：把身高、尺码、内搭和裙撑条件一起展示。</li><li>外观与触感：同版同色再比较，不从亮闪图片或“丝绒”款名推断成分。</li><li>单裙与小物：包含物、固定方式及每组发货期分别列清楚。</li></ol><p class="caption">这些问题来自有限样本，不用于热销排名、复购率或新店利润判断。</p></section>'
    body += f'<section class="section"><h2>采样与来源</h2><p>累计读取{sampling["read_records"]}篇小红书记录，{sampling["excluded_records"]}篇因误配或未能识别目标而未纳入，保留以下{source_count}篇相关材料。按品牌、款名、实穿和相反意见主动选读，非随机样本；并非每个新增款式都有小红书覆盖。互动数不相加成销量，视频尚未观看。店铺和品牌同名账号的经营主体、原创权属未全部核验。</p><p class="caption">{esc(sampling.get("notes", ""))}</p><ol class="source-list">'
    for s in sample_sources:
        body += f'<li><a href="{esc(s["url"])}" target="_blank" rel="noopener">{esc(s["title"])} ↗</a><small>{esc(s["kind"])}</small></li>'
    body += '</ol><details><summary>一条同名候选为何撤回？</summary><p>原“蜜语糖匣·萌兔物语OP”缺独立商品依据；实际读到的同名测评属于小花猪水手服，已排除，另补青提咩咩候选。这不证明原款一定不存在。</p><a href="https://www.xiaohongshu.com/explore/6a3d440a000000000f0178c8" target="_blank" rel="noopener">查看被排除的同名原帖 ↗</a></details></section>'
    excluded = [s for s in sampling.get("excluded_details", []) if "6a3d440a000000000f0178c8" not in s["url"]]
    if excluded:
        body += '<section class="section"><details><summary>其他已读但未纳入的笔记</summary><ul>'+''.join('<li>'+esc(s["reason"])+ ' <a href="'+esc(s["url"])+ '" target="_blank" rel="noopener">对应来源 ↗</a></li>' for s in excluded)+'</ul></details></section>'
    script = '''<script>
const cards=Array.from(document.querySelectorAll('.tile')), search=document.getElementById('sweet-search'), brand=document.getElementById('brand-filter');
function filterCards(){const q=search.value.trim().toLowerCase();let count=0;cards.forEach(c=>{const show=(!q||c.dataset.search.toLowerCase().includes(q))&&(!brand.value||c.dataset.brand===brand.value);c.hidden=!show;if(show)count++});document.getElementById('result-count').textContent='显示'+count+'个条目';document.getElementById('empty-state').hidden=count>0}
search.addEventListener('input',filterCards);brand.addEventListener('change',filterCards);document.getElementById('clear-filter').addEventListener('click',()=>{search.value='';brand.value='';filterCards()});
</script>'''
    return shell('甜系款式调研', body+script, updated=updated)


def build_topic(root, items):
    selected = [i for i in items if i.get('research_record')]
    selected.sort(key=lambda i: (i.get('added_at', ''), i.get('verified_at', '')), reverse=True)
    if not selected:
        return
    path = root / 'data/topics/sweet_sources.json'
    sample_sources = json.loads(path.read_text()) if path.exists() else []
    sampling_path = root / 'data/topics/sweet_sampling.json'
    sampling = json.loads(sampling_path.read_text()) if sampling_path.exists() else None
    dest = root / 'sweet'
    dest.mkdir(exist_ok=True)
    (dest/'index.html').write_text(render_topic(selected, sample_sources, sampling))
    review_path = root/'data/topics/sweet_review.json'
    if review_path.exists():
        (dest/'review.html').write_text(render_review(selected, json.loads(review_path.read_text())))
