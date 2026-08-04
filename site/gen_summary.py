# -*- coding: utf-8 -*-
"""DeepSeek 批量中文摘要生成 — 一次性请求，质量接近人工。
读 pharma_raw.json → 噪音过滤 → DeepSeek 批量翻译 → pharma_final.json
"""
import json, re, urllib.request, ssl, os
from datetime import datetime, timedelta

DEEPSEEK_URL = "https://api.deepseek.com/chat/completions"
# Key 从外部文件读取，避免暴露到 git
_keypath = os.path.join(os.path.dirname(__file__), "deepseek_key.txt")
if os.path.exists(_keypath):
    with open(_keypath) as f:
        DEEPSEEK_KEY = f.read().strip()
else:
    DEEPSEEK_KEY = ""

# ---------- 噪音过滤 ----------
NOISE_KW = [
    "securities law violations", "investor alert", "sued for",
    "contact the djs", "contact sbs", "lead plaintiff", "class action",
    "floating rate", "mesa laboratories", "first solar", "futu holdings",
    "peabody energy", "score fitness", "genius group", "insulet corporation",
    "sponsored", "building a best practice", "life sciences location analysis",
    "mba graduates", "dscsa compliance", "serialization system", "gs1 certification",
    "inizio launches", "intelligence economy",
    "upstream risks that can delay your path to ind",
    # 明显非医药
    "lane office furniture", "consumer cellular", "domino", "natural grocers",
    "lindblad expeditions", "décor", "furniture",
]

# ---------- DeepSeek 批量翻译 ----------

def filter_items(raw):
    """噪音过滤 + 去重"""
    seen, clean = set(), []
    for it in raw:
        blob = (it.get("title", "") + " " + it.get("desc", "")).lower()
        if any(k in blob for k in NOISE_KW):
            continue
        key = it.get("url") or it["title"][:40].lower()
        if key in seen:
            continue
        seen.add(key)
        clean.append(it)
    return clean


def batch_translate(items, max_per_batch=40):
    """发送给 DeepSeek 批量翻译标题 + 生成中文摘要"""
    # 构建批量 prompt
    titles = []
    for idx, it in enumerate(items):
        src = it.get("source", "").replace("·经开区官网", "")
        t = it.get("title", "")
        titles.append(f"[{idx}] {t}")

    # 分批
    all_results = {}
    for batch_start in range(0, len(titles), max_per_batch):
        batch = titles[batch_start:batch_start + max_per_batch]
        # 用局部编号发给 DeepSeek，解析时加回 batch_start
        local_titles = []
        for local_i, global_i in enumerate(range(batch_start, min(batch_start + max_per_batch, len(titles)))):
            local_titles.append(f"[{local_i}] {items[global_i].get('title','')}")
        prompt = f"""你是一个生物医药新闻编辑。请将以下每条英文/中文新闻标题翻译为简洁的中文摘要（≤60字）。

要求：
- 每条摘要独立一行，格式为 "[序号] 摘要"
- 保留关键实体（药名/公司名/靶点/适应证）的英文原名
- 中文主语优先，表达专业、简洁
- 临床进展提及阶段和适应证
- 交易并购提及金额和方向
- 论文按 "期刊：关键发现" 格式

新闻列表：
{chr(10).join(local_titles)}"""

        payload = json.dumps({
            "model": "deepseek-chat",
            "messages": [
                {"role": "system", "content": "你是生物医药专业新闻摘要编辑，输出简洁准确的中文摘要。"},
                {"role": "user", "content": prompt}
            ],
            "temperature": 0.3,
            "max_tokens": 4096,
            "stream": False
        }).encode("utf-8")

        req = urllib.request.Request(DEEPSEEK_URL, data=payload, headers={
            "Authorization": f"Bearer {DEEPSEEK_KEY}",
            "Content-Type": "application/json"
        })
        ctx = ssl.create_default_context()
        print(f"  → 批次 {batch_start//max_per_batch+1}: {len(batch)} 条...", end=" ", flush=True)
        try:
            with urllib.request.urlopen(req, timeout=60, context=ctx) as resp:
                data = json.loads(resp.read().decode("utf-8"))
                content = data["choices"][0]["message"]["content"]
            print("OK")
        except Exception as e:
            print(f"FAIL: {e}")
            continue

        # 解析响应
        for line in content.strip().split("\n"):
            m = re.match(r'\[(\d+)\]\s*(.+)', line.strip())
            if m:
                idx = int(m.group(1)) + batch_start
                summary = m.group(2).strip()[:60]
                all_results[idx] = summary

    return all_results


# ---------- 分类规则 ----------

def classify(title, desc, orig_sec):
    blob = (title + " " + desc).lower()
    sec = orig_sec or "行业动态"
    
    # 论文源强制归类
    if "Nat Rev Drug" in title or "europe pmc" in blob or "journal" in desc.lower():
        sec = "论文研究"
    # 亦庄
    if "亦庄" in title or "经开区" in title:
        sec = "亦庄园区动态"
    # 监管
    if any(k in blob for k in ["fda grants", "fda expands", "fda approv", "fda ok", "获批", "上市许可",
                                 "fast track", "breakthrough", "孤儿药", "label", "扩大.*适应"]):
        return "监管审批"
    # 临床
    if any(k in blob for k in ["phase 1", "phase 2", "phase 3", "phase i", "trial", "临床"]):
        return "临床试验"
    # 交易
    if any(k in blob for k in ["acqui", "merger", "merge", "buyout", "ipo", "raise", "funding",
                                 "partnership", "collaboration", "licens deal", "收购", "并购", "融资",
                                 "megadeal", "megamerger"]):
        if not any(k in blob for k in ["appoint", "phase", "trial"]):
            return "交易速览"
    # 政策
    if any(k in blob for k in ["legislation", "regulatory", "医保", "集采", "medicare", "medicaid", "340b"]):
        return "政策追踪"
    # 观点
    if any(k in blob for k in ["opinion", "editorial", "commentary", "perspective", "viewpoint", "观点"]):
        return "政策与观点"
    return sec


# ---------- 主流程 ----------

def main():
    raw = json.load(open("pharma_raw.json", encoding="utf-8"))
    print(f"原始: {len(raw)} 条")
    clean = filter_items(raw)
    print(f"去噪: {len(clean)} 条")

    print("调用 DeepSeek 批量生成中文摘要...")
    summaries = batch_translate(clean)

    so = ["监管审批", "临床试验", "交易速览", "行业动态", "亦庄园区动态", "论文研究", "政策追踪", "政策与观点"]
    secs = {k: [] for k in so}
    missing = 0

    for idx, it in enumerate(clean):
        s = summaries.get(idx)
        if s:
            it["summary"] = s[:60]
        else:
            it["summary"] = it.get("title", "")[:60]
            missing += 1

        it["section"] = classify(it.get("title", ""), it.get("desc", ""), it.get("section", "行业动态"))
        secs[it["section"]].append(it)

    print(f"DeepSeek 翻译: {len(clean)-missing}/{len(clean)} 条成功")

    ch = [
        {"name": "Endpoints News", "home": "https://endpts.com/"},
        {"name": "STAT News", "home": "https://www.statnews.com/"},
        {"name": "BioPharma Dive", "home": "https://www.biopharmadive.com/"},
        {"name": "GEN", "home": "https://www.genengnews.com/"},
        {"name": "Pharma Times", "home": "https://www.pharmatimes.com/"},
        {"name": "Pharmaceutical Executive", "home": "https://www.pharmexec.com/"},
        {"name": "Nat Rev Drug Discovery", "home": "https://www.nature.com/nrd/"},
        {"name": "ClinicalTrials.gov", "home": "https://clinicaltrials.gov/"},
        {"name": "Europe PMC", "home": "https://europepmc.org/"},
        {"name": "北京亦庄·经开区官网", "home": "https://kfqgw.beijing.gov.cn/"},
        {"name": "SEC EDGAR", "home": "https://www.sec.gov/"},
    ]

    d = datetime.now()
    r = {
        "reportDate": d.strftime("%Y-%m-%d"),
        "window": f"{(d - timedelta(days=3)).strftime('%Y-%m-%d')} ~ {d.strftime('%Y-%m-%d')}",
        "channels": ch,
        "sections": [{"label": k, "items": secs[k]} for k in so],
        "sourceNote": "聚合国际媒体/临试/文献/园区/交易所等公开渠道。中文摘要 DeepSeek AI 生成，仅供参考。",
    }
    total = sum(len(v) for v in secs.values())
    json.dump(r, open("pharma_final.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print(f"\npharma_final.json: {total} 条")
    for k in so:
        print(f"  {k}: {len(secs[k])} 条")

if __name__ == "__main__":
    main()
