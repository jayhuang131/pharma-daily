# -*- coding: utf-8 -*-
"""生成生物医药周报 HTML 邮件正文（浅底深字，表格排版）。"""
import html

MON = "2026-08-10"
FRI = "2026-08-14"
TITLE = "生物医药创新药周报 | 2026 年 8 月 14 日（本周）"
OVERVIEW = f"本期数据窗口 {MON} ~ {FRI}，共精选 73 条，覆盖 8 个版块。"
SITE_URL = "https://19338310dcbc4726a0b86cb2c28db96b.gz3.agentos-app.net"

# 版块顺序：监管审批 / 临床试验 / 交易速览 / 行业动态 / 亦庄园区动态 / 论文研究 / 政策追踪 / 政策与观点
SECTIONS = [
    ("监管审批", [
        ("Taiho 与 Cullinan 的 zipalertinib 在 EGFR 20 外显子突变肺癌中数据亮眼，威胁多款已获批药物",
         "https://www.biopharmadive.com/news/taiho-cullinan-zipalertinib-egfr-exon20-lung-cancer-results/827785/"),
        ("溶瘤病毒疗法获 FDA 批准，肿瘤免疫治疗再添新选择",
         "https://www.nature.com/articles/d41573-026-00136-z"),
        ("北京经开区上半年两款Ⅰ类新药获批上市，数量占全市一半",
         "https://kfqgw.beijing.gov.cn/ywdt/gzdt/202608/t20260810_4816422.html"),
    ]),
    ("临床试验", [
        ("Survodutide（GLP-1/GCG 双激动剂）开展 2 型糖尿病血糖控制研究",
         "https://clinicaltrials.gov/study/NCT07754461"),
        ("BTK 抑制剂 Remibrutinib 评估多发性硬化脑影像与免疫变化",
         "https://clinicaltrials.gov/study/NCT07758270"),
        ("Kupando Ⅰ期临床试验完成首例患者给药",
         "https://pharmatimes.com/news/kupando-doses-first-patient-in-phase-1-trial/"),
    ]),
    ("交易速览", [
        ("PTC 押注 Sangamo 法布里病基因疗法，分析师视为高风险高回报交易",
         "https://www.biopharmadive.com/news/ptc-sangamo-fabry-gene-therapy-bankruptcy-sale-lilly/827767/"),
        ("礼来发起六起诉讼，打击 retatrutide 减肥药黑市",
         "https://www.biopharmadive.com/news/lilly-lawsuit-retatrutide-black-market-obesity-drug/827659/"),
    ]),
    ("行业动态", [
        ("Boulevard 以 6500 万美元启动，开发靶向自身免疫疾病药物",
         "https://www.biopharmadive.com/news/boulevard-immune-drugs-igan-georg-schett/827583/"),
        ("迷幻药开发商 Definium 的 LSD 药片再获积极数据",
         "https://www.biopharmadive.com/news/definium-lsd-psychedelics-trial-results-gad-anxiety/827669/"),
    ]),
    ("亦庄园区动态", [
        ("经开区审议生物医药创新平台建设、AI4Chip 行动计划等事项",
         "https://kfqgw.beijing.gov.cn/ywdt/lddt/202608/t20260810_4816437.html"),
        ("全球首个企业自研药物完成类风湿关节炎临床首例给药",
         "https://kfqgw.beijing.gov.cn/cxyzkfq/yzal/202608/t20260807_4813186.html"),
    ]),
    ("论文研究", [
        ("CRISPR 靶向 BRAF 致癌基因，治疗儿童低级别胶质瘤",
         "https://doi.org/10.64898/2026.08.12.744431"),
        ("二甲双胍、抗生素等常用药塑造肠道菌群，关联结直肠肿瘤",
         "https://doi.org/10.64898/2026.08.12.26360274"),
    ]),
    ("政策追踪", []),
    ("政策与观点", [
        ("Pharmaceutical Executive 公布 2026 新兴医药领袖获奖名单",
         "https://www.pharmexec.com/view/daily-2026-emerging-leaders-winners"),
    ]),
]

CHANNELS = [
    "Endpoints News", "Fierce Biotech", "STAT News", "Pharma Times",
    "Pharmaceutical Executive", "PRNewswire BioTech", "BioPharma Dive", "GEN",
    "Nature Reviews Drug Discovery", "ClinicalTrials.gov", "Europe PMC",
    "北京亦庄·经开区官网", "SEC EDGAR", "CDE 药审中心",
]


def esc(s):
    return html.escape(s, quote=False)


rows = []
for label, items in SECTIONS:
    if not items:
        rows.append(
            f'<tr><td style="padding:10px 12px;border-bottom:1px solid #e6e8eb;color:#6b7280;font-size:13px;">'
            f'<b style="color:#1f2937;">{esc(label)}</b>&nbsp;&nbsp;本周无新增</td></tr>'
        )
        continue
    rows.append(
        f'<tr><td style="padding:12px 12px 4px;background:#f3f4f6;border-bottom:1px solid #e6e8eb;">'
        f'<b style="font-size:14px;color:#111827;">{esc(label)}</b></td></tr>'
    )
    for i, (summary, url) in enumerate(items, 1):
        rows.append(
            f'<tr><td style="padding:8px 12px;border-bottom:1px solid #f0f1f3;">'
            f'<div style="font-size:14px;color:#111827;line-height:1.5;">{i}. {esc(summary)}</div>'
            f'<div style="margin-top:3px;font-size:12px;">'
            f'<a href="{esc(url)}" style="color:#1d4ed8;text-decoration:none;">阅读原文 →</a>'
            f'</div></td></tr>'
        )

rows_html = "\n".join(rows)
channels_html = "、".join(esc(c) for c in CHANNELS)

html_doc = f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{esc(TITLE)}</title>
</head>
<body style="margin:0;padding:0;background:#f5f6f8;font-family:'Segoe UI','Microsoft YaHei',Arial,sans-serif;">
<table role="presentation" width="100%" cellpadding="0" cellspacing="0" style="background:#f5f6f8;padding:20px 0;">
  <tr>
    <td align="center">
      <table role="presentation" width="640" cellpadding="0" cellspacing="0" style="max-width:640px;width:100%;background:#ffffff;border:1px solid #e6e8eb;border-radius:6px;overflow:hidden;">
        <!-- 标题区 -->
        <tr>
          <td style="padding:22px 24px;background:#0f172a;">
            <div style="font-size:19px;font-weight:700;color:#ffffff;line-height:1.4;">{esc(TITLE)}</div>
            <div style="margin-top:6px;font-size:12px;color:#cbd5e1;">{esc(OVERVIEW)}</div>
          </td>
        </tr>
        <!-- 精选列表 -->
        <tr>
          <td style="padding:0;">
            <table role="presentation" width="100%" cellpadding="0" cellspacing="0">
{rows_html}
            </table>
          </td>
        </tr>
        <!-- 页脚 -->
        <tr>
          <td style="padding:18px 24px;background:#f9fafb;border-top:1px solid #e6e8eb;">
            <div style="font-size:12px;color:#6b7280;line-height:1.7;">
              <b style="color:#374151;">数据来源：</b>{channels_html}。<br>
              <b style="color:#374151;">完整日报：</b><a href="{esc(SITE_URL)}" style="color:#1d4ed8;text-decoration:none;">{esc(SITE_URL)}</a>
            </div>
            <div style="margin-top:8px;font-size:11px;color:#9ca3af;">
              本邮件由生物医药日报系统自动生成，摘要为 AI 生成，仅供参考，不构成投资建议。
            </div>
          </td>
        </tr>
      </table>
    </td>
  </tr>
</table>
</body>
</html>
"""

with open("weekly_report_20260814.html", "w", encoding="utf-8") as f:
    f.write(html_doc)

print("已生成 weekly_report_20260814.html，长度:", len(html_doc))
print("精选条目数:", sum(len(i) for _, i in SECTIONS))
