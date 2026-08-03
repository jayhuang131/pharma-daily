# -*- coding: utf-8 -*-
"""读取 pharma_final.json，渲染「生物医药创新药晨报」独立网站：
  1) index.html         —— 站点首页（Landing：简介 / 数据源 / 同步设置 / 入口）
  2) latest.html        —— 最新一期晨报（带收藏 + 跨设备同步）
  3) archive.html       —— 历史存档（按日期列出全部日报）
  4) report-<date>.html —— 各期日报（供存档直链）
  并维护 archive_meta.json。无外部资源（除可选的 config.js 同步地址）。
"""
import json, os, sys, shutil
from datetime import datetime

WD = ["周一", "周二", "周三", "周四", "周五", "周六", "周日"]

CSS = r'''
  :root{
    --bg:#0b0f17; --bg2:#0e131d; --card:#151b27; --line:#263041;
    --text:#e8edf5; --muted:#9aa7bd; --faint:#6b7689;
    --accent:#34d399; --accent2:#22d3ee; --chip:#1e2a3d; --chiptext:#7dd3c0; --gold:#fbbf24;
  }
  *{box-sizing:border-box;margin:0;padding:0}
  body{background:radial-gradient(1200px 600px at 70% -10%, #122031 0%, var(--bg) 55%) fixed;
    color:var(--text); font-family:-apple-system,BlinkMacSystemFont,"Segoe UI","PingFang SC","Microsoft YaHei",sans-serif;
    line-height:1.6; -webkit-font-smoothing:antialiased}
  a{color:inherit}
  .wrap{max-width:1120px;margin:0 auto;padding:0 20px 60px}
  /* 站点顶栏 */
  .sitenav{position:sticky;top:0;z-index:30;background:rgba(11,15,23,.9);backdrop-filter:blur(10px);border-bottom:1px solid var(--line)}
  .sitenav .inner{max-width:1120px;margin:0 auto;padding:10px 20px;display:flex;align-items:center;gap:18px}
  .sitenav .brand{font-weight:800;font-size:16px;color:var(--text);text-decoration:none;display:flex;align-items:center;gap:7px}
  .sitenav .brand .badge{font-size:18px}
  .sitenav a.navlink{font-size:14px;color:var(--muted);text-decoration:none;transition:.15s}
  .sitenav a.navlink:hover,.sitenav a.navlink.active{color:var(--accent)}
  .sitenav .spacer{flex:1}
  .favToggle{cursor:pointer;font-size:13px;color:var(--muted);border:1px solid var(--line);background:transparent;padding:6px 12px;border-radius:999px;transition:.15s}
  .favToggle:hover{color:var(--text);border-color:var(--gold)}
  .favToggle.on{color:#0b0f17;background:var(--gold);border-color:var(--gold);font-weight:700}
  .favCount{font-size:12.5px;color:var(--faint)}
  /* 首页 */
  .hero{padding:54px 0 26px}
  .kicker{display:inline-flex;align-items:center;gap:8px;font-size:13px;color:var(--accent);
    border:1px solid var(--line);background:rgba(52,211,153,.08);padding:5px 12px;border-radius:999px}
  .kicker .dot{width:7px;height:7px;border-radius:50%;background:var(--accent);box-shadow:0 0 10px var(--accent)}
  h1{font-size:38px;line-height:1.15;margin:18px 0 8px;font-weight:800;letter-spacing:-.5px}
  h1 .hl{background:linear-gradient(90deg,var(--accent),var(--accent2));-webkit-background-clip:text;background-clip:text;color:transparent}
  .sub{color:var(--muted);font-size:16px;max-width:640px}
  .cta{display:flex;flex-wrap:wrap;gap:12px;margin-top:26px}
  .btn{font-size:15px;font-weight:700;text-decoration:none;padding:13px 22px;border-radius:12px;transition:.18s;display:inline-flex;align-items:center;gap:8px}
  .btn.primary{background:linear-gradient(90deg,var(--accent),var(--accent2));color:#06231b}
  .btn.primary:hover{transform:translateY(-2px);box-shadow:0 10px 26px rgba(52,211,153,.25)}
  .btn.ghost{border:1px solid var(--line);color:var(--text)}
  .btn.ghost:hover{border-color:var(--accent);color:var(--accent)}
  .cards{display:grid;grid-template-columns:repeat(auto-fit,minmax(240px,1fr));gap:16px;margin-top:34px}
  .panel{background:linear-gradient(180deg,var(--card),var(--bg2));border:1px solid var(--line);border-radius:16px;padding:22px}
  .panel h3{font-size:16px;margin-bottom:10px;display:flex;align-items:center;gap:8px}
  .panel p,.panel li{color:var(--muted);font-size:14px}
  .panel ul{margin:8px 0 0 18px}
  .channels{display:flex;flex-wrap:wrap;gap:8px;margin-top:14px}
  .channels span{font-size:12px;color:var(--chiptext);background:var(--chip);border:1px solid #2c3a4f;border-radius:999px;padding:4px 11px}
  /* 同步设置 */
  .syncbox{margin-top:14px}
  .syncrow{display:flex;gap:8px;margin-top:10px;flex-wrap:wrap}
  .syncrow input{flex:1;min-width:220px;background:var(--bg);border:1px solid var(--line);color:var(--text);border-radius:10px;padding:10px 12px;font-size:14px}
  .syncrow input:focus{outline:none;border-color:var(--accent)}
  .syncrow button{cursor:pointer;border:1px solid var(--line);background:transparent;color:var(--text);border-radius:10px;padding:10px 16px;font-size:14px;transition:.15s}
  .syncrow button:hover{border-color:var(--accent);color:var(--accent)}
  .syncrow button.save{background:var(--accent);color:#06231b;border-color:var(--accent);font-weight:700}
  .syncstatus{margin-top:10px;font-size:13px;color:var(--faint)}
  .syncstatus.ok{color:var(--accent)}
  .syncstatus.err{color:#f87171}
  code{background:#0c1320;border:1px solid var(--line);border-radius:6px;padding:1px 6px;font-size:12.5px;color:var(--chiptext)}
  /* channel-stats (首页管道面板) */
  .src-stats{display:grid;grid-template-columns:repeat(auto-fill,minmax(180px,1fr));gap:10px;margin-top:12px}
  .src-item{display:flex;justify-content:space-between;align-items:center;background:rgba(255,255,255,.03);border:1px solid var(--line);border-radius:10px;padding:10px 14px}
  .src-item .sn{font-size:13px;color:var(--muted)}
  .src-item .sc{font-size:15px;font-weight:700;color:var(--accent)}
  /* 晨报页 */
  .sub2{color:var(--muted);font-size:15px}
  .sub2 b{color:var(--text)}
  .stats{display:grid;grid-template-columns:repeat(auto-fit,minmax(140px,1fr));gap:14px;margin-top:24px}
  .stat{background:linear-gradient(180deg,var(--card),var(--bg2));border:1px solid var(--line);border-radius:16px;padding:18px 16px}
  .stat .n{font-size:30px;font-weight:800;color:var(--accent)}
  .stat .l{font-size:13px;color:var(--muted);margin-top:4px}
  .nav{position:sticky;top:57px;z-index:20;background:rgba(11,15,23,.85);backdrop-filter:blur(10px);border-bottom:1px solid var(--line);margin-top:8px}
  .nav .inner{max-width:1120px;margin:0 auto;padding:10px 20px;display:flex;flex-wrap:wrap;gap:8px;align-items:center}
  .nav a{font-size:13px;color:var(--muted);text-decoration:none;border:1px solid var(--line);padding:6px 12px;border-radius:999px;transition:.15s;white-space:nowrap}
  .nav a:hover{color:var(--text);border-color:var(--accent);background:rgba(52,211,153,.08)}
  .nav a .c{color:var(--accent);font-weight:700;margin-left:5px}
  .nav .spacer{flex:1}
  .backlink{font-size:13px;color:var(--accent2);text-decoration:none;border:1px solid var(--line);padding:6px 12px;border-radius:999px}
  .backlink:hover{border-color:var(--accent2)}
  section{padding-top:38px;scroll-margin-top:120px}
  .sec-head{display:flex;align-items:baseline;gap:12px;border-left:4px solid var(--accent);padding-left:14px;margin-bottom:18px}
  .sec-head h2{font-size:22px;font-weight:700}
  .sec-head .cnt{font-size:13px;color:var(--faint)}
  .empty{color:var(--faint);font-size:14px;border:1px dashed var(--line);border-radius:12px;padding:18px;background:rgba(255,255,255,.02)}
  .grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(320px,1fr));gap:16px}
  .card{position:relative;background:linear-gradient(180deg,var(--card),var(--bg2));border:1px solid var(--line);border-radius:16px;padding:18px;display:flex;flex-direction:column;gap:10px;transition:.18s;overflow:hidden}
  .card:hover{transform:translateY(-3px);border-color:#3a4a63;box-shadow:0 12px 30px rgba(0,0,0,.35)}
  .card .idx{position:absolute;top:12px;right:14px;font-size:13px;font-weight:800;color:var(--accent);background:rgba(52,211,153,.1);border:1px solid rgba(52,211,153,.25);border-radius:8px;padding:1px 8px;min-width:30px;text-align:center}
  .card h3{font-size:16px;font-weight:700;line-height:1.4;padding-right:42px}
  /* 监管审批里程碑高亮 */
  .card.regulatory{border-left:3px solid var(--gold);background:linear-gradient(180deg,#1b2220,var(--bg2))}
  .card.regulatory:hover{border-left-color:#f59e0b}
  .card.regulatory .idx{background:rgba(251,191,36,.15);border-color:rgba(251,191,36,.3);color:var(--gold)}
  .card.regulatory .milestone{display:inline-flex;align-items:center;gap:4px;
    font-size:11px;color:var(--gold);border:1px solid rgba(251,191,36,.25);
    background:rgba(251,191,36,.08);border-radius:999px;padding:2px 8px;margin-left:6px}
  .card.regulatory .milestone::before{content:'';width:5px;height:5px;border-radius:50%;background:var(--gold)}
  /* 里程碑徽章 */
  .ms-badges{display:flex;flex-wrap:wrap;gap:6px;margin-top:-4px;margin-bottom:2px}
  .ms-badge{font-size:11px;font-weight:600;border-radius:999px;padding:2px 9px;line-height:1.5}
  .ms-badge.ph3{color:#c084fc;background:rgba(192,132,252,.12);border:1px solid rgba(192,132,252,.3)}
  .ms-badge.ph2{color:#60a5fa;background:rgba(96,165,250,.12);border:1px solid rgba(96,165,250,.3)}
  .ms-badge.ph1{color:#94a3b8;background:rgba(148,163,184,.12);border:1px solid rgba(148,163,184,.3)}
  .ms-badge.ft{color:var(--gold);background:rgba(251,191,36,.12);border:1px solid rgba(251,191,36,.3)}
  .ms-badge.bt{color:#f59e0b;background:rgba(245,158,11,.12);border:1px solid rgba(245,158,11,.3)}
  .ms-badge.ok{color:var(--accent);background:rgba(52,211,153,.12);border:1px solid rgba(52,211,153,.3)}
  .ms-badge.deal{color:#38bdf8;background:rgba(56,189,248,.12);border:1px solid rgba(56,189,248,.3)}
  .ms-badge.ipo{color:#f472b6;background:rgba(244,114,182,.12);border:1px solid rgba(244,114,182,.3)}
  /* 交易速览卡片 */
  .card.deal{border-left:3px solid #38bdf8;background:linear-gradient(180deg,#151d24,var(--bg2))}
  .card.deal:hover{border-left-color:#60a5fa}
  .card.deal .idx{background:rgba(56,189,248,.12);border-color:rgba(56,189,248,.25);color:#38bdf8}
  /* 政策追踪卡片 */
  .card.policy{border-left:3px solid #818cf8;background:linear-gradient(180deg,#171720,var(--bg2))}
  .card.policy:hover{border-left-color:#a5b4fc}
  .card.policy .idx{background:rgba(129,140,248,.12);border-color:rgba(129,140,248,.25);color:#818cf8}
  .meta{display:flex;flex-wrap:wrap;align-items:center;gap:8px}
  .chip{font-size:12px;color:var(--chiptext);background:var(--chip);border:1px solid #2c3a4f;border-radius:999px;padding:3px 10px}
  .time{font-size:12px;color:var(--faint)}
  .summary{font-size:14px;color:var(--muted);flex:1}
  .foot{display:flex;align-items:center;justify-content:space-between;gap:8px}
  .more{font-size:13px;color:var(--accent);text-decoration:none;font-weight:600;display:inline-flex;align-items:center;gap:4px}
  .more:hover{gap:8px}
  .fav{cursor:pointer;border:1px solid var(--line);background:transparent;color:var(--faint);font-size:18px;line-height:1;border-radius:9px;width:34px;height:30px;transition:.15s}
  .fav:hover{color:var(--gold);border-color:var(--gold)}
  .fav.active{color:var(--gold);border-color:var(--gold);background:rgba(251,191,36,.1)}
  footer{margin-top:46px;border-top:1px solid var(--line);padding-top:20px;color:var(--faint);font-size:13px}
  footer b{color:var(--muted)}
  footer .note{margin-top:8px;font-size:12.5px;line-height:1.7}
  footer .src{margin-top:10px;font-size:12.5px}
  footer .src a{color:var(--chiptext);text-decoration:none;border-bottom:1px dotted #2c3a4f}
  /* archive index */
  .arc-item{display:flex;align-items:center;gap:16px;background:linear-gradient(180deg,var(--card),var(--bg2));border:1px solid var(--line);border-radius:14px;padding:16px 18px;margin-bottom:12px;text-decoration:none;transition:.15s}
  .arc-item:hover{border-color:var(--accent);transform:translateX(4px)}
  .arc-item .d{font-size:20px;font-weight:800;color:var(--text);min-width:130px}
  .arc-item .w{font-size:13px;color:var(--faint);min-width:48px}
  .arc-item .t{font-size:13px;color:var(--muted);flex:1}
  .badge-now{font-size:11.5px;color:#0b0f17;background:var(--accent);border-radius:999px;padding:2px 9px;font-weight:700}
  .arc-item .go{color:var(--accent);font-weight:700}
  @media (max-width:560px){
    h1{font-size:27px}
    .grid{grid-template-columns:1fr}.stats{grid-template-columns:repeat(2,1fr)}
    .arc-item .d{min-width:0;font-size:17px}
    .nav{top:57px}
    .cta{flex-direction:column}
    .cta .btn{justify-content:center;text-align:center}
    .syncrow{flex-direction:column}.syncrow input{min-width:auto}
    .src-stats{grid-template-columns:1fr}
    .sitenav .inner{gap:10px;flex-wrap:wrap}
  }
'''

# 配置脚本：可被部署者改成自己的同步后端地址；也为首页 UI 提供默认值
CONFIG_JS = r'''
// 跨设备同步后端地址：留空则自动尝试同源 /api/favs，失败回退浏览器本地。
// 部署到公开网址时，把下面改成你的同步服务地址（需公网可达，如 http://your-server:8000）。
window.__SYNC_API__ = "";
'''

# ---- 同步地址解析 + 收藏逻辑（所有页面共用）----
SYNC_CFG_JS = r'''
// 同步地址 / 令牌：优先 config.js，其次首页 UI 存在 localStorage 的值
(function(){
  try{
    window.__SYNC_API__=(localStorage.getItem('pharma_sync_api')||window.__SYNC_API__||'').trim();
    window.__SYNC_TOKEN__=(localStorage.getItem('pharma_sync_token')||window.__SYNC_TOKEN__||'').trim();
  }catch(e){}
})();
function apiBase(){var s=(window.__SYNC_API__||'').trim();return s?s.replace(/\/+$/,''):'';}
function favApi(){var b=apiBase();return b?b+'/api/favs':'/api/favs';}
function favHeaders(json){var h={};if(json)h['Content-Type']='application/json';
  if(window.__SYNC_TOKEN__)h['X-Fav-Token']=window.__SYNC_TOKEN__;return h;}
'''

FAV_JS = r'''
const FAV_KEY='pharma_favs';
let FAVS=[];        // [{url,title,section,ts}]
let SERVER=false;   // 是否连上同步服务（跨设备共享）
let FAV_ONLY=false;
function lsLoad(){try{return JSON.parse(localStorage.getItem(FAV_KEY))||[]}catch(e){return[]}}
function lsSave(a){try{localStorage.setItem(FAV_KEY,JSON.stringify(a))}catch(e){}}
async function loadFavs(){
  if(!apiBase()){FAVS=lsLoad();SERVER=false;return;}   // 未配置后端 -> 本地
  try{const r=await fetch(favApi(),{cache:'no-store',headers:favHeaders(false)});
    if(r.ok){FAVS=await r.json();SERVER=true;return;}}catch(e){}
  FAVS=lsLoad();SERVER=false;                          // 后端不可达 -> 本地回退
}
function isFav(u){return FAVS.some(f=>f.url===u);}
function refreshCount(){const el=document.getElementById('favCount');
  if(el)el.textContent='已收藏 '+FAVS.length+' 篇'+(SERVER?' · 已同步':' · 本地');}
function paint(btn){const on=isFav(btn.dataset.url);
  btn.classList.toggle('active',on);btn.textContent=on?'★':'☆';btn.title=on?'取消收藏':'收藏';}
async function toggle(btn){
  const u=btn.dataset.url,t=btn.dataset.title||'',s=btn.dataset.section||'';
  if(SERVER){
    try{
      if(isFav(u))await fetch(favApi()+'?url='+encodeURIComponent(u),{method:'DELETE',headers:favHeaders(false)});
      else await fetch(favApi(),{method:'POST',headers:favHeaders(true),
        body:JSON.stringify({url:u,title:t,section:s,ts:Date.now()})});
      const r=await fetch(favApi(),{cache:'no-store',headers:favHeaders(false)});
      if(r.ok)FAVS=await r.json();
    }catch(e){SERVER=false;}
  }
  if(!SERVER){
    const i=FAVS.findIndex(f=>f.url===u);
    if(i>=0)FAVS.splice(i,1);else FAVS.push({url:u,title:t,section:s,ts:Date.now()});
    lsSave(FAVS);
  }
  document.querySelectorAll('.fav').forEach(b=>{if(b.dataset.url===u)paint(b);});
  refreshCount();
  if(FAV_ONLY)applyFilter();
}
function applyFilter(){
  document.querySelectorAll('.card').forEach(c=>{
    c.style.display=(!FAV_ONLY||isFav(c.dataset.url))?'':'none';
  });
  document.querySelectorAll('section[data-sec]').forEach(sec=>{
    const any=[...sec.querySelectorAll('.card')].some(c=>c.style.display!=='none');
    sec.style.display=any?'':'none';
  });
}
document.addEventListener('click',e=>{
  const btn=e.target.closest('.fav');
  if(btn)toggle(btn);
});
document.addEventListener('DOMContentLoaded',async()=>{
  await loadFavs();
  document.querySelectorAll('.fav').forEach(paint);
  refreshCount();
  const tg=document.getElementById('favToggle');
  if(tg)tg.addEventListener('click',()=>{FAV_ONLY=!FAV_ONLY;tg.classList.toggle('on',FAV_ONLY);
    tg.textContent=FAV_ONLY?'★ 只看收藏':'☆ 只看收藏';applyFilter();});
  // 首页同步设置
  const inp=document.getElementById('syncUrl');
  if(inp){
    const tinp=document.getElementById('syncToken');
    inp.value=window.__SYNC_API__||'';
    if(tinp)tinp.value=window.__SYNC_TOKEN__||'';
    const st=document.getElementById('syncStatus');
    const save=document.getElementById('syncSave');
    const clr=document.getElementById('syncClear');
    function setStatus(t,cls){st.textContent=t;st.className='syncstatus '+(cls||'');}
    if(window.__SYNC_API__)setStatus('当前同步地址：'+window.__SYNC_API__+(window.__SYNC_TOKEN__?'（已带令牌）':'')+'，已生效','ok');
    else setStatus('未配置同步地址，收藏仅保存在本浏览器。填入你的同步服务地址即可跨设备共享。');
    save.onclick=async()=>{
      const v=inp.value.trim();
      const tk=tinp?tinp.value.trim():'';
      try{localStorage.setItem('pharma_sync_api',v);localStorage.setItem('pharma_sync_token',tk);}catch(e){}
      window.__SYNC_API__=v;window.__SYNC_TOKEN__=tk;
      if(!v){setStatus('已清除，收藏仅本浏览器保存。');await loadFavs();refreshCount();return;}
      try{const r=await fetch(favApi(),{cache:'no-store',headers:favHeaders(false)});
        if(r.ok){await loadFavs();refreshCount();setStatus('已连接同步服务：'+v+(tk?'（已带令牌）':''),'ok');}
        else if(r.status===401)setStatus('已保存，但后端要求令牌校验失败(401)。请确认令牌填写正确，且后端 FAV_TOKEN 与之匹配。','err');
        else setStatus('已保存，但连接测试返回 '+r.status+'，请确认地址可公网访问。','err');
      }catch(e){setStatus('已保存，但无法连接（'+e.message+'）。请确认服务已启动且可公网访问。','err');}
    };
    clr.onclick=()=>{try{localStorage.removeItem('pharma_sync_api');localStorage.removeItem('pharma_sync_token');}catch(e){}window.__SYNC_API__='';window.__SYNC_TOKEN__='';inp.value='';if(tinp)tinp.value='';setStatus('已清除，收藏仅本浏览器保存。');};
  }
});
'''


def site_nav(active, with_fav=False, with_search=False):
    links = [
        ("index.html", "首页", "home"),
        ("latest.html", "今日晨报", "today"),
        ("archive.html", "历史存档", "archive"),
        ("weekly.html", "本周周报", "weekly"),
    ]
    nav = '<nav class="sitenav"><div class="inner">'
    nav += '<a class="brand" href="index.html"><span class="badge">💊</span> 生物医药晨报</a>'
    for href, label, key in links:
        cls = "navlink" + (" active" if key == active else "")
        nav += f'<a class="{cls}" href="{href}">{label}</a>'
    nav += '<span class="spacer"></span>'
    if with_search:
        nav += ('<input type="text" id="searchBox" placeholder="搜索标题/公司/药品..." '
                'style="background:var(--bg);border:1px solid var(--line);color:var(--text);'
                'border-radius:8px;padding:6px 14px;font-size:13px;width:200px;margin-right:8px" '
                'oninput="doSearch(this.value)">')
    if with_fav:
        nav += ('<button class="favToggle" id="favToggle">☆ 只看收藏</button>'
                '<span class="favCount" id="favCount">已收藏 0 篇</span>')
    nav += '</div></nav>'
    return nav


def page_head(title, css_extra=""):
    return (f'<!DOCTYPE html>\n<html lang="zh-CN">\n<head>\n<meta charset="UTF-8">\n'
            f'<meta name="viewport" content="width=device-width, initial-scale=1.0">\n'
            f'<title>{title}</title>\n<script src="config.js"></script>\n'
            f'<style>{CSS}{css_extra}</style>\n</head>\n<body>\n')


def page_foot(note=""):
    return (f'<footer><div>本站为生物医药 / 创新药行业资讯聚合演示，数据来自公开权威渠道，仅供参考，不构成投资建议。</div>'
            f'{("<div class=\"note\">"+note+"</div>") if note else ""}'
            f'</footer>\n</body>\n</html>')


def render_home(data):
    date = data["reportDate"]
    total = sum(len(s["items"]) for s in data["sections"])
    channels = data.get("channels", [])
    note = data.get("sourceNote", "")
    ch_html = "".join(f"<span>{c['name']}</span>" for c in channels)
    # 按来源统计条数
    src_cnt = {}
    for sec in data["sections"]:
        for it in sec["items"]:
            src = it.get("source", "未知")
            src_cnt[src] = src_cnt.get(src, 0) + 1
    src_stats = "".join(
        f'<div class="src-item"><span class="sn">{s}</span><span class="sc">{c}</span></div>'
        for s, c in sorted(src_cnt.items(), key=lambda x: -x[1]))
    body = (
        site_nav("home") +
        '<div class="wrap"><div class="hero">'
        '<span class="kicker"><span class="dot"></span> 生物医药 · 创新药 晨报 · 多渠道聚合</span>'
        '<h1>生物医药行业<br><span class="hl">创新药每日晨报</span></h1>'
        f'<p class="sub">聚合国际医药媒体、官方临床/文献数据库与园区官网的公开资讯，每日自动生成。最新一期：<b>{date}</b>（共 <b>{total}</b> 条 · <b>{len(src_cnt)}</b> 个渠道）。</p>'
        '<div class="cta">'
        '<a class="btn primary" href="latest.html">阅读今日晨报 →</a>'
        '<a class="btn ghost" href="archive.html">历史存档</a>'
        '</div></div>'
        '<div class="cards">'
        f'<div class="panel"><h3>📊 今日数据管道（{len(src_cnt)} 个渠道 · {total} 条）</h3>'
        f'<div class="src-stats">{src_stats}</div></div>'
        '<div class="panel"><h3>⭐ 收藏跨设备同步</h3>'
        '<div class="syncbox"><p>收藏默认只存本浏览器。想跨设备共享，把本站指向你的同步服务即可（在运行 <code>pharma_server.py</code> 的机器/服务器上填写其可访问地址）：</p>'
        '<div class="syncrow"><input id="syncUrl" placeholder="https://你的隧道地址:8000"><button class="save" id="syncSave">保存</button><button id="syncClear">清除</button></div>'
        '<div class="syncrow"><input id="syncToken" placeholder="同步令牌（后端设了 FAV_TOKEN 时必填，留空表示无）"></div>'
        '<div id="syncStatus" class="syncstatus"></div></div></div>'
        '<div class="panel"><h3>🗂 关于本站</h3>'
        '<ul><li>每日自动聚合创新药相关动态</li><li>八版块：监管审批 / 临床试验 / 交易速览 / 行业动态 / 亦庄园区动态 / 论文研究 / 政策追踪 / 政策与观点</li><li>里程碑徽章：Phase 3 / Fast Track / Breakthrough / 获批 / 交易 / IPO 等</li><li>收藏可跨设备同步（需自备同步服务）</li></ul></div>'
        '</div></div>'
    )
    html = page_head("生物医药晨报 · 独立网站") + body + page_foot(note)
    html = html.replace('</body>', '<script>' + SYNC_CFG_JS + FAV_JS + '</script></body>')
    return html


def render_archive(entries):
    items = ""
    for e in entries:
        badge = '<span class="badge-now">最新</span>' if e.get("latest") else ''
        items += (f'<a class="arc-item" href="{e["file"]}">'
                  f'<span class="d">{e["date"]}</span>'
                  f'<span class="w">{e["weekday"]}</span>'
                  f'<span class="t">共 {e["total"]} 条</span>{badge}'
                  f'<span class="go">查看 →</span></a>\n')
    if not items:
        items = '<div class="empty">暂无历史日报。</div>'
    body = (site_nav("archive") +
            '<div class="wrap"><div class="hero">'
            '<span class="kicker"><span class="dot"></span> 生物医药 · 创新药 晨报</span>'
            '<h1><span class="hl">日报历史存档</span></h1>'
            '<p class="sub">每日自动聚合的生物医药 / 创新药行业日报，按日期留存，点击任意一天回看。</p></div>'
            f'<main>{items}</main></div>')
    html = page_head("生物医药行业日报 · 历史存档") + body + page_foot(
        "收藏通过同步服务（favs.json）跨设备共享；若未配置同步服务，则自动回退为浏览器本地存储。")
    html = html.replace('</body>', '<script>' + SYNC_CFG_JS + FAV_JS + '</script></body>')
    return html


def render_report(data, is_latest=False):
    sections = data["sections"]
    channels = data.get("channels", [])
    data_json = json.dumps(data, ensure_ascii=False)
    body = (
        site_nav("today", with_fav=True, with_search=True) +
        '<div class="wrap">'
        '<header class="hero">'
        '<span class="kicker"><span class="dot"></span> 生物医药 · 创新药 晨报 · 多渠道聚合</span>'
        f'<h1>{data["reportDate"]} <span class="hl">生物医药行业日报</span></h1>'
        f'<p class="sub2">数据窗口 <b>{data["window"]}</b> · 共 <b id="totalN">0</b> 条 · 覆盖 <b>{len(channels)}</b> 个权威公开渠道</p>'
        '<div class="channels" id="channels"></div>'
        '<div class="stats" id="stats"></div>'
        '</header>'
        '<nav class="nav"><div class="inner">'
        '<a class="backlink" href="archive.html">← 日报存档</a>'
        '<span id="nav"></span>'
        '<span class="spacer"></span>'
        '<button class="favToggle" id="favToggle">☆ 只看收藏</button>'
        '<span class="favCount" id="favCount">已收藏 0 篇</span>'
        '</div></nav>'
        '<main id="main"></main>'
        '<footer>'
        '<div>本日报共收录 <b id="footTotal">0</b> 条生物医药 / 创新药相关动态。</div>'
        f'<div class="note">{data.get("sourceNote","")}</div>'
        '<div class="src" id="srcLinks"></div>'
        '</footer>'
        '</div>'
    )
    script = r'''
<script>
const DATA = __DATA_JSON__;
const WD = ["周日","周一","周二","周三","周四","周五","周六"];
function fmtBJ(iso){ if(!iso) return ""; const d=new Date(iso); const bj=new Date(d.getTime()+8*3600*1000);
  const m=bj.getUTCMonth()+1,day=bj.getUTCDate(),wd=WD[bj.getUTCDay()];
  const hh=String(bj.getUTCHours()).padStart(2,'0'),mm=String(bj.getUTCMinutes()).padStart(2,'0');
  return `${m}月${day}日 ${wd} ${hh}:${mm}`; }
const chEl=document.getElementById('channels');
(DATA.channels||[]).forEach(c=>{const s=document.createElement('span');s.textContent=c.name;chEl.appendChild(s);});
const statsEl=document.getElementById('stats');
DATA.sections.forEach(s=>{const d=document.createElement('div');d.className='stat';
  d.innerHTML=`<div class="n">${s.items.length}</div><div class="l">${s.label}</div>`;statsEl.appendChild(d);});
const navEl=document.getElementById('nav');
DATA.sections.forEach((s,i)=>{const a=document.createElement('a');a.href=`#sec-${i}`;
  a.innerHTML=`${s.label}<span class="c">${s.items.length}</span>`;navEl.appendChild(a);});
let idx=0; const mainEl=document.getElementById('main');
DATA.sections.forEach((s,i)=>{
  const sec=document.createElement('section');sec.id=`sec-${i}`;sec.setAttribute('data-sec',i);
  sec.innerHTML=`<div class="sec-head"><h2>${s.label}</h2><span class="cnt">${s.items.length} 条</span></div>`;
  if(!s.items.length){const e=document.createElement('div');e.className='empty';
    e.textContent='本期该渠道未检索到相关动态。';sec.appendChild(e);}
  else{const g=document.createElement('div');g.className='grid';
    [...s.items].sort((a,b)=>new Date(b.time)-new Date(a.time)).forEach(it=>{idx++;
      const c=document.createElement('article');c.className='card';c.dataset.url=it.url;
      if(s.label==='监管审批')c.classList.add('regulatory');
      if(s.label==='交易速览')c.classList.add('deal');
      if(s.label==='政策追踪')c.classList.add('policy');
      c.innerHTML=`<div class="idx">${idx}</div><h3>${it.title}</h3>
        <div class="meta"><span class="chip">${it.source}</span><span class="time">${fmtBJ(it.time)}（北京时间）</span></div>
        <p class="summary">${it.summary}</p>
        <div class="foot"><a class="more" href="${it.url}" target="_blank" rel="noopener noreferrer">阅读原文 →</a>
        <button class="fav" data-url="${it.url}" data-title="${it.title}" data-section="${s.label}" title="收藏">☆</button></div>`;
      g.appendChild(c);});
    sec.appendChild(g);}
  mainEl.appendChild(sec);
});
document.getElementById('totalN').textContent=idx;
document.getElementById('footTotal').textContent=idx;
const sl=document.getElementById('srcLinks');
if((DATA.channels||[]).length){sl.innerHTML='来源渠道：'+DATA.channels.map(c=>`<a href="${c.home}" target="_blank" rel="noopener noreferrer">${c.name}</a>`).join(' · ');}
// 里程碑徽章注入（投资视角关键信号）
document.querySelectorAll('.card').forEach(c=>{
  const t=(c.querySelector('h3')?.textContent||'')+(c.querySelector('.summary')?.textContent||'');
  const b=[];
  if(/\bphase\s*3\b|phase\s*iii|iii期/.test(t.toLowerCase()))b.push('<span class="ms-badge ph3">Phase 3</span>');
  if(/\bphase\s*2\b|phase\s*ii(?!\s*i)|ii期/.test(t.toLowerCase()))b.push('<span class="ms-badge ph2">Phase 2</span>');
  if(/\bphase\s*1\b|phase\s*i(?!\s*i)|i期/.test(t.toLowerCase()))b.push('<span class="ms-badge ph1">Phase 1</span>');
  if(/fast\s*track|快速通道/.test(t.toLowerCase()))b.push('<span class="ms-badge ft">Fast Track</span>');
  if(/breakthrough|突破性疗法/.test(t.toLowerCase()))b.push('<span class="ms-badge bt">突破性</span>');
  if(/fda\s*approv|获批|批准上市|authori[sz]/i.test(t.toLowerCase()))b.push('<span class="ms-badge ok">获批</span>');
  if(/\$[\d.,]+\s*(billion|million|亿|万)|[\d.]+\s*(亿|万)\s*(美元|美金)/.test(t))b.push('<span class="ms-badge deal">交易</span>');
  if(/\bipo\b|首次公开|上市/.test(t.toLowerCase()))b.push('<span class="ms-badge ipo">IPO</span>');
  if(b.length){const d=document.createElement('div');d.className='ms-badges';
    d.innerHTML=b.join('');c.insertBefore(d,c.querySelector('.meta'));}
});
// 搜索框
function doSearch(q){
  if(!q||q.trim().length<2){document.querySelectorAll('.card').forEach(c=>c.style.display='');
    document.querySelectorAll('section[data-sec]').forEach(s=>s.style.display='');return;}
  q=q.toLowerCase();
  document.querySelectorAll('.card').forEach(c=>{
    const txt=(c.querySelector('h3')?.textContent||'')+(c.querySelector('.summary')?.textContent||'');
    c.style.display=txt.toLowerCase().includes(q)?'':'none';
  });
  document.querySelectorAll('section[data-sec]').forEach(sec=>{
    const any=[...sec.querySelectorAll('.card')].some(c=>c.style.display!=='none');
    sec.style.display=any?'':'none';
  });
}
</script>
'''
    html = page_head(f"生物医药晨报 · {data['reportDate']}") + body + "</body>\n</html>"
    html = html.replace('</body>',
                        '<script>' + SYNC_CFG_JS + FAV_JS + '</script>'
                        + script.replace("__DATA_JSON__", data_json) + '</body>')
    return html


def weekday_cn(date_str):
    d = datetime.strptime(date_str, "%Y-%m-%d")
    return WD[d.weekday()]


def render_weekly(data, archive_entries):
    """本周周报：本周统计 + 八版块 TOP + 各渠道统计"""
    from collections import Counter
    sections = data["sections"]
    total = sum(len(s["items"]) for s in sections)
    channels_str = " · ".join(c["name"] for c in data.get("channels", []))

    # 按渠道统计
    src_cnt = Counter()
    for sec in sections:
        for it in sec["items"]:
            src_cnt[it.get("source", "未知")] += 1
    src_rows = "".join(
        f"<div class='src-item'><span class='sn'>{s}</span><span class='sc'>{c}</span></div>"
        for s, c in src_cnt.most_common())

    # 各版块 TOP
    sec_html = ""
    for sec in sections:
        items = sec["items"]
        if not items:
            continue
        items_html = ""
        top_n = min(5, len(items))
        for i, it in enumerate(items[:top_n]):
            items_html += (
                f"<div class='card'>"
                f"<div class='idx'>{i+1}</div>"
                f"<h3>{it['title']}</h3>"
                f"<div class='meta'><span class='chip'>{it.get('source','')}</span></div>"
                f"<p class='summary'>{it.get('summary','')}</p>"
                f"<a class='more' href='{it.get('url','#')}' target='_blank'>阅读原文 →</a>"
                f"</div>"
            )
        sec_html += (
            f"<section><div class='sec-head'><h2>{sec['label']}</h2>"
            f"<span class='cnt'>共 {len(items)} 条</span></div>"
            f"<div class='grid'>{items_html}</div></section>"
        )

    body = (
        site_nav("weekly") +
        f'<div class="wrap"><div class="hero">'
        f'<span class="kicker"><span class="dot"></span> 生物医药 · 创新药 晨报</span>'
        f'<h1><span class="hl">本周周报</span></h1>'
        f'<p class="sub2">报告日期 <b>{data["reportDate"]}</b> · 数据窗口 <b>{data["window"]}</b> · '
        f'共 <b>{total}</b> 条 · <b>{len(src_cnt)}</b> 个渠道</p>'
        f'<div class="cards">'
        f'<div class="panel"><h3>📊 渠道统计（{len(src_cnt)} 路 · {total} 条）</h3>'
        f'<div class="src-stats">{src_rows}</div></div>'
        f'</div></div>'
        f'<nav class="nav" style="top:57px"><div class="inner">'
        f'<a class="backlink" href="index.html">← 回首页</a>'
        f'<a href="#sec-0">监管审批</a><a href="#sec-1">临床试验</a>'
        f'<a href="#sec-2">交易速览</a><a href="#sec-3">行业动态</a>'
        f'<a href="#sec-4">亦庄园区</a><a href="#sec-5">论文研究</a>'
        f'<a href="#sec-6">政策追踪</a><a href="#sec-7">政策与观点</a>'
        f'</div></nav>'
        f'<main>{sec_html}</main>'
        f'<footer><div>本周共 {total} 条动态，覆盖 {len(src_cnt)} 个渠道。</div>'
        f'<div class="note">{data.get("sourceNote","")}</div></footer></div>'
    )

    html = page_head(f"生物医药晨报 · 本周周报 · {data['reportDate']}") + body + page_foot(
        f"渠道：{channels_str}。中文摘要 AI 生成，仅供参考。")
    return html


def main():
    src = sys.argv[1] if len(sys.argv) > 1 else "pharma_final.json"
    data = json.load(open(src, encoding="utf-8"))
    date = data["reportDate"]
    total = sum(len(s["items"]) for s in data["sections"])

    # 1) 各期日报 + 最新入口
    report_file = f"report-{date}.html"
    with open(report_file, "w", encoding="utf-8") as f:
        f.write(render_report(data, is_latest=False))
    with open("latest.html", "w", encoding="utf-8") as f:
        f.write(render_report(data, is_latest=True))

    # 2) 维护存档元数据
    meta_path = "archive_meta.json"
    meta = {}
    if os.path.exists(meta_path):
        try:
            meta = json.load(open(meta_path, encoding="utf-8"))
        except Exception:
            meta = {}
    meta[date] = {"file": report_file, "total": total, "weekday": weekday_cn(date)}
    json.dump(meta, open(meta_path, "w", encoding="utf-8"), ensure_ascii=False, indent=1)

    # 3) 历史索引（日期倒序）+ 首页 + 周报
    entries = []
    for d in sorted(meta.keys(), reverse=True):
        e = dict(meta[d])
        e["date"] = d
        entries.append(e)
    if entries:
        entries[0]["latest"] = True
    with open("archive.html", "w", encoding="utf-8") as f:
        f.write(render_archive(entries))
    with open("index.html", "w", encoding="utf-8") as f:
        f.write(render_home(data))

    # 4) 周报
    with open("weekly.html", "w", encoding="utf-8") as f:
        f.write(render_weekly(data, entries))

    # 5) config.js
    with open("config.js", "w", encoding="utf-8") as f:
        f.write(CONFIG_JS)

    print(f"site built: index.html + latest.html + archive.html + weekly.html + {report_file} | date={date} total={total} | 存档 {len(entries)} 期")


if __name__ == "__main__":
    main()
