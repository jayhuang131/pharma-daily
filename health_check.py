# -*- coding: utf-8 -*-
"""每日晨报流水线健康检查：检查代理/报告/推送，写 health.json；失败写 NEED_FIX.flag。"""
import json, os, subprocess
from datetime import datetime

BASE = os.path.dirname(os.path.abspath(__file__))
GIT = r"C:\Users\zijia\.workbuddy\vendor\PortableGit\cmd\git.exe"
PROXY = "http://127.0.0.1:10808"


def check_proxy():
    try:
        out = subprocess.run(
            ["curl", "-s", "-o", "NUL", "-w", "%{http_code}", "--max-time", "8",
             "-x", PROXY, "https://api.github.com"],
            capture_output=True, timeout=15)
        code = out.stdout.decode("utf-8", "ignore").strip()
        return code == "200", "proxy_http_" + (code or "none")
    except Exception as e:
        return False, "proxy_error:" + str(e)[:60]


def check_report():
    p = os.path.join(BASE, "pharma_final.json")
    if not os.path.exists(p):
        return False, "no pharma_final.json"
    try:
        d = json.load(open(p, encoding="utf-8"))
        date = d.get("reportDate", "")
        total = sum(len(s.get("items", [])) for s in d.get("sections", []))
        today = datetime.now().strftime("%Y-%m-%d")
        if date != today:
            return False, f"reportDate={date} != today={today}"
        if total < 10:
            return False, f"only {total} items"
        return True, f"{date} {total} items"
    except Exception as e:
        return False, "report_error:" + str(e)[:60]


def check_push():
    try:
        head = subprocess.run([GIT, "-C", BASE, "rev-parse", "HEAD"],
                              capture_output=True, timeout=10).stdout.decode().strip()
        origin = subprocess.run([GIT, "-C", BASE, "rev-parse", "origin/main"],
                                capture_output=True, timeout=10).stdout.decode().strip()
        return head == origin, f"head={head[:8]} origin={origin[:8]}"
    except Exception as e:
        return False, "push_error:" + str(e)[:60]


def main():
    p_ok, p_msg = check_proxy()
    r_ok, r_msg = check_report()
    u_ok, u_msg = check_push()
    ok = p_ok and r_ok and u_ok
    reasons = []
    if not p_ok:
        reasons.append("proxy:" + p_msg)
    if not r_ok:
        reasons.append("report:" + r_msg)
    if not u_ok:
        reasons.append("push:" + u_msg)
    health = {
        "time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "ok": ok,
        "proxy": {"ok": p_ok, "detail": p_msg},
        "report": {"ok": r_ok, "detail": r_msg},
        "push": {"ok": u_ok, "detail": u_msg},
        "reasons": reasons,
    }
    with open(os.path.join(BASE, "health.json"), "w", encoding="utf-8") as f:
        json.dump(health, f, ensure_ascii=False, indent=1)
    flag = os.path.join(BASE, "NEED_FIX.flag")
    if not ok:
        with open(flag, "w", encoding="utf-8") as f:
            f.write(health["time"] + " | " + " ; ".join(reasons))
    else:
        try:
            os.remove(flag)
        except OSError:
            pass
    print("health:", "OK" if ok else "FAIL", "|", (" ; ".join(reasons) if reasons else "all good"))


if __name__ == "__main__":
    main()
