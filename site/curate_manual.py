# -*- coding: utf-8 -*-
import json; from datetime import datetime, timedelta
raw = json.load(open("pharma_raw.json", encoding="utf-8"))

C = {
    0:  {"summary": "Qnovia 获新型抗菌肽授权，拓展抗感染药物管线。", "section": "交易速览"},
    1:  {"summary": "糖尿病患者自述：用未经 FDA 批准的软件管理血糖的困境与呼吁。", "section": "政策与观点"},
    2:  {"summary": "礼来扩大未获批阿尔茨海默药特殊使用计划，回应患者强烈诉求。", "section": "监管审批"},
    3:  {"summary": "FDA 扩大 Pluvicto 适应证，覆盖绝大多数转移性前列腺癌患者。", "section": "监管审批"},
    4:  {"summary": "默沙东抗 TL1A 抗体在化脓性汗腺炎中获胜，溃疡性结肠炎试验失败。", "section": "临床试验"},
    5:  {"summary": "阿斯利康与百时美施贵宝举行合并谈判，或将诞生超大规模药企。", "section": "交易速览"},
    6:  {"summary": "噬菌体联合粪菌移植显著降低复发性尿路感染和抗生素使用。", "section": "临床试验"},
    # 7-12 小规模临床试验 skip
    13: {"summary": "业界激辩阿斯利康-BMS 超级合并：规模红利还是反垄断风险？", "section": "交易速览"},
    14: {"summary": "特朗普政府推动法院裁定的精神卫生服务，初创企业迎来新机遇。", "section": "行业动态"},
    15: {"summary": "制药行业对阿斯利康-BMS 潜在合并提出多项反垄断和市场质疑。", "section": "交易速览"},
    16: {"summary": "华尔街不看好阿斯利康-BMS 超级合并，股价反应平淡。", "section": "交易速览"},
    17: {"summary": "Supernus 与 Individor 合并，强化中枢神经系统药物管线。", "section": "交易速览"},
    18: {"summary": "消息称阿斯利康与 BMS 已完成首轮合并谈判。", "section": "交易速览"},
    19: {"summary": "Receptor.AI 与 Sethera 合作构建 AI 驱动的闭环药物发现平台。", "section": "交易速览"},
    22: {"summary": "Beam Therapeutics 提交 8-K 重大事项报告。", "section": "行业动态"},
    24: {"summary": "Larimar Therapeutics 提交 8-K 重大事项报告。", "section": "行业动态"},
    26: {"summary": "拜耳不顾德国削减开支，推进中风新药德国上市计划。", "section": "行业动态"},
    29: {"summary": "专访：美国如何消除监管壁垒应对中国生物科技的崛起。", "section": "政策与观点"},
    30: {"summary": "基因组图谱揭示先天淋巴细胞中的自身免疫病风险基因。", "section": "论文研究"},
    31: {"summary": "小肯尼迪和奥兹称医疗补助削减是'谣言'，事实更为复杂。", "section": "政策与观点"},
    32: {"summary": "Pathos 与阿斯利康、中国康宁杰瑞达成合作，拟融资 3 亿美元。", "section": "交易速览"},
    33: {"summary": "加州最高法院支持吉利德，认定药企无「创新义务」。", "section": "行业动态"},
    34: {"summary": "小罗伯特·肯尼迪采访引发疫苗、大流行和麻疹问题的多方纠正。", "section": "行业动态"},
    35: {"summary": "生物制品研发平台在复杂治疗模式上力不从心，亟需变革。", "section": "论文研究"},
    36: {"summary": "密歇根报告美国首两例腹泻寄生虫相关死亡病例。", "section": "行业动态"},
    37: {"summary": "BioNTech 正式任命 Sobi 高管 Oelkers 为新任 CEO。", "section": "行业动态"},
    38: {"summary": "联邦医保取消突破性医疗器械特殊通道，产业界强烈反对。", "section": "政策追踪"},
    40: {"summary": "Sandoz 以 4.5 亿美元与 43 州就仿制药定价诉讼达成和解。", "section": "行业动态"},
    41: {"summary": "Curium 以 80 亿美元收购核药竞争对手 Lantheus，行业整合加速。", "section": "交易速览"},
    43: {"summary": "Polpharma Biologics 生物类似药正式获 FDA 与 EMA 受理审评。", "section": "监管审批"},
    44: {"summary": "Parsortix 液体活检技术在 ADC 靶点检测中展现潜力。", "section": "行业动态"},
    46: {"summary": "Capricor DMD 细胞疗法遭 FDA 质疑有效性，股价持续暴跌。", "section": "监管审批"},
    47: {"summary": "生物医药合规沙龙在经开区举办，为企业送上风险防控服务包。", "section": "亦庄园区动态"},
    48: {"summary": "经开区医药健康产业创新成果集中涌现，多项技术突破落地。", "section": "亦庄园区动态"},
    49: {"summary": "生物医药人才沙龙举办，搭建高端引才交流与产业对接平台。", "section": "亦庄园区动态"},
    50: {"summary": "综述：小分子结合蛋白的设计策略与药物开发前景。", "section": "论文研究"},
    51: {"summary": "综述：治疗性 mRNA 翻译效率的优化策略与进展。", "section": "论文研究"},
    52: {"summary": "综述：靶向肿瘤相关巨噬细胞的免疫治疗新策略。", "section": "论文研究"},
    53: {"summary": "基因超大簇产生协同抗生素，为耐药菌治疗提供新途径。", "section": "论文研究"},
    54: {"summary": "噬菌体疗法在克罗恩病中展现治疗潜力。", "section": "论文研究"},
}

so = ["监管审批", "临床试验", "交易速览", "行业动态", "亦庄园区动态", "论文研究", "政策追踪", "政策与观点"]
secs = {k: [] for k in so}

for i, it in enumerate(raw):
    d = C.get(i)
    if d is None: continue
    item = dict(it)
    for k, v in d.items():
        item[k] = v
    if not item.get("desc"): item["desc"] = item.get("summary", "")
    secs[item["section"]].append(item)

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

dt = datetime.now()
r = {
    "reportDate": dt.strftime("%Y-%m-%d"),
    "window": f"{(dt - timedelta(days=3)).strftime('%Y-%m-%d')} ~ {dt.strftime('%Y-%m-%d')}",
    "channels": ch,
    "sections": [{"label": k, "items": secs[k]} for k in so],
    "sourceNote": "数据来自 Endpoints/STAT/GEN/BioPharma Dive 等权威渠道。中文摘要人工精选翻译，仅供参考。",
}
total = sum(len(v) for v in secs.values())
json.dump(r, open("pharma_final.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)
print(f"pharma_final.json: {total} 条")
for k in so: print(f"  {k}: {len(secs[k])} 条")
