
from fastapi import FastAPI, HTTPException
from typing import Tuple, List, Set, Iterable, Optional
from urllib.parse import urljoin, urlparse
from urllib.request import Request, urlopen
from urllib.robotparser import RobotFileParser
from html.parser import HTMLParser
from collections import deque
import os
import ssl
import re
import time

app = FastAPI()

# ---- Simple HTML text extractor (ignores <script>, <style>, <noscript>) ----
class TextExtractor(HTMLParser):
    def __init__(self):
        super().__init__()
        self._texts: List[str] = []
        self._ignore_stack: List[str] = []

    def handle_starttag(self, tag, attrs):
        if tag in ("script", "style", "noscript"):
            self._ignore_stack.append(tag)

    def handle_endtag(self, tag):
        if self._ignore_stack and self._ignore_stack[-1] == tag:
            self._ignore_stack.pop()

    def handle_data(self, data):
        if not self._ignore_stack:
            # Collapse whitespace segments to single spaces for cleanliness
            text = re.sub(r"\s+", " ", data)
            if text.strip():
                self._texts.append(text.strip())

    def get_text(self) -> str:
        return " ".join(self._texts)

def extract_text_from_html(html: str) -> str:
    parser = TextExtractor()
    parser.feed(html)
    parser.close()
    text = parser.get_text()
    # Optional: normalize excessive spaces/newlines further
    text = re.sub(r"\s{2,}", " ", text).strip()
    return text

# ---- HTML link extractor for <a href="..."> ----
class LinkExtractor(HTMLParser):
    def __init__(self, base_url: str):
        super().__init__()
        self.base_url = base_url
        self.links: Set[str] = set()

    def handle_starttag(self, tag, attrs):
        if tag == "a":
            for (k, v) in attrs:
                if k == "href" and v:
                    try:
                        abs_url = urljoin(self.base_url, v)
                        self.links.add(abs_url)
                    except Exception:
                        pass

def extract_links(html: str, base_url: str) -> Set[str]:
    parser = LinkExtractor(base_url)
    parser.feed(html)
    parser.close()
    return parser.links

# ---- robots.txt helper ----
def build_robot_parser(start_url: str, user_agent: str) -> RobotFileParser:
    parsed = urlparse(start_url)
    robots_url = f"{parsed.scheme}://{parsed.netloc}/robots.txt"
    rp = RobotFileParser()
    rp.set_url(robots_url)
    try:
        # May fail if robots.txt doesn’t exist; that’s fine—default allow
        rp.read()
    except Exception:
        pass
    return rp

# ---- Core crawler (same-domain BFS, robots-aware) ----
def crawl_site(
    start_url: str,
    max_pages: int = 30,
    max_bytes: int = 5_000_000,  # total HTML bytes cap (politeness & memory)
    request_timeout: int = 10,
    sleep_between: float = 0.0,  # set to 0.5–1.0 to be extra polite
) -> Tuple[str, List[str]]:
    """
    Returns (full_text, visited_urls)
    """
    parsed_start = urlparse(start_url)
    if parsed_start.scheme not in ("http", "https") or not parsed_start.netloc:
        raise ValueError("Invalid start URL")

    same_netloc = parsed_start.netloc
    context = ssl.create_default_context()
    user_agent = "SiteIngestBot/1.0 (+https://yourdomain.example/bot-info)"  # customize
    headers = {"User-Agent": user_agent}

    rp = build_robot_parser(start_url, user_agent)

    visited: Set[str] = set()
    queue: deque[str] = deque([start_url])
    total_bytes = 0
    texts: List[str] = []

    while queue and len(visited) < max_pages and total_bytes < max_bytes:
        url = queue.popleft()
        if url in visited:
            continue
        visited.add(url)

        p = urlparse(url)
        if p.scheme not in ("http", "https") or p.netloc != same_netloc:
            continue

        # robots.txt check
        try:
            if hasattr(rp, "can_fetch") and not rp.can_fetch(user_agent, url):
                continue
        except Exception:
            # If robots check fails, default to skipping
            continue

        # Fetch
        try:
            req = Request(url, headers=headers)
            with urlopen(req, timeout=request_timeout, context=context) as resp:
                ctype = resp.headers.get("Content-Type", "")
                if "text/html" not in ctype:
                    continue
                raw = resp.read()
                total_bytes += len(raw)
                if total_bytes > max_bytes:
                    break
                html = raw.decode("utf-8", errors="ignore")
        except Exception:
            continue

        # Extract readable text
        page_text = extract_text_from_html(html)
        if page_text:
            texts.append(page_text)

        # Extract and enqueue same-domain links
        try:
            links = extract_links(html, url)
            for link in links:
                pl = urlparse(link)
                if pl.scheme in ("http", "https") and pl.netloc == same_netloc:
                    if link not in visited:
                        queue.append(link)
        except Exception:
            pass

        if sleep_between > 0:
            time.sleep(sleep_between)

    full_text = ("\n\n").join(texts)
    return full_text, list(visited)

# ---- Utility: keep the single-vector idea safe for large sites ----
def clamp_text(text: str, max_chars: int = 200_000) -> str:
    """
    If your embedder has token/length limits, clamp here so we still produce one vector.
    Adjust max_chars to your model’s true capacity (e.g., ~8k tokens ~ 32k-48k chars).
    """
    if len(text) <= max_chars:
        return text
    # Simple truncation; you could do smarter summarization if needed
    return text[:max_chars]