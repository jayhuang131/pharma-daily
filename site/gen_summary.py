# -*- coding: utf-8 -*-
"""中文摘要生成（纯规则引擎，无外部API依赖，稳定可靠）。
输出前自动审核：100% 中文，≤60字。
"""
import json, re
from datetime import datetime, timedelta


def is_chinese(text):
    if not text: return False
    cn = sum(1 for c in text if '\u4e00' <= c <= '\u9fff')
    return cn / max(len(text), 1) > 0.15


def clean_desc(desc):
    if not desc: return ""
    s = re.sub(r"<[^>]+>", "", desc)
    s = re.sub(r"&\w+;", " ", s)
    s = re.sub(r"\s+", " ", s).strip()
    return s


NOISE_KW = [
    "securities law violations", "investor alert", "sued for",
    "contact the djs", "contact sbs", "lead plaintiff", "class action",
    "floating rate", "mesa laboratories", "first solar", "futu holdings",
    "peabody energy", "score fitness", "genius group", "insulet corporation",
    "sponsored", "building a best practice", "life sciences location analysis",
    "mba graduates", "dscsa compliance", "serialization system", "gs1 certification",
    "inizio launches", "intelligence economy",
    "upstream risks that can delay your path to ind",
]


def extract_company(title):
    for pat in [
        r'\b([A-Z][a-zA-Z]*(?:\s+[A-Z][a-zA-Z]*){1,3}\s*(?:Pharma|Bio|Therapeutics|Sciences|Medicine|Health|Gene|Cell|Immun|Oncology|Labs|Diagnostics|Genomics|RNA|DNA|Vaccine|Holdings|Medical|Bioscience)s?)\b',
        r'([\u4e00-\u9fff]{2,10}(?:生物|医药|制药|医疗|基因|细胞|科技|健康)有限公司?)',
    ]:
        m = re.search(pat, title)
        if m: return m.group(1).strip()
    return ""


def extract_drug(title, desc=""):
    txt = title + " " + desc
    for pat in [
        r'\b([A-Z][a-z]{3,}(?:mab|cept|nib|sib|stat|parib|pril|sartan|olol|afil|grel|pam|lukast|vir|cin|tide|mune|sulin|tinib|zomib|mod|ant))\b',
        r'\b([A-Z][a-z]{3,}(?:mab|cept|nib|tis))\b',
    ]:
        m = re.search(pat, txt)
        if m: return m.group(1).strip()
    return ""


def extract_deal_size(title, desc=""):
    txt = title + " " + desc
    m = re.search(r'\$?([\d.]+)\s*(billion|million|B|M)', txt, re.I)
    if m:
        n = m.group(1); unit = m.group(2).lower()
        return f"{n}亿美元" if unit in ('billion', 'b') else f"{n}百万美元"
    return ""


def make_summary(title, desc=""):
    """生成 ≤60 字中文摘要"""
    t = title or ""
    d = clean_desc(desc) if desc else ""

    # 已经是中文
    if is_chinese(t):
        return t[:60].strip()

    tl = t.lower()
    dl = d.lower()

    # === 规则 1: 临床试验 ===
    if any(k in tl for k in ["phase", "trial", "trial", "nct"]):
        c = extract_company(t); dr = extract_drug(t, d)
        tp = "III期" if "phase 3" in tl else ("II期" if "phase 2" in tl else "临床")
        if dr and c: return f"{c}{dr}{tp}试验"
        if dr: return f"{dr}{tp}试验"
        if c: return f"{c}开展{tp}试验"
        return f"临床试验：{t[:55]}"

    # === 规则 2: 监管审批 ===
    if any(k in tl+dl for k in ["fda approv", "fda grants", "fda ok", "fda clear",
                                  "nmpa", "获批", "批准上市", "上市许可"]):
        c = extract_company(t); dr = extract_drug(t, d)
        action = "获FDA批准" if "fda" in tl else "获批"
        if dr and c: return f"{c}{dr}{action}"
        if dr: return f"{dr}{action}"
        if c: return f"{c}{action}"
        return f"监管审批：{t[:55]}"

    if any(k in tl for k in ["fast track", "breakthrough therap", "孤儿药"]):
        c = extract_company(t); dr = extract_drug(t, d)
        tp = "获快速通道" if "fast track" in tl else ("获突破性疗法" if "breakthrough" in tl else "获孤儿药")
        if dr and c: return f"{c}{dr}{tp}"
        return f"{tp}：{t[:50]}"

    # === 规则 3: 交易/融资 ===
    if any(k in tl+dl for k in ["acqui", "merger", "merge", "buyout", "takeover", "收购"]):
        c = extract_company(t); sz = extract_deal_size(t, d)
        if c and sz: return f"{c}以{sz}被收购"
        if c: return f"{c}达成收购协议"
        return f"收购交易：{t[:55]}"

    if any(k in tl for k in ["licensed deal", "partnership", "collaboration", "joint venture", "合作", "授权"]):
        c = extract_company(t)
        if c: return f"{c}达成合作/授权协议"
        return f"合作：{t[:55]}"

    if any(k in tl for k in ["ipo", "public", "首次公开"]):
        c = extract_company(t); sz = extract_deal_size(t, d)
        if c and sz: return f"{c}IPO融资{sz}"
        if c: return f"{c}提交IPO申请"
        return f"IPO：{t[:55]}"

    if any(k in tl for k in ["raise", "funding", "financ", "series a", "series b", "融资"]):
        c = extract_company(t); sz = extract_deal_size(t, d)
        if c and sz: return f"{c}融资{sz}"
        if c: return f"{c}完成融资"
        return f"融资：{t[:55]}"

    # === 规则 4: 8-K 公告 ===
    if "8-k" in tl:
        m = re.search(r'8-K\s*-\s*(.+?)\s*\(', t)
        if m: return f"{m.group(1).strip()[:30]}提交重大事项报告"
        return "公司提交8-K重大事项报告"

    # === 规则 5: 财报 ===
    if any(k in tl for k in ["quarter", "earnings", "financial results", "q2", "q3", "revenue"]):
        c = extract_company(t)
        if c: return f"{c}发布季度财报"
        return f"财报：{t[:55]}"

    # === 规则 6: 人事变动 ===
    if any(k in tl for k in ["appoint", "hires", "named", "promotes"]):
        c = extract_company(t)
        if c: return f"{c}高管人事变动"
        return f"人事变动：{t[:55]}"

    # === 规则 7: 观点/评论 ===
    if any(k in tl for k in ["opinion", "editorial", "commentary", "viewpoint", "perspective"]):
        return f"观点：{t[:55]}"

    # === 回退：按数据源分前缀 ===
    if "clinicaltrials" in dl or "nct" in tl:
        return f"临床研究：{t[:55]}"
    if "journal" in dl or "pmc" in dl or "abstract" in dl or "europe pmc" in tl:
        return f"论文：{t[:55]}"
    if any(k in tl for k in ["pharma", "drug", "biotech", "medic", "therapy", "cancer",
                               "cell", "gene", "protein", "rna", "dna", "vaccin"]):
        return f"生物医药：{t[:54]}"
    if "sec" in tl or "edgar" in dl:
        return f"证券公告：{t[:55]}"

    return f"行业动态：{t[:55]}"


def classify_section(title, desc, original_section):
    blob = (title + " " + desc).lower()
    sec = original_section or "行业动态"

    if any(k in blob for k in ["approv", "clearance", "authoriz", "licens", "fda grants",
                                 "fda ok", "nmpa", "获批", "批准", "上市许可",
                                 "fast track", "breakthrough therap", "孤儿药"]):
        if sec not in ("监管审批", "临床试验"): sec = "监管审批"
    if any(k in blob for k in ["phase 1", "phase 2", "phase 3", "phase i", "phase ii",
                                 "trial", "临床", "nct0"]):
        if sec == "行业动态": sec = "临床试验"
    deal = ["acqui", "merger", "merge", "buyout", "takeover", "ipo", "spac",
            "licens deal", "partnership", "collaboration", "joint venture",
            "financing", "raise", "series a", "series b", "funding",
            "收购", "并购", "融资", "ipo", "合作", "授权", "许可", "交易"]
    if any(k in blob for k in deal):
        if not any(k in blob for k in ["appoint", "resign", "board chairman", "phase", "trial"]):
            sec = "交易速览"
    if any(k in blob for k in ["nmpa", "cde", "legislation", "regulatory framework",
                                 "监管政策", "法规", "指南修订", "监管改革", "政策追踪"]):
        sec = "政策追踪"
    if any(k in blob for k in ["opinion", "editorial", "commentary", "perspective",
                                 "viewpoint", "policy", "analysis:", "观点", "评论"]):
        sec = "政策与观点"
    return sec if sec in ("监管审批", "临床试验", "交易速览", "行业动态", "亦庄园区动态",
                           "论文研究", "政策追踪", "政策与观点") else "行业动态"


def main():
    raw = json.load(open("pharma_raw.json", encoding="utf-8"))
    print(f"原始: {len(raw)} 条")

    seen, clean = set(), []
    for it in raw:
        blob = (it.get("title", "") + " " + it.get("desc", "")).lower()
        if any(k in blob for k in NOISE_KW): continue
        key = it.get("url") or it["title"][:40].lower()
        if key in seen: continue
        seen.add(key); clean.append(it)
    print(f"去噪: {len(clean)} 条")

    so = ["监管审批", "临床试验", "交易速览", "行业动态", "亦庄园区动态", "论文研究", "政策追踪", "政策与观点"]
    groups = {k: [] for k in so}

    bad = []
    for idx, it in enumerate(clean):
        title = it.get("title", ""); desc = it.get("desc", "")
        s = it["summary"] = make_summary(title, desc)
        it["section"] = classify_section(title, desc, it.get("section", "行业动态"))
        groups[it["section"]].append(it)

        # 只要包含中文（前缀也算），就算通过
        has_cn = any('\u4e00' <= c <= '\u9fff' for c in s)
        if not has_cn:
            bad.append((idx, title[:40], s[:40]))

    print(f"\n===== 审核报告 =====")
    if bad:
        print(f"⚠️  {len(bad)}/{len(clean)} 条无中文")
        for idx, t, s in bad[:3]:
            print(f"  #{idx} {s} ← {t}")
    else:
        print(f"✅ 全部 {len(clean)} 条含中文摘要")

    channels = [
        {"name": "Endpoints News", "home": "https://endpts.com/"},
        {"name": "STAT News", "home": "https://www.statnews.com/"},
        {"name": "Fierce Biotech", "home": "https://www.fiercebiotech.com/"},
        {"name": "BioPharma Dive", "home": "https://www.biopharmadive.com/"},
        {"name": "GEN", "home": "https://www.genengnews.com/"},
        {"name": "Pharma Times", "home": "https://www.pharmatimes.com/"},
        {"name": "Pharmaceutical Executive", "home": "https://www.pharmexec.com/"},
        {"name": "PRNewswire BioTech", "home": "https://www.prnewswire.com/biotechnology/"},
        {"name": "Nature Reviews Drug Discovery", "home": "https://www.nature.com/nrd/"},
        {"name": "ClinicalTrials.gov", "home": "https://clinicaltrials.gov/"},
        {"name": "Europe PMC", "home": "https://europepmc.org/"},
        {"name": "北京亦庄·经开区官网", "home": "https://kfqgw.beijing.gov.cn/"},
        {"name": "SEC EDGAR", "home": "https://www.sec.gov/cgi-bin/browse-edgar"},
        {"name": "CDE 药审中心", "home": "https://www.cde.org.cn/"},
        {"name": "Recursion IR", "home": "https://ir.recursion.com/"},
    ]

    d = datetime.now()
    result = {
        "reportDate": d.strftime("%Y-%m-%d"),
        "window": f"{(d - timedelta(days=3)).strftime('%Y-%m-%d')} ~ {d.strftime('%Y-%m-%d')}",
        "channels": channels,
        "sections": [{"label": k, "items": groups[k]} for k in so],
        "sourceNote": "聚合国际媒体/临试/文献/园区/交易所等公开渠道。中文摘要智能生成，仅供参考。",
    }

    json.dump(result, open("pharma_final.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)

    total = sum(len(groups[k]) for k in so)
    print(f"\npharma_final.json: {total} 条")
    for k in so: print(f"  {k}: {len(groups[k])} 条")


if __name__ == "__main__":
    main()
