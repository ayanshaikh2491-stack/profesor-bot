import json
import os
import urllib.request
import urllib.parse
from http.server import BaseHTTPRequestHandler
from pathlib import Path


class handler(BaseHTTPRequestHandler):
    """Vercel Python serverless — Web Search API + Static file fallback"""

    def do_GET(self):
        # API endpoint
        if self.path.startswith("/api/search"):
            return self.handle_search()

        # Serve static files
        return self.serve_static()

    def handle_search(self):
        from urllib.parse import urlparse, parse_qs
        q = parse_qs(urlparse(self.path).query).get("q", [""])[0]

        if not q:
            return self._json({"error": "No query"})

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

            self._json({"results": results})
        except Exception as e:
            self._json({"error": str(e)})

    def serve_static(self):
        """Serve static files"""
        # Determine file path
        path = self.path.lstrip("/")
        if not path or path.endswith("/"):
            path = "index.html"

        # Security: prevent directory traversal
        clean_path = os.path.normpath(path).lstrip(os.sep)
        file_path = Path(__file__).parent.parent / clean_path

        # MIME types
        mime_map = {
            ".html": "text/html; charset=utf-8",
            ".js": "application/javascript",
            ".css": "text/css",
            ".json": "application/json",
            ".png": "image/png",
            ".ico": "image/x-icon",
            ".svg": "image/svg+xml",
        }

        ext = os.path.splitext(str(file_path))[1].lower()
        content_type = mime_map.get(ext, "application/octet-stream")

        try:
            with open(file_path, "rb") as f:
                content = f.read()
            self.send_response(200)
            self.send_header("Content-Type", content_type)
            self.send_header("Content-Length", str(len(content)))
            self.send_header("Access-Control-Allow-Origin", "*")
            self.send_header("Service-Worker-Allowed", "/")
            self.end_headers()
            self.wfile.write(content)
        except (FileNotFoundError, PermissionError):
            self.send_response(404)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(json.dumps({"error": "Not found"}).encode())

    def _json(self, data):
        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.send_header("Access-Control-Allow-Origin", "*")
        self.end_headers()
        self.wfile.write(json.dumps(data, ensure_ascii=False).encode())
