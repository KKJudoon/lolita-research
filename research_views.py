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
}


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
    if r.get("retailer_reference"):
        body += render_retailer_reference(r["retailer_reference"], sources)
    body += '<section class="section"><h2>价格与发货</h2><p>'+esc(item["price"]["note"])+'</p>'
    records = r.get("price_records", [])
    selected = [p for p in records if p["basis"] == "selected_sku_display"]
    if selected:
        body += '<div class="table-scroll"><table><thead><tr><th>选定组合</th><th>页面展示价</th><th>发货文案</th><th>商品原页</th></tr></thead><tbody>'
        for p in selected:
            body += f'<tr><td>{esc(" / ".join(p["selection"]))}<small>SKU {esc(p["sku_id"])}</small></td><td>¥{esc(p["amount_cny"])}</td><td>{esc(p["shipping_text"])}</td><td><a href="{esc(p["url"])}" target="_blank" rel="noopener">对应SKU ↗</a></td></tr>'
        body += '</tbody></table></div><p class="caption">2026-10-24 16:18：选齐颜色组合与M码后记录；未核结算优惠及实付。</p>'
    elif records:
        labels = {"store_card_unselected":"未选SKU的店铺卡片价", "historical_third_party_reference":"历史图鉴参考", "unselected_minimum_not_dress_price":"未选SKU最低展示，不能当单裙价", "promotion_title_sku_unknown":"推广标题线索，SKU与权益未核", "uncertain_visible_comment":"不确定的评论报价，不能当官方价"}
        body += '<ul>' + ''.join(f'<li>¥{esc(p["amount_cny"])}：{esc(labels.get(p["basis"], p["basis"]))}</li>' for p in records) + '</ul>'
    else:
        body += '<p class="muted">尚无与此研究目标对应的官方SKU报价。</p>'
    body += '</section><section class="section"><h2>用户反馈与适用条件</h2>'
    if r["feedback"]:
        for f in r["feedback"]:
            s = sources[f["source"]]
            label = "零售页评价／批次与独立性未核" if f["nature"] == "retailer_review_visible_self_report" else "个体自述／可见评论"
            body += f'<article class="feedback"><div class="kind">{esc(label)}</div><p>{esc(f["summary"])}</p><a href="{esc(s["url"])}" target="_blank" rel="noopener">查看对应来源 ↗</a></article>'
        body += '<p class="caption">正文与可见评论已读；未观看的视频不写成视频结论。版本、配色、体型、渠道和推广关系未全部统一。</p>'
    else:
        body += '<p class="muted">尚无与本条目具体版本对应的独立实穿材料；宣传不替代用户验收。</p>'
    body += '</section><section class="section"><h2>还需核验</h2><ul>' + ''.join('<li>'+esc(x)+'</li>' for x in r["unknowns"]) + '</ul></section>'
    body += '<section class="section"><h2>设计讨论问题</h2><p class="question">'+esc(r["discussion"])+'</p><p class="caption">这是后续验证问题，不代表已确定的产品定位、定价或质量结论。</p></section>'
    body += '<section class="section"><h2>原始来源</h2><ul class="sources">'
    for sid in r["source_refs"]:
        s = sources[sid]
        body += f'<li><a href="{esc(s["url"])}" target="_blank" rel="noopener">{esc(KINDS.get(s["kind"],s["kind"]))} · {esc(sid)} ↗</a><small>{esc(s["scope"])}</small></li>'
    if item.get("image_source_url"):
        body += f'<li><a href="{esc(item["image_source_url"])}" target="_blank" rel="noopener">参考图片出处 ↗</a><small>{esc(item.get("image_note", ""))}</small></li>'
    body += '</ul></section>'
    return shell(item["name"], body, updated=updated)


def render_topic(items, sample_sources):
    updated = max(i.get("verified_at", "2026-10-24") for i in items)
    body = f'<header class="hero"><div class="eyebrow">SWEET LOLITA · {esc(updated.replace("-", "."))} 更新</div><h1>甜系款式调研</h1><p>从具体款式、配件和穿着反馈出发，记录已经读到的材料，也保留版本、价格与规格的缺口。点击款式可看SKU、正反反馈和原始来源。</p><div class="stats"><div><strong>3</strong> <span>家店铺线索</span></div><div><strong>6</strong> <span>个研究条目</span></div><div><strong>17</strong> <span>篇小红书相关材料</span></div></div><p class="muted">本批为1个系列待选款、5个款式候选；17篇材料中含2篇品牌同名账号宣传，不代表17名独立买家。</p></header>'
    references = [i for i in items if i["research_record"].get("retailer_reference")]
    if references:
        body += '<section class="section"><h2>本次补充：公开商品资料</h2><p>以下款式已补独立零售页的材质陈述、套装说明和厘米尺码表，可从款式详情直接查看。按相同商品图及结构建立对应；原店同批次参数仍待复核，海外报价与淘宝价分开。</p><div class="link-row">'+''.join(f'<a href="../items/{esc(i["id"])}.html#retailer-reference">{esc(i["name"])} →</a>' for i in references)+'</div></section>'
    body += '<div class="controls"><label>搜索款名或品牌<input id="sweet-search" type="search" placeholder="例如：梦呓蝶、蜜语糖匣"></label><label>店铺<select id="brand-filter"><option value="">全部店铺</option>' + ''.join(f'<option>{esc(b)}</option>' for b in dict.fromkeys(i["brand"] for i in items)) + '</select></label><button id="clear-filter" type="button">清除筛选</button><span class="count" id="result-count" aria-live="polite">显示6个条目</span></div><div class="grid" id="sweet-grid">'
    for item in items:
        url = '../items/'+item['id']+'.html'
        visual = f'<a class="visual" href="{url}"><img src="../{esc(item["posters"][0])}" alt="{esc(item["name"])}参考图" loading="lazy"></a>' if item.get('posters') else f'<a class="visual empty" href="{url}">对版图片待补</a>'
        body += f'<article class="tile" data-brand="{esc(item["brand"])}" data-search="{esc(item["name"]+" "+item["brand"])}">{visual}<div class="tile-body"><div class="brand">{esc(item["brand"])}</div><h2><a href="{url}">{esc(item["name"])}</a></h2><p class="version">{esc(item["research_record"]["version"])}</p><span class="pill">{esc(item["status_label"])}</span><p class="price">{esc(item["price"]["display_label"])}</p><p class="caption">{esc(item.get("image_note") or "先保留有据可查的条目，不用近似款代图")}</p><a class="open" href="{url}">看款式资料与来源 →</a></div></article>'
    body += '</div><p id="empty-state" class="empty-state" hidden>没有匹配条目，试试其他款名或清除筛选。</p>'
    body += '<section class="section"><h2>本批先讨论什么</h2><ol><li>胸口覆盖、裙长与遮蔽：把身高、尺码、内搭和裙撑条件一起展示。</li><li>外观与触感：同版同色再比较，不从亮闪图片或“丝绒”款名推断成分。</li><li>单裙与小物：包含物、固定方式及每组发货期分别列清楚。</li></ol><p class="caption">这些问题来自有限样本，不用于热销排名、复购率或新店利润判断。</p></section>'
    body += '<section class="section"><h2>采样与来源</h2><p>累计读取18篇小红书记录，排除1篇同名误配，保留以下17篇相关材料。按品牌、款名、实穿和相反意见主动选读，非随机样本；互动数不相加成销量，视频尚未观看。店铺和品牌同名账号的经营主体、原创权属未全部核验。</p><ol class="source-list">'
    for s in sample_sources:
        body += f'<li><a href="{esc(s["url"])}" target="_blank" rel="noopener">{esc(s["title"])} ↗</a><small>{esc(s["kind"])}</small></li>'
    body += '</ol><details><summary>一条同名候选为何撤回？</summary><p>原“蜜语糖匣·萌兔物语OP”缺独立商品依据；实际读到的同名测评属于小花猪水手服，已排除，另补青提咩咩候选。这不证明原款一定不存在。</p><a href="https://www.xiaohongshu.com/explore/6a3d440a000000000f0178c8" target="_blank" rel="noopener">查看被排除的同名原帖 ↗</a></details></section>'
    script = '''<script>
const cards=Array.from(document.querySelectorAll('.tile')), search=document.getElementById('sweet-search'), brand=document.getElementById('brand-filter');
function filterCards(){const q=search.value.trim().toLowerCase();let count=0;cards.forEach(c=>{const show=(!q||c.dataset.search.toLowerCase().includes(q))&&(!brand.value||c.dataset.brand===brand.value);c.hidden=!show;if(show)count++});document.getElementById('result-count').textContent='显示'+count+'个条目';document.getElementById('empty-state').hidden=count>0}
search.addEventListener('input',filterCards);brand.addEventListener('change',filterCards);document.getElementById('clear-filter').addEventListener('click',()=>{search.value='';brand.value='';filterCards()});
</script>'''
    return shell('甜系款式调研', body+script, updated=updated)


def build_topic(root, items):
    selected = [i for i in items if i.get('research_record')]
    if not selected:
        return
    path = root / 'data/topics/sweet_sources.json'
    sample_sources = json.loads(path.read_text()) if path.exists() else []
    dest = root / 'sweet'
    dest.mkdir(exist_ok=True)
    (dest/'index.html').write_text(render_topic(selected, sample_sources))
