import json
import os
import urllib.request
import urllib.parse
from http.server import BaseHTTPRequestHandler
from pathlib import Path


class handler(BaseHTTPRequestHandler):
    """Dummy handler - redirects to main chat.py (WSGI)"""
    
    def do_GET(self):
        self.send_response(302)
        self.send_header("Location", "/")
        self.end_headers()
