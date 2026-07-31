# -*- coding: utf-8 -*-
"""今日清洗：61 条 → 精选 35 条左右 → pharma_final.json"""
import json, sys

raw = json.load(open("pharma_raw.json", encoding="utf-8"))

# 手工标注：{index: {"summary": str, "section": str} or None=skip}
C = {
    0:  {"summary": "Latigo 非阿片类镇痛药在关键术后痛试验中达主要终点，对标 Vertex。", "section": "监管审批"},
    1:  {"summary": "Lynavoy（IBAT 抑制剂）获 CHMP 推荐批准用于 PBC 胆汁淤积性瘙痒。", "section": "监管审批"},
    2:  {"summary": "Nezglyal 获 CHMP 正面意见，用于男孩脑肾上腺脑白质营养不良。", "section": "监管审批"},
    3:  {"summary": "Vista 试验启动癌症疫苗首次人体给药，评估 infinitopes 治疗平台。", "section": "临床试验"},
    4:  {"summary": "华沙医科大学：GLP-1 激动剂术前停用建议对全麻诱导影响研究。", "section": "临床试验"},
    5:  None,  # 跳过（GLP-1 术前指南，偏麻醉）
    6:  {"summary": "Atsena 两款基因疗法获 EMA 孤儿药认定，推动关键临床试验。", "section": "监管审批"},
    7:  {"summary": "强生双靶骨髓瘤方案 III 期显示显著生存获益。", "section": "临床试验"},
    8:  None,  # 跳过（sponsored content）
    9:  {"summary": "Spruce Biosciences：Tralesinidase 早期可及治疗黏多糖贮积症。", "section": "临床试验"},
    10: {"summary": "OrbusNeich 在日本启动药物涂层球囊冠状动脉关键临床。", "section": "临床试验"},
    11: None,  # 跳过（尼可地尔对 RA，非创新药方向）
    12: {"summary": "Daewoong DWP14012（P-CAB）III 期评估对糜烂性食管炎疗效。", "section": "临床试验"},
    13: None,  # 跳过（眼压药，非创新药方向）
    14: {"summary": "Apnimed 以 1.92 亿美元 IPO 推进睡眠呼吸暂停药物，预计 2027 上市。", "section": "交易速览"},
    15: None, 16: None,  # 跳过（律所广告）
    17: {"summary": "Regeneron/Sanofi 拟扩大 Dupixent 合作范围。", "section": "交易速览"},
    18: {"summary": "J&J 收购 Sail Biomedicines、Processa 获得授权等本周交易汇总。", "section": "交易速览"},
    19: None, 20: None, 21: None, 22: None, 23: None, 24: None,  # 跳过（律所广告）
    25: None,  # 跳过（非药公司 8-K）
    26: {"summary": "ImmunityBio, Inc. 提交 8‑K 重大事项报告。", "section": "行业动态"},
    27: None,  # 跳过（MESA Labs 非创新药）
    28: {"summary": "Aldeyra Therapeutics, Inc. 提交 8‑K 重大事项报告。", "section": "行业动态"},
    29: {"summary": "Oric Pharmaceuticals, Inc. 提交 8‑K 重大事项报告。", "section": "行业动态"},
    30: {"summary": "Replimune 黑色素瘤疗法 RP1 获 FDA 咨询委员会多数支持。", "section": "监管审批"},
    31: {"summary": "特朗普 100% 药品关税首轮推迟，不在本周五启动。", "section": "政策追踪"},
    32: None,  # sponsored
    33: None,  # 跳过（政治人事）
    34: {"summary": "UCB 股价在 Bimzelx 收入超预期后仍下滑，市场担忧管线接续。", "section": "行业动态"},
    35: {"summary": "Sanofi 新 CEO 计划 R&D 管线清理、加大 M&A、押注中国战略。", "section": "行业动态"},
    36: None, 37: None, 38: None, 39: None, 40: None, 41: None,  # 跳过（供应商/合规指南）
    42: {"summary": "Recursion 将发布 2026 Q2 业绩更新，8 月 5 日召开投资者电话会。", "section": "行业动态"},
    43: None,  # sponsored
    44: {"summary": "生物医药人才沙龙在经开区举办，搭建引才交流平台。", "section": "亦庄园区动态"},
    45: {"summary": "沙砾生物（TIL 细胞治疗）北京总部在经海产业园启用。", "section": "亦庄园区动态"},
    46: {"summary": "国际医药创新公园人才保障房全面封顶。", "section": "亦庄园区动态"},
    47: {"summary": "Nature Reviews：小分子可阻断 β-arrestin，开辟 GPCR 信号新策略。", "section": "论文研究"},
    48: {"summary": "口服大环 PCSK9 抑制剂获 FDA 批准，降脂治疗进入口服时代。", "section": "监管审批"},  # FDA approval
    49: {"summary": "念珠菌基因组数据库 CGD 新版界面与工具发布。", "section": "论文研究"},
    50: {"summary": "结构自由位点分辨对比学习扩展小分子虚拟筛选能力。", "section": "论文研究"},
    51: {"summary": "蛋白质组学鉴定 CLDN3 为小细胞肺癌肿瘤选择性治疗靶点。", "section": "论文研究"},
    52: {"summary": "动态纳米颗粒组装用于生物医学微型机器人精准递药。", "section": "论文研究"},
    53: {"summary": "功能化石墨烯量子点结合 Tau 蛋白的计算机建模。", "section": "论文研究"},
    54: {"summary": "人类 Bindome：全蛋白组尺度设计结合物候选者图谱。", "section": "论文研究"},
    55: {"summary": "评分函数偏差：构建筛选中机器学习的表现评估。", "section": "论文研究"},
    56: {"summary": "从贝宁分离的新型克雷伯菌噬菌体表征。", "section": "论文研究"},
    57: {"summary": "慢性口服芬太尼产生动态行为适应的机制。", "section": "论文研究"},
    58: {"summary": "封装细胞技术递送 CNTF 保护光感受器的研究。", "section": "论文研究"},
    59: {"summary": "PharmaExec 日报：J&J 收购 Sail、Sanofi 管线大清理、GS1 认证解读。", "section": "政策与观点"},
    60: None,  # sponsored
}

# 构建 channels
channels = [
    {"name": "Endpoints News", "home": "https://endpts.com/"},
    {"name": "Fierce Biotech", "home": "https://www.fiercebiotech.com/"},
    {"name": "STAT News", "home": "https://www.statnews.com/"},
    {"name": "Pharma Times", "home": "https://www.pharmatimes.com/"},
    {"name": "Pharmaceutical Executive", "home": "https://www.pharmexec.com/"},
    {"name": "PRNewswire BioTech", "home": "https://www.prnewswire.com/biotechnology/"},
    {"name": "BioPharma Dive", "home": "https://www.biopharmadive.com/"},
    {"name": "GEN", "home": "https://www.genengnews.com/"},
    {"name": "Nature Reviews Drug Discovery", "home": "https://www.nature.com/nrd/"},
    {"name": "ClinicalTrials.gov", "home": "https://clinicaltrials.gov/"},
    {"name": "Europe PMC", "home": "https://europepmc.org/"},
    {"name": "北京亦庄·经开区官网", "home": "https://kfqgw.beijing.gov.cn/"},
    {"name": "SEC EDGAR", "home": "https://www.sec.gov/cgi-bin/browse-edgar"},
    {"name": "CDE 药审中心", "home": "https://www.cde.org.cn/"},
]

sections_order = ["监管审批", "临床试验", "交易速览", "行业动态", "亦庄园区动态", "论文研究", "政策追踪", "政策与观点"]
sections = {k: [] for k in sections_order}

for i, it in enumerate(raw):
    dec = C.get(i, None)
    if dec is None:
        continue
    item = dict(it)
    for k, v in dec.items():
        item[k] = v
    if not item.get("desc"):
        item["desc"] = item.get("summary", "")
    sections[item["section"]].append(item)

result = {
    "reportDate": "2026-07-31",
    "window": "2026-07-28 ~ 2026-07-31",
    "channels": channels,
    "sections": [{"label": k, "items": sections[k]} for k in sections_order],
    "sourceNote": "数据来自 Endpoints News / STAT News / Fierce Biotech / BioPharma Dive / "
                   "Pharma Times / Pharmaceutical Executive / PRNewswire BioTech / GEN / "
                   "Nature Reviews Drug Discovery / ClinicalTrials.gov / Europe PMC / "
                   "北京亦庄·经开区官网 / SEC EDGAR / CDE 药审中心（P1/P2）等权威公开渠道。"
                   "摘要为 AI 自动生成，仅供参考。",
}

total = sum(len(v) for v in sections.values())
json.dump(result, open("pharma_final.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)
print(f"pharma_final.json: {total} 条 | {dict((k, len(v)) for k, v in sections.items())}")
