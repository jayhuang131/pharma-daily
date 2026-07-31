# -*- coding: utf-8 -*-
"""生物医药/创新药 多渠道聚合抓取脚本。
从权威公开渠道（RSS + 免费 API）拉取近期动态，分类去重，输出 pharma_raw.json。
标题/摘要为原文（多为英文），中文摘要由生成步骤补写进 pharma_final.json。
"""
import json, re, time, urllib.request, urllib.parse, socket, html as ihtml, ssl
import xml.etree.ElementTree as ET
from email.utils import parsedate_to_datetime
from datetime import datetime, timezone, timedelta

socket.setdefaulttimeout(30)
UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"

NEWS_DAYS = 3     # 行业媒体新闻窗口
CT_DAYS   = 4     # 临床试验窗口
PAPER_DAYS= 7     # 论文窗口
PER_FEED  = 8     # 每个媒体源最多保留条数
PER_CT    = 6
PER_PAPER = 10

NOW = datetime.now(timezone.utc)

def http(url, tries=3, timeout=15, ssl_loose=False, extra_headers=None):
    last = None
    ctx = ssl.create_default_context()
    if ssl_loose:
        ctx.check_hostname = False
        ctx.verify_mode = ssl.CERT_NONE
    headers = {"User-Agent": UA, "Accept": "*/*"}
    if extra_headers:
        headers.update(extra_headers)
    for i in range(tries):
        try:
            req = urllib.request.Request(url, headers=headers)
            with urllib.request.urlopen(req, timeout=timeout, context=ctx) as r:
                return r.read()
        except Exception as e:
            last = e
            time.sleep(1.2 * (i + 1))
    raise last

def reachable(host, timeout=5):
    """快速连通性预检，避免被墙/不可达主机长时间阻塞。"""
    try:
        req = urllib.request.Request(host, headers={"User-Agent": UA})
        with urllib.request.urlopen(req, timeout=timeout) as r:
            return r.status < 500
    except Exception:
        return False

def lname(tag):
    return tag.split("}")[-1].lower()

def clean(s):
    if not s:
        return ""
    s = ihtml.unescape(s)
    s = s.replace("<![CDATA[", "").replace("]]>", " ")  # 先去 CDATA 包裹，避免被当标签删掉
    s = re.sub(r"<[^>]+>", " ", s)          # 去 HTML 标签
    s = re.sub(r"\s+", " ", s).strip()
    return s

def parse_time(raw):
    if not raw:
        return None
    raw = raw.strip()
    try:
        dt = parsedate_to_datetime(raw)     # RFC822
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=timezone.utc)
        return dt.astimezone(timezone.utc)
    except Exception:
        pass
    try:
        return datetime.fromisoformat(raw.replace("Z", "+00:00")).astimezone(timezone.utc)
    except Exception:
        pass
    # 只有日期
    for f in ("%Y-%m-%d", "%Y/%m/%d"):
        try:
            return datetime.strptime(raw[:10], f).replace(tzinfo=timezone.utc)
        except Exception:
            pass
    return None

def parse_feed(xml_bytes, source, default_section):
    root = ET.fromstring(xml_bytes)
    items = []
    # RSS <item> / RDF <item> / Atom <entry>
    nodes = [e for e in root.iter() if lname(e.tag) in ("item", "entry")]
    for node in nodes:
        d = {}
        for ch in node:
            ln = lname(ch.tag)
            if ln in ("title",) and "title" not in d:
                d["title"] = clean(ch.text)
            elif ln == "link":
                # Atom link 可能在 href 属性
                if ch.text and ch.text.strip():
                    d.setdefault("url", ch.text.strip())
                elif ch.get("href"):
                    d.setdefault("url", ch.get("href"))
            elif ln in ("pubdate", "date", "published", "updated", "coverdate"):
                d.setdefault("time", parse_time(ch.text))
            elif ln in ("description", "summary", "encoded", "content"):
                d.setdefault("desc", clean(ch.text))
        if d.get("title") and d.get("url"):
            items.append({
                "title": d["title"],
                "url": d["url"],
                "source": source,
                "time": d["time"].strftime("%Y-%m-%dT%H:%M:%SZ") if d.get("time") else None,
                "desc": d.get("desc", ""),
                "section": default_section,
            })
    return items

def classify(title, desc, default):
    t = (title + " " + desc).lower()
    if any(k in t for k in ["approv", "clearance", "authoriz", "licens", "fda grants", "fda ok", "nmpa",
                             "获批", "批准", "上市许可", "fast track", "breakthrough therap", "快速通道", "孤儿药"]):
        return "监管审批"
    if any(k in t for k in ["phase 1", "phase 2", "phase 3", "phase i", "phase ii", "trial", "临床", "nct0"]):
        return "临床试验"
    # 交易速览（并购/融资/合作/IPO）
    deal = ["acqui", "merger", "merge", "buyout", "takeover", "ipo", "spac",
            "licens deal", "partnership", "collaboration", "joint venture",
            "financing", "raise", "series a", "series b", "funding",
            "收购", "并购", "融资", "IPO", "合作", "授权", "许可", "交易"]
    if any(k in t for k in deal):
        if not any(k in t for k in ["appoint", "resign", "board chairman", "phase", "trial",
                                     "award", "grant of", "inducement"]):
            return "交易速览"
    # 政策追踪（NMPA/CDE/医保/集采）
    if any(k in t for k in ["nmpa", "cde", "legislation", "regulatory framework",
                             "监管政策", "法规", "指南修订", "监管改革", "医保", "集采",
                             "招标", "定价", "目录调整", "药品法"]):
        return "政策追踪"
    if any(k in t for k in ["opinion", "editorial", "commentary", "perspective", "viewpoint", "policy", "analysis:", "观点", "评论"]):
        return "政策与观点"
    return default

# ---------- 1) 国际行业媒体 RSS ----------
RSS_FEEDS = [
    ("Endpoints News",            "https://endpts.com/feed/"),
    ("STAT News",                 "https://www.statnews.com/feed/"),
    ("Pharma Times",              "https://www.pharmatimes.com/rss"),
    ("Pharmaceutical Executive",  "https://www.pharmexec.com/rss"),
    ("Nat Rev Drug Discovery",    "https://www.nature.com/nrd.rss"),
]

def fetch_rss():
    out = []
    cutoff = NOW - timedelta(days=NEWS_DAYS)
    for source, url in RSS_FEEDS:
        try:
            items = parse_feed(http(url), source, "行业动态")
        except Exception as e:
            print(f"  [RSS] {source} 抓取失败: {e}")
            continue
        kept = 0
        for it in items:
            t = parse_time(it["time"]) if it["time"] else None
            if t is None or t < cutoff:
                continue
            it["section"] = ("论文研究" if source == "Nat Rev Drug Discovery"
                             else classify(it["title"], it["desc"], "行业动态"))
            out.append(it)
            kept += 1
            if kept >= PER_FEED:
                break
        print(f"  [RSS] {source}: 保留 {kept} 条")
    return out

# ---------- 2) ClinicalTrials.gov 临床试验（药物干预） ----------
def fetch_clinicaltrials():
    start = (NOW - timedelta(days=CT_DAYS)).strftime("%Y-%m-%d")
    end = NOW.strftime("%Y-%m-%d")
    adv = f"AREA[StudyFirstPostDate]RANGE[{start},{end}] AND AREA[InterventionType]DRUG"
    url = ("https://clinicaltrials.gov/api/v2/studies?format=json&pageSize=60"
           "&filter.advanced=" + urllib.parse.quote(adv))
    try:
        d = json.loads(http(url).decode("utf-8", "ignore"))
    except Exception as e:
        print("  [CT] 抓取失败:", e)
        return []
    out = []
    for s in d.get("studies", []):
        p = s.get("protocolSection", {})
        idm = p.get("identificationModule", {})
        stm = p.get("statusModule", {})
        des = p.get("descriptionModule", {})
        cond = p.get("conditionsModule", {})
        nct = idm.get("nctId")
        title = idm.get("briefTitle") or idm.get("officialTitle")
        if not (nct and title):
            continue
        org = (idm.get("organization") or {}).get("fullName") or (p.get("sponsorCollaboratorsModule", {}).get("leadSponsor") or {}).get("name", "")
        conds = "、".join((cond.get("conditions") or [])[:3])
        brief = clean(des.get("briefSummary", ""))[:220]
        date = (stm.get("studyFirstPostDateStruct") or {}).get("date") or stm.get("lastUpdatePostDateStruct", {}).get("date")
        t = parse_time(date) if date else None
        out.append({
            "title": title,
            "url": f"https://clinicaltrials.gov/study/{nct}",
            "source": "ClinicalTrials.gov",
            "time": t.strftime("%Y-%m-%dT%H:%M:%SZ") if t else None,
            "desc": f"登记号 {nct}；申办方 {org}；适应症 {conds}。{brief}",
            "section": "临床试验",
            "_nct": nct,
        })
        if len(out) >= PER_CT:
            break
    print(f"  [CT] ClinicalTrials.gov: 保留 {len(out)} 条")
    return out

# ---------- 3) Europe PMC 论文 ----------
def fetch_papers():
    start = (NOW - timedelta(days=PAPER_DAYS)).strftime("%Y-%m-%d")
    end = NOW.strftime("%Y-%m-%d")
    q = (f'FIRST_PDATE:[{start} TO {end}] AND '
         '(drug OR therapeutic OR inhibitor OR antibody OR vaccine OR oncology OR "clinical trial" OR pharmacology OR "drug discovery")')
    params = {"format": "json", "resultType": "core", "pageSize": "40",
              "sort": "FIRST_PDATE_D desc", "query": q}
    url = "https://www.ebi.ac.uk/europepmc/webservices/rest/search?" + urllib.parse.urlencode(params)
    try:
        d = json.loads(http(url).decode("utf-8", "ignore"))
    except Exception as e:
        print("  [PMC] 抓取失败:", e)
        return []
    out = []
    for r in d.get("resultList", {}).get("result", []):
        title = clean(r.get("title", ""))
        if not title:
            continue
        date = r.get("firstPublicationDate") or r.get("firstIndexDate")
        t = parse_time(date) if date else None
        doi = r.get("doi")
        pmid = r.get("pmid")
        url2 = f"https://doi.org/{doi}" if doi else (f"https://europepmc.org/article/MED/{pmid}" if pmid else "")
        if not url2:
            continue
        journal = r.get("journalTitle") or ""
        abstr = clean(r.get("abstractText", ""))[:260]
        out.append({
            "title": title,
            "url": url2,
            "source": "Europe PMC",
            "time": t.strftime("%Y-%m-%dT%H:%M:%SZ") if t else None,
            "desc": f"期刊 {journal}。{abstr}",
            "section": "论文研究",
        })
        if len(out) >= PER_PAPER:
            break
    print(f"  [PMC] Europe PMC: 保留 {len(out)} 条")
    return out

# ---------- 4) 北京经开区（亦庄）政府官网：生物医药相关新闻 ----------
YZ_COLS = [
    "https://kfqgw.beijing.gov.cn/ywdt/",                     # 要闻动态
    "https://kfqgw.beijing.gov.cn/ywdt/gzdt/index.html",      # 工作动态
    "https://kfqgw.beijing.gov.cn/ywdt/gdcyfzgd/index.html",  # 高端产业发展高地
    "https://kfqgw.beijing.gov.cn/cxyzkfq/",                  # 创新亦庄
]
YZ_BIO = ["医药", "生物医药", "创新药", "药企", "制药", "药品", "疫苗", "基因", "细胞",
          "医疗器械", "临床", "诊断", "生命科学", "生物技术", "医疗健康", "肿瘤医院",
          "新药", "药物", "医药工业"]
YZ_DAYS = 8
YZ_PAGES = ["index.html", "index_1.html", "index_2.html"]

def _yz_body_desc(page_html):
    m = re.search(r'class="details_page"([\s\S]*)', page_html)
    seg = m.group(1) if m else page_html
    seg = re.sub(r"<script[\s\S]*?</script>", " ", seg)
    seg = re.sub(r"<style[\s\S]*?</style>", " ", seg)
    txt = re.sub(r"<[^>]+>", " ", seg)
    txt = ihtml.unescape(txt)
    txt = re.sub(r"\s+", " ", txt).strip()
    # 去掉“标题 来源：… 时间：… 分享：… 打印 收藏”头部，只留正文
    if "收藏" in txt:
        txt = txt.split("收藏", 1)[1].strip()
    return txt[:280]

def fetch_yizhuang():
    cutoff = NOW - timedelta(days=YZ_DAYS)
    seen, out = set(), []
    for col in YZ_COLS:
        base = col if col.endswith("/") else col[:col.rfind("/") + 1]
        for pg in YZ_PAGES:
            page = urllib.parse.urljoin(base, pg)
            try:
                h = http(page).decode("utf-8", "ignore")
            except Exception:
                continue
            for m in re.finditer(r'<a[^>]+href="([^"]*t(\d{8})_\d+\.html)"[^>]*?(?:title="([^"]*)")?[^>]*>(.*?)</a>', h, re.S):
                href, d8, tattr, text = m.groups()
                title = (tattr or re.sub(r"<[^>]+>", "", text)).strip()
                absu = urllib.parse.urljoin(page, href)
                if not title or absu in seen:
                    continue
                seen.add(absu)
                if not any(k in title for k in YZ_BIO):
                    continue
                try:
                    dt = datetime.strptime(d8, "%Y%m%d").replace(tzinfo=timezone.utc)
                except Exception:
                    continue
                if dt < cutoff:
                    continue
                out.append({
                    "title": title,
                    "url": absu,
                    "source": "北京亦庄·经开区官网",
                    "time": dt.strftime("%Y-%m-%dT%H:%M:%SZ"),
                    "desc": "",
                    "section": "亦庄园区动态",
                })
    # 抓正文作摘要素材
    for it in out:
        try:
            it["desc"] = _yz_body_desc(http(it["url"]).decode("utf-8", "ignore"))
        except Exception:
            pass
    out.sort(key=lambda x: x["time"], reverse=True)
    print(f"  [YZ] 北京亦庄官网: 保留 {len(out)} 条")
    return out

# ---------- 5) Google News RSS（中英多查询，兜底聚合全球/亚洲/公司PR） ----------
GN_DAYS = 3
GN_PER_QUERY = 6
# (查询串, 语言) —— 覆盖全球医药媒体、监管里程碑、AI 药企与公司 PR
GN_QUERIES = [
    ("biopharma FDA approval OR fast track OR breakthrough therapy", "en"),
    ("cancer drug phase 3 clinical trial results", "en"),
    ("Insilico OR Recursion OR Absci OR Schrodinger AI drug discovery", "en"),
    ("创新药 获批 OR 临床 OR FDA 快速通道", "zh"),
    ("港股 生物医药 公告 获批 OR 临床", "zh"),
    ("英矽智能 OR 港股 创新药 公告", "zh"),
]
# 相关性过滤（命中任一才保留，避免无关资讯）
GN_BIO = ["药", "制药", "临床", "试验", "获批", "批准", "上市", "疗法", "肿瘤", "癌症",
          "biopharm", "pharma", "drug", "clinical", "trial", "fda", "approval", "therapy",
          "vaccine", "antibody", "oncolog", "medic", "biosimilar", "biotech", "gen", "cell",
          "fast track", "breakthrough", "nda", "inda", "管线", "适应症", "创新药"]

def _gn_params(q, lang):
    if lang == "zh":
        return urllib.parse.urlencode({"q": q, "hl": "zh-CN", "gl": "CN", "ceid": "CN:zh-Hans"})
    return urllib.parse.urlencode({"q": q, "hl": "en-US", "gl": "US", "ceid": "US:en"})

def parse_gn(xml_bytes, lang):
    """解析 Google News RSS：标题形如 'Headline - Publisher'，去除后缀；来源取 <source>。"""
    try:
        root = ET.fromstring(xml_bytes)
    except Exception:
        return []
    out = []
    for node in [e for e in root.iter() if lname(e.tag) in ("item", "entry")]:
        d = {}
        for ch in node:
            ln = lname(ch.tag)
            if ln == "title" and "title" not in d:
                d["title"] = clean(ch.text)
            elif ln == "link":
                if ch.text and ch.text.strip():
                    d.setdefault("url", ch.text.strip())
                elif ch.get("href"):
                    d.setdefault("url", ch.get("href"))
            elif ln in ("pubdate", "date", "published"):
                d.setdefault("time", parse_time(ch.text))
            elif ln == "source":
                d.setdefault("src", clean(ch.text))
            elif ln in ("description", "summary", "content"):
                d.setdefault("desc", clean(ch.text))
        if not (d.get("title") and d.get("url")):
            continue
        title = d["title"]
        # 去掉 " - Publisher" 后缀
        if " - " in title:
            head, _, pub = title.rpartition(" - ")
            if pub and len(pub) < 40:
                title = head
        out.append({
            "title": title,
            "url": d["url"],
            "source": d.get("src") or "Google News",
            "time": d["time"].strftime("%Y-%m-%dT%H:%M:%SZ") if d.get("time") else None,
            "desc": d.get("desc", ""),
        })
    return out

def fetch_google_news():
    cutoff = NOW - timedelta(days=GN_DAYS)
    out, seen = [], set()
    if not reachable("https://news.google.com", 5):
        print("  [GN] Google News 当前环境不可达，跳过（在可访问外网的机器上会自动生效）")
        return out
    for q, lang in GN_QUERIES:
        url = "https://news.google.com/rss/search?" + _gn_params(q, lang)
        try:
            items = parse_gn(http(url, tries=1, timeout=8), lang)
        except Exception as e:
            print(f"  [GN] 查询失败 [{q[:30]}…]: {e}")
            continue
        kept = 0
        for it in items:
            t = parse_time(it["time"]) if it["time"] else None
            if t is None or t < cutoff:
                continue
            blob = (it["title"] + " " + it["desc"]).lower()
            if not any(k in blob for k in GN_BIO):
                continue
            key = it["url"]
            if key in seen:
                continue
            seen.add(key)
            it["section"] = classify(it["title"], it["desc"], "行业动态")
            out.append(it)
            kept += 1
            if kept >= GN_PER_QUERY:
                break
        print(f"  [GN] {lang} 查询「{q[:24]}…」: 保留 {kept} 条")
    print(f"  [GN] Google News 合计: {len(out)} 条")
    return out

# ---------- 6) 新浪财经 feed 聚合（国内可通，替代 Google News 在受限网络中的角色） ----------
SN_DAYS = 3
SN_NUM = 8          # 每查询取 n 条
SN_MAX  = 6         # 每查询上限保留
# 关键词（新浪 feed 不支持布尔，用独立查询分别触发）
SN_KEYS = [
    "创新药 获批",
    "FDA 快速通道",
    "生物医药 临床试验",
    "英矽智能",
    "港股 创新药 公告",
    "肿瘤 新药 突破性疗法",
]

def fetch_sina_news():
    if not reachable("https://feed.mix.sina.com.cn", 5):
        print("  [SN] 新浪 feed 不可达，跳过")
        return []
    cutoff = NOW - timedelta(days=SN_DAYS)
    out, seen = [], set()
    for kw in SN_KEYS:
        params = urllib.parse.urlencode({"pageid": "153", "lid": "2510",
                                          "k": kw, "num": str(SN_NUM), "page": "1"})
        url = "https://feed.mix.sina.com.cn/api/roll/get?" + params
        try:
            raw = http(url, tries=1, timeout=10).decode("utf-8", "ignore")
            data = json.loads(raw)
            items = data.get("result", {}).get("data", [])
        except Exception as e:
            print(f"  [SN] 查询失败 [{kw}]: {e}")
            continue
        kept = 0
        for it in items:
            title = (it.get("title") or "").strip()
            link  = (it.get("url") or it.get("wapurl") or "").strip()
            if not (title and link):
                continue
            ts = it.get("ctime")
            t = None
            if ts:
                try:
                    t = datetime.fromtimestamp(float(ts), tz=timezone.utc)
                except Exception:
                    pass
            if t and t < cutoff:
                continue
            desc = (it.get("intro") or it.get("summary") or it.get("wapsummary") or "").strip()
            media = it.get("media_name") or "新浪新闻"
            blob = (title + " " + desc).lower()
            if not any(k in blob for k in GN_BIO):
                continue
            key = link
            if key in seen:
                continue
            seen.add(key)
            out.append({
                "title": title,
                "url": link,
                "source": media,
                "time": (t or NOW).strftime("%Y-%m-%dT%H:%M:%SZ"),
                "desc": desc,
                "section": classify(title, desc, "行业动态"),
            })
            kept += 1
            if kept >= SN_MAX:
                break
        print(f"  [SN] 查询「{kw}」: 保留 {kept} 条")
    print(f"  [SN] 新浪 feed 合计: {len(out)} 条")
    return out

# ---------- 7) 港交所 HKEXnews 上市公司公告（直接接口，可达时生效） ----------
HKEX_WATCH = ["3696", "1801", "962", "9926", "6990", "1177", "2196", "6160", "1952", "1501"]
def fetch_hkex():
    """尝试直接拉取 HKEXnews 上市公司公告；接口受反爬/重定向保护时优雅返回空，
    由 Google News 中对港交所/港股创新药的定向查询兜底覆盖。"""
    out = []
    if not reachable("https://www1.hkexnews.hk", 5):
        print("  [HKEX] HKEXnews 当前环境不可达，跳过（在可访问外网的机器上会自动生效）")
        return out
    try:
        body = ("lang=EN&market=SEH&category=0&searchType=0&stockId=&"
                "from=20260720&to=20260729&sortDir=0&sortByOptions=0&titleContains=&onlyOurNews=N")
        req = urllib.request.Request(
            "https://www1.hkexnews.hk/child/php/getnewannouncement.php",
            data=body.encode("utf-8"),
            headers={"User-Agent": UA, "Referer": "https://www1.hkexnews.hk/search/titlesearch.xhtml",
                     "Content-Type": "application/x-www-form-urlencoded", "Accept": "*/*"})
        raw = urllib.request.urlopen(req, timeout=15).read().decode("utf-8", "ignore")
        # 能解析出公告 JSON 才采用（结构随站点变动，解析失败即放弃）
        import json as _json
        data = _json.loads(raw)
        items = data if isinstance(data, list) else data.get("data") or data.get("result") or []
        for a in items:
            head = a.get("headline") or a.get("title") or ""
            if not head:
                continue
            out.append({
                "title": head,
                "url": a.get("pdfUrl") or a.get("url") or "",
                "source": "HKEXnews 公告 " + str(a.get("stockCode", "")),
                "time": (parse_time(a.get("publishedAt") or a.get("date")) or NOW).strftime("%Y-%m-%dT%H:%M:%SZ"),
                "desc": "",
                "section": classify(head, "", "行业动态"),
            })
        print(f"  [HKEX] 直接接口: 保留 {len(out)} 条")
    except Exception as e:
        print(f"  [HKEX] 直接接口暂不可用（{e}），已由 Google News 港股查询兜底")
    return out

# ---------- P1 渠道 ----------
SEC_UA = "Mozilla/5.0 (biopharma-report@agentos-app.net) Chrome/124.0 Safari/537.36"
BIOTECH_COS = {"pharma", "therap", "bioscien", "biotech", "oncology", "immun",
               "medicin", "vaccine", "cancer", "genomics", "genetics", "rna", "dna",
               "antibod", "protein", "drug", "molecular", "biolog", "cellular",
               "cell", "gene", "diagnost", "health", "scientif", "laborator"}

# --- P1a) FDA 新闻发布 RSS ---
FDA_RSS = "https://www.fda.gov/about-fda/contact-fda/stay-informed/rss-feeds/press-releases/rss.xml"

def fetch_fda_press():
    out = []
    try:
        items = parse_feed(http(FDA_RSS, tries=1, timeout=12, ssl_loose=True), "FDA Press", "监管审批")
    except Exception as e:
        print(f"  [FDA] 抓取失败: {e}")
        return out
    cutoff = NOW - timedelta(days=NEWS_DAYS)
    kept = 0
    for it in items:
        t = parse_time(it["time"]) if it["time"] else None
        if t is None or t < cutoff:
            continue
        blob = (it["title"] + " " + it.get("desc", "")).lower()
        if not any(k in blob for k in ["drug", "therap", "approv", "treat", "vaccin",
                                         "biolog", "oncology", "clinical", "device",
                                         "药品", "药", "临床", "治疗"]):
            continue
        it["section"] = classify(it["title"], it.get("desc", ""), "监管审批")
        out.append(it)
        kept += 1
        if kept >= 5:
            break
    print(f"  [FDA] FDA Press: 保留 {kept} 条")
    return out

# --- P1b) SEC EDGAR 8-K / 10-K 公告 ---
SEC_ATOM = "https://www.sec.gov/cgi-bin/browse-edgar?action=getcurrent&type=8-K&count=40&output=atom"

def parse_sec_atom(xml_bytes):
    """解析 SEC 的 ATOM XML：entry → title(company/form) / link / updated / summary"""
    root = ET.fromstring(xml_bytes)
    ns = "http://www.w3.org/2005/Atom"
    items = []
    for entry in root.iter(f"{{{ns}}}entry"):
        title = entry.find(f"{{{ns}}}title")
        link  = entry.find(f"{{{ns}}}link")
        updated = entry.find(f"{{{ns}}}updated")
        summary = entry.find(f"{{{ns}}}summary")
        if title is not None and title.text:
            items.append({
                "title": title.text.strip(),
                "url": link.get("href", "") if link is not None else "",
                "time": parse_time(updated.text) if updated is not None and updated.text else None,
                "desc": clean(summary.text) if summary is not None and summary.text else "",
            })
    return items

def fetch_sec_edgar():
    out = []
    try:
        raw = http(SEC_ATOM, tries=1, timeout=12, extra_headers={"User-Agent": SEC_UA})
        # SEC ATOM XML 用 ISO-8859-1
        try:
            txt = raw.decode("utf-8")
        except Exception:
            txt = raw.decode("iso-8859-1", "ignore")
        items = parse_sec_atom(txt.encode("utf-8") if isinstance(txt, str) else txt)
    except Exception as e:
        print(f"  [SEC] 抓取失败: {e}")
        return out
    cutoff = NOW - timedelta(days=NEWS_DAYS)
    kept = 0
    for it in items:
        t = it.get("time") or NOW
        if t < cutoff:
            continue
        title = it["title"]  # e.g. "8-K - Recursion Pharmaceuticals, Inc. (RXRX) (Filer)"
        if not any(k in title.lower() for k in BIOTECH_COS):
            continue  # 过滤到只有生物医药公司
        it["source"] = "SEC EDGAR"
        it["time"] = t.strftime("%Y-%m-%dT%H:%M:%SZ") if isinstance(t, datetime) else str(t)
        it["section"] = classify(title, it.get("desc", ""), "行业动态")
        if any(k in title.lower() for k in ["appoint", "departure", "resign", "compensation",
                                              "change in directors", "amendment to code",
                                              "shareholder director", "voting result"]):
            continue  # 去掉纯公司治理/人事变动噪音
        out.append(it)
        kept += 1
        if kept >= 8:
            break
    print(f"  [SEC] SEC EDGAR 8-K: 保留 {kept} 条")
    return out

# --- P1c) AI 药企 IR 新闻室 ---
IR_FEEDS = [
    ("Recursion IR",    "https://ir.recursion.com/rss/news-releases.xml"),
]

def fetch_company_ir():
    out = []
    for name, url in IR_FEEDS:
        try:
            items = parse_feed(http(url, tries=1, timeout=10), name, "行业动态")
        except Exception:
            continue
        cutoff = NOW - timedelta(days=NEWS_DAYS)
        kept = 0
        for it in items:
            t = parse_time(it["time"]) if it["time"] else None
            if t is None or t < cutoff:
                continue
            it["section"] = classify(it["title"], it.get("desc", ""), "行业动态")
            out.append(it)
            kept += 1
            if kept >= 3:
                break
        if kept:
            print(f"  [IR] {name}: 保留 {kept} 条")
    print(f"  [IR] 公司 IR 合计: {len(out)} 条")
    return out

def main():
    print("抓取窗口: 新闻 %d 天 / 临床 %d 天 / 论文 %d 天" % (NEWS_DAYS, CT_DAYS, PAPER_DAYS))
    items = []
    items += fetch_rss()
    items += fetch_clinicaltrials()
    items += fetch_papers()
    items += fetch_yizhuang()
    items += fetch_google_news()
    items += fetch_sina_news()
    items += fetch_hkex()
    items += fetch_fda_press()
    items += fetch_sec_edgar()
    items += fetch_company_ir()

    # 去重（按 url，其次按标题前40字）
    seen, dedup = set(), []
    for it in items:
        key = it["url"] or it["title"][:40].lower()
        if key in seen:
            continue
        seen.add(key)
        dedup.append(it)
    # 排序：版块固定顺序 + 版块内按时间倒序
    order = ["监管审批", "临床试验", "交易速览", "行业动态", "亦庄园区动态", "论文研究", "政策追踪", "政策与观点"]
    dedup.sort(key=lambda x: (order.index(x["section"]) if x["section"] in order else 99,
                              -(parse_time(x["time"]).timestamp() if x["time"] else 0)))
    json.dump(dedup, open("pharma_raw.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    from collections import Counter
    print("合计:", len(dedup), "条 | 版块分布:", dict(Counter(i["section"] for i in dedup)))
    print("已写出 pharma_raw.json")

if __name__ == "__main__":
    main()
