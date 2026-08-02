# -*- coding: utf-8 -*-
"""全自动流水线：抓取 → 中文摘要清洗 → 渲染 → 推 GitHub。适合每日定时跑。"""
import json, subprocess, sys, os
from datetime import datetime

PY = sys.executable

print("===== Step 1: pharma_fetch.py =====")
subprocess.run([PY, "pharma_fetch.py"], check=False)

if not os.path.exists("pharma_raw.json"):
    print("[ERR] pharma_raw.json not found, abort.")
    sys.exit(1)

# ----- Step 2: 中文摘要生成（含噪音过滤、去重、分类） -----
print("===== Step 2: gen_summary.py =====")
subprocess.run([PY, "gen_summary.py"], check=False)

if not os.path.exists("pharma_final.json"):
    print("[ERR] pharma_final.json not found, abort.")
    sys.exit(1)

# ----- Step 3: 渲染 -----
print("===== Step 3: pharma_build.py =====")
subprocess.run([PY, "pharma_build.py", "pharma_final.json"], check=False)

# ----- Step 4: 同步到 site/ -----
print("===== Step 4: sync to site/ =====")
site_files = ["index.html", "latest.html", "archive.html", "archive_meta.json",
              "pharma_final.json", "config.js", "pharma_fetch.py", "pharma_build.py",
              "gen_summary.py", "auto_build.py"]
for f in site_files:
    if os.path.exists(f):
        subprocess.run(["cp", f, "site/"], check=False)
import glob as _glob
for f in _glob.glob("report-*.html"):
    subprocess.run(["cp", f, "site/"], check=False)

# ----- Step 5: git push -----
print("===== Step 5: git push =====")
d = datetime.now()
try:
    subprocess.run(["git", "add", "-A"], check=False)
    subprocess.run(["git", "commit", "-m", f"auto: {d.strftime('%Y-%m-%d')} 日报"], check=False)
    subprocess.run(["git", "push", "origin", "main"], check=False)
    print("Git push done.")
except Exception as e:
    print(f"Git push failed (network?): {e}")

print("===== DONE =====")
