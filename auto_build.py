# -*- coding: utf-8 -*-
"""全自动流水线：抓取 → 规则清洗 → 渲染 → 推 GitHub。适合 Windows 任务计划程序定时跑。"""
import json, subprocess, sys, os

print("===== Step 1: pharma_fetch.py =====")
subprocess.run([sys.executable, "pharma_fetch.py"], check=False)

if not os.path.exists("pharma_raw.json"):
    print("[ERR] pharma_raw.json not found, abort.")
    sys.exit(1)

raw = json.load(open("pharma_raw.json", encoding="utf-8"))

# ----- 规则清洗（替代手工 AI 摘要）-----
# 噪音过滤
noise_kw = ["securities law violations", "investor alert", "sued for", "contact the djs",
            "contact sbs", "lead plaintiff", "class action", "floating rate",
            "mesa laboratories", "first solar", "futu holdings", "peabody energy",
            "score fitness", "genius group", "insulet corporation",
            "sponsored", "upstream risks", "building a best practice",
            "life sciences location analysis", "mba graduates",
            "dscsa compliance", "serialization system", "gs1 certification",
            "inizio launches", "intelligence economy"]

# 去重 + 去噪
seen, clean = set(), []
for it in raw:
    t = (it.get("title") or "").lower()
    d = (it.get("desc") or "").lower()
    blob = t + d
    if any(k in blob for k in noise_kw):
        continue
    key = it.get("url") or it["title"][:40].lower()
    if key in seen:
        continue
    seen.add(key)
    clean.append(it)

# 补中文摘要：有 desc 就取前 60 字，没有就用标题
for it in clean:
    if not it.get("summary"):
        txt = it.get("desc") or it.get("title") or ""
        it["summary"] = txt[:60].strip()

sections_order = ["监管审批", "临床试验", "交易速览", "行业动态", "亦庄园区动态", "论文研究", "政策追踪", "政策与观点"]
groups = {k: [] for k in sections_order}
for it in clean:
    sec = it.get("section", "行业动态")
    if sec not in groups:
        sec = "行业动态"
    groups[sec].append(it)

channels = [
    {"name": "Endpoints News", "home": "https://endpts.com/"},
    {"name": "Fierce Biotech", "home": "https://www.fiercebiotech.com/"},
    {"name": "STAT News", "home": "https://www.statnews.com/"},
    {"name": "BioPharma Dive", "home": "https://www.biopharmadive.com/"},
    {"name": "Pharma Times", "home": "https://www.pharmatimes.com/"},
    {"name": "Pharmaceutical Executive", "home": "https://www.pharmexec.com/"},
    {"name": "PRNewswire BioTech", "home": "https://www.prnewswire.com/biotechnology/"},
    {"name": "GEN", "home": "https://www.genengnews.com/"},
    {"name": "Nature Reviews Drug Discovery", "home": "https://www.nature.com/nrd/"},
    {"name": "ClinicalTrials.gov", "home": "https://clinicaltrials.gov/"},
    {"name": "Europe PMC", "home": "https://europepmc.org/"},
    {"name": "北京亦庄·经开区官网", "home": "https://kfqgw.beijing.gov.cn/"},
    {"name": "SEC EDGAR", "home": "https://www.sec.gov/cgi-bin/browse-edgar"},
    {"name": "CDE 药审中心", "home": "https://www.cde.org.cn/"},
]

from datetime import datetime
d = datetime.now()

result = {
    "reportDate": d.strftime("%Y-%m-%d"),
    "window": f"{(d.replace(day=d.day-3)).strftime('%Y-%m-%d')} ~ {d.strftime('%Y-%m-%d')}",
    "channels": channels,
    "sections": [{"label": k, "items": groups[k]} for k in sections_order],
    "sourceNote": "全自动聚合，来源含国际媒体/临试/文献/交易所/园区/药审等公开渠道。摘要为 AI/规则生成，仅供参考。",
}

total = sum(len(groups[k]) for k in sections_order)
json.dump(result, open("pharma_final.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)
print(f"pharma_final.json: {total} 条")

# ----- Step 3: 渲染 -----
print("===== Step 3: pharma_build.py =====")
subprocess.run([sys.executable, "pharma_build.py", "pharma_final.json"], check=False)

# ----- Step 4: git push -----
print("===== Step 4: git push =====")
try:
    subprocess.run(["git", "add", "-A"], check=False)
    subprocess.run(["git", "commit", "-m", f"auto: {d.strftime('%Y-%m-%d')} 日报"], check=False)
    subprocess.run(["git", "push", "origin", "main"], check=False)
    print("Git push done.")
except Exception as e:
    print(f"Git push failed (network?): {e}")

print("===== DONE =====")
