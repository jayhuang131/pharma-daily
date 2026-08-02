# -*- coding: utf-8 -*-
"""自动中文摘要生成。
用有道免费翻译 API（国内可用，无严格限流）为英文条目生成中文摘要。
读 pharma_raw.json → 输出 pharma_final.json。
"""
import json, re, time, urllib.request, urllib.parse, hashlib, random
from datetime import datetime, timedelta

UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/124.0.0.0 Safari/537.36"

# ---------- 翻译工具（有道免费接口，无 key 也能用） ----------

def _ts():
    return str(int(time.time() * 1000))

def translate(text):
    """有道翻译免费接口，无需 API key"""
    if not text or len(text) < 3:
        return text
    try:
        params = urllib.parse.urlencode({"q": text, "from": "auto", "to": "zh-CHS"})
        url = f"https://aidemo.youdao.com/trans"
        req = urllib.request.Request(url, data=params.encode(),
            headers={"User-Agent": UA, "Content-Type": "application/x-www-form-urlencoded"})
        with urllib.request.urlopen(req, timeout=8) as r:
            data = json.loads(r.read().decode("utf-8", "ignore"))
            result = data.get("translation")
            if isinstance(result, list) and result:
                return "".join(result)
            if isinstance(result, str) and result:
                return result
    except Exception:
        pass
    return text  # 失败保留原文


def is_chinese(text):
    if not text:
        return False
    cn = sum(1 for c in text if '\u4e00' <= c <= '\u9fff')
    return cn / max(len(text), 1) > 0.3


def clean_desc(desc):
    """清理描述文本"""
    if not desc:
        return ""
    s = re.sub(r"<[^>]+>", "", desc)
    s = re.sub(r"&\w+;", " ", s)
    s = re.sub(r"\s+", " ", s).strip()
    return s


def make_summary(title, desc, tr_title):
    """生成中文摘要"""
    parts = []
    if tr_title and is_chinese(tr_title):
        parts.append(tr_title[:40])

    if desc:
        d = clean_desc(desc)
        if d and not is_chinese(d):
            tr_d = translate(d[:100])
            if tr_d and tr_d != d and is_chinese(tr_d):
                parts.append(tr_d[:50])

    if not parts:
        return title[:60]
    result = "；".join(parts)
    return result[:80].strip()


# ---------- 噪音过滤 ----------

NOISE_KW = [
    "securities law violations", "investor alert", "sued for", "contact the djs",
    "contact sbs", "lead plaintiff", "class action", "floating rate",
    "mesa laboratories", "first solar", "futu holdings", "peabody energy",
    "score fitness", "genius group", "insulet corporation", "sponsored",
    "upstream risks", "building a best practice", "life sciences location analysis",
    "mba graduates", "dscsa compliance", "serialization system", "gs1 certification",
    "inizio launches", "intelligence economy",
]

# ---------- 主流程 ----------

def main():
    raw = json.load(open("pharma_raw.json", encoding="utf-8"))
    print(f"原始数据: {len(raw)} 条")

    # 去噪去重
    seen, clean = set(), []
    for it in raw:
        t = (it.get("title") or "").lower()
        d = (it.get("desc") or "").lower()
        if any(k in (t+d) for k in NOISE_KW):
            continue
        key = it.get("url") or it["title"][:40].lower()
        if key in seen:
            continue
        seen.add(key)
        clean.append(it)

    print(f"去噪后: {len(clean)} 条，开始生成中文摘要...")

    sections_order = ["监管审批", "临床试验", "交易速览", "行业动态", "亦庄园区动态", "论文研究", "政策追踪", "政策与观点"]
    groups = {k: [] for k in sections_order}

    total_items = len(clean)
    for idx, it in enumerate(clean):
        sec = it.get("section", "行业动态")
        if sec not in groups:
            sec = "行业动态"

        # 自动重分类
        blob = (it.get("title", "") + " " + it.get("desc", "")).lower()
        if any(k in blob for k in ["approv","clearance","authoriz","licens","fda grants","fda ok","nmpa",
                                     "获批","批准","上市许可","fast track","breakthrough therap","快速通道","孤儿药"]):
            if sec not in ("监管审批","临床试验"): sec = "监管审批"
        if any(k in blob for k in ["phase 1","phase 2","phase 3","phase i","phase ii","trial","临床","nct0"]):
            if sec == "行业动态": sec = "临床试验"
        deal = ["acqui","merger","merge","buyout","takeover","ipo","spac","licens deal",
                "partnership","collaboration","joint venture","financing","raise","series a","series b",
                "funding","收购","并购","融资","ipo","合作","授权","许可","交易"]
        if any(k in blob for k in deal):
            if not any(k in blob for k in ["appoint","resign","board chairman","phase","trial"]):
                sec = "交易速览"
        if any(k in blob for k in ["nmpa","cde","legislation","regulatory framework",
                                     "监管政策","法规","指南修订","监管改革","医保","集采",
                                     "招标","定价","目录调整","药品法"]):
            sec = "政策追踪"
        if any(k in blob for k in ["opinion","editorial","commentary","perspective",
                                     "viewpoint","policy","analysis:","观点","评论"]):
            sec = "政策与观点"

        # 翻译标题 + 摘要
        title = it.get("title", "")
        desc = it.get("desc", "")

        tr_title = ""
        if title and not is_chinese(title):
            tr_title = translate(title[:80])
        elif title:
            tr_title = title[:60]

        it["summary"] = make_summary(title, desc, tr_title)
        it["section"] = sec
        groups[sec].append(it)

        # 进度
        pct = (idx + 1) * 100 // total_items
        if (idx + 1) % 5 == 0 or idx == total_items - 1:
            print(f"  [{idx+1}/{total_items}] {pct}% | {it['summary'][:45]}")
        else:
            print(f"  [{idx+1}/{total_items}] {pct}%")

        time.sleep(0.8)  # 控制翻译频率

    # channels
    channels = [
        {"name": "Endpoints News", "home": "https://endpts.com/"},
        {"name": "STAT News", "home": "https://www.statnews.com/"},
        {"name": "Fierce Biotech", "home": "https://www.fiercebiotech.com/"},
        {"name": "BioPharma Dive", "home": "https://www.biopharmadive.com/"},
        {"name": "GEN", "home": "https://www.genengnews.com/"},
        {"name": "Pharma Times", "home": "https://www.pharmatimes.com/"},
        {"name": "Pharmaceutical Executive", "home": "https://www.pharmexec.com/"},
        {"name": "PRNewswire BioTech", "home": "https://www.prnewswire.com/biotechnology/"},
        {"name": "Nat Rev Drug Discovery", "home": "https://www.nature.com/nrd/"},
        {"name": "ClinicalTrials.gov", "home": "https://clinicaltrials.gov/"},
        {"name": "Europe PMC", "home": "https://europepmc.org/"},
        {"name": "北京亦庄·经开区官网", "home": "https://kfqgw.beijing.gov.cn/"},
        {"name": "SEC EDGAR", "home": "https://www.sec.gov/cgi-bin/browse-edgar"},
        {"name": "Recursion IR", "home": "https://ir.recursion.com/"},
    ]

    d = datetime.now()
    result = {
        "reportDate": d.strftime("%Y-%m-%d"),
        "window": f"{(d - timedelta(days=3)).strftime('%Y-%m-%d')} ~ {d.strftime('%Y-%m-%d')}",
        "channels": channels,
        "sections": [{"label": k, "items": groups[k]} for k in sections_order],
        "sourceNote": "聚合国际媒体/临试/文献/园区/交易所等公开渠道。中文摘要 AI 自动翻译生成，仅供参考。",
    }

    total = sum(len(groups[k]) for k in sections_order)
    json.dump(result, open("pharma_final.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print(f"\npharma_final.json: {total} 条")
    for k in sections_order:
        print(f"  {k}: {len(groups[k])} 条")


if __name__ == "__main__":
    main()
