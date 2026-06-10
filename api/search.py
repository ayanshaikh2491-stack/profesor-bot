import json
import urllib.request
import urllib.parse
from http.server import BaseHTTPRequestHandler


class handler(BaseHTTPRequestHandler):
    """Vercel Python serverless function — Web Search Agent"""

    def do_GET(self):
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

    def _json(self, data):
        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.send_header("Access-Control-Allow-Origin", "*")
        self.end_headers()
        self.wfile.write(json.dumps(data, ensure_ascii=False).encode())
