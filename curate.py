# -*- coding: utf-8 -*-
"""一键清洗：读 pharma_raw → 去噪 → 中文摘要 → 版块调整 → 输出 pharma_final"""
import json
from datetime import datetime

raw = json.load(open("pharma_raw.json", encoding="utf-8"))

# 每条 raw 的处理决策：None 表示保留不动；dict 表示覆盖字段
# 索引从 0 开始（对应 raw 列表）
curate = {
    # ===== 监管审批 (3→2) =====
    0: {"summary": "Nezglyal 获欧盟 CHMP 正面意见，用于治疗男孩脑肾上腺脑白质营养不良（cALD）。", "section": "监管审批"},
    1: None,  # 跳过（Simtriyo 日报摘要，与 2 重复）
    2: {"summary": "FDA 批准 Otsuka 首创 Simtriyo，用于成人及儿童精神分裂症与双相障碍。", "section": "监管审批"},
    # ===== 临床试验 =====
    3: {"summary": "Oak Hill Bio 与 RA Capital SPAC 合并；InnoCare TYK2 抑制剂 III 期临床达终点。", "section": "临床试验"},
    4: {"summary": "FDA 审查员质疑 Replimune 黑色素瘤 RP1 疗法 III 期未证明有效性。", "section": "临床试验"},
    5: {"summary": "OrbusNeich 在日本启动药物涂层球囊冠状动脉关键临床试验。", "section": "临床试验"},
    6: {"summary": "TruTechnologies 主席解读「试验闪电战」为何使临床研究撤离美国。", "section": "政策与观点"},
    # CT 原始 6 条（7-12）
    7:  {"summary": "Vast Therapeutics ALX1 吸入剂治疗支气管扩张的剂量探索研究。", "section": "临床试验"},
    8:  {"summary": "仁济医院：Darolutamide+多西他赛+ADT 新辅助治疗前列腺癌 II 期。", "section": "临床试验"},
    9:  {"summary": "Alterity Therapeutics 为完成 ATH434-201 的 MSA 患者提供开放性延伸用药。", "section": "临床试验"},
    10: {"summary": "深圳信立泰 SAL0137 口服治疗高脂血症的随机双盲安慰剂对照 II 期。", "section": "临床试验"},
    11: {"summary": "Sun Pharma 外用制剂最大使用量药代动力学研究。", "section": "临床试验"},
    12: {"summary": "UCSD：在转移性乳腺癌标准疗法中联用 HER 抑制剂的疗效试验。", "section": "临床试验"},
    # ===== 行业动态 =====
    13: {"summary": "临床 AI 聊天机器人席卷医学界，医生该信任通用还是专科 LLM？", "section": "行业动态"},
    14: None,  # 跳过（生物技术通缉犯花边）
    15: {"summary": "美国糖尿病协会面临辞退呼声，吁请耐心等待内部审查结果。", "section": "行业动态"},
    # SEC 4 条
    16: None,  # 跳过（First Choice Healthcare 非创新药）
    17: {"summary": "Yarrow Bioscience, Inc. 提交 8‑K 重大事项报告。", "section": "监管审批"},
    18: None,  # 跳过（Acadia Healthcare 非创新药）
    19: {"summary": "Tempest Therapeutics, Inc. 提交 8‑K 重大事项报告。", "section": "行业动态"},
    # 继续行业动态
    20: {"summary": "BioMarin 与 n‑Lorem 携手为 ReNU 综合征开发首款 ASO 疗法。", "section": "行业动态"},
    21: None,  # 跳过（Fauci 听证会，非生物医药）
    22: {"summary": "FDA 提醒投资者注意咨询委员会对审批风险的信号作用。", "section": "政策与观点"},
    23: None,  # 跳过（J&J 爽身粉赔偿，非创新药）
    24: {"summary": "FDA 更新 GLP-1 减重药物的仿制药开发指南草案。", "section": "行业动态"},
    25: {"summary": "美国拟限外国博士生签证时限，专家警告将损害科研竞争力。", "section": "行业动态"},
    26: None,  # 跳过（Fauci 听证会预览，政治花边）
    27: {"summary": "FDA 咨询委员会辩论灰色市场多肽的监管未来。", "section": "行业动态"},
    28: {"summary": "Alnylam 股价年内下跌 30% 的背后：管线接续与市场分歧。", "section": "行业动态"},
    29: None,  # 跳过（与 20 重复的 BioMarin 新闻，保留 20 即可）
    30: {"summary": "Pharma M&A 周报：Oak Hill-SPAC、Apnimed IPO、CORE 等交易动态。", "section": "行业动态"},
    31: {"summary": "Mirae 获 540 万美元，将患者聊天文本转化为结构化诊疗数据。", "section": "行业动态"},
    32: None,  # 跳过（MBA 职业建议，完全不相关）
    33: {"summary": "argenx 以 22 亿美元收购 Forte Biosciences 进军皮肤病自免管线。", "section": "行业动态"},
    34: {"summary": "诺禾致源欧洲剑桥中心扩展单细胞测序能力。", "section": "行业动态"},
    35: None,  # 跳过（职场健康峰会）
    # ===== 亦庄（3 条全留）=====
    36: {"summary": "沙砾生物北京总部（TIL 细胞治疗）在经海产业园启用。", "section": "亦庄园区动态"},
    37: {"summary": "国际医药创新公园人才保障房全面封顶。", "section": "亦庄园区动态"},
    38: {"summary": "经开区华润医药等企业入选 2025 年度中国医药工业百强。", "section": "亦庄园区动态"},
    # ===== 论文 =====
    39: {"summary": "Nature Reviews：前列腺素 E2 驱动癌症相关恶病质机制。", "section": "论文研究"},
    40: {"summary": "综述：血脑屏障在精神疾病中的作用与实验模型进展。", "section": "论文研究"},
    41: {"summary": "甜菜红素作为糖尿病肾病等多靶点治疗剂的评估。", "section": "论文研究"},
    42: {"summary": "BV 计算器：免费开源在线工具用于生物学变异估计。", "section": "论文研究"},
    43: {"summary": "提高肝硬化和 HIV 患者甲肝疫苗率的质控改善项目。", "section": "论文研究"},
    44: {"summary": "亚临床甲减/甲减孕妇的甲状腺功能变化纵向研究。", "section": "论文研究"},
    45: {"summary": "阴道雌激素不同涂抹方式预防尿路感染的随机非劣效试验。", "section": "论文研究"},
    46: {"summary": "COVID-19 与 HIV 双重感染对孕产妇不良出生结局的影响。", "section": "论文研究"},
    47: {"summary": "孕妇产前暴露于多替拉韦的妊娠与新生儿结局。", "section": "论文研究"},
    48: {"summary": "心理治疗中目标问题识别与修改过程的机制研究。", "section": "论文研究"},
    49: {"summary": "免疫检查点抑制剂起始时皮肤异常与皮疹发生相关。", "section": "论文研究"},
    # ===== 政策与观点 =====
    50: {"summary": "观点：VA 医疗体系可助美国赢得对华生物技术竞赛。", "section": "政策与观点"},
    51: None,  # 跳过（儿童住院隔离，非生物医药创新）
}

# 构建 channels
channels = [
    {"name": "Endpoints News", "home": "https://endpts.com/"},
    {"name": "STAT News", "home": "https://www.statnews.com/"},
    {"name": "Pharma Times", "home": "https://www.pharmatimes.com/"},
    {"name": "Pharmaceutical Executive", "home": "https://www.pharmexec.com/"},
    {"name": "Nature Reviews Drug Discovery", "home": "https://www.nature.com/nrd/"},
    {"name": "ClinicalTrials.gov", "home": "https://clinicaltrials.gov/"},
    {"name": "Europe PMC", "home": "https://europepmc.org/"},
    {"name": "北京亦庄·经开区官网", "home": "https://kfqgw.beijing.gov.cn/"},
    {"name": "SEC EDGAR", "home": "https://www.sec.gov/cgi-bin/browse-edgar"},
]

# 按版块归并
sections_order = ["监管审批", "临床试验", "交易速览", "行业动态", "亦庄园区动态", "论文研究", "政策追踪", "政策与观点"]
sections = {k: [] for k in sections_order}

for i, it in enumerate(raw):
    dec = curate.get(i, None)
    if dec is None:
        continue  # 被跳过的条目
    item = dict(it)
    if isinstance(dec, dict):
        for k, v in dec.items():
            item[k] = v
    if not item.get("desc"):
        item["desc"] = item["summary"]
    sections[item["section"]].append(item)

result = {
    "reportDate": "2026-07-29",
    "window": "2026-07-26 ~ 2026-07-29",
    "channels": channels,
    "sections": [{"label": k, "items": sections[k]} for k in sections_order],
    "sourceNote": "数据来自 Endpoints News / STAT News / Pharma Times / Pharmaceutical Executive / "
                   "Nature Reviews Drug Discovery / ClinicalTrials.gov / Europe PMC / "
                   "北京亦庄·经开区官网 / SEC EDGAR（P1新增）等权威公开渠道。摘要为 AI 自动生成，仅供参考。",
}

total = sum(len(v) for v in sections.values())
json.dump(result, open("pharma_final.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)
print(f"pharma_final.json: {total} 条 | ", {k: len(v) for k, v in sections.items()})
