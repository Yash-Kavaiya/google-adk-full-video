from __future__ import annotations

import argparse
import json
import re
import urllib.parse
import urllib.request
from html import unescape
from html.parser import HTMLParser
from pathlib import Path


class MainExtractor(HTMLParser):
    def __init__(self, base_url: str) -> None:
        super().__init__(convert_charrefs=True)
        self.base_url = base_url
        self.main_depth = 0
        self.capture_depth = 0
        self.skip_depth = 0
        self.current: list[str] = []
        self.blocks: list[str] = []
        self.links: list[dict[str, str]] = []
        self.current_href: str | None = None
        self.current_link_text: list[str] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        attrs_dict = dict(attrs)
        if tag == "a" and attrs_dict.get("href"):
            self.current_href = urllib.parse.urljoin(self.base_url, attrs_dict["href"] or "")
            self.current_link_text = []
        if tag == "main":
            self.main_depth += 1
        elif self.main_depth:
            self.main_depth += 1
        if not self.main_depth:
            return
        if tag in {"script", "style", "svg", "noscript"}:
            self.skip_depth += 1
        if not self.skip_depth and tag in {"h1", "h2", "h3", "h4", "p", "li", "dt", "dd", "th", "td", "pre", "code"}:
            self.flush()
            self.capture_depth += 1

    def handle_endtag(self, tag: str) -> None:
        if tag == "a" and self.current_href:
            text = clean(" ".join(self.current_link_text))
            self.links.append({"text": text, "url": self.current_href})
            self.current_href = None
            self.current_link_text = []
        if not self.main_depth:
            return
        if tag in {"script", "style", "svg", "noscript"} and self.skip_depth:
            self.skip_depth -= 1
        if not self.skip_depth and tag in {"h1", "h2", "h3", "h4", "p", "li", "dt", "dd", "th", "td", "pre", "code"} and self.capture_depth:
            self.capture_depth -= 1
            self.flush()
        self.main_depth -= 1

    def handle_data(self, data: str) -> None:
        if self.current_href:
            self.current_link_text.append(data)
        if self.main_depth and not self.skip_depth:
            if self.capture_depth:
                self.current.append(data)

    def flush(self) -> None:
        text = clean(" ".join(self.current))
        if text and (not self.blocks or text != self.blocks[-1]):
            self.blocks.append(text)
        self.current = []


def clean(text: str) -> str:
    return re.sub(r"\s+", " ", unescape(text)).strip()


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("url")
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()
    request = urllib.request.Request(args.url, headers={"User-Agent": "Mozilla/5.0"})
    with urllib.request.urlopen(request, timeout=60) as response:
        body = response.read().decode("utf-8", "replace")
    extractor = MainExtractor(args.url)
    extractor.feed(body)
    extractor.flush()
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.with_suffix(".html").write_text(body, encoding="utf-8")
    args.out.with_suffix(".txt").write_text("\n".join(extractor.blocks) + "\n", encoding="utf-8")
    dedup: dict[str, dict[str, str]] = {}
    for link in extractor.links:
        dedup.setdefault(link["url"], link)
    args.out.with_suffix(".links.json").write_text(
        json.dumps(list(dedup.values()), ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    print(json.dumps({"url": args.url, "blocks": len(extractor.blocks), "links": len(dedup), "bytes": len(body)}))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
