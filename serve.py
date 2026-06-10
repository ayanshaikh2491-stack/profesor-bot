"""
Professor Server — Render deployment
Web search agent + PWA app
"""
import os
import json
import urllib.request
import urllib.parse
import sys
from pathlib import Path
from http.server import HTTPServer, SimpleHTTPRequestHandler
from socketserver import ThreadingMixIn

PORT = int(os.getenv("PORT", 8000))
HOST = "0.0.0.0"
DIR = Path(__file__).parent


class ThreadedServer(ThreadingMixIn, HTTPServer):
    """Multi-threaded server so search doesn't block other requests"""
    allow_reuse_address = True


class ProfessorHandler(SimpleHTTPRequestHandler):
    """Handler with PWA headers + web search API"""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=str(DIR), **kwargs)

    def end_headers(self):
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Service-Worker-Allowed", "/")
        self.send_header("Cache-Control", "no-cache")
        super().end_headers()

    def do_OPTIONS(self):
        self.send_response(200)
        self.end_headers()

    def do_GET(self):
        if self.path.startswith("/api/search?"):
            return self.handle_search()
        super().do_GET()

    def handle_search(self):
        """DuckDuckGo web search — no API key needed"""
        from urllib.parse import urlparse, parse_qs
        q = parse_qs(urlparse(self.path).query).get("q", [""])[0]
        if not q:
            return self.send_json({"error": "No query"})

        try:
            url = f"https://api.duckduckgo.com/?q={urllib.parse.quote(q)}&format=json&no_html=1"
            req = urllib.request.Request(url, headers={"User-Agent": "ProfesorBot/1.0"})
            with urllib.request.urlopen(req, timeout=10) as resp:
                data = json.loads(resp.read())

            results = []
            if data.get("AbstractText"):
                results.append({
                    "title": "Summary",
                    "text": data["AbstractText"],
                    "url": data.get("AbstractURL", ""),
                })
            if data.get("RelatedTopics"):
                for r in data["RelatedTopics"][:5]:
                    if isinstance(r, dict) and "Text" in r:
                        results.append({
                            "title": r.get("Text", "").split(" - ")[0],
                            "text": r.get("Text", ""),
                            "url": r.get("FirstURL", ""),
                        })
            if not results:
                results.append({"title": "No results", "text": "Try a different query.", "url": ""})

            self.send_json({"results": results})
        except Exception as e:
            self.send_json({"error": str(e)})

    def send_json(self, data):
        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.end_headers()
        self.wfile.write(json.dumps(data, ensure_ascii=False).encode())

    def log_message(self, fmt, *args):
        sys.stderr.write(f"[Professor] {args[0] if args else ''}\n")


def main():
    print()
    print("=" * 55)
    print("  PROFESSOR AGENT — Starting on Render")
    print("=" * 55)
    print(f"  Port: {PORT}")
    print(f"  Serving: {DIR}")
    print(f"  Web Intel API: /api/search?q=...")
    print("=" * 55)
    print()

    server = ThreadedServer((HOST, PORT), ProfessorHandler)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nProfessor signing off...")
        server.server_close()


if __name__ == "__main__":
    main()
