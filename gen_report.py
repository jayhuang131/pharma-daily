# -*- coding: utf-8 -*-
import json

data = {
    "reportDate": "2026-07-29",
    "windowStart": "2026-07-22",
    "windowEnd": "2026-07-28",
    "source": "AI HOT (aihot.virxact.com)",
    "sections": [
        {
            "label": "模型发布/更新",
            "items": []
        },
        {
            "label": "产品发布/更新",
            "items": [
                {
                    "title": "OpenAI 向全美用户开放 ChatGPT Health，声称模型推理能力优于临床医生",
                    "source": "The Verge：AI",
                    "time": "2026-07-23T17:00:00.000Z",
                    "url": "https://www.theverge.com/ai-artificial-intelligence/970115/openai-chatgpt-health-launch-claims",
                    "summary": "OpenAI 向全美 18 岁以上用户开放 ChatGPT Health，可连接病历与 Apple Health 等健康数据，称推理能力优于临床医生（健康负责人随后缓和表述）。"
                }
            ]
        },
        {
            "label": "行业动态",
            "items": [
                {
                    "title": "特朗普政府公布“创世纪任务”拨款，50 亿美元投向 AI 科学项目",
                    "source": "The Verge：AI",
                    "time": "2026-07-24T14:43:55.000Z",
                    "url": "https://www.theverge.com/science/970534/genesis-mission-ai-science-funding-trump-grants",
                    "summary": "特朗普政府公布首批“创世纪任务”拨款，向 278 个 AI 驱动科学项目投入 50 亿美元，涵盖药物发现、能源与先进材料等领域。"
                },
                {
                    "title": "Insilico CEO：AI + 中国研发将药物发现缩短至 9 个月",
                    "source": "X：X.PIN",
                    "time": "2026-07-23T08:18:20.000Z",
                    "url": "https://x.com/thexpin/status/2080205860878340404",
                    "summary": "英矽智能 CEO 称，AI 与中国研发生态已将药物发现周期压缩至约一年，最快 9 个月完成候选提名，首款 AI 药物 Rentosertib 已进入 II 期临床。"
                },
                {
                    "title": "美国宣布投入 50 亿美元，利用 AI 攻克慢性病、加速药物研发",
                    "source": "IT之家",
                    "time": "2026-07-22T11:28:17.000Z",
                    "url": "https://www.ithome.com/0/980/291.htm",
                    "summary": "美国政府拟投入 50 亿美元，借助 AI 攻克慢性病病因、加速药物研发，由 15 个联邦部门参与，微软另捐 4000 万美元 AI 算力。"
                }
            ]
        },
        {
            "label": "论文研究",
            "items": [
                {
                    "title": "Chamaileon：面向多靶点与多状态蛋白结合剂设计的跨情境绑定框架",
                    "source": "HuggingFace Daily Papers",
                    "time": "2026-07-26T00:00:00.000Z",
                    "url": "https://arxiv.org/abs/2607.23518",
                    "summary": "Chamaileon 将蛋白结合剂设计从单靶点、单状态扩展至多靶点与多状态场景，统一跨情境绑定建模，代码已开源并在新基准上领先。"
                },
                {
                    "title": "北大团队基于 AlphaFold3 接触概率开发 ContactSeek 框架，赋能精准碱基编辑",
                    "source": "IT之家",
                    "time": "2026-07-25T05:17:22.000Z",
                    "url": "https://www.ithome.com/0/981/478.htm",
                    "summary": "北大团队基于 AlphaFold3 接触概率开发 ContactSeek，鉴定决定编辑特异性的关键残基并工程化改造碱基编辑工具，在维持效率的同时降低脱靶。"
                },
                {
                    "title": "团队用 AlphaFold 重新设计基因编辑蛋白以提升安全性",
                    "source": "Ars Technica：AI",
                    "time": "2026-07-24T17:31:26.000Z",
                    "url": "https://arstechnica.com/science/2026/07/team-uses-alphafold-ai-to-redesign-gene-editing-proteins-to-make-them-safer",
                    "summary": "研究团队改造 AlphaFold 识别基因编辑蛋白中导致脱靶的关键区域并加以修改，显著降低脱靶率，成果发表于《自然》。"
                }
            ]
        },
        {
            "label": "技巧与观点",
            "items": [
                {
                    "title": "OpenAI 报告：AI 编程智能体正加速基因组学等科学计算领域发展",
                    "source": "OpenAI 官网",
                    "time": "2026-07-28T17:00:00.000Z",
                    "url": "https://openai.com/index/scientific-computing-agentic-ai",
                    "summary": "OpenAI 发布实地报告，展示科学家如何用 AI 编程智能体现代化科学计算，在基因组学等领域显著加速从假设到验证的发现周期。"
                },
                {
                    "title": "微软与 Broad 研究所用 AI 推进精准肿瘤学",
                    "source": "X：Microsoft Research",
                    "time": "2026-07-24T17:05:00.000Z",
                    "url": "https://x.com/MSFTResearch/status/2080700789572456501",
                    "summary": "微软研究与 Broad 研究所合作 Project Ex Vivo（获 Dana-Farber 支持），借助 AI 更好地理解癌细胞状态，推进精准肿瘤学。"
                }
            ]
        }
    ]
}

data_json = json.dumps(data, ensure_ascii=False)

html = r'''<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>生物医药晨报 · __REPORTDATE__</title>
<style>
  :root{
    --bg:#0b0f17; --bg2:#0e131d; --card:#151b27; --card2:#1a2230;
    --line:#263041; --text:#e8edf5; --muted:#9aa7bd; --faint:#6b7689;
    --accent:#34d399; --accent2:#22d3ee; --chip:#1e2a3d; --chiptext:#7dd3c0;
    --idx:#34d399;
  }
  *{box-sizing:border-box;margin:0;padding:0}
  body{
    background:radial-gradient(1200px 600px at 70% -10%, #122031 0%, var(--bg) 55%) fixed;
    color:var(--text); font-family:-apple-system,BlinkMacSystemFont,"Segoe UI","PingFang SC","Microsoft YaHei",sans-serif;
    line-height:1.6; -webkit-font-smoothing:antialiased;
  }
  a{color:inherit}
  .wrap{max-width:1120px;margin:0 auto;padding:0 20px 60px}

  /* HERO */
  .hero{padding:46px 0 30px}
  .kicker{display:inline-flex;align-items:center;gap:8px;font-size:13px;color:var(--accent);
    border:1px solid var(--line);background:rgba(52,211,153,.08);padding:5px 12px;border-radius:999px;letter-spacing:.5px}
  .kicker .dot{width:7px;height:7px;border-radius:50%;background:var(--accent);box-shadow:0 0 10px var(--accent)}
  h1{font-size:38px;line-height:1.2;margin:16px 0 6px;font-weight:800;letter-spacing:-.5px}
  h1 .hl{background:linear-gradient(90deg,var(--accent),var(--accent2));-webkit-background-clip:text;background-clip:text;color:transparent}
  .sub{color:var(--muted);font-size:15px}
  .sub b{color:var(--text)}

  .stats{display:grid;grid-template-columns:repeat(auto-fit,minmax(150px,1fr));gap:14px;margin-top:26px}
  .stat{background:linear-gradient(180deg,var(--card),var(--bg2));border:1px solid var(--line);border-radius:16px;padding:18px 16px}
  .stat .n{font-size:30px;font-weight:800;color:var(--accent)}
  .stat .l{font-size:13px;color:var(--muted);margin-top:4px}

  /* NAV */
  .nav{position:sticky;top:0;z-index:20;background:rgba(11,15,23,.82);backdrop-filter:blur(10px);
    border-bottom:1px solid var(--line);margin-top:8px}
  .nav .inner{max-width:1120px;margin:0 auto;padding:10px 20px;display:flex;flex-wrap:wrap;gap:8px}
  .nav a{font-size:13px;color:var(--muted);text-decoration:none;border:1px solid var(--line);
    padding:6px 12px;border-radius:999px;transition:.15s;white-space:nowrap}
  .nav a:hover{color:var(--text);border-color:var(--accent);background:rgba(52,211,153,.08)}
  .nav a .c{color:var(--accent);font-weight:700;margin-left:5px}

  /* SECTION */
  section{padding-top:38px;scroll-margin-top:58px}
  .sec-head{display:flex;align-items:baseline;gap:12px;border-left:4px solid var(--accent);padding-left:14px;margin-bottom:18px}
  .sec-head h2{font-size:22px;font-weight:700}
  .sec-head .cnt{font-size:13px;color:var(--faint)}
  .empty{color:var(--faint);font-size:14px;border:1px dashed var(--line);border-radius:12px;padding:18px;background:rgba(255,255,255,.02)}

  /* GRID + CARD */
  .grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(320px,1fr));gap:16px}
  .card{position:relative;background:linear-gradient(180deg,var(--card),var(--bg2));border:1px solid var(--line);
    border-radius:16px;padding:18px 18px 16px;display:flex;flex-direction:column;gap:10px;transition:.18s;overflow:hidden}
  .card:hover{transform:translateY(-3px);border-color:#3a4a63;box-shadow:0 12px 30px rgba(0,0,0,.35)}
  .card .idx{position:absolute;top:12px;right:14px;font-size:13px;font-weight:800;color:var(--idx);
    background:rgba(52,211,153,.1);border:1px solid rgba(52,211,153,.25);border-radius:8px;padding:1px 8px;min-width:30px;text-align:center}
  .card h3{font-size:16.5px;font-weight:700;line-height:1.4;padding-right:42px}
  .meta{display:flex;flex-wrap:wrap;align-items:center;gap:8px}
  .chip{font-size:12px;color:var(--chiptext);background:var(--chip);border:1px solid #2c3a4f;border-radius:999px;padding:3px 10px}
  .time{font-size:12px;color:var(--faint)}
  .summary{font-size:14px;color:var(--muted);flex:1}
  .more{font-size:13px;color:var(--accent);text-decoration:none;font-weight:600;display:inline-flex;align-items:center;gap:4px;width:fit-content}
  .more:hover{gap:8px}

  footer{margin-top:46px;border-top:1px solid var(--line);padding-top:20px;color:var(--faint);font-size:13px}
  footer b{color:var(--muted)}
  footer .note{margin-top:8px;font-size:12.5px;color:var(--faint);line-height:1.7}
  @media (max-width:560px){
    h1{font-size:28px}
    .grid{grid-template-columns:1fr}
    .stats{grid-template-columns:repeat(2,1fr)}
  }
</style>
</head>
<body>
<div class="wrap">

  <header class="hero">
    <span class="kicker"><span class="dot"></span> 生物医药 · 创新药 晨报</span>
    <h1>__REPORTDATE__ <span class="hl">生物医药行业日报</span></h1>
    <p class="sub">数据窗口 <b>__WINSTART__ ~ __WINEND__</b>（近 7 天） · 共 <b id="totalN">0</b> 条 · 来源 <b>__SOURCE__</b></p>
    <div class="stats" id="stats"></div>
  </header>

  <nav class="nav"><div class="inner" id="nav"></div></nav>

  <main id="main"></main>

  <footer>
    <div>本日报共收录 <b id="footTotal">0</b> 条生物医药 / 创新药相关动态，数据源：<b>__SOURCE__</b>。</div>
    <div class="note">
      说明：今日（__REPORTDATE__）AI HOT 编辑日报共 24 条，均为通用 AI 资讯，未含生物医药 / 创新药内容；
      本晨报改为从 AI HOT 全量条目库按「创新药 / 药物 / 制药 / 临床 / 蛋白 / 基因 / 生物科技」等关键词检索近 7 天相关动态后整理。
      「模型发布 / 更新」版块本期未检索到生物医药相关的模型发布，故留空。
    </div>
  </footer>

</div>

<script>
const DATA = __DATA_JSON__;

const WD = ["周日","周一","周二","周三","周四","周五","周六"];
function fmtBJ(iso){
  const d = new Date(iso);
  const bj = new Date(d.getTime() + 8*3600*1000);
  const m = bj.getUTCMonth()+1, day = bj.getUTCDate();
  const wd = WD[bj.getUTCDay()];
  const hh = String(bj.getUTCHours()).padStart(2,'0');
  const mm = String(bj.getUTCMinutes()).padStart(2,'0');
  return `${m}月${day}日 ${wd} ${hh}:${mm}`;
}

// 全局连续编号：按版块固定顺序遍历
let globalIdx = 0;
const sections = DATA.sections;

// Hero 统计
const statsEl = document.getElementById('stats');
sections.forEach(s=>{
  const n = s.items.length;
  const div = document.createElement('div');
  div.className='stat';
  div.innerHTML = `<div class="n">${n}</div><div class="l">${s.label}</div>`;
  statsEl.appendChild(div);
});

// 导航
const navEl = document.getElementById('nav');
sections.forEach((s,i)=>{
  const a = document.createElement('a');
  a.href = `#sec-${i}`;
  a.innerHTML = `${s.label}<span class="c">${s.items.length}</span>`;
  navEl.appendChild(a);
});

// 正文
const mainEl = document.getElementById('main');
sections.forEach((s,i)=>{
  const sec = document.createElement('section');
  sec.id = `sec-${i}`;
  const head = document.createElement('div');
  head.className='sec-head';
  head.innerHTML = `<h2>${s.label}</h2><span class="cnt">${s.items.length} 条</span>`;
  sec.appendChild(head);

  if(s.items.length===0){
    const e = document.createElement('div');
    e.className='empty';
    e.textContent='本期未检索到该版块相关的生物医药 / 创新药动态。';
    sec.appendChild(e);
  } else {
    const grid = document.createElement('div');
    grid.className='grid';
    // 版块内按发布时间倒序
    const items = [...s.items].sort((a,b)=> new Date(b.time)-new Date(a.time));
    items.forEach(it=>{
      globalIdx++;
      const card = document.createElement('article');
      card.className='card';
      card.innerHTML = `
        <div class="idx">${globalIdx}</div>
        <h3>${it.title}</h3>
        <div class="meta">
          <span class="chip">${it.source}</span>
          <span class="time">${fmtBJ(it.time)}（北京时间）</span>
        </div>
        <p class="summary">${it.summary}</p>
        <a class="more" href="${it.url}" target="_blank" rel="noopener noreferrer">阅读原文 →</a>
      `;
      grid.appendChild(card);
    });
    sec.appendChild(grid);
  }
  mainEl.appendChild(sec);
});

document.getElementById('totalN').textContent = globalIdx;
document.getElementById('footTotal').textContent = globalIdx;
</script>
</body>
</html>
'''

html = (html
        .replace("__REPORTDATE__", data["reportDate"])
        .replace("__WINSTART__", data["windowStart"])
        .replace("__WINEND__", data["windowEnd"])
        .replace("__SOURCE__", data["source"])
        .replace("__DATA_JSON__", data_json))

with open("bio_pharma_morning_report.html", "w", encoding="utf-8") as f:
    f.write(html)
print("written bio_pharma_morning_report.html, bytes=", len(html))
print("total items:", sum(len(s['items']) for s in data['sections']))
