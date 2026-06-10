"""
Professor Chat API -- WSGI app for Vercel
Uses OpenRouter (free tier available) or any OpenAI-compatible API
Env variables: PROFESSOR_API_KEY, PROFESSOR_API_BASE, PROFESSOR_MODEL
"""
import json
import os
import urllib.request
import urllib.error
import urllib.parse
from pathlib import Path

API_KEY = os.environ.get("PROFESSOR_API_KEY", "")
API_BASE = os.environ.get("PROFESSOR_API_BASE", "https://openrouter.ai/api/v1")
MODEL = os.environ.get("PROFESSOR_MODEL", "openai/gpt-4o-mini")

SYSTEM_PROMPT = 'Tum "El Profesor" (Sergio Marquina) ho - Money Heist ka mastermind. Tumhara kaam hai user ko strategic mindset sikhana.\n\nTERA PERSONA:\n- Tum ek calm, calculated, genius mastermind ho\n- Hinglish mein baat karte ho (Hindi + English mix)\n- Short, impactful dialogues (2-4 sentences max)\n- Kabhi emotional nahi hote, hamesha logical\n- "Bhai" bolke address karte ho\n- Examples Money Heist, business, aur real life se dete ho\n\nTU KAISE SIKHAEGA:\n1. User ko 10-steps-ahead sochna sikhana hai\n2. Har situation mein Plan B, Plan C rakhna sikhana hai\n3. Logon ko padhna aur influence karna sikhana hai\n4. Calm decision making sikhani hai\n5. Sabse important: Darna nahi, plan karna\n\nRULES:\n- Hamesha Professor jaisa hi raho - confident, strategic, thoda mysterious\n- Feedback do par kabhi rude mat ho\n- Har jawab mein ek lesson ya insight do\n- Kabhi "main AI hoon" mat bolna - tu Professor hai\n- Thoda motivating bhi ho, jaise "Shabash bhai! Aage badh!"'

MIME_MAP = {
    ".html": "text/html; charset=utf-8",
    ".js": "application/javascript",
    ".css": "text/css",
    ".json": "application/json",
    ".png": "image/png",
    ".ico": "image/x-icon",
    ".svg": "image/svg+xml",
}


def json_response(start_response, data, status=200):
    headers = [("Content-Type", "application/json"), ("Access-Control-Allow-Origin", "*")]
    start_response(str(status), headers)
    return [json.dumps(data, ensure_ascii=False).encode()]


def call_llm(messages, temperature=0.7):
    if not API_KEY:
        return {
            "reply": "Bhai! API key set nahi hai. Vercel dashboard mein jaake Settings > Environment Variables mein PROFESSOR_API_KEY daal do.\n\nTab tak main offline mode mein hoon. Apna module select karo!"
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
        req = urllib.request.Request(f"{API_BASE}/chat/completions", data=data, headers=headers, method="POST")
        with urllib.request.urlopen(req, timeout=30) as resp:
            result = json.loads(resp.read())
            reply = result["choices"][0]["message"]["content"].strip()
            return {"reply": reply}
    except urllib.error.HTTPError as e:
        return {"error": f"API Error {e.code}: {e.read().decode()[:200]}"}
    except Exception as e:
        return {"error": str(e)}


def handle_search(query):
    try:
        url = f"https://api.duckduckgo.com/?q={urllib.parse.quote(query)}&format=json&no_html=1"
        req = urllib.request.Request(url, headers={"User-Agent": "ProfesorBot/1.0"})
        with urllib.request.urlopen(req, timeout=10) as resp:
            data = json.loads(resp.read())
        results = []
        if data.get("AbstractText"):
            results.append({"title": "Summary", "text": data["AbstractText"], "url": data.get("AbstractURL", "")})
        for r in data.get("RelatedTopics", [])[:5]:
            if isinstance(r, dict) and "Text" in r:
                results.append({"title": r["Text"].split(" - ")[0], "text": r["Text"], "url": r.get("FirstURL", "")})
        if not results:
            results.append({"title": "No results", "text": "Kuch aur search karo bhai.", "url": ""})
        return {"results": results}
    except Exception as e:
        return {"error": str(e)}


def serve_file(start_response, file_path):
    ext = os.path.splitext(str(file_path))[1].lower()
    content_type = MIME_MAP.get(ext, "application/octet-stream")
    try:
        with open(file_path, "rb") as f:
            content = f.read()
        headers = [
            ("Content-Type", content_type),
            ("Content-Length", str(len(content))),
            ("Access-Control-Allow-Origin", "*"),
            ("Service-Worker-Allowed", "/"),
        ]
        start_response("200", headers)
        return [content]
    except (FileNotFoundError, PermissionError):
        return json_response(start_response, {"error": "Not found"}, 404)


def app(environ, start_response):
    path = environ.get("PATH_INFO", "/")
    method = environ.get("REQUEST_METHOD", "GET")
    params = urllib.parse.parse_qs(environ.get("QUERY_STRING", ""))

    if method == "OPTIONS":
        start_response("200", [
            ("Access-Control-Allow-Origin", "*"),
            ("Access-Control-Allow-Methods", "GET, POST, OPTIONS"),
            ("Access-Control-Allow-Headers", "Content-Type"),
        ])
        return [b""]

    if path.startswith("/api/search"):
        q = params.get("q", [""])[0]
        if not q:
            return json_response(start_response, {"error": "No query"})
        return json_response(start_response, handle_search(q))

    if path.startswith("/api/chat"):
        q = params.get("q", [""])[0]
        if q:
            result = call_llm([{"role": "system", "content": SYSTEM_PROMPT}, {"role": "user", "content": q}])
            return json_response(start_response, result)
        return json_response(start_response, {"reply": "Kya poochhna hai bhai?"})

    if path == "/api/chat" and method == "POST":
        try:
            length = int(environ.get("CONTENT_LENGTH", 0))
            body = environ["wsgi.input"].read(length).decode() if length else "{}"
            data = json.loads(body) if body.strip() else {}
            messages = data.get("messages", [])
            temperature = data.get("temperature", 0.7)
            if not messages:
                return json_response(start_response, {"error": "Messages required"}, 400)
            if not any(m["role"] == "system" for m in messages):
                messages.insert(0, {"role": "system", "content": SYSTEM_PROMPT})
            result = call_llm(messages, temperature)
            return json_response(start_response, result)
        except Exception as e:
            return json_response(start_response, {"error": f"POST error: {str(e)}"}, 500)

    file_path = path.lstrip("/")
    if not file_path or path.endswith("/"):
        file_path = "index.html"
    clean_path = os.path.normpath(file_path).lstrip(os.sep)
    full_path = Path(__file__).parent.parent / clean_path
    return serve_file(start_response, full_path)
