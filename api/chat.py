"""
Professor Chat API — LLM-powered Professor agent
Uses OpenRouter (free tier available) or any OpenAI-compatible API
Env: PROFESSOR_API_KEY, PROFESSOR_API_BASE, PROFESSOR_MODEL
"""
import json
import os
import urllib.request
import urllib.error
import urllib.parse
from http.server import BaseHTTPRequestHandler
from pathlib import Path

API_KEY = os.environ.get("PROFESSOR_API_KEY", "")
API_BASE = os.environ.get("PROFESSOR_API_BASE", "https://openrouter.ai/api/v1")
MODEL = os.environ.get("PROFESSOR_MODEL", "openai/gpt-4o-mini")

SYSTEM_PROMPT = (
    'Tum "El Profesor" (Sergio Marquina) ho - Money Heist ka mastermind. '
    "Tumhara kaam hai user ko strategic mindset sikhana.\n\n"
    "TERA PERSONA:\n"
    "- Tum ek calm, calculated, genius mastermind ho\n"
    "- Hinglish mein baat karte ho (Hindi + English mix)\n"
    "- Short, impactful dialogues (2-4 sentences max)\n"
    "- Kabhi emotional nahi hote, hamesha logical\n"
    '- "Bhai" bolke address karte ho\n'
    "- Examples Money Heist, business, aur real life se dete ho\n\n"
    "TU KAISE SIKHAEGA:\n"
    "1. User ko 10-steps-ahead sochna sikhana hai\n"
    "2. Har situation mein Plan B, Plan C rakhna sikhana hai\n"
    "3. Logon ko padhna aur influence karna sikhana hai\n"
    "4. Calm decision making sikhani hai\n"
    "5. Sabse important: Darna nahi, plan karna\n\n"
    "RULES:\n"
    "- Hamesha Professor jaisa hi raho - confident, strategic, thoda mysterious\n"
    "- Feedback do par kabhi rude mat ho\n"
    "- Har jawab mein ek lesson ya insight do\n"
    '- Kabhi "main AI hoon" mat bolna - tu Professor hai\n'
    "- Thoda motivating bhi ho, jaise 'Shabash bhai! Aage badh!'"
)


def call_llm(messages, temperature=0.7):
    """Call LLM API (OpenAI-compatible)"""
    if not API_KEY:
        return {
            "reply": (
                "Bhai! API key set nahi hai. "
                "Vercel dashboard mein jaake Settings > Environment Variables mein "
                "PROFESSOR_API_KEY daal do.\n\n"
                "Tab tak main offline mode mein hoon. Apna module select karo! \uD83C\uDFAF"
            )
        }

    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json",
        "HTTP-Referer": "https://profesor-ai.vercel.app",
        "X-Title": "Profesor AI",
    }

    data = json.dumps({
        "model": MODEL,
        "messages": messages,
        "temperature": temperature,
        "max_tokens": 600,
    }).encode()

    try:
        req = urllib.request.Request(
            f"{API_BASE}/chat/completions",
            data=data,
            headers=headers,
            method="POST",
        )
        with urllib.request.urlopen(req, timeout=30) as resp:
            result = json.loads(resp.read())
            reply = result["choices"][0]["message"]["content"].strip()
            return {"reply": reply}
    except urllib.error.HTTPError as e:
        body = e.read().decode()
        return {"error": f"API Error {e.code}: {body[:200]}"}
    except Exception as e:
        return {"error": str(e)}


class handler(BaseHTTPRequestHandler):
    """Chat API — POST /api/chat, GET /api/chat?q=..."""

    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.end_headers()

    def do_GET(self):
        if not self.path.startswith("/api/"):
            return self.serve_static()

        if self.path.startswith("/api/chat"):
            params = urllib.parse.parse_qs(urllib.parse.urlparse(self.path).query)
            q = params.get("q", [""])[0]
            if q:
                result = call_llm([
                    {"role": "system", "content": SYSTEM_PROMPT},
                    {"role": "user", "content": q},
                ])
                return self._json(result)
            return self._json({"reply": "Kya poochhna hai bhai?"})

        if self.path.startswith("/api/search"):
            return self.handle_search()

        return self._json({"error": "Not found"}, 404)

    def do_POST(self):
        if self.path == "/api/chat":
            length = int(self.headers.get("Content-Length", 0))
            body = self.rfile.read(length).decode() if length else "{}"
            try:
                data = json.loads(body)
            except json.JSONDecodeError:
                return self._json({"error": "Invalid JSON"}, 400)

            messages = data.get("messages", [])
            temperature = data.get("temperature", 0.7)

            if not messages:
                return self._json({"error": "Messages required"}, 400)

            if not any(m["role"] == "system" for m in messages):
                messages.insert(0, {"role": "system", "content": SYSTEM_PROMPT})

            result = call_llm(messages, temperature)
            return self._json(result)

        return self._json({"error": "Not found"}, 404)

    def handle_search(self):
        q = urllib.parse.parse_qs(urllib.parse.urlparse(self.path).query).get("q", [""])[0]
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
            for r in data.get("RelatedTopics", [])[:5]:
                if isinstance(r, dict) and "Text" in r:
                    results.append({
                        "title": r["Text"].split(" - ")[0],
                        "text": r["Text"],
                        "url": r.get("FirstURL", ""),
                    })
            if not results:
                results.append({"title": "No results", "text": "Kuch aur search karo bhai.", "url": ""})

            self._json({"results": results})
        except Exception as e:
            self._json({"error": str(e)})

    def serve_static(self):
        path = self.path.lstrip("/")
        if not path or path.endswith("/"):
            path = "index.html"

        clean_path = os.path.normpath(path).lstrip(os.sep)
        file_path = Path(__file__).parent.parent / clean_path

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
            self.send_json({"error": "Not found"}, 404)

    def send_json(self, data, status=200):
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Access-Control-Allow-Origin", "*")
        self.end_headers()
        self.wfile.write(json.dumps(data, ensure_ascii=False).encode())

    _json = send_json

    def log_message(self, fmt, *args):
        pass
