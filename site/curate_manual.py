# -*- coding: utf-8 -*-
"""手工精选 + 中文翻译，替代自动 gen_summary.py"""
import json
from datetime import datetime, timedelta

raw = json.load(open("pharma_raw.json", encoding="utf-8"))

# 手工标注：{index: {"summary": str, "section": str} 或 None=skip}
C = {
    0:  {"summary": "Amgen 云服务遭黑客入侵，患者数据泄露。", "section": "行业动态"},
    1:  {"summary": "美国州医学委员会联合会领导层撰文回应行业监管质疑。", "section": "政策与观点"},
    # 2: Recursion 激励奖，skip
    # 3: 数据工具赞助内容，skip
    4:  {"summary": "微生物群衍生代谢物可增强猴模型中 HIV 治疗效果。", "section": "论文研究"},
    5:  {"summary": "诺和诺德抗炎药治疗心脏病意外失败，新疗法路径受质疑。", "section": "临床试验"},
    6:  {"summary": "Latigo 非阿片类镇痛药 II 期数据积极；碱基编辑技术取得进展。", "section": "临床试验"},
    # 7-12: 小规模临床试验，skip
    13: {"summary": "Supernus 与 Indivior 合并，打造 CNS 药物领军企业。", "section": "交易速览"},
    # 14: Lane Office Furniture, skip
    # 15: Consumer Cellular, skip
    16: {"summary": "Receptor.AI 与 Sethera 合作构建闭环药物发现与优化平台。", "section": "交易速览"},
    17: {"summary": "Dash Bio 完成 3000 万美元 A 轮融资，Oak HC/FT 领投。", "section": "交易速览"},
    18: {"summary": "阿斯利康与百时美施贵宝据报正进行合并谈判。", "section": "交易速览"},
    19: {"summary": "FDA 咨询委员会 10:3 投票支持 Replimune RP1 黑色素瘤疗法。", "section": "监管审批"},
    20: {"summary": "赛诺菲寻求重建与再生元合作关系；Apnimed IPO 融资上调。", "section": "交易速览"},
    21: {"summary": "Braveheart、Attovia、Vogenx 集中宣布 IPO，生物技术上市潮持续。", "section": "交易速览"},
    22: {"summary": "Rocket Pharmaceuticals 提交 8-K 重大事项报告。", "section": "行业动态"},
    # 23: Orthopaedic Advocacy, skip
    24: {"summary": "Keenova 宣布 Xiaflex 新研究数据发表，推动适应证拓展。", "section": "行业动态"},
    # 25: Lindblad Expeditions, skip
    26: {"summary": "BioNTech 任命 Sobi 前高管 Guido Oelkers 为新任 CEO。", "section": "行业动态"},
    27: {"summary": "Twist Bioscience 提交 8-K 重大事项报告。", "section": "行业动态"},
    # 28: Natural Grocers, skip
    29: {"summary": "Cocrystal Pharma 提交 8-K 重大事项报告。", "section": "行业动态"},
    # 30: BioNTech CEO 重复，skip
    31: {"summary": "Ocular Therapeutix 提交 8-K 重大事项报告。", "section": "行业动态"},
    # 32-33: Domino's Pizza, skip
    34: {"summary": "TG Therapeutics 提交 8-K 重大事项报告。", "section": "行业动态"},
    35: {"summary": "Tonix Pharmaceuticals 提交 8-K 重大事项报告。", "section": "行业动态"},
    36: {"summary": "Krystal Biotech 提交 8-K 重大事项报告。", "section": "行业动态"},
    37: {"summary": "Polpharma Biologics 生物类似药获 FDA 与 EMA 受理审评。", "section": "监管审批"},
    38: {"summary": "Seaport Therapeutics 提交 8-K 重大事项报告。", "section": "行业动态"},
    # 39-40: 已跳过
    41: {"summary": "AI 语音记录工具进入医学教育：是实用工具还是思维拐杖？", "section": "行业动态"},
    42: {"summary": "新项目帮助心衰患者术前增强体质，提高心脏移植成功率。", "section": "临床试验"},
    43: {"summary": "Capricor DMD 细胞疗法遭 FDA 专家组质疑，股价暴跌。", "section": "监管审批"},
    44: {"summary": "参议院提案拟阻止特朗普将联邦科研拨款政治化的计划。", "section": "政策与观点"},
    45: {"summary": "密歇根州最高法院裁定可调查礼来胰岛素定价行为。", "section": "行业动态"},
    46: {"summary": "Alnylam 股价持续下挫；多家药企 Q2 财报汇总。", "section": "行业动态"},
    47: {"summary": "特朗普政府再度推动 340B 药品折扣计划改革。", "section": "政策追踪"},
    48: {"summary": "艾伯维称 Skyrizi 免疫药物增长势头强劲，无惧竞争加剧。", "section": "行业动态"},
    49: {"summary": "氯胺酮触发性别特异性脑修复反应，或指导抑郁症精准治疗。", "section": "论文研究"},
    50: {"summary": "分子 GPS 机制引导中性粒细胞精准定位感染灶。", "section": "论文研究"},
    51: {"summary": "制药行业团体发声支持 340B 药品折扣改革方案。", "section": "政策追踪"},
    52: {"summary": "特朗普政府修订 340B 药品折扣试点方案细则。", "section": "政策追踪"},
    53: {"summary": "Resilience 与礼来投资 7.5 亿美元扩建辛辛那提制药基地。", "section": "行业动态"},
    54: {"summary": "FDA 细胞与基因治疗委员会投票支持 Replimune RP1 疗效数据。", "section": "监管审批"},
    55: {"summary": "关税加速制药制造回流美国，德国加大生科投资应对。", "section": "行业动态"},
    56: {"summary": "专利保护与药品可及性的全球博弈：MFN 最惠国待遇争议。", "section": "政策与观点"},
    57: {"summary": "经开区医药健康产业创新成果集中涌现，多项技术突破。", "section": "亦庄园区动态"},
    58: {"summary": "生物医药人才沙龙在经开区举办，搭建高端引才交流平台。", "section": "亦庄园区动态"},
    59: {"summary": "沙砾生物北京总部在经海产业园启用，经开区细胞基因治疗产业再添新军。", "section": "亦庄园区动态"},
    60: {"summary": "卡格列净对庆大霉素肾毒性分子保护机制的新见解。", "section": "论文研究"},
    61: {"summary": "眼内长效释放前列腺素类药物植入物治疗青光眼的综述。", "section": "论文研究"},
    64: {"summary": "加速 NK 细胞疗法临床转化的欧洲专家共识报告。", "section": "论文研究"},
    66: {"summary": "BRAF 抑制剂在胶质瘤中毒性管理与耐药策略的实践指南。", "section": "论文研究"},
    70: {"summary": "神经科医生自述：从诊断 ALS 到自己成为患者的经历。", "section": "政策与观点"},
    # 其他 Europe PMC 论文和临床试验 skip
}

# 构建
sections_order = ["监管审批", "临床试验", "交易速览", "行业动态", "亦庄园区动态", "论文研究", "政策追踪", "政策与观点"]
sections = {k: [] for k in sections_order}

for i, it in enumerate(raw):
    dec = C.get(i, None)
    if dec is None:
        continue  # skip
    item = dict(it)
    for k, v in dec.items():
        item[k] = v
    if not item.get("desc"):
        item["desc"] = item.get("summary", "")
    sections[item["section"]].append(item)

# 实际拉到数据的渠道
channels = [
    {"name": "Endpoints News", "home": "https://endpts.com/"},
    {"name": "STAT News", "home": "https://www.statnews.com/"},
    {"name": "Fierce Biotech", "home": "https://www.fiercebiotech.com/"},
    {"name": "BioPharma Dive", "home": "https://www.biopharmadive.com/"},
    {"name": "GEN", "home": "https://www.genengnews.com/"},
    {"name": "Pharma Times", "home": "https://www.pharmatimes.com/"},
    {"name": "Pharmaceutical Executive", "home": "https://www.pharmexec.com/"},
    {"name": "PRNewswire BioTech", "home": "https://www.prnewswire.com/biotechnology/"},
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
    "sections": [{"label": k, "items": sections[k]} for k in sections_order],
    "sourceNote": "数据来自 Endpoints News / STAT News / GEN / BioPharma Dive / Pharma Times / Pharmaceutical Executive 等权威公开渠道。中文摘要人工精选翻译，仅供参考，不构成投资建议。",
}

total = sum(len(v) for v in sections.values())
json.dump(result, open("pharma_final.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)
print(f"pharma_final.json: {total} 条")
for k in sections_order:
    print(f"  {k}: {len(sections[k])} 条")
