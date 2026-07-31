# -*- coding: utf-8 -*-
"""生物医药晨报 —— 收藏同步服务（零依赖，仅用标准库）。

启动：  python pharma_server.py [port]
默认端口 8000，监听 0.0.0.0（同局域网设备均可访问）。

功能：
  - 静态托管当前目录下的日报 HTML（index.html / report-*.html / bio_pharma_morning_report.html）
  - /api/favs
        GET    -> 返回收藏列表 JSON（[{url,title,section,ts}, ...]）
        POST   -> 新增一条收藏（body: JSON {url,title,section,ts}），按 url 去重
        DELETE -> 删除一条收藏（?url=...）
  收藏持久化在 favs.json，所有访问同一服务的设备 / 浏览器共享 -> 天然跨设备同步。

可选鉴权：设置环境变量 FAV_TOKEN，则所有 /api/favs 请求需带
          Header: X-Fav-Token: <token>   或  ?token=<token>
          适合把服务暴露到公网时使用。
"""
import json, os, sys, time, threading
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import urlparse, parse_qs, unquote

ROOT = os.path.dirname(os.path.abspath(__file__))
FAVS_PATH = os.path.join(ROOT, "favs.json")
# 令牌优先级：环境变量 FAV_TOKEN > 同目录 sync_token.txt（首行）。留空则不做鉴权。
TOKEN = os.environ.get("FAV_TOKEN", "").strip()
if not TOKEN:
    _tok_file = os.path.join(ROOT, "sync_token.txt")
    if os.path.exists(_tok_file):
        try:
            with open(_tok_file, encoding="utf-8") as _f:
                TOKEN = _f.readline().strip()
        except Exception:
            TOKEN = ""
_lock = threading.Lock()


def load_favs():
    if not os.path.exists(FAVS_PATH):
        return []
    try:
        with open(FAVS_PATH, encoding="utf-8") as f:
            data = json.load(f)
            return data if isinstance(data, list) else []
    except Exception:
        return []


def save_favs(arr):
    tmp = FAVS_PATH + ".tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(arr, f, ensure_ascii=False, indent=1)
    os.replace(tmp, FAVS_PATH)


class Handler(BaseHTTPRequestHandler):
    protocol_version = "HTTP/1.1"

    def log_message(self, *a):
        pass  # 静默访问日志

    def _read_body(self):
        try:
            ln = int(self.headers.get("Content-Length", 0) or 0)
        except Exception:
            ln = 0
        if ln <= 0:
            return b""
        buf = bytearray()
        while len(buf) < ln:
            chunk = self.rfile.read(min(ln - len(buf), 65536))
            if not chunk:
                break
            buf.extend(chunk)
        return bytes(buf)

    def _auth_ok(self):
        if not TOKEN:
            return True
        h = self.headers.get("X-Fav-Token", "")
        q = parse_qs(urlparse(self.path).query).get("token", [""])[0]
        return h == TOKEN or q == TOKEN

    def _send_json(self, obj, code=200):
        body = json.dumps(obj, ensure_ascii=False).encode("utf-8")
        self.send_response(code)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(body)

    def _send_file(self, path):
        try:
            with open(path, "rb") as f:
                body = f.read()
        except Exception:
            self.send_error(404, "Not Found")
            return
        ext = os.path.splitext(path)[1].lower()
        ct = {
            "html": "text/html; charset=utf-8",
            "css": "text/css",
            "js": "application/javascript",
            "json": "application/json",
            "svg": "image/svg+xml",
        }.get(ext, "application/octet-stream")
        self.send_response(200)
        self.send_header("Content-Type", ct)
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self):
        u = urlparse(self.path)
        if u.path == "/api/favs":
            if not self._auth_ok():
                self._send_json({"error": "unauthorized"}, 401)
                return
            self._send_json(load_favs())
            return
        if u.path in ("", "/"):
            p = os.path.join(ROOT, "index.html")
        else:
            rel = unquote(u.path).lstrip("/").replace("\\", "/")
            p = os.path.normpath(os.path.join(ROOT, rel))
            if not p.startswith(ROOT):
                self.send_error(403, "Forbidden")
                return
        if os.path.isdir(p):
            p = os.path.join(p, "index.html")
        if not os.path.exists(p):
            self.send_error(404, "Not Found")
            return
        self._send_file(p)

    def _parse_json(self, raw):
        for enc in ("utf-8-sig", "utf-8", "gbk", "latin-1"):
            try:
                return json.loads(raw.decode(enc))
            except Exception:
                continue
        return {}

    def do_POST(self):
        u = urlparse(self.path)
        if u.path != "/api/favs":
            self.send_error(404)
            return
        if not self._auth_ok():
            self._send_json({"error": "unauthorized"}, 401)
            return
        raw = self._read_body()
        obj = self._parse_json(raw)
        url = (obj.get("url") or "").strip()
        if not url:
            self._send_json({"error": "url required"}, 400)
            return
        with _lock:
            favs = load_favs()
            if not any(f.get("url") == url for f in favs):
                favs.append({
                    "url": url,
                    "title": obj.get("title", ""),
                    "section": obj.get("section", ""),
                    "ts": int(obj.get("ts", 0) or time.time() * 1000),
                })
                save_favs(favs)
        self._send_json(favs)

    def do_DELETE(self):
        u = urlparse(self.path)
        if u.path != "/api/favs":
            self.send_error(404)
            return
        if not self._auth_ok():
            self._send_json({"error": "unauthorized"}, 401)
            return
        url = parse_qs(u.query).get("url", [""])[0].strip()
        if not url:
            self._send_json({"error": "url required"}, 400)
            return
        with _lock:
            favs = [f for f in load_favs() if f.get("url") != url]
            save_favs(favs)
        self._send_json(favs)


if __name__ == "__main__":
    port = int(sys.argv[1]) if len(sys.argv) > 1 else 8000
    bind = os.environ.get("FAV_BIND", "0.0.0.0")
    srv = ThreadingHTTPServer((bind, port), Handler)
    print(f"生物医药晨报同步服务已启动： http://{bind}:{port}/")
    print(f"收藏数据文件： {FAVS_PATH}")
    if TOKEN:
        print("已启用 Token 鉴权（环境变量 FAV_TOKEN）。")
    try:
        srv.serve_forever()
    except KeyboardInterrupt:
        print("\n服务已停止。")
